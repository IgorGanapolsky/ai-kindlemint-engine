# KindleMint Validators Documentation

## Overview

The KindleMint validators provide comprehensive content validation for puzzle books, ensuring quality, correctness, and compliance with publishing standards. Unlike basic QA checks that only verify PDF structure, these validators inspect the actual puzzle content for correctness, uniqueness, and solvability.

## Validator Types

### 1. SudokuValidator (`sudoku_validator.py`)

Validates Sudoku puzzles for correctness and quality.

#### Validation Rules

##### Structure Validation
- **Required Fields**: `grid`, `solution`, `difficulty`
- **Grid Requirements**:
  - Must be a 9x9 list of lists
  - Each cell must be an integer between 0-9
  - 0 represents an empty cell, 1-9 are clues
- **Solution Requirements**:
  - Must be a 9x9 list of lists
  - Each cell must be an integer between 1-9
- **Difficulty Requirements**:
  - Must be a string: "easy", "medium", "hard", or "expert"

##### Content Validation
- **No Duplicates**: Ensures no duplicate values in:
  - Any row
  - Any column
  - Any 3x3 box
- **Solution Completeness**:
  - Each row must contain all digits 1-9 exactly once
  - Each column must contain all digits 1-9 exactly once
  - Each 3x3 box must contain all digits 1-9 exactly once
- **Grid-Solution Consistency**: All clues in the grid must match the solution
- **Difficulty Clue Counts**:
  - Easy: 32-48 clues (target: 40)
  - Medium: 25-36 clues (target: 30)
  - Hard: 20-28 clues (target: 24)
  - Expert: 17-26 clues (target: 20)
- **No Empty Rows/Columns**: Every row and column must have at least one clue

##### Solvability Validation
- **Unique Solution**: Puzzle must have exactly one solution
- **Solution Verification**: Provided solution must match computed solution

#### Usage Example
```python
from kindlemint.validators import SudokuValidator, validate_sudoku_content

# Validate a directory of puzzles
result = validate_sudoku_content("/path/to/puzzles", strict=True)

# Or use the validator directly
validator = SudokuValidator(strict_mode=False)
result = validator.validate_directory("/path/to/puzzles")
```

### 2. SudokuPDFImageValidator (`sudoku_pdf_image_validator.py`)

Validates that Sudoku puzzle images are properly rendered in PDF files.

#### Validation Checks
- **Page Count**: Verifies expected number of pages (200+ for standard books)
- **Image Presence**: Ensures puzzle and solution pages have actual images
- **Text Fallback Detection**: Identifies pages using text representation instead of images
- **Image Quality**:
  - Minimum resolution: 300x300 pixels
  - Minimum file size: 10KB
- **Critical Failures**:
  - Less than 90% of expected puzzle pages have images
  - Less than 90% of expected solution pages have images
  - Any pages using text fallback

#### Usage Example
```python
from kindlemint.validators.sudoku_pdf_image_validator import validate_sudoku_pdf

# Validate a PDF file
passed = validate_sudoku_pdf("/path/to/sudoku_book.pdf")
# Creates: pdf_image_validation_report.json
```

### 3. SudokuBookQAValidator (`sudoku_book_qa.py`)

Comprehensive QA validator for complete Sudoku books.

#### Validation Checks
- **PDF Content**:
  - Page count verification (200+ expected)
  - Ensures puzzles show blanks, not complete solutions
  - Text extraction and analysis
- **Puzzle Directory**:
  - Metadata file existence
  - Initial grid has blank cells (zeros)
  - Clue count within valid range (17-50)
  - Puzzle image files exist
- **Image Analysis**:
  - White space ratio indicates blank cells
  - Detects if puzzles appear completely filled

#### Usage Example
```python
from kindlemint.validators.sudoku_book_qa import validate_sudoku_book

# Validate a complete book
passed = validate_sudoku_book("/path/to/book.pdf")
# Creates: qa_report.json
```

