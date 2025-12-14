# Project Maintenance

This guide covers maintenance tasks for the RCPCH Clinical Calculators project.

## Removing a Calculator

If you need to remove a calculator (e.g., duplicate, deprecated, or replaced by a better implementation), follow these steps:

### Step 1: Identify Files to Remove

Each calculator typically consists of:
- **Calculator file**: `calculators/calculator_name.py`
- **Test file**: `tests/test_calculator_name.py`
- **Related documentation** (if specific to that calculator)

### Step 2: Remove the Files

Use Git to remove the files properly:

```bash
git rm calculators/calculator_name.py
git rm tests/test_calculator_name.py
```

### Step 3: Update Documentation

Update any documentation that references the removed calculator:

- Remove from lists of available calculators (e.g., README.md, docs/overview.md)
- Update examples that used the removed calculator
- Update API reference documentation if needed
- Add a note in the changelog if maintaining one

### Step 4: Run Tests

Ensure all remaining tests still pass after removal:

```bash
docker compose run --rm api pytest
```

### Step 5: Commit the Changes

Commit with a clear message explaining the removal:

```bash
git commit -m "Remove [calculator name]

Reason: [Brief explanation, e.g., 'Duplicate of HbA1c converter' or 'Replaced by improved implementation']

Removed:
- calculators/calculator_name.py
- tests/test_calculator_name.py
- [any other removed files]"
```

### Step 6: Submit Pull Request

Create a PR with:
- Clear explanation of why the calculator is being removed
- What (if anything) replaces its functionality
- Confirmation that all tests pass
- Documentation updates included

## Updating Dependencies

### Python Dependencies

1. Update `requirements.txt` or `pyproject.toml`
2. Test thoroughly with the new dependencies:
   ```bash
   docker compose down
   docker compose up --build
   docker compose run --rm api pytest
   ```
3. Update any affected documentation

### Frontend Dependencies

For web client dependencies (loaded via CDN):
1. Update version numbers in `site/index.html` and `site/docs.html`
2. Test the web interface thoroughly
3. Check for any breaking changes in the library documentation

## Deprecating a Calculator

If a calculator needs to be deprecated (but not immediately removed):

### Step 1: Mark as Deprecated

Add a deprecation notice in the calculator's docstring:

```python
"""
# Calculator Name

⚠️ **DEPRECATED**: This calculator is deprecated and will be removed in version X.X.
Please use [replacement calculator] instead.

## Description
...
"""
```

### Step 2: Add Runtime Warning

Add a deprecation warning in the `calculate()` function:

```python
import warnings

def calculate(params: dict) -> CalculationResponse:
    warnings.warn(
        "This calculator is deprecated and will be removed in version X.X. "
        "Please use [replacement] instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... rest of implementation
```

### Step 3: Update Documentation

- Add deprecation notice to README and docs
- Document the migration path to the replacement
- Set a target version for removal

### Step 4: Communicate Changes

- Announce deprecation in release notes
- Provide migration guide for users
- Give adequate notice before removal (suggest 2-3 minor versions)

## Versioning

The project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Add functionality in a backward-compatible manner
- **PATCH** version: Backward-compatible bug fixes

### When to Bump Versions

- **MAJOR**: Removing calculators, breaking API changes
- **MINOR**: Adding new calculators, new features
- **PATCH**: Bug fixes, documentation updates, non-breaking improvements

## Release Process

1. **Prepare Release**
   - Ensure all tests pass
   - Update version number in relevant files
   - Update CHANGELOG.md (if maintained)
   - Review and update documentation

2. **Create Release**
   - Tag the release: `git tag -a v1.0.0 -m "Version 1.0.0"`
   - Push tags: `git push origin --tags`
   - Create GitHub release with release notes

3. **Deploy**
   - GitHub Pages deploys automatically from `live` branch
   - API deployment (if applicable) follows separate process

## Monitoring and Maintenance

### Regular Tasks

- **Weekly**: Review open issues and PRs
- **Monthly**: Check dependency updates
- **Quarterly**: Review and update documentation
- **Annually**: Audit all calculators for clinical accuracy

### Health Checks

- Monitor GitHub Actions for build failures
- Check API availability and response times
- Review error logs and user feedback
- Validate calculator outputs against clinical guidelines

## Emergency Fixes

For critical bugs or security issues:

1. **Create hotfix branch** from `live`:
   ```bash
   git checkout live
   git pull
   git checkout -b hotfix/critical-issue
   ```

2. **Implement fix** with tests

3. **Fast-track review** and merge

4. **Deploy immediately** and notify users

## Archive Strategy

For historical calculators that are no longer actively maintained:

1. Move to `calculators/archived/` directory
2. Remove from active API endpoints
3. Keep tests but mark as archived
4. Document in README or separate archive documentation
5. Maintain read-only access for reference

## Getting Help

For maintenance questions:

- **Documentation**: [Full Documentation](https://rcpch.github.io/clinical-calculators/docs.html)
- **Issues**: [GitHub Issues](https://github.com/rcpch/clinical-calculators/issues)
- **Maintainers**: Tag `@rcpch` team in GitHub
