# PR Automation Workflow

This document explains how the automated pull request creation works for calculator submissions.

## Overview

The PR automation uses **GitHub Actions workflow_dispatch** to create pull requests automatically. When a user clicks "Submit PR" in the calculator generator, it triggers a GitHub Actions workflow that creates a branch, commits files, runs tests, and creates a PR.

## Architecture

```
User Browser → FastAPI → GitHub API → GitHub Actions → Pull Request
```

1. **User** fills in calculator form and clicks "Submit PR"
2. **Browser** sends calculator data to FastAPI endpoint
3. **FastAPI** (`/submit-calculator`) calls GitHub API with workflow_dispatch
4. **GitHub Actions** workflow runs automatically
5. **Workflow** creates branch, commits files, runs tests, creates PR

## Components

### 1. Frontend (site/generator.html)

Collects:
- Calculator specification (name, description, reference)
- Input parameters
- Calculation logic
- Optional user attribution (GitHub username, name, affiliation)

Sends to API:
```javascript
{
  spec: "TOML string",
  calculator_code: "Python code",
  test_code: "Test code",
  name: "calculator_name",
  description: "Calculator description",
  submitter_github: "username",      // Optional
  submitter_name: "Full Name",       // Optional
  submitter_affiliation: "Hospital"  // Optional
}
```

### 2. API Server (api/main.py)

**Endpoint:** `POST /submit-calculator`

**Rate Limit:** 3 requests per minute

**Process:**
1. Validates required fields
2. Gets GitHub token from environment
3. Calls `GitHubPRService.submit_calculator()`
4. Returns workflow dispatch status

### 3. PR Service (core/pr_service.py)

**Class:** `GitHubPRService`

**Method:** `submit_calculator()`

**Process:**
1. Prepares workflow inputs with calculator data
2. Calls GitHub API workflow_dispatch endpoint
3. Returns success status and GitHub Actions link

**GitHub API Call:**
```python
POST /repos/{owner}/{repo}/actions/workflows/create-calculator-pr.yml/dispatches
Headers:
  Authorization: Bearer {GITHUB_TOKEN}
  Accept: application/vnd.github+json
Body:
  {
    "ref": "live",
    "inputs": {
      "calculator_name": "...",
      "calculator_code": "...",
      "test_code": "...",
      "spec": "...",
      "description": "...",
      "submitter_github": "...",  // Optional
      "submitter_name": "...",    // Optional
      "submitter_affiliation": "..." // Optional
    }
  }
```

### 4. GitHub Actions Workflow

**File:** `.github/workflows/create-calculator-pr.yml`

**Trigger:** `workflow_dispatch` (manual/API trigger)

**Inputs:**
- `calculator_name` - Calculator name in snake_case
- `calculator_code` - Complete Python calculator code
- `test_code` - Complete test code
- `spec` - TOML specification
- `description` - Calculator description
- `submitter_github` - Optional GitHub username
- `submitter_name` - Optional submitter name
- `submitter_affiliation` - Optional affiliation

**Steps:**

1. **Checkout Repository**
   - Checks out `live` branch
   - Full history for proper branching

2. **Set Up Python**
   - Python 3.11
   - Installs pytest, pydantic, fastapi

3. **Create Branch**
   - Branch name: `calculator/{name}`
   - From: `live` branch

4. **Write Files**
   - Calculator: `calculators/{name}.py`
   - Tests: `tests/test_{name}.py`

5. **Run Tests**
   - Executes: `pytest tests/test_{name}.py -v`
   - Captures output (even if tests fail)
   - Continues even if tests fail (for review)

6. **Commit Files**
   - Commit message includes description
   - Authored by: `github-actions[bot]`

7. **Push Branch**
   - Pushes to: `origin calculator/{name}`

8. **Build PR Body**
   - Includes: files added, specification, test results
   - Adds submitter attribution if provided
   - Links back to generator

9. **Create Pull Request**
   - Uses: `peter-evans/create-pull-request@v6`
   - Base: `live`
   - Labels: `calculator`, `auto-generated`
   - Title: "Add {name} calculator"

## Authentication & Permissions

### GitHub Token Setup

The API server needs a **Personal Access Token (PAT)** with specific permissions.

#### Creating a Fine-Grained PAT

1. Go to **GitHub.com** → Profile → **Settings**
2. **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
3. Click **Generate new token**
4. Configure:
   - **Name:** Clinical Calculators PR Automation
   - **Expiration:** 90 days (or longer)
   - **Resource owner:** rcpch (the organization)
   - **Repository access:** Only select repositories → clinical-calculators
   - **Permissions:**
     - ✅ **Contents:** Read and write (create branches, commit files)
     - ✅ **Pull requests:** Read and write (create PRs)
     - ✅ **Workflows:** Read and write (trigger workflow_dispatch)
5. Click **Generate token**
6. Copy token (starts with `github_pat_...`)

#### Organization Approval

If the organization requires approval:
1. Organization admin goes to: `github.com/orgs/rcpch/settings/personal-access-tokens-onboarding`
2. Approves the pending token request

#### Adding to API Server

