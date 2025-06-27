# Safe Migration Example

## How to Migrate a Module Without Breaking CI

### Step 1: Copy the Module
```bash
# Example: Migrating config_loader.py
cp scripts/config_loader.py src/kindlemint/utils/config.py
```

### Step 2: Update Imports in New Module
```python
# In src/kindlemint/utils/config.py
# Change:
from scripts.some_other_module import something

# To:
from kindlemint.some_other_module import something
# Or keep using scripts. during transition
```

### Step 3: Create a Wrapper in Original Location
```python
# In scripts/config_loader.py
"""
Compatibility wrapper - redirects to new location.
TODO: Remove after all imports are updated.
"""
import warnings
warnings.warn(
    "Importing from scripts.config_loader is deprecated. "
    "Use 'from kindlemint.utils.config import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from kindlemint.utils.config import *
```

### Step 4: Update Package __init__.py
```python
# In src/kindlemint/utils/__init__.py
from .config import load_config, ConfigManager

__all__ = ['load_config', 'ConfigManager']
```

### Step 5: Test Both Import Styles
```python
# Old style (shows deprecation warning but works)
from scripts.config_loader import load_config

# New style (preferred)
from kindlemint.utils.config import load_config
```

### Step 6: Gradually Update Imports
1. Update test files first
2. Update non-critical scripts
3. Update CI workflows last
4. Remove compatibility wrapper

## Example Migration Order

### Phase 1: Low Risk (No CI Dependencies)
- [ ] config_loader.py → utils/config.py
- [ ] api_manager_enhanced.py → utils/api.py  
- [ ] claude_cost_tracker.py → utils/cost_tracker.py

### Phase 2: Medium Risk (Test Dependencies)
- [ ] sudoku_generator.py → engines/sudoku.py
- [ ] word_search_generator.py → engines/wordsearch.py
- [ ] puzzle_validators.py → validators/puzzle.py

### Phase 3: High Risk (CI Dependencies)  
- [ ] enhanced_qa_validator_v3.py → validators/qa.py
- [ ] crossword_engine_v3_fixed.py → engines/crossword.py
- [ ] book_layout_bot.py → generators/pdf.py

## Benefits of This Approach
1. ✅ No broken imports
2. ✅ CI continues to work
3. ✅ Gradual migration
4. ✅ Easy rollback if needed
5. ✅ Clear deprecation warnings