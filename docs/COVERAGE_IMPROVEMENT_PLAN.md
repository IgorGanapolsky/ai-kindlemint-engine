# 📈 Coverage Improvement Plan: 10% → 50%+

## Current Status
- **Current Coverage**: 10%
- **Target Coverage**: 50%+ (Industry standard)
- **Timeline**: 1-2 weeks

## 🎯 Quick Wins (Day 1: 10% → 25%)

### 1. Zero-Coverage Modules (Easiest)
These files have 0% coverage and just need basic tests:

```bash
# Run these commands to add tests for each module:
pytest tests/unit/test_agent_types.py -v --cov=src/kindlemint/agents/agent_types
pytest tests/unit/test_utils_config.py -v --cov=src/kindlemint/utils/config
pytest tests/unit/test_base_validator.py -v --cov=src/kindlemint/validators/base_validator
```

**Priority Targets** (0% → 70%+ each):
- [ ] `agents/agent_types.py` (14 lines) ✅ Test created
- [ ] `utils/config.py` (106 lines) ✅ Test created
- [ ] `validators/base_validator.py` (97 lines) ✅ Test created
- [ ] `cli.py` (60 lines) - Just test command parsing
- [ ] `social/__init__.py` (2 lines) - Just imports

### 2. Low-Coverage Modules (Under 20%)
Boost these from ~10% to 60%+:

- [ ] `engines/sudoku.py` (9% → 60%)
- [ ] `engines/wordsearch.py` (18% → 60%)
- [ ] `utils/api.py` (17% → 60%)
- [ ] `validators/crossword_validator.py` (10% → 60%)

## 📊 Week 1 Strategy (25% → 40%)

### Day 2-3: Core Business Logic
Focus on your money-making code:

```python
# tests/unit/test_sudoku_engine.py
def test_sudoku_generation():
    """Test sudoku puzzle generation"""
    from kindlemint.engines.sudoku import SudokuEngine

    engine = SudokuEngine()
    puzzle = engine.generate(difficulty="easy")
    assert puzzle.is_valid()
    assert puzzle.difficulty == "easy"
    assert len(puzzle.grid) == 9
```

### Day 4-5: Agent System
Test the agent framework:

```python
# tests/unit/test_message_protocol.py
def test_agent_messages():
    """Test agent communication"""
    from kindlemint.agents.message_protocol import Message, MessageType

    msg = Message(
        type=MessageType.TASK,
        content="Generate puzzle",
        sender="coordinator"
    )
    assert msg.type == MessageType.TASK
```

## 🚀 Week 2 Strategy (40% → 50%+)

### Integration Tests
These give more coverage per test:

```python
# tests/integration/test_book_pipeline.py
def test_full_book_generation():
    """Test complete book generation pipeline"""
    # This single test might cover 5-10 modules!
    from kindlemint.engines.sudoku import SudokuEngine
    from kindlemint.validators.sudoku_validator import SudokuValidator

    engine = SudokuEngine()
    validator = SudokuValidator()

    puzzles = engine.generate_book(count=10)
    result = validator.validate_book(puzzles)
    assert result.is_valid
```

## 💡 Pro Tips for Fast Coverage

### 1. Use Parametrized Tests
```python
@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_puzzle_difficulties(difficulty):
    puzzle = generate_puzzle(difficulty)
    assert puzzle.difficulty == difficulty
```

### 2. Mock External Dependencies
```python
@patch('kindlemint.utils.api.requests.post')
def test_api_call(mock_post):
    mock_post.return_value.json.return_value = {"status": "ok"}
    result = make_api_call()
    assert result["status"] == "ok"
```

### 3. Test Error Cases
```python
def test_invalid_input():
    with pytest.raises(ValueError):
        SudokuEngine().generate(difficulty="impossible")
```

## 📋 Coverage Tracking Commands

```bash
# Run all tests with coverage
pytest --cov=src/kindlemint --cov-report=html

# View coverage report in browser
open htmlcov/index.html

# Check specific module coverage
pytest tests/unit/test_sudoku_engine.py --cov=src/kindlemint/engines/sudoku --cov-report=term-missing

# Update SonarCloud
git add tests/
git commit -m "test: improve coverage from 10% to 25%"
git push
```

## 🎯 Module Priority List

### High Impact (Test These First):
1. **engines/** - Core business logic
2. **validators/** - Quality assurance
3. **agents/base_agent.py** - Foundation class
4. **utils/config.py** - Used everywhere

### Medium Impact:
1. **agents/message_protocol.py** - Already 77%
2. **agents/task_system.py** - Already 72%
3. **utils/__init__.py** - Quick win

### Low Priority (Test Later):
1. **orchestrator/** - Complex, mock-heavy
2. **social/** - Not core functionality
3. **context/** - Voice processing complexity

## 🏆 Success Metrics

- **Day 1**: 10% → 25% (Quick wins)
- **Week 1**: 25% → 40% (Core modules)
- **Week 2**: 40% → 50%+ (Integration)

## 🔄 Continuous Improvement

1. **Pre-commit Hook**: Add coverage check
   ```yaml
   # .pre-commit-config.yaml
   - repo: local
     hooks:
       - id: coverage-check
         name: Check test coverage
         entry: pytest --cov=src/kindlemint --cov-fail-under=40
         language: system
         pass_filenames: false
   ```

2. **CI Pipeline**: Fail builds under 40%
   ```yaml
   # .github/workflows/tests.yml
   - name: Check coverage
     run: pytest --cov=src/kindlemint --cov-fail-under=40
   ```

3. **SonarCloud**: Set quality gate at 40%

Remember: **Perfect is the enemy of good**. Get to 50% first, then improve gradually!
