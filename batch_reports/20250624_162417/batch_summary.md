# KindleMint Engine Batch Processing Report
Generated: 2025-06-24 16:24:17
Batch ID: 20250624_162417

## 📊 Summary
- **Books Processed**: 1
- **Successful**: 0
- **Failed**: 1
- **Success Rate**: 0.0%
- **Total Time**: 00:00:00

## 📚 Book Details

### Test Crossword Book
- **Status**: ❌ Failed
- **Processing Time**: 0m 0s
- **Steps Completed**: 0
- **Error**: Step generate_puzzles failed: Puzzle generation failed: usage: crossword_engine_v2.py [-h] --output OUTPUT [--count COUNT]
                              [--difficulty {easy,medium,hard,mixed}]
                              [--grid-size GRID_SIZE]
                              [--word-count WORD_COUNT]
                              [--max-word-length MAX_WORD_LENGTH]
crossword_engine_v2.py: error: unrecognized arguments: --grid_size 15 --word_count 20 --max_word_length 10


## 🚀 Recommendations
- Review any failed books and address errors
- Check QA reports for quality issues
- Verify hardcover cover wraps for proper alignment
- Run batch processor with --resume flag to retry failed books
