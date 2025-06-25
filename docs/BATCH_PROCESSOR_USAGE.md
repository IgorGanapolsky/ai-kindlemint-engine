# 🏭 KindleMint Engine Batch Processor – Usage Guide  
*(docs/BATCH_PROCESSOR_USAGE.md)*  

The **Batch Processor** (`scripts/batch_processor.py`) is a command-line orchestrator that automates every step of KindleMint book production—puzzle generation, PDF/EPUB layout, hardcover packaging, QA, and reporting—for **multiple books in a single run**.  
It is the operational backbone that lets Igor hit the **“5 books per week”** goal without drowning in manual steps.

---

## 1 · Why You Need It
| Pain Without Batch | Relief With Batch |
|--------------------|-------------------|
| Manually invoking 4–5 scripts per book | One command for any number of books |
| Hard to track which volume failed | Auto-saving progress & JSON status |
| Tedious to restart after crash | `--resume` flag continues exactly where it left off |
| No aggregate visibility | Markdown/JSON reports per run with success rate & timings |

---

## 2 · Prerequisites
1. **Python 3.11** + all repo requirements  
   ```bash
   pip install -r requirements.txt
   ```  
2. OS packages for PDF/EPUB tooling (ImageMagick, Ghostscript on macOS/Linux).  
3. Repo checked out at the project root (`ai-kindlemint-engine`).  

---

## 3 · Batch Configuration File
Create a JSON file describing the books to build.  
Example: `config/batch_example.json` (already committed).

Key sections:

| Field | Meaning | Example |
|-------|---------|---------|
| `batch_name` | Friendly label | `"Weekly Book Production"` |
| `delay_between_books` | Seconds to pause to avoid CPU spikes | `60` |
| `books[]` | Array of book objects | — |

Book object essentials:

| Field | Required | Notes |
|-------|----------|-------|
| `id` | ✅ | Unique slug |
| `title`, `subtitle` | ✅ | Display names |
| `series_name`, `volume` | ✅ | Controls folder layout |
| `puzzle_type` | ✅ | `crossword`, `sudoku`, `word_search` |
| `puzzle_count`, `difficulty` | ✅ | Generation parameters |
| `pages` | ✅ | Needed for spine calc |
| `create_epub`, `create_hardcover` | optional | Booleans |
| `puzzle_params`, `pdf_params` | optional | Script-specific flags |

---

## 4 · Running a Batch

### 4.1 Basic run
```bash
python scripts/batch_processor.py config/batch_example.json
```
Produces:
* `batch_reports/<TIMESTAMP>/batch_summary.md` – human-readable report  
* `batch_reports/<TIMESTAMP>/batch_report.json` – machine report  
* `batch_reports/<TIMESTAMP>/book_<ID>.json` – per-book logs

### 4.2 Verbose mode
```bash
python scripts/batch_processor.py config/batch_example.json --verbose
```
Stream debug logs to console & `batch_processor.log`.

### 4.3 Resume after crash
If power fails at book 3/5:
```bash
python scripts/batch_processor.py config/batch_example.json \
       --resume batch_reports/20250624_1642/batch_progress.json
```
Processor skips completed books and continues.

---

## 5 · Understanding Output Structure
```
books/
└─ active_production/
   └─ <Series>/
      └─ volume_<N>/
         ├─ puzzles/               # Generated puzzles
         ├─ paperback/             # Interior PDF + metadata
         ├─ kindle/                # EPUB + metadata
         ├─ hardcover/             # Cover wrap, KDP JSON, checklist
         └─ qa/                    # JSON + txt reports
batch_reports/
└─ 20250624_1642/
   ├─ batch_summary.md
   ├─ batch_report.json
   └─ book_<ID>.json
```

---

## 6 · How It Helps Achieve 5 Books/Week

1. **Serial automation** – Generates & validates each book in ~20 min  
   → 5 books ≈ 2 hrs of unattended runtime.  
2. **Error containment** – One bad volume doesn’t abort the whole run; QA must pass (`publish_ready:true`).  
3. **Resume & logging** – Overnight runs safe to resume, so failures never waste previous work.  
4. **Unified reports** – Quick glance shows if weekly quota met; flags which titles need fixes.  

---

## 7 · Tips & Best Practices
* **Small test batch** first (`books: [1 item]`) to verify config.  
* Keep **cover images** in `templates/` or series folder; batch will copy paths.  
* Use **GitHub Actions** to schedule the command on a self-hosted runner for real hands-off nights.  
* Include only **one heavy step at a time** (e.g., turn off EPUB when troubleshooting PDF).  
* Version control your `config/*.json` to track series roadmap.  

---

## 8 · Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `FileNotFoundError` for generator script | Missing or unsupported puzzle generator script (e.g., Sudoku, Word Search) | Implement or add the appropriate `scripts/*.py` or choose a supported `puzzle_type` |
| `Step create_pdf failed` | Fonts or images missing | Check paths, rerun with `--verbose` |
| `publish_ready:false` in QA | Layout problems | Open `qa_validation_report.txt` for details |
| Batch never ends | External script awaiting user input | Add `--non-interactive` flags or mock resources |

---

## 9 · Next Enhancements
* Parallel execution per CPU core  
* Slack / email notification on batch completion  
* Granular CLI flags (`--skip-qa`, `--only-qa`)  
* Integration with cost-tracking scripts for real-time ROI.

---

### Happy Minting 🚀
With the batch processor in place, Igor can confidently queue up **an entire week’s catalogue in one go**, wake up, skim the summary, and upload the passed books to KDP—hitting the revenue-driven target with minimal friction.
