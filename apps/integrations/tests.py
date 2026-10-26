
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