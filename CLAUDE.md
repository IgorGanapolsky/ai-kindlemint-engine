# Claude Memory

## Important Reminders

### Always Push Changes
**CRITICAL**: Always commit and push changes immediately after making them. Igor expects all fixes and updates to be pushed to the repository automatically.

### Workflow Commands
- Lint: `npm run lint` (check if available)
- Typecheck: `npm run typecheck` (check if available)
- Test: `npm test` (check if available)

### Repository Structure
- Main deployment script: `scripts/utilities/deploy_lambda.py`
- GitHub Actions workflows: `.github/workflows/`
- Lambda functions: `lambda/`
- Core application: `kindlemint/`

### Cover Design Policy
**NEVER generate covers automatically.** Always provide DALL-E prompts for Igor to use instead of creating cover images programmatically. Store all DALL-E prompts in checklist.md files for easy reference and reuse.