### 4. CrosswordValidator (`crossword_validator.py`)

Validates crossword puzzles for structure and content integrity.

#### Validation Rules
- Grid structure and dimensions
- Clue-answer consistency
- Word placement validation
- Black square patterns
- Symmetry checks
- Solution verification

### 5. WordSearchValidator (`wordsearch_validator.py`)

Validates word search puzzles for completeness and solvability.

#### Validation Rules
- Grid structure validation
- Word list verification
- All words findable in grid
- Direction validation (horizontal, vertical, diagonal)
- No overlapping word conflicts

## Validation Workflow

### 1. Individual Puzzle Validation
```python
puzzle_data = {
    "id": 1,
    "grid": [[5,3,0,0,7,0,0,0,0], ...],  # 9x9 grid
    "solution": [[5,3,4,6,7,8,9,1,2], ...],  # 9x9 solution
    "difficulty": "medium"
}

validator = SudokuValidator()
issues = validator.validate_puzzle(puzzle_data, puzzle_id=1)
```

### 2. Batch Validation
```python
from kindlemint.validators import validate_puzzle_batch

# Validate all puzzles in a directory
result = validate_puzzle_batch(
    puzzle_dir="/path/to/puzzles",
    puzzle_type="sudoku",
    strict=True  # Treat warnings as errors
)
```

### 3. Full Book Validation Pipeline
```python
# Step 1: Validate puzzle content
content_result = validate_sudoku_content("/path/to/puzzles")

# Step 2: Generate PDF
# ... PDF generation code ...

# Step 3: Validate PDF images
pdf_result = validate_sudoku_pdf("/path/to/book.pdf")

# Step 4: Run comprehensive QA
qa_result = validate_sudoku_book("/path/to/book.pdf")
```

## Validation Results

### ValidationResult Object
```python
{
    "validation_passed": true,
    "total_puzzles": 100,
    "valid_puzzles": 98,
    "invalid_puzzles": 2,
    "errors": 3,
    "warnings": 5,
    "issues": [
        {
            "severity": "error",
            "description": "Duplicate value 5 in row 3",
            "puzzle_id": 42,
            "location": "grid[3][7]",
            "recommendation": "Remove duplicate or correct the value"
        }
    ]
}
```

### Issue Severities
- **ERROR**: Critical issues that must be fixed
- **WARNING**: Issues that should be addressed but aren't blocking
- **INFO**: Informational messages

## Integration with CI/CD

The validators are integrated into the GitHub Actions workflow:

```yaml
- name: Validate Puzzle Content
  run: |
    python -m kindlemint.validators validate_puzzle_batch \
      --dir ./puzzles \
      --type sudoku \
      --strict
```

## Best Practices

1. **Always validate before PDF generation** to catch issues early
2. **Use strict mode** in production to ensure highest quality
3. **Store validation reports** for audit trails
4. **Monitor validation metrics** to identify patterns
5. **Run all three validators** for complete coverage:
   - Content validation (logical correctness)
   - PDF image validation (rendering quality)
   - Book QA validation (overall structure)

## Error Recovery

When validation fails:

1. Check the specific error messages and locations
2. Use the recommendations provided in the validation report
3. Fix issues in the source data
4. Re-run validation
5. Only proceed to PDF generation after all validations pass

## Performance Considerations

- **Batch Processing**: Validators process multiple puzzles efficiently
- **Parallel Validation**: Can run multiple validators concurrently
- **Caching**: Results can be cached to avoid re-validation
- **Memory Usage**: Large books may require increased memory allocation

## Extending Validators

To add new validation rules:

1. Inherit from `PuzzleValidator` base class
2. Implement required abstract methods
3. Add specific validation logic
4. Update the validator registry

Example:
```python
from kindlemint.validators.base_validator import PuzzleValidator

class KakuroValidator(PuzzleValidator):
    def validate_puzzle(self, puzzle_data, puzzle_id):
        # Custom validation logic
        pass
```
