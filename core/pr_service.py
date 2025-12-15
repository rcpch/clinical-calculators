"""
Service for creating GitHub pull requests with generated calculators.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from core.generator import generate_calculator_code


class PRSubmissionError(Exception):
    """Error during PR submission process."""

    pass


class GitHubPRService:
    """Service for creating PRs with generated calculators."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.calculators_dir = repo_path / "calculators"
        self.tests_dir = repo_path / "tests"

    def submit_calculator(
        self,
        name: str,
        calculator_code: str,
        test_code: str,
        spec: dict[str, Any],
    ) -> dict[str, str]:
        """
        Create branch, commit files, run tests, and create PR.

        Args:
            name: Calculator name
            calculator_code: Generated calculator code
            test_code: Generated test code
            spec: Calculator specification

        Returns:
            Dictionary with PR details (branch, pr_url, test_results)

        Raises:
            PRSubmissionError: If any step fails
        """
        branch_name = f"calculator/{name}"

        try:
            # Create new branch from live
            self._run_git(["checkout", "live"])
            self._run_git(["pull", "origin", "live"])
            self._run_git(["checkout", "-b", branch_name])

            # Write calculator file
            calc_file = self.calculators_dir / f"{name}.py"
            calc_file.write_text(calculator_code)

            # Write test file
            test_file = self.tests_dir / f"test_{name}.py"
            test_file.write_text(test_code)

            # Run tests
            test_results = self._run_tests(test_file)

            # Commit files
            self._run_git(["add", str(calc_file), str(test_file)])
            commit_message = self._build_commit_message(spec)
            self._run_git(["commit", "-m", commit_message])

            # Push branch
            self._run_git(["push", "origin", branch_name])

            # Create PR using gh CLI
            pr_url = self._create_pr(branch_name, spec)

            # Return to previous branch
            self._run_git(["checkout", "-"])

            return {
                "branch": branch_name,
                "pr_url": pr_url,
                "test_results": test_results,
                "calculator_file": str(calc_file),
                "test_file": str(test_file),
            }

        except Exception as e:
            # Cleanup: try to delete branch if it was created
            try:
                self._run_git(["checkout", "-"])
                self._run_git(["branch", "-D", branch_name])
            except Exception:
                pass
            raise PRSubmissionError(f"Failed to submit calculator: {e}") from e

    def _run_git(self, args: list[str]) -> str:
        """Run git command and return output."""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def _run_tests(self, test_file: Path) -> str:
        """Run pytest on the test file."""
        result = subprocess.run(
            ["pytest", str(test_file), "-v"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        return result.stdout

    def _build_commit_message(self, spec: dict[str, Any]) -> str:
        """Build descriptive commit message."""
        calc = spec["calculator"]
        name = calc["name"]
        description = calc["description"]
        reference = calc.get("reference", "")

        message = f"Add {name} calculator\n\n"
        message += f"{description}\n\n"
        if reference:
            message += f"Reference: {reference}\n\n"
        message += "Generated via calculator generator UI"

        return message

    def _create_pr(self, branch_name: str, spec: dict[str, Any]) -> str:
        """Create PR using gh CLI."""
        calc = spec["calculator"]
        description = calc["description"]
        reference = calc.get("reference", "")

        pr_body = f"""## Calculator Description
{description}

## Clinical Reference
{reference or "Not specified"}

## Generated Files
- Calculator: `calculators/{calc['name']}.py`
- Tests: `tests/test_{calc['name']}.py`

## Inputs
"""
        for inp in spec["inputs"]:
            pr_body += f"- **{inp['name']}** ({inp['type']}): {inp.get('description', '')}\n"
            if "min" in inp or "max" in inp:
                pr_body += f"  Range: {inp.get('min', '-')} to {inp.get('max', '-')}\n"

        pr_body += "\n---\nGenerated via calculator generator UI"

        # Create PR using gh CLI
        result = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                "live",
                "--head",
                branch_name,
                "--title",
                f"Add {calc['name']} calculator",
                "--body",
                pr_body,
            ],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract PR URL from output
        pr_url = result.stdout.strip()
        return pr_url


# Singleton instance
def get_pr_service() -> GitHubPRService:
    """Get PR service instance."""
    repo_path = Path(__file__).parent.parent
    return GitHubPRService(repo_path)
