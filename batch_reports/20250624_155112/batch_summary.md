# KindleMint Engine Batch Processing Report
Generated: 2025-06-24 15:51:12
Batch ID: 20250624_155112

## 📊 Summary
- **Books Processed**: 1
- **Successful**: 0
- **Failed**: 1
- **Success Rate**: 0.0%
- **Total Time**: 00:00:00

## 📚 Book Details

### Large Print Crossword Masters
- **Status**: ❌ Failed
- **Processing Time**: 0m 0s
- **Steps Completed**: 1
- **Error**: Step create_pdf failed: PDF layout failed: usage: book_layout_bot.py [-h] --book-config BOOK_CONFIG --puzzle-dir
                          PUZZLE_DIR --output-dir OUTPUT_DIR
                          [--page_size PAGE_SIZE] [--font_size FONT_SIZE]
                          [--include_solutions INCLUDE_SOLUTIONS]
                          [--title_page TITLE_PAGE] [--toc TOC]
                          [--answer_key ANSWER_KEY]
book_layout_bot.py: error: the following arguments are required: --book-config, --puzzle-dir


## 🚀 Recommendations
- Review any failed books and address errors
- Check QA reports for quality issues
- Verify hardcover cover wraps for proper alignment
- Run batch processor with --resume flag to retry failed books
