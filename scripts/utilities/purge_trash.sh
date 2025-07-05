#!/bin/bash
# Purge .trash directory when it gets too large

TRASH_DIR=".trash"
MAX_SIZE_MB=10

if [ -d "$TRASH_DIR" ]; then
    SIZE=$(du -sm "$TRASH_DIR" 2>/dev/null | cut -f1)
    if [ -n "$SIZE" ] && [ "$SIZE" -gt "$MAX_SIZE_MB" ]; then
        echo "🗑️  Purging $TRASH_DIR (${SIZE}MB > ${MAX_SIZE_MB}MB limit)..."
        rm -rf "$TRASH_DIR"
        echo "✅ Trash purged!"
    else
        echo "📊 Trash size: ${SIZE}MB (under ${MAX_SIZE_MB}MB limit)"
    fi
else
    echo "✨ No trash to purge"
fi