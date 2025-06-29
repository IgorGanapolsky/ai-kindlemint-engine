# Book Archival Workflow with GitHub LFS

## Overview

After publishing books to Amazon KDP, we archive them from `active_production` to `published_archive` using GitHub LFS to manage storage efficiently.

## Setup (One-time)

1. **Install Git LFS**:
   ```bash
   brew install git-lfs
   git lfs install
   ```

2. **Verify Installation**:
   ```bash
   git lfs version
   ```

## Archival Process

### 1. List Active Books

See what's ready to archive:
```bash
python scripts/archive_published_books.py --list
```

### 2. Archive a Complete Series

Archive all volumes in a series (recommended after publishing):
```bash
python scripts/archive_published_books.py --series Large_Print_Sudoku_Masters --commit
```

### 3. Archive Individual Book

Archive a specific volume:
```bash
python scripts/archive_published_books.py --book Large_Print_Sudoku_Masters volume_1
```

### 4. Archive Options

- **Keep puzzle images** (not recommended, increases size):
  ```bash
  python scripts/archive_published_books.py --series Large_Print_Sudoku_Masters --keep-puzzles
  ```

- **Custom commit message**:
  ```bash
  python scripts/archive_published_books.py --series Large_Print_Sudoku_Masters --commit --message "Archive Sudoku series after successful launch"
  ```

## What Gets Archived

### Always Archived:
- 📄 PDF interiors (paperback)
- 📱 EPUB files (Kindle)
- 📚 Hardcover packages
- 📊 All metadata files

### Optionally Archived:
- 🖼️ Puzzle images (can be regenerated)

## Storage Structure

```
books/
├── active_production/     # Working files (not in LFS)
│   └── [currently working books]
│
└── published_archive/     # Archived books (in Git LFS)
    └── Series_Name_YYYYMMDD/
        └── volume_X/
            ├── paperback/
            ├── kindle/
            ├── hardcover/
            ├── metadata/
            └── archive_metadata.json
```

## Restoration Process

To restore an archived book:

1. **Pull from LFS**:
   ```bash
   git lfs pull
   ```

2. **Copy back to active**:
   ```bash
   cp -r books/published_archive/Large_Print_Sudoku_Masters_20250627/volume_1 \
         books/active_production/Large_Print_Sudoku_Masters/
   ```

3. **Regenerate puzzles if needed**:
   ```bash
   python scripts/sudoku_generator.py --output books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles --count 100 --difficulty easy
   ```

## Best Practices

1. **Archive After Publishing**: Only archive books that are live on Amazon KDP
2. **Don't Keep Puzzle Images**: They can be regenerated and save ~85MB per volume
3. **Regular Cleanup**: Archive books weekly to keep active_production lean
4. **Verify Before Removal**: The script asks for confirmation before deleting from active_production

## Git LFS Storage Limits

- GitHub Free: 1 GB storage, 1 GB bandwidth/month
- GitHub Pro: 2 GB storage, 2 GB bandwidth/month
- Additional data packs: $5 for 50 GB storage + 50 GB bandwidth

### Storage Estimates:
- PDF interior: ~5-10 MB
- EPUB: ~1-2 MB
- Metadata: < 1 MB
- **Total per book**: ~10-15 MB (without puzzle images)

## Automation

Add to your publishing checklist:
```bash
# After successful KDP publication:
./scripts/archive_published_books.py --series [SERIES_NAME] --commit
git push origin main
```
