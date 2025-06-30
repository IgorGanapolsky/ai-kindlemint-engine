# Code Hygiene Report
Generated: 2025-06-30 15:51:33
Repository: /Users/igorganapolsky/workspace/git/ai/ai-kindlemint-engine

## Summary
🔍 Code Hygiene Analysis Summary
Found 7 issues across 7 categories:

+----------------+---------+-------------------------------------------------------+
| Category       |   Count | Description                                           |
+================+=========+=======================================================+
| Ci Artifacts   |     132 | Found 132 CI artifact files scattered in the codeb... |
+----------------+---------+-------------------------------------------------------+
| Duplicates     |     304 | Found 304 duplicate files across 103 groups...        |
+----------------+---------+-------------------------------------------------------+
| Empty Dirs     |      10 | Found 10 empty directories...                         |
+----------------+---------+-------------------------------------------------------+
| Gitignore      |       3 | .gitignore is missing 3 recommended patterns...       |
+----------------+---------+-------------------------------------------------------+
| Naming         |       5 | Found 5 files with naming convention issues...        |
+----------------+---------+-------------------------------------------------------+
| Root Clutter   |       1 | Found 1 files cluttering the root directory...        |
+----------------+---------+-------------------------------------------------------+
| Scattered Docs |      70 | Found 70 documentation files that could be better ... |
+----------------+---------+-------------------------------------------------------+

## Detailed Issues

### Ci Artifacts

- Found 132 CI artifact files scattered in the codebase

### Duplicates

- Found 304 duplicate files across 103 groups

### Empty Dirs

- Found 10 empty directories

### Gitignore

- .gitignore is missing 3 recommended patterns

### Naming

- Found 5 files with naming convention issues

### Root Clutter

- Found 1 files cluttering the root directory

### Scattered Docs

- Found 70 documentation files that could be better organized

## Recommended Actions

Run the following command to clean up these issues:
```bash
python agents/code_hygiene_orchestrator.py clean --interactive
```