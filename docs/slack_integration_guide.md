# Slack Integration Guide for Batch Processor

## Overview

The KindleMint Engine batch processor now includes Slack integration for real-time notifications about batch processing status, errors, and individual book completions.

## Setup

### 1. Get a Slack Webhook URL

1. Go to https://api.slack.com/apps
2. Create a new app or select an existing one
3. Enable "Incoming Webhooks"
4. Add a new webhook to your desired channel
5. Copy the webhook URL

### 2. Configure Environment Variable

```bash
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
```

### 3. Optional: Enable Per-Book Notifications

By default, only batch completion and error notifications are sent. To receive notifications for each book:

```bash
export SLACK_NOTIFY_PER_BOOK=true
```

## Notification Types

### 1. Batch Completion Notification
- Sent when entire batch processing completes
- Shows success rate, processing time, and summary statistics
- Lists any failed books with error messages
- Color-coded based on success rate (green/orange/red)

### 2. Critical Error Notifications
- Sent when a book fails to process
- Includes error details and context
- Shows which step failed and steps completed
- Always red color for visibility

### 3. Individual Book Notifications (Optional)
- Sent after each book completes (success or failure)
- Shows processing time and steps completed
- Useful for monitoring long-running batches
- Enable with `SLACK_NOTIFY_PER_BOOK=true`

### 4. Fatal Error Notifications
- Sent if batch processor crashes unexpectedly
- Includes configuration details for debugging
- Helps identify systemic issues

## Testing

Run the test script to verify your Slack integration:

```bash
python scripts/test_slack_integration.py
```

This will send test notifications to your configured Slack channel.

## Integration Details

### Fallback Behavior
- If Slack module is not available, batch processor continues normally
- If webhook URL is not set, notifications are logged but not sent
- Notification failures don't interrupt batch processing

### Sentry Integration
- Slack notifications are tracked as Sentry breadcrumbs
- Slack API errors are captured in Sentry
- Both systems work together for comprehensive monitoring

### Performance Impact
- Notifications are sent asynchronously
- Minimal impact on batch processing time
- Failures timeout after 10 seconds

## Example Notifications

### Batch Success
```
✅ Batch Processing Complete: 20240101_120000
Books Processed: 10
Success Rate: 100.0%
Succeeded: 10
Failed: 0
Total Time: 00:45:23
```

### Book Error
```
❌ KindleMint Engine Error
Error: Book processing failed: Large Print Crossword Vol. 5
Type: RuntimeError
Message: PDF layout failed: No puzzles found in directory
Context:
• book_id: crossword_vol_5
• batch_id: 20240101_120000
• last_step: generate_puzzles
```

## Best Practices

1. **Channel Selection**: Use a dedicated channel for batch notifications
2. **Alert Fatigue**: Use `SLACK_NOTIFY_PER_BOOK` sparingly for large batches
3. **Error Handling**: Monitor error notifications to identify patterns
4. **Integration Testing**: Test notifications before production batches

## Troubleshooting

### Notifications Not Sending
1. Check `SLACK_WEBHOOK_URL` is set correctly
2. Verify webhook URL is valid and active
3. Check Slack workspace permissions
4. Review batch processor logs for errors

### Too Many Notifications
1. Disable per-book notifications: `unset SLACK_NOTIFY_PER_BOOK`
2. Consider batching smaller groups of books
3. Use error notifications only

### Missing Information
1. Check batch configuration includes all metadata
2. Verify book titles and IDs are properly set
3. Review notification formatting in logs
