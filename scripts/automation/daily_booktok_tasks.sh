#!/bin/bash
# Daily BookTok Automation Tasks

echo "🌅 Running daily BookTok automation..."

# Check today's posting schedule
echo "📅 Today's posting schedule:"
if [ -f "data/social_content/posting_calendar.csv" ]; then
    grep "$(date +%Y-%m-%d)" data/social_content/posting_calendar.csv || echo "No posts scheduled for today"
else
    echo "No posting calendar found"
fi

# Generate content queue for next 7 days
echo "📋 Updating content queue..."

# Check for new books that need social content
echo "📚 Checking for new books..."
for book_dir in books/*/; do
    if [ -d "$book_dir" ] && [ ! -d "${book_dir}social_media_content" ]; then
        echo "New book found: $(basename "$book_dir")"
        echo "Run: python3 demo_booktok_setup.py to generate content"
    fi
done

echo "✅ Daily automation complete!"
