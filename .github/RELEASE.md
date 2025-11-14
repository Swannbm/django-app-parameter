# Release Process

## Automated PyPI Publishing

This project uses GitHub Actions to automatically publish new versions to PyPI when a version tag is created.

## Prerequisites

### 1. Configure PyPI Trusted Publishing

You need to set up PyPI Trusted Publishing (no API token required):

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new "pending publisher" with these settings:
   - **PyPI Project Name**: `django-app-parameter`
   - **Owner**: `Swannbm` (your GitHub username)
   - **Repository name**: `django-app-parameter`
   - **Workflow name**: `publish.yml`
   - **Environment name**: (leave empty)

This setup is more secure than using API tokens and is the recommended approach.

## How to Release a New Version

### Step 1: Update Version Number

Update the version in [pyproject.toml](../pyproject.toml):

```bash
poetry version patch  # for 1.1.3 -> 1.1.4
# or
poetry version minor  # for 1.1.3 -> 1.2.0
# or
poetry version major  # for 1.1.3 -> 2.0.0
```

### Step 2: Update CHANGELOG (recommended)

Document your changes in a CHANGELOG.md file.

### Step 3: Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to $(poetry version -s)"
git push origin master
```

### Step 4: Create and Push Tag

```bash
# Create a tag matching the version in pyproject.toml
git tag v$(poetry version -s)
git push origin v$(poetry version -s)
```

For example, if your version is `1.1.4`:
```bash
git tag v1.1.4
git push origin v1.1.4
```

### Step 5: Automated Workflow

Once the tag is pushed, GitHub Actions will automatically:

1. ✅ Run all tests on Python 3.10, 3.11, 3.12, 3.13
2. ✅ Run all tests on Django 4.2 and 5.1
3. ✅ Run linters (ruff, pyright)
4. ✅ Verify the tag version matches `pyproject.toml` version
5. ✅ Build the package with Poetry
6. ✅ Publish to PyPI using Trusted Publishing

### Step 6: Verify Publication

After the workflow completes (usually 5-10 minutes):

1. Check the [Actions tab](https://github.com/Swannbm/django-app-parameter/actions) for workflow status
2. Verify the new version on PyPI: https://pypi.org/project/django-app-parameter/
3. Test installation: `pip install django-app-parameter==$(poetry version -s)`

## Troubleshooting

### Version Mismatch Error

If you see "Tag version does not match Poetry version":
- Ensure the tag version (without 'v') matches the version in `pyproject.toml`
- Example: tag `v1.2.3` should match `version = "1.2.3"` in pyproject.toml

### Publishing Fails

1. Check that PyPI Trusted Publishing is correctly configured
2. Verify the workflow has the correct permissions (`id-token: write`)
3. Check the workflow logs in the Actions tab

### Tests Fail

Fix the tests before creating the tag. The workflow will not publish if any tests fail.

## Manual Publishing (Emergency)

If you need to publish manually:

```bash
poetry build
poetry publish
```

You'll need to configure Poetry with your PyPI credentials first:
```bash
poetry config pypi-token.pypi your-api-token
```

## Quick Reference

```bash
# Complete release workflow
poetry version patch                    # Update version
git add pyproject.toml                  # Stage changes
git commit -m "Bump version to $(poetry version -s)"  # Commit
git push origin master                  # Push changes
git tag v$(poetry version -s)           # Create tag
git push origin v$(poetry version -s)   # Push tag (triggers publish)
```
