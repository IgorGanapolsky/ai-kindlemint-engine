# Commit Message Validation

## Purpose
Ensures all commits follow conventional commit format for consistency and automated changelog generation.

## Rules
- **Format**: `type(scope): description`
- **Types**: feat, fix, docs, style, refactor, perf, test, chore, build, ci
- **Merge commits**: Automatically excluded from validation

## Examples
✅ `feat(auth): add user login functionality`
✅ `fix: resolve database connection issue`
✅ `docs: update README with new features`
✅ `Merge branch 'feature/new-auth' into main` (auto-excluded)

❌ `add new feature` (missing type)
❌ `WIP: work in progress` (invalid type)

## Technical Implementation
- Validation runs in `.github/workflows/pr-validation.yml`
- Merge commits starting with "Merge " are automatically skipped
- Prevents CI/CD pipeline breaks from GitHub's auto-generated merge commits