Add to `.env` file:
```bash
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Optional configuration:
```bash
GITHUB_REPO_OWNER=rcpch
GITHUB_REPO_NAME=clinical-calculators
```

Restart API server to pick up changes:
```bash
docker compose restart api
```

### Workflow Token

The `${{ secrets.GITHUB_TOKEN }}` used in the workflow is **automatically provided** by GitHub Actions. No setup required.

## User Attribution

Users can optionally identify themselves in three ways:

### 1. GitHub Username (Preferred)
- Field: "GitHub Username"
- Result: PR body includes `GitHub: @username`
- Benefits: Proper GitHub mention, can be assigned/credited

### 2. Name Only
- Field: "Name"
- Result: PR body includes `Name: Full Name`
- Use when: User doesn't have GitHub account

### 3. Name + Affiliation
- Fields: "Name" and "Affiliation"
- Result: PR body includes both
- Use when: Attribution to institution needed

### 4. Anonymous
- Leave all fields blank
- PR created by `github-actions[bot]`
- Still valid, just no attribution

## Workflow Monitoring

### Check Workflow Status

1. Go to **GitHub.com** → Repository → **Actions**
2. Find workflow run: "Create Calculator PR"
3. Click to see:
   - Branch creation
   - File commits
   - Test execution results
   - PR creation status

### Successful Run

✅ Green checkmark indicates:
- Branch created successfully
- Files committed
- Tests ran (may pass or fail)
- PR created and linked

### Failed Run

❌ Red X indicates one of:
- Invalid calculator code (syntax error)
- Permission issues (check PAT)
- GitHub API error
- Branch already exists

View logs for details.

## PR Review Process

### Automated Checks

When PR is created:
1. GitHub Actions run all tests
2. Test results visible in PR
3. Code changes reviewable in Files tab

### Manual Review

Reviewer should check:
1. **Calculator Logic** - Clinically correct
2. **Test Coverage** - Adequate test cases
3. **Documentation** - Clear description and reference
4. **Code Quality** - Follows project patterns
5. **Attribution** - Proper credit if provided

### Approval & Merge

Once approved:
1. Merge to `live` branch
2. Calculator available at API endpoint
3. Shows in UI calculator list

## Troubleshooting

### "GITHUB_TOKEN environment variable not set"

**Cause:** API server can't find token

**Fix:**
1. Add `GITHUB_TOKEN=...` to `.env` file
2. Restart API: `docker compose restart api`

### "GitHub API error: 401"

**Cause:** Invalid or expired token

**Fix:**
1. Generate new PAT
2. Update `.env`
3. Restart API

### "GitHub API error: 403"

**Cause:** Token lacks permissions or awaiting org approval

**Fix:**
1. Verify PAT has Contents, Pull requests, and Workflows permissions
2. Check org admin approved token
3. Ensure token scoped to correct repository

### "GitHub API error: 404"

**Cause:** Workflow file doesn't exist on target branch

**Fix:**
1. Ensure workflow file exists on `live` branch
2. Check workflow filename matches exactly: `create-calculator-pr.yml`

### Workflow dispatched but no PR created

**Cause:** Workflow ran but encountered error

**Fix:**
1. Go to GitHub Actions tab
2. Find the workflow run
3. Check logs for errors
4. Common issues:
   - Python syntax error in generated code
   - Branch already exists (choose different name)
   - Test execution timeout

### PR created but tests failing

**Cause:** Generated calculator has issues

**Fix:**
- This is expected - PR is for review
- Reviewer can request changes
- User can update via additional commits
- Or close PR and regenerate

## Security Considerations

### Token Security

- ✅ Store token in `.env` file (gitignored)
- ✅ Use fine-grained token (minimal permissions)
- ✅ Set expiration date
- ❌ Never commit token to repository
- ❌ Never share token publicly
- ❌ Don't use classic token (too permissive)

### Rate Limiting

API endpoint has rate limit: **3 requests per minute**

Prevents:
- Accidental spam
- Malicious PR flooding
- GitHub API quota exhaustion

### Input Validation

All inputs validated before workflow dispatch:
- Calculator name: snake_case pattern
- Code: Python syntax checked during generation
- Spec: TOML format validated
- Description: Required, max length enforced

## Future Enhancements

### Planned Features

- [ ] **OAuth Login** - Users authenticate with GitHub directly
- [ ] **Webhook Feedback** - Real-time PR status updates
- [ ] **Calculator Preview** - Test calculator before submitting
- [ ] **Draft PRs** - Create draft for review before marking ready
- [ ] **Batch Submission** - Submit multiple calculators at once
- [ ] **Update Existing** - Modify existing calculator via PR
- [ ] **Template Selection** - Choose from calculator templates

### Potential Improvements

- **CI/CD Integration** - Auto-deploy on merge
- **Slack Notifications** - Alert team of new submissions
- **Quality Scoring** - Auto-score calculator quality
- **A/B Testing** - Test multiple calculation approaches
- **Version Control** - Track calculator evolution

## Related Documentation

- [Calculator Generator Overview](calculator-generator.md) - Main generator documentation
- [Development Setup](index.md) - Getting started guide
- [API Documentation](../api/main.py) - API endpoint details
- [Workflow File](.github/workflows/create-calculator-pr.yml) - Actual workflow code
