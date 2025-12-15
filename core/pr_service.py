"""
Service for creating GitHub pull requests with generated calculators.
"""

from __future__ import annotations

import os

import httpx


class PRSubmissionError(Exception):
    """Error during PR submission process."""

    pass


class GitHubPRService:
    """Service for creating PRs with generated calculators via GitHub Actions."""

    def __init__(
        self,
        github_token: str,
        repo_owner: str = "rcpch",
        repo_name: str = "clinical-calculators",
    ):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base = "https://api.github.com"

    async def submit_calculator(
        self,
        name: str,
        calculator_code: str,
        test_code: str,
        spec: str,
        description: str,
        submitter_github: str | None = None,
        submitter_name: str | None = None,
        submitter_affiliation: str | None = None,
    ) -> dict[str, str]:
        """
        Trigger GitHub Actions workflow to create PR.

        Args:
            name: Calculator name
            calculator_code: Generated calculator code
            test_code: Generated test code
            spec: Calculator specification (TOML string)
            description: Calculator description
            submitter_github: Optional GitHub username of submitter
            submitter_name: Optional name of submitter
            submitter_affiliation: Optional affiliation of submitter

        Returns:
            Dictionary with workflow details

        Raises:
            PRSubmissionError: If workflow dispatch fails
        """
        try:
            # Prepare workflow inputs - ensure all strings are properly formatted
            # GitHub Actions has a 65535 byte limit per input
            inputs = {
                "calculator_name": str(name).strip(),
                "calculator_code": str(calculator_code),
                "test_code": str(test_code),
                "spec": str(spec),
                "description": str(description).strip(),
            }

            # Add optional submitter information
            if submitter_github:
                inputs["submitter_github"] = str(submitter_github).strip()
            if submitter_name:
                inputs["submitter_name"] = str(submitter_name).strip()
            if submitter_affiliation:
                inputs["submitter_affiliation"] = str(submitter_affiliation).strip()
            
            # Validate input sizes (GitHub Actions limit is 65535 bytes per input)
            for key, value in inputs.items():
                if len(value.encode('utf-8')) > 65535:
                    raise PRSubmissionError(
                        f"Input '{key}' exceeds GitHub Actions size limit of 65535 bytes"
                    )

            # Trigger GitHub Actions workflow
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/create-calculator-pr.yml/dispatches"

            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            payload = {
                "ref": "live",
                "inputs": inputs,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 204:
                    # Workflow dispatched successfully
                    branch_name = f"calculator/{name}"
                    return {
                        "success": True,
                        "message": "Workflow dispatched successfully",
                        "branch": branch_name,
                        "workflow_status": "Workflow is running. Check GitHub Actions for progress.",
                        "pr_url": f"https://github.com/{self.repo_owner}/{self.repo_name}/pulls",
                    }
                else:
                    # Try to parse JSON error response from GitHub
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", response.text)
                    except Exception:
                        error_msg = response.text[:200]  # Limit error message length
                    
                    raise PRSubmissionError(
                        f"GitHub API error (status {response.status_code}): {error_msg}"
                    )

        except Exception as e:
            raise PRSubmissionError(f"Failed to dispatch workflow: {e}") from e


def get_pr_service() -> GitHubPRService:
    """Get PR service instance."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise PRSubmissionError("GITHUB_TOKEN environment variable not set")

    return GitHubPRService(
        github_token=github_token,
        repo_owner=os.getenv("GITHUB_REPO_OWNER", "rcpch"),
        repo_name=os.getenv("GITHUB_REPO_NAME", "clinical-calculators"),
    )
