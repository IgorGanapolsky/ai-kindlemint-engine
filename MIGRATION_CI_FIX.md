# CI Fix & Migration Strategy

## Problem
We started archiving scripts but CI/CD workflows depend on specific script locations:
- `enhanced_qa_validator_v3.py` - Used by comprehensive_qa.yml
- `enhanced_qa_validator_v2.py` - Used by book_qa_validation.yml and production_qa.yml
- `crossword_engine_v3_fixed.py` - Used by tests

## Immediate Fix (Completed)
✅ Restored critical scripts:
- enhanced_qa_validator.py
- enhanced_qa_validator_v2.py
- enhanced_qa_validator_v3.py
- crossword_engine_v3_fixed.py

## Proper Migration Strategy

### Phase 1: Compatibility Layer (This Week)
1. Keep critical scripts in place
2. Create new modular structure in parallel
3. Add import redirects in scripts

### Phase 2: Update Imports (Next Week)
1. Update test imports to use new structure
2. Update GitHub Actions workflows
3. Update any remaining script dependencies

### Phase 3: Remove Old Scripts (Week 3)
1. Verify all imports work with new structure
2. Archive old scripts
3. Clean up compatibility layer

## Scripts That MUST Stay (For Now)
```
scripts/
├── enhanced_qa_validator_v2.py     # Used by CI
├── enhanced_qa_validator_v3.py     # Used by CI
├── crossword_engine_v3_fixed.py    # Used by tests
├── sudoku_generator.py             # Used by multiple scripts
├── word_search_generator.py        # Used by multiple scripts
├── book_layout_bot.py              # Core PDF generation
├── config_loader.py                # Used everywhere
└── api_manager_enhanced.py         # API management
```

## Safe to Archive
- All volume-specific scripts (create_volume_*.py)
- Old versions without CI dependencies
- Duplicate scripts not in active use

## Next Steps
1. Commit the restored files to fix CI
2. Create compatibility imports
3. Gradually migrate with proper testing
