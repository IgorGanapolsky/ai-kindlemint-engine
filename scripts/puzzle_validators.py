#!/usr/bin/env python3
"""
Puzzle Validators - Domain-aware validation for puzzles
"""
import json
import re
from collections import Counter
from math import sqrt
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import PyPDF2


def validate_sudoku(metadata_dir):
    """
    Validate Sudoku puzzles for uniqueness, solvability, and rule compliance.
    Returns a list of issues: [{ 'puzzle_id': int, 'description': str }, ...]
    """
    issues = []
    md = Path(metadata_dir)
    for meta_file in sorted(md.glob("sudoku_puzzle_*.json")):
        try:
            data = json.loads(meta_file.read_text())
            pid = data.get("id")
            grid = data.get("initial_grid")
            n = len(grid)
            # Check grid shape
            if any(len(row) != n for row in grid):
                issues.append({"puzzle_id": pid, "description": "Grid is not square"})
                continue
            # Check values
            for r, row in enumerate(grid):
                for c, v in enumerate(row):
                    if not isinstance(v, int) or v < 0 or v > n:
                        issues.append(
                            {
                                "puzzle_id": pid,
                                "description": f"Invalid value at ({r},{c}): {v}",
                            }
                        )
            # Check row/col uniqueness
            for i in range(n):
                seen = set()
                for v in grid[i]:
                    if v != 0 and v in seen:
                        issues.append(
                            {
                                "puzzle_id": pid,
                                "description": f"Duplicate value {v} in row {i}",
                            }
                        )
                    seen.add(v)
                seen = set()
                for row in grid:
                    v = row[i]
                    if v != 0 and v in seen:
                        issues.append(
                            {
                                "puzzle_id": pid,
                                "description": f"Duplicate value {v} in column {i}",
                            }
                        )
                    seen.add(v)
            # Check subgrid uniqueness if possible
            block = int(sqrt(n))
            if block * block == n:
                for br in range(0, n, block):
                    for bc in range(0, n, block):
                        seen = set()
                        for r in range(br, br + block):
                            for c in range(bc, bc + block):
                                v = grid[r][c]
                                if v != 0 and v in seen:
                                    issues.append(
                                        {
                                            "puzzle_id": pid,
                                            "description": f"Duplicate value {v} in block starting at ({br},{bc})",
                                        }
                                    )
                                seen.add(v)
            # Count solutions
            sol_count = _count_solutions(grid, limit=2)
            if sol_count == 0:
                issues.append({"puzzle_id": pid, "description": "No valid solutions"})
            elif sol_count > 1:
                issues.append(
                    {"puzzle_id": pid, "description": "Multiple solutions detected"}
                )
        except Exception as e:
            issues.append(
                {
                    "puzzle_id": None,
                    "description": f"Error validating puzzle file {meta_file.name}: {e}",
                }
            )
    return issues


def _count_solutions(grid, limit=2):
    """Backtracking solver to count solutions up to a limit."""
    n = len(grid)
    # Find first empty cell
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                total = 0
                for v in range(1, n + 1):
                    if _is_safe(grid, r, c, v):
                        grid[r][c] = v
                        total += _count_solutions(grid, limit)
                        grid[r][c] = 0
                        if total >= limit:
                            return total
                return total
    # No empty cells: found a solution
    return 1


