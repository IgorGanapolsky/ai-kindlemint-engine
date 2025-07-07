#!/bin/bash
# STEALTH MODE: Parallel Book Factory
# Generate multiple books simultaneously using git worktrees

echo "🏭 PARALLEL BOOK FACTORY - STEALTH MODE"
echo "======================================"

# Create worktrees for parallel execution
echo "🔧 Setting up parallel worktrees..."

# Book 1: Sudoku for Beginners
git worktree add ../worktrees/book-sudoku-beginners -b books/sudoku-beginners 2>/dev/null || true
cd ../worktrees/book-sudoku-beginners
cp ../../api/../scripts/quick_book_generator.py .
python quick_book_generator.py &
PID1=$!

# Book 2: Crossword Classics  
git worktree add ../worktrees/book-crossword-classics -b books/crossword-classics 2>/dev/null || true
cd ../worktrees/book-crossword-classics
cp ../../api/../scripts/quick_book_generator.py .
python quick_book_generator.py &
PID2=$!

# Book 3: Word Search Wonders
git worktree add ../worktrees/book-wordsearch-wonders -b books/wordsearch-wonders 2>/dev/null || true
cd ../worktrees/book-wordsearch-wonders  
cp ../../api/../scripts/quick_book_generator.py .
python quick_book_generator.py &
PID3=$!

# Wait for all to complete
echo "⏳ Generating 3 books in parallel..."
wait $PID1 $PID2 $PID3

echo "✅ All books generated!"
echo ""
echo "📊 REVENUE POTENTIAL:"
echo "- 3 books x $9.99 = $29.97 per customer"
echo "- 100 sales/month = $2,997/month"
echo "- 1000 sales/month = $29,970/month"
echo ""
echo "🚀 NEXT: Upload to KDP and START SELLING!"