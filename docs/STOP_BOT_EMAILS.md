# How to Stop GitHub Bot Email Spam

## 🚨 Quick Fix: GitHub Settings

Go to: **https://github.com/settings/notifications**

### 1. Actions Section
- **Uncheck** "Failed workflows only"  
- **Uncheck** "Send notifications for workflow runs"

### 2. Watching Settings  
- Change from "All Activity" to **"Participating and @mentions"**

### 3. Custom Routing
- Add routing rules to send bot notifications to a different email or disable them

---

## 📧 Gmail Filters (If You Want to Keep Some Notifications)

### Auto-Archive All Bot Emails:
1. Gmail → Settings → Filters → Create new filter
2. **From**: `*bot*@users.noreply.github.com OR github-actions@github.com`
3. **Actions**:
   - ✅ Skip the Inbox (Archive it)
   - ✅ Apply label "GitHub/Bots"
   - ✅ Never mark as important

### Filter Only Failed Tests:
```
From: github-actions[bot]
Subject: "Failed" OR "❌"
Action: Skip Inbox, Apply label "Failed Tests"
```

---

## 🔇 Nuclear Option: Unwatch the Repository

If you're the owner but don't need email notifications:
1. Go to https://github.com/IgorGanapolsky/ai-kindlemint-engine
2. Click "Watch" → "Custom" → Uncheck everything except:
   - Issues (assigned, created, or mentioned)
   - Pull requests (assigned, created, or mentioned)

---

## 🤖 Bot-Specific Unsubscribe

Each bot has different unsubscribe methods:

### CodeRabbit
- Click "unsubscribe" link in any CodeRabbit email
- Or add to `.coderabbit.yml`:
  ```yaml
  notifications:
    email: false
  ```

### Pixeebot
- Reply "unsubscribe" to any Pixeebot PR
- Or block the bot entirely

### GitHub Actions
- Can only control via GitHub notification settings
- Or use email filters

---

## 🎯 Recommended Setup

1. **GitHub**: Turn off Action email notifications
2. **Gmail**: Create filter for `*bot*` → Skip Inbox
3. **Keep**: Only direct mentions and assigned issues

This way you'll only get emails when someone specifically needs your attention!