def _is_safe(grid, r, c, v):
    n = len(grid)
    # Row/col
    for i in range(n):
        if grid[r][i] == v or grid[i][c] == v:
            return False
    # Block
    block = int(sqrt(n))
    if block * block == n:
        br = (r // block) * block
        bc = (c // block) * block
        for i in range(br, br + block):
            for j in range(bc, bc + block):
                if grid[i][j] == v:
                    return False
    return True


def validate_word_search(metadata_dir):
    """
    Validate Word Search puzzles to ensure each word appears exactly once.
    Returns a list of issues: [{ 'puzzle_id': int, 'word': str, 'description': str }, ...]
    """
    issues = []
    md = Path(metadata_dir)
    for meta_file in sorted(md.glob("word_search_puzzle_*.json")):
        try:
            data = json.loads(meta_file.read_text())
            pid = data.get("id")
            grid = data.get("grid", [])
            words = data.get("words", [])
            # Build char matrix
            n = len(grid)
            if any(len(row) != n for row in grid):
                issues.append(
                    {
                        "puzzle_id": pid,
                        "word": None,
                        "description": "Grid is not square",
                    }
                )
                continue
            # Search each word
            for w in words:
                count = _find_word_count(grid, w)
                if count == 0:
                    issues.append(
                        {"puzzle_id": pid, "word": w, "description": "Word not found"}
                    )
                elif count > 1:
                    issues.append(
                        {
                            "puzzle_id": pid,
                            "word": w,
                            "description": f"Word found {count} times",
                        }
                    )
        except Exception as e:
            issues.append(
                {
                    "puzzle_id": None,
                    "word": None,
                    "description": f"Error validating puzzle file {meta_file.name}: {e}",
                }
            )
    return issues


def _find_word_count(grid, word):
    """Count word occurrences in all 8 directions."""
    n = len(grid)
    word = word.upper()
    wlen = len(word)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    count = 0
    for r in range(n):
        for c in range(n):
            for dr, dc in dirs:
                rr, cc = r, c
                matched = True
                for ch in word:
                    if (
                        rr < 0
                        or rr >= n
                        or cc < 0
                        or cc >= n
                        or grid[rr][cc].upper() != ch
                    ):
                        matched = False
                        break
                    rr += dr
                    cc += dc
                if matched:
                    count += 1
    return count


def validate_crossword(metadata_dir):
    """
    Advanced crossword validation with solution checks.
    Returns a list of issues: [{ 'puzzle_id': int, 'description': str }, ...]
    """
    issues = []
    md = Path(metadata_dir)
    for meta_file in sorted(md.glob("puzzle_*.json")):
        try:
            data = json.loads(meta_file.read_text())
            pid = data.get("id")
            clues = data.get("clues", {})
            pos_map = data.get("clue_positions", {})
            grid = data.get("grid_pattern")

            if grid:
                # Domain-aware validation only when grid pattern is available
                # Check for empty or invalid answers
                for direction in ["across", "down"]:
                    for clue_data in clues.get(direction, []):
                        if len(clue_data) < 3:
                            issues.append(
                                {
                                    "puzzle_id": pid,
                                    "description": f"Invalid {direction} clue format",
                                }
                            )
                            continue
                        num, clue_text, answer = (
                            clue_data[0],
                            clue_data[1],
                            clue_data[2],
                        )
                        if not answer or not answer.strip():
                            issues.append(
                                {
                                    "puzzle_id": pid,
                                    "description": f"Empty answer for {direction} {num}",
                                }
                            )
                        if not clue_text or clue_text.strip() == "":
                            issues.append(
                                {
                                    "puzzle_id": pid,
                                    "description": f"Empty clue text for {direction} {num}",
                                }
                            )
                        if answer and not answer.replace(" ", "").isalpha():
                            issues.append(
                                {
                                    "puzzle_id": pid,
                                    "description": f'Invalid answer "{answer}" for {direction} {num} - contains non-letters',
                                }
                            )
                # Validate grid-based length and positions
                # Build number to position mapping
                # Build number to position mapping
                number_positions = {}
                for key, num in pos_map.items():
                    try:
                        r, c = map(int, key.split(","))
                        number_positions[num] = (r, c)
                    except Exception:
                        continue
                # Validate across clues
                for num, _, ans in clues.get("across", []):
                    if num not in number_positions:
                        issues.append(
                            {
                                "puzzle_id": pid,
                                "description": f"No position for across clue number {num}",
                            }
                        )
                        continue
                    r, c = number_positions[num]
                    # Count horizontal cells until black square or edge
                    length = 0
                    while c + length < len(grid[0]) and grid[r][c + length] != "#":
                        length += 1
                    if length != len(ans):
                        issues.append(
                            {
                                "puzzle_id": pid,
                                "description": f"Across clue {num} length mismatch: expected {length}, got {len(ans)}",
                            }
                        )
                # Validate down clues
                for num, _, ans in clues.get("down", []):
                    if num not in number_positions:
                        issues.append(
                            {
                                "puzzle_id": pid,
                                "description": f"No position for down clue number {num}",
                            }
                        )
                        continue
                    r, c = number_positions[num]
                    length = 0
                    while r + length < len(grid) and grid[r + length][c] != "#":
                        length += 1
                    if length != len(ans):
                        issues.append(
                            {
                                "puzzle_id": pid,
                                "description": f"Down clue {num} length mismatch: expected {length}, got {len(ans)}",
                            }
                        )
            else:
                # Fallback: basic count check
                expected = len(clues.get("across", [])) + len(clues.get("down", []))
                actual = len(pos_map)
                if expected != actual:
                    issues.append(
                        {
                            "puzzle_id": pid,
                            "description": f"Expected {expected} clues, found {actual} positions",
                        }
                    )
        except Exception as e:
            issues.append(
                {
                    "puzzle_id": None,
                    "description": f"Error validating puzzle file {meta_file.name}: {e}",
                }
            )
    return issues


def validate_crossword_solutions_in_pdf(pdf_path: Path) -> Tuple[bool, Dict]:
    """
    Validate that all crossword solutions in a PDF are properly filled with letters.
    Returns (success, stats_dict)
    """
    try:
        with open(pdf_path, "rb") as file:
            pdf = PyPDF2.PdfReader(file)
            page_count = len(pdf.pages)

            # Find solution section
            solution_start = None
            for i in range(min(100, page_count), page_count):
                text = pdf.pages[i].extract_text()
                if "Solution" in text or "Answer" in text:
                    solution_start = i
                    break

            if solution_start is None:
                return False, {"error": "No solution section found"}

            # Check each solution page
            empty_solutions = []
            valid_solutions = 0
            total_solutions = 0

            for page_num in range(solution_start, page_count):
                page_text = pdf.pages[page_num].extract_text()

                # Find puzzle numbers
                puzzle_matches = re.findall(
                    r"(?:Solution for |Answer to )?Puzzle (\d+)", page_text
                )

                for puzzle_num in puzzle_matches:
                    total_solutions += 1
                    puzzle_id = int(puzzle_num)

                    # Extract solution text after puzzle number
                    parts = page_text.split(f"Puzzle {puzzle_num}")
                    if len(parts) > 1:
                        solution_text = parts[1][:1500]  # Get more text

                        # Count letters in solution
                        letter_count = len(re.findall(r"[A-Z]", solution_text))

                        # Check for grid pattern (rows of letters)
                        grid_lines = re.findall(r"[A-Z\s■]{10,}", solution_text)
                        grid_letter_count = sum(
                            len(re.findall(r"[A-Z]", line)) for line in grid_lines
                        )

                        # A 15x15 crossword should have 150+ letters
                        if letter_count < 150 or grid_letter_count < 100:
                            empty_solutions.append(puzzle_id)
                        else:
                            # Additional check: variety of letters
                            unique_letters = len(
                                set(re.findall(r"[A-Z]", solution_text))
                            )
                            if unique_letters < 15:  # Should use most of alphabet
                                empty_solutions.append(puzzle_id)
                            else:
                                valid_solutions += 1

            success_rate = (
                valid_solutions / total_solutions if total_solutions > 0 else 0
            )

            return success_rate > 0.95, {
                "total_solutions": total_solutions,
                "valid_solutions": valid_solutions,
                "empty_solutions": len(empty_solutions),
                "empty_solution_ids": empty_solutions[:10],  # First 10
                "success_rate": success_rate,
            }

    except Exception as e:
        return False, {"error": str(e)}


def validate_clue_content(clue_text: str) -> Tuple[bool, str]:
    """
    Validate individual clue content for quality and correctness.
    Returns (is_valid, error_message)
    """
    # Check for placeholder patterns
    placeholder_patterns = [
        r"word meaning \w+",
        r"related term",
        r"placeholder",
        r"test",
        r"^clue \d+$",
        r"^word \d+$",
        r"TODO",
        r"FIXME",
        r"XXX",
        r"temp",
        r"dummy",
    ]

    clue_lower = clue_text.lower().strip()

    for pattern in placeholder_patterns:
        if re.search(pattern, clue_lower, re.IGNORECASE):
            return False, f"Placeholder pattern detected: {pattern}"

    # Check minimum quality
    if len(clue_text.split()) < 2:
        return False, "Clue too short (less than 2 words)"

    if len(clue_text) < 5:
        return False, "Clue too short (less than 5 characters)"

    # Check for repetitive patterns
    if re.match(r"^(\w+\s+){1,2}$", clue_text):
        return False, "Clue appears to be incomplete"

    # Check for question marks or incomplete sentences
    if clue_text.count("?") > 3:
        return False, "Too many question marks"

    return True, ""


def validate_crossword_clue_quality_in_pdf(pdf_path: Path) -> Tuple[bool, Dict]:
    """
    Validate that crossword clues in PDF are actual clues, not placeholders.
    Returns (success, stats_dict)
    """
    try:
        with open(pdf_path, "rb") as file:
            pdf = PyPDF2.PdfReader(file)

            invalid_clues = []
            total_clues = 0
            pages_checked = 0

            # Check first 50 pages for puzzles
            for page_num in range(min(50, len(pdf.pages))):
                page_text = pdf.pages[page_num].extract_text()

                # Look for puzzle pages
                if re.search(r"Puzzle \d+ - Clues", page_text) or "ACROSS" in page_text:
                    pages_checked += 1

                    # Extract clues using various patterns
                    clue_patterns = [
                        r"\d+\.\s+(.+?)(?=\d+\.|$|ACROSS|DOWN)",  # Numbered clues
                        r"(?:ACROSS|DOWN)\s*\n((?:.+\n)+)",  # Section-based
                    ]

                    for pattern in clue_patterns:
                        matches = re.findall(pattern, page_text, re.MULTILINE)
                        for match in matches:
                            # Clean up the match
                            clue_lines = match.strip().split("\n")
                            for line in clue_lines:
                                # Extract clue text after number
                                clue_match = re.match(r"\d+\.\s+(.+)", line.strip())
                                if clue_match:
                                    clue_text = clue_match.group(1).strip()
                                    total_clues += 1

                                    is_valid, error = validate_clue_content(clue_text)
                                    if not is_valid:
                                        invalid_clues.append(
                                            {
                                                "page": page_num + 1,
                                                "clue": clue_text,
                                                "error": error,
                                            }
                                        )

            success_rate = (
                (total_clues - len(invalid_clues)) / total_clues
                if total_clues > 0
                else 0
            )

            return success_rate > 0.95, {
                "pages_checked": pages_checked,
                "total_clues": total_clues,
                "invalid_clues": len(invalid_clues),
                "invalid_examples": invalid_clues[:10],  # First 10 examples
                "success_rate": success_rate,
            }

    except Exception as e:
        return False, {"error": str(e)}


def validate_crossword_metadata(metadata_dir: Path) -> List[Dict]:
    """Enhanced crossword validation for metadata with strict answer checks"""
    issues = []

    # First run standard validation
    standard_issues = validate_crossword(metadata_dir)
    issues.extend(standard_issues)

    # Additional answer validation
    md = Path(metadata_dir)
    for meta_file in sorted(md.glob("puzzle_*.json")):
        try:
            data = json.loads(meta_file.read_text())
            pid = data.get("id")
            clues = data.get("clues", {})

            # Check for duplicate clues
            all_clue_texts = []
            for direction in ["across", "down"]:
                for clue_data in clues.get(direction, []):
                    if len(clue_data) > 1:
                        all_clue_texts.append(clue_data[1])

            clue_counts = Counter(all_clue_texts)
            for clue, count in clue_counts.items():
                if count > 2:  # Allow up to 2 duplicates
                    issues.append(
                        {
                            "puzzle_id": pid,
                            "description": f'Clue "{clue}" appears {count} times',
                        }
                    )

            # Validate each clue content
            for direction in ["across", "down"]:
                for clue_data in clues.get(direction, []):
                    if len(clue_data) > 1:
                        clue_text = clue_data[1]
                        is_valid, error = validate_clue_content(clue_text)
                        if not is_valid:
                            issues.append(
                                {
                                    "puzzle_id": pid,
                                    "description": f'Invalid clue: {error} - "{clue_text}"',
                                }
                            )

        except Exception as e:
            issues.append(
                {
                    "puzzle_id": None,
                    "description": f"Error in enhanced validation: {str(e)}",
                }
            )

    return issues
