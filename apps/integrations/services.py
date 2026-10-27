
import os
import re
from urllib.parse import urlparse

import requests
from django.core.exceptions import ImproperlyConfigured


GITHUB_API = "https://api.github.com"
REQUEST_TIMEOUT = 20


class GitHubIntegrationError(Exception):
    """Raised when a GitHub repository cannot be inspected."""


def parse_github_url(repository_url):
    """Accept a GitHub repository URL and return its owner and name."""
    parsed = urlparse(repository_url.strip())

    if parsed.scheme != "https" or parsed.hostname != "github.com":
        raise GitHubIntegrationError(
            "Enter a valid HTTPS URL from github.com."
        )

    if parsed.query or parsed.fragment:
        raise GitHubIntegrationError(
            "Repository URLs must not contain query parameters or fragments."
        )

    parts = [part for part in parsed.path.strip("/").split("/") if part]

    if len(parts) != 2:
        raise GitHubIntegrationError(
            "Enter a repository URL such as "
            "https://github.com/owner/repository."
        )

    owner, name = parts
    name = re.sub(r"\.git$", "", name)

    if not owner or not name:
        raise GitHubIntegrationError("The repository URL is incomplete.")

    return owner, name




def _github_get(path):
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise ImproperlyConfigured(
            "GITHUB_TOKEN is missing. Add it to your local .env file."
        )

    try:
        response = requests.get(
            f"{GITHUB_API}{path}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise GitHubIntegrationError(
            "Could not reach GitHub. Check your internet connection and try again."
        ) from exc

    status_code = response.status_code

    if status_code == 401:
        raise GitHubIntegrationError(
            "GitHub rejected the token. Check that GITHUB_TOKEN is valid."
        )

    if status_code == 404:
        raise GitHubIntegrationError(
            "Repository or resource not found, or your token cannot access it."
        )

    if status_code in (403, 429):
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            raise GitHubIntegrationError(
                f"GitHub asked us to retry after {retry_after} seconds."
            )

        if remaining == "0" or status_code == 429:
            message = "GitHub API rate limit reached."
            if reset:
                message += (
                    f" The rate limit resets at Unix timestamp {reset}."
                )
            raise GitHubIntegrationError(message)

        raise GitHubIntegrationError(
            "GitHub denied access. Check the token's repository permissions "
            "and whether the account can access this repository."
        )

    if not response.ok:
        raise GitHubIntegrationError(
            f"GitHub returned HTTP {status_code}."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise GitHubIntegrationError(
            "GitHub returned an unexpected response."
        ) from exc

    """Retrieve repository paths from the latest commit's recursive Git tree.

    Return a bounded list of entries, whether the tree was truncated,
    and an error message if the tree could not be inspected.
    """
    if not latest_commit_sha:
        return [], False, "No commit SHA was available to inspect the tree."

    try:
        commit_data = _github_get(
            f"{base_path}/git/commits/{latest_commit_sha}"
        )
        tree_sha = commit_data.get("tree", {}).get("sha")

        if not tree_sha:
            return [], False, "GitHub did not return a tree SHA."

        tree_data = _github_get(
            f"{base_path}/git/trees/{tree_sha}?recursive=1"
        )
        entries = tree_data.get("tree", [])

        if not isinstance(entries, list):
            return [], False, "GitHub returned an unexpected tree structure."

        # Bound the amount of tree data retained by the application.
        limit = 5000
        normalized_entries = [
            {
                "path": entry.get("path", ""),
                "type": entry.get("type", ""),
                "size": entry.get("size"),
            }
            for entry in entries[:limit]
            if entry.get("path")
        ]

        was_truncated = bool(tree_data.get("truncated")) or len(entries) > limit

        return normalized_entries, was_truncated, ""

    except GitHubIntegrationError as exc:
        return [], False, str(exc)


def inspect_repository(owner, name):
    """Read repository metadata, root files, README and latest commit."""
    encoded_owner = requests.utils.quote(owner, safe="")
    encoded_name = requests.utils.quote(name, safe="")
    base_path = f"/repos/{encoded_owner}/{encoded_name}"

    metadata = _github_get(base_path)
    contents = _github_get(f"{base_path}/contents")
    commits = _github_get(f"{base_path}/commits")

    if not isinstance(contents, list) or not isinstance(commits, list):
        raise GitHubIntegrationError(
            "GitHub returned an unexpected repository structure."
        )

    readme = ""
    readme_url = metadata.get("html_url", "").rstrip("/") + "/blob/"

    try:
        readme_data = _github_get(f"{base_path}/readme")
        readme_download_url = readme_data.get("download_url")

        if readme_download_url:
            # Only fetch content from GitHub's raw-content host.
            parsed_download = urlparse(readme_download_url)
            if parsed_download.hostname != "raw.githubusercontent.com":
                raise GitHubIntegrationError(
                    "GitHub returned an unexpected README download URL."
                )

            response = requests.get(
                readme_download_url,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            readme = response.text[:50000]
    except GitHubIntegrationError as exc:
        if "unexpected README download URL" in str(exc):
            raise
        # A missing README should not prevent repository inspection.
    except requests.RequestException:
        # Repository metadata and file listing are still useful.
        pass

    latest_commit = commits[0] if commits else {}
    commit_info = latest_commit.get("commit", {})
    
    tree_entries, tree_truncated, tree_error = inspect_repository_tree(
        base_path,
        latest_commit.get("sha",""),
    )

    return {
        "full_name": metadata.get("full_name", f"{owner}/{name}"),
        "html_url": metadata.get("html_url", ""),
        "description": metadata.get("description") or "",
        "private": metadata.get("private", False),
        "default_branch": metadata.get("default_branch", ""),
        "stars": metadata.get("stargazers_count", 0),
        "language": metadata.get("language"),
        "root_files": [
            {
                "name": item.get("name", ""),
                "type": item.get("type", ""),
                "path": item.get("path", ""),
            }
            for item in contents[:100]
        ],
        "readme": readme,
        "full_tree" : tree_entries,
        "tree_truncated" : tree_truncated,
        "tree_error" : tree_error,
        "latest_commit_sha": latest_commit.get("sha", ""),
        "latest_commit_message": commit_info.get("message", ""),
        "latest_commit_date": (
            commit_info.get("author", {}).get("date", "")
        ),
    }
