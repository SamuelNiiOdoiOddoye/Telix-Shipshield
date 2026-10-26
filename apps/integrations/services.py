
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

    if response.status_code == 404:
        raise GitHubIntegrationError(
            "Repository not found or your token cannot access it."
        )

    if response.status_code == 401:
        raise GitHubIntegrationError(
            "GitHub rejected the token. Check GITHUB_TOKEN."
        )

    if response.status_code == 403:
        raise GitHubIntegrationError(
            "GitHub denied the request or a rate limit was reached."
        )

    if not response.ok:
        raise GitHubIntegrationError(
            f"GitHub returned HTTP {response.status_code}."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise GitHubIntegrationError(
            "GitHub returned an unexpected response."
        ) from exc


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
        "latest_commit_sha": latest_commit.get("sha", ""),
        "latest_commit_message": commit_info.get("message", ""),
        "latest_commit_date": (
            commit_info.get("author", {}).get("date", "")
        ),
    }
