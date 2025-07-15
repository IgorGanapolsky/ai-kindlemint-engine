#!/bin/bash
# Gumroad Course Upload Script

echo "🚀 Uploading backend course to Gumroad..."

# Course details
COURSE_NAME="Create Your Own Puzzle Book - Complete Course"
COURSE_PRICE="97"
COURSE_FILE="backend_course/course_package.zip"
COURSE_DESCRIPTION="Learn how to create and publish your own puzzle books. Complete course with templates, scripts, and step-by-step guidance."

# Upload using Gumroad CLI (if available) or manual instructions
if command -v gumroad &> /dev/null; then
    gumroad upload "$COURSE_FILE" --name "$COURSE_NAME" --price "$COURSE_PRICE" --description "$COURSE_DESCRIPTION"
else
    echo "📋 Manual upload instructions:"
    echo "1. Go to https://gumroad.com/dashboard"
    echo "2. Click 'New Product'"
    echo "3. Upload: $COURSE_FILE"
    echo "4. Set name: $COURSE_NAME"
    echo "5. Set price: \$$COURSE_PRICE"
    echo "6. Add description: $COURSE_DESCRIPTION"
    echo "7. Publish!"
fi

echo "✅ Course upload script created"
