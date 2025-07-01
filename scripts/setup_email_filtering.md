# 📧 Executive Email Filtering Setup

## Gmail Filter for Bot Notifications

**Create this Gmail filter to automatically handle bot spam:**

### Filter Criteria:
```
From: notifications@github.com
Subject: [IgorGanapolsky/ai-kindlemint-engine]
Body contains: "seer-by-sentry[bot]" OR "commented on this pull request"
```

### Actions:
- ✅ **Skip Inbox** (archive immediately)
- ✅ **Apply label: "GitHub Bots"**
- ✅ **Mark as read**
- ✅ **Never send to Spam**

## Executive Summary Emails Only

**Keep only these important notifications:**
- PR approvals and merges
- Security alerts
- Build failures
- Manual review requests

## Setup Instructions:

1. **Gmail → Settings → Filters and Blocked Addresses**
2. **Create New Filter**
3. **Paste criteria above**
4. **Apply actions**
5. **Apply to existing conversations: Yes**

**Result: Bot spam → Auto-archived, Important stuff → Inbox**