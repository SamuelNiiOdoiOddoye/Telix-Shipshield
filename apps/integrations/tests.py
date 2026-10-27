
import os
from unittest.mock import Mock, patch

from django.core.exceptions import ImproperlyConfigured

from apps.integrations.services import (
    GitHubIntegrationError,
    _github_get,
)

from django.test import SimpleTestCase

from apps.integrations.views import build_health_findings


class RepositoryHealthAuditTests(SimpleTestCase):
    
    def setUp(self):
        self.details = {
            "full_name": "example/project",
            "html_url": "https://github.com/example/project",
            "default_branch": "main",
            "latest_commit_sha": "abc123",
            "root_files": [
                {"name": "README.md", "type": "file", "path": "README.md"},
                {"name": "requirements.txt", "type": "file", "path": "requirements.txt"},
                {"name": "tests", "type": "dir", "path": "tests"},
                {"name": ".github", "type": "dir", "path": ".github"},
            ],
            "full_tree" : [
                {"path" : "README.md", "type" : "blob"},
                {"path" : "backend/pyproject.toml", "type":"blob"},
                {"path" : "apps/example/tests/test_example.py", "type":"blob"},
                {"path" : ".github/workflows/ci.yml", "type" : "blob"},
            ],
            "tree_truncated" : False,
            "tree_error" : "",
            "readme": (
                "# Example Project\n\n"
                "## Installation and Setup\n"
                "Install dependencies before running the project.\n\n"
                "## Usage\n"
                "Run the application.\n\n"
                "## Testing\n"
                "Run the test suite.\n"
            ),
        }

    def test_detects_readme_manifest_tests_and_ci_indicators(self):
        findings = build_health_findings(self.details)
        by_id = {finding["id"]: finding for finding in findings}

        self.assertEqual(by_id["readme_presence"]["status"], "passed")
        self.assertEqual(by_id["dependency_manifest"]["status"], "passed")
        self.assertEqual(by_id["test_presence"]["status"], "passed")
        self.assertEqual(by_id["ci_presence"]["status"], "passed")

    def test_detects_missing_readme_sections(self):
        self.details["readme"] = "# Example Project\n\nA short description."
        findings = build_health_findings(self.details)
        by_id = {finding["id"]: finding for finding in findings}

        self.assertEqual(by_id["readme_setup"]["status"], "failed")
        self.assertTrue(by_id["readme_setup"]["recommendation"])
        self.assertEqual(by_id["readme_usage"]["status"], "failed")
        self.assertEqual(by_id["readme_testing"]["status"], "failed")

    def test_missing_test_indicators_are_unverified_not_failed(self):
        details = {
            **self.details,
            "root_files": [
                {"name": "README.md", "type": "file", "path": "README.md"},
            ],
            "full_tree": [
                {"path": "README.md", "type": "blob"},
            ],
            "tree_truncated": False,
            "tree_error": "",
        }

        findings = build_health_findings(details)
        by_id = {finding["id"]: finding for finding in findings}

        self.assertEqual(by_id["test_presence"]["status"], "unverified")
        self.assertTrue(by_id["test_presence"]["recommendation"])

        details = {
            **self.details,
            "full_tree" : [
                {"path": "README.md", "type":"blob"},
            ],
            "tree_truncated":False,
            "tree_error":"",
        }
        
        self.details["root_files"] = [
            {"name": "README.md", "type": "file", "path": "README.md"},
        ]
        findings = build_health_findings(details)
        by_id = {finding["id"]: finding for finding in findings}

        self.assertEqual(by_id["test_presence"]["status"], "unverified")
        self.assertTrue(by_id["test_presence"]["recommendation"])

    def test_missing_readme_is_a_failed_check(self):
        self.details["root_files"] = [
            {"name": "requirements.txt", "type": "file", "path": "requirements.txt"},
        ]
        self.details["readme"] = ""

        findings = build_health_findings(self.details)
        by_id = {finding["id"]: finding for finding in findings}

        self.assertEqual(by_id["readme_presence"]["status"], "failed")
        self.assertTrue(by_id["readme_presence"]["evidence"])
        self.assertTrue(by_id["readme_presence"]["recommendation"])

    def test_findings_include_evidence_and_status(self):
        findings = build_health_findings(self.details)

        self.assertTrue(findings)

        for finding in findings:
            self.assertIn(
                finding["status"],
                {"passed", "failed", "unverified"},
            )
            self.assertTrue(finding["evidence"])
            self.assertIn("summary", finding)
            self.assertIn("recommendation", finding)

    def test_finding_ids_are_unique(self):
        findings = build_health_findings(self.details)
        finding_ids = [finding["id"] for finding in findings]

        self.assertEqual(
            len(finding_ids),
            len(set(finding_ids)),
            "Each repository health finding must have a unique ID.",
        )

    def test_detects_nested_dependency_manifest(self):
        findings = build_health_findings(self.details)
        manifest = next(
            item for item in findings
            if item["id"] == "dependency_manifest"
        )

        self.assertEqual(manifest["status"], "passed")
        self.assertTrue(
            any(
                evidence["source_path"] == "backend/pyproject.toml"
                for evidence in manifest["evidence"]
            )
        )

    def test_detects_nested_test_file(self):
        findings = build_health_findings(self.details)
        tests = next(
            item for item in findings
            if item["id"] == "test_presence"
        )

        self.assertEqual(tests["status"], "passed")
        self.assertTrue(
            any(
                evidence["source_path"]
                == "apps/example/tests/test_example.py"
                for evidence in tests["evidence"]
            )
        )

    def test_detects_github_actions_workflow(self):
        findings = build_health_findings(self.details)
        ci = next(
            item for item in findings
            if item["id"] == "ci_presence"
        )

        self.assertEqual(ci["status"], "passed")
        self.assertTrue(
            any(
                evidence["source_path"] == ".github/workflows/ci.yml"
                for evidence in ci["evidence"]
            )
        )

    def test_detecting_test_files_does_not_claim_tests_passed(self):
        findings = build_health_findings(self.details)
        by_id = {finding["id"]: finding for finding in findings}

        self.assertEqual(by_id["test_presence"]["status"], "passed")
        self.assertEqual(by_id["test_execution"]["status"], "unverified")

    def test_detecting_ci_config_does_not_claim_workflow_succeeded(self):
        findings = build_health_findings(self.details)
        by_id = {finding["id"]: finding for finding in findings}

        self.assertEqual(by_id["ci_presence"]["status"], "passed")
        self.assertEqual(by_id["ci_execution"]["status"], "unverified")

    def test_incomplete_tree_does_not_claim_indicators_are_absent(self):
        details = {
            **self.details,
            "full_tree": [],
            "tree_truncated": True,
        }

        findings = build_health_findings(details)
        relevant_ids = {
            "dependency_manifest",
            "test_presence",
            "ci_presence",
        }

        for finding in findings:
            if finding["id"] in relevant_ids:
                self.assertEqual(finding["status"], "unverified")


