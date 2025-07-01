# PR Strategy Implementation Learnings

## Key Learnings for Future Guidance

### 1. **Be Explicit About Expected Failures**
When implementing CI/CD infrastructure, ALWAYS explain upfront that:
- Initial PR will have failing checks
- This is NORMAL and EXPECTED
- The failures prove the system is working
- Infrastructure PRs should be merged despite failures

### 2. **Personal vs Organization Repos**
- Personal repos have limited branch protection options
- Cannot use team/user restrictions on personal repos
- Need separate scripts for personal vs org repos
- Always check repo type before suggesting protection rules

### 3. **Clear Action Steps**
Always provide:
1. What they're seeing (explain each check status)
2. Why it's happening (context is crucial)
3. Exactly what to click/type (be specific)
4. What happens next (set expectations)

### 4. **Common Confusion Points**
Users often get confused by:
- Failing CI checks on infrastructure PRs
- Multiple AI tools commenting (explain each one)
- CodeQL alerts vs actual bugs
- When to merge despite failures

### 5. **Workflow Explanation Template**
```
Current State:
- ✅ What's working: [list passing checks]
- ❌ What's failing: [list failures and WHY]
- 🔧 What needs fixing: [specific issues]

Actions Required:
1. [Specific action with exact button/command]
2. [Next action with reasoning]
3. [Follow-up steps]

Expected Outcome:
- [What will happen after each action]
- [Timeline expectations]
```

### 6. **Always Create Helper Scripts**
When main approach fails:
1. Identify why (permissions, repo type, etc.)
2. Create alternative solution immediately
3. Test commands before suggesting
4. Provide both options

### 7. **PR Review Tools Status**
Current landscape:
- ✅ Sentry AI - Works well, provides actionable feedback
- ✅ CodeRabbit - Comprehensive reviews
- ✅ DeepSource - Good for code quality
- ❌ Cursor Bugbot - Beta, unreliable, poor integration
- ✅ GitHub Copilot - Good for quick fixes
- ✅ CodeQL - Excellent for security

### 8. **Implementation Strategy**
For complex changes:
1. Infrastructure PR first (expect failures)
2. Document what's normal vs concerning
3. Provide escape hatches for issues
4. Create incremental fix PRs after

### 9. **Communication Style**
- Use visual indicators (✅ ❌ 🎯 🚨)
- Break down complex info into sections
- Provide both summary and details
- Always end with clear next action

### 10. **Troubleshooting Approach**
When things don't work as expected:
1. Acknowledge what user is seeing
2. Explain why it's happening
3. Provide immediate workaround
4. Create permanent solution
5. Document for future reference

## Commands to Remember

```bash
# Personal repo branch protection
gh api --method PUT /repos/{owner}/{repo}/branches/main/protection \
  -f required_status_checks[strict]=true \
  -f enforce_admins=false

# Check PR status
gh pr checks

# View workflow runs
gh run list

# Cancel stuck workflows
gh run cancel
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Branch protection fails | Check if personal vs org repo |
| CI checks timing out | Add timeout-minutes to jobs |
| Too many AI comments | Consolidate in workflow |
| Flaky tests blocking | Add retry logic or mark as allowed failure |
| Permission errors | Add permissions block to workflow |

---
Last Updated: July 1, 2025
Context: User implementing PR-based development strategy on ai-kindlemint-engine