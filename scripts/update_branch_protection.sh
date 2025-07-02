#!/bin/bash
# Update branch protection to use single CI check

echo "Updating branch protection rules..."

gh api repos/IgorGanapolsky/ai-kindlemint-engine/branches/main/protection   --method PUT   --header "Accept: application/vnd.github+json"   --input - << EOF
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["CI Status"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false,
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false,
  "required_conversation_resolution": false
}
EOF

echo "✅ Branch protection updated to use single CI Status check"