class GitHubAPIErrorHandlingTests(SimpleTestCase):
    """Test GitHub API handling without making real HTTP requests."""

    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "test-token"},
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @patch("apps.integrations.services.requests.get")
    def test_successful_response_returns_json(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = {"full_name": "owner/repository"}
        response.headers = {}
        mock_get.return_value = response

        result = _github_get("/repos/owner/repository")

        self.assertEqual(
            result,
            {"full_name": "owner/repository"},
        )
        mock_get.assert_called_once()

    @patch("apps.integrations.services.requests.get")
    def test_401_reports_invalid_token(self, mock_get):
        response = Mock()
        response.status_code = 401
        response.headers = {}
        mock_get.return_value = response

        with self.assertRaisesMessage(
            GitHubIntegrationError,
            "GitHub rejected the token",
        ):
            _github_get("/user")

    @patch("apps.integrations.services.requests.get")
    def test_403_reports_insufficient_permissions(self, mock_get):
        response = Mock()
        response.status_code = 403
        response.headers = {"X-RateLimit-Remaining": "10"}
        mock_get.return_value = response

        with self.assertRaisesMessage(
            GitHubIntegrationError,
            "GitHub denied access",
        ):
            _github_get("/repos/owner/repository")

    @patch("apps.integrations.services.requests.get")
    def test_403_rate_limit_is_identified(self, mock_get):
        response = Mock()
        response.status_code = 403
        response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1900000000",
        }
        mock_get.return_value = response

        with self.assertRaisesMessage(
            GitHubIntegrationError,
            "GitHub API rate limit reached",
        ):
            _github_get("/user")

    @patch("apps.integrations.services.requests.get")
    def test_429_reports_retry_after(self, mock_get):
        response = Mock()
        response.status_code = 429
        response.headers = {"Retry-After": "30"}
        mock_get.return_value = response

        with self.assertRaisesMessage(
            GitHubIntegrationError,
            "retry after 30 seconds",
        ):
            _github_get("/user")

    @patch("apps.integrations.services.requests.get")
    def test_missing_token_is_rejected(self, mock_get):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesMessage(
                ImproperlyConfigured,
                "GITHUB_TOKEN is missing",
            ):
                _github_get("/user")

        mock_get.assert_not_called()
        
    @patch("apps.integrations.services.requests.get")
    def test_network_error_is_wrapped(self, mock_get):
        import requests

        mock_get.side_effect = requests.RequestException(
            "connection failed"
        )

        with self.assertRaisesMessage(
            GitHubIntegrationError,
            "Could not reach GitHub",
        ):
            _github_get("/user")

    @patch("apps.integrations.services.requests.get")
    def test_invalid_json_is_wrapped(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.ok = True
        response.json.side_effect = ValueError("invalid JSON")
        response.headers = {}
        mock_get.return_value = response

        with self.assertRaisesMessage(
            GitHubIntegrationError,
            "unexpected response",
        ):
            _github_get("/user")
