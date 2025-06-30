# Code Hygiene Report
Generated: 2025-06-30 15:46:52
Repository: /Users/igorganapolsky/workspace/git/ai/ai-kindlemint-engine

## Summary
🔍 Code Hygiene Analysis Summary
Found 8 issues across 8 categories:

+-------------------+---------+-------------------------------------------------------+
| Category          |   Count | Description                                           |
+===================+=========+=======================================================+
| Ci Artifacts      |     130 | Found 130 CI artifact files scattered in the codeb... |
+-------------------+---------+-------------------------------------------------------+
| Duplicates        |     247 | Found 247 duplicate files across 46 groups...         |
+-------------------+---------+-------------------------------------------------------+
| Empty Dirs        |       2 | Found 2 empty directories...                          |
+-------------------+---------+-------------------------------------------------------+
| Gitignore         |      12 | .gitignore is missing 12 recommended patterns...      |
+-------------------+---------+-------------------------------------------------------+
| Naming            |       5 | Found 5 files with naming convention issues...        |
+-------------------+---------+-------------------------------------------------------+
| Root Clutter      |       2 | Found 2 files cluttering the root directory...        |
+-------------------+---------+-------------------------------------------------------+
| Scattered Docs    |      53 | Found 53 documentation files that could be better ... |
+-------------------+---------+-------------------------------------------------------+
| Scattered Scripts |      11 | Found 11 scripts in the root directory...             |
+-------------------+---------+-------------------------------------------------------+

## Detailed Issues

### Ci Artifacts

- Found 130 CI artifact files scattered in the codebase

### Duplicates

- Found 247 duplicate files across 46 groups

### Empty Dirs

- Found 2 empty directories

### Gitignore

- .gitignore is missing 12 recommended patterns

### Naming

- Found 5 files with naming convention issues

### Root Clutter

- Found 2 files cluttering the root directory

### Scattered Docs

- Found 53 documentation files that could be better organized

### Scattered Scripts

- Found 11 scripts in the root directory

## Recommended Actions

Run the following command to clean up these issues:
```bash
python agents/code_hygiene_orchestrator.py clean --interactive
```