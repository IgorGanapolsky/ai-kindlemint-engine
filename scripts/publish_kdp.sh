#!/bin/bash
# Publish the latest generated book file
BOOK_FILE=$(ls output/*.kpf | sort | tail -n 1)

if [ -z "$BOOK_FILE" ]; then
    echo "❌ No .kpf files found in output directory"
    exit 1
fi

echo "📤 Uploading $BOOK_FILE to KDP"
python scripts/publish_to_kdp.py "$BOOK_FILE"