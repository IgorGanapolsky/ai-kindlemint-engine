# KindleMint Engine – Implementation Plan

> **Last major update: June 25 2025 – Quality-Refresh complete**  
> Crossword Engine v3 & Enhanced QA Validator v2 are live; books now pass KDP checks with 95 %+ QA scores.

## Current State (June 2025)

### ✅ Implemented
- **Crossword Engine v3** – real, solvable 15×15 grids (theme-aware, balanced clues)  
- **Enhanced QA Validator v2** – dictionary validation, intersection checks, grid-connectivity, duplicate detection  
- Stable **PDF interior generator** (book_layout_bot)  
- EPUB & hardcover cover-wrap generation  
- GitHub Actions: content-first QA + nightly market-research PRs  
- Manual but reliable KDP publishing workflow  
- Basic Sudoku & Word-Search generators (CLI)

### 🚧 Partially Implemented
- Cover template automation (currently DALL-E manual step)  
- Sales/revenue CSV ingest & dashboard (local prototype)  
- Cost usage tracking (SERPAPI / Claude)  
- Batch file organisation (semi-manual)

### ❌ Not Implemented
- AWS infrastructure
- Zero-touch publishing
- Revenue tracking
- Cost monitoring
- Sales analytics
- Multi-series management

_(no longer listed: “Quality assurance” – now complete)_

## Realistic 90-Day Plan
### Month 1 – Hardening (July 2025)
**Goal**: Consolidate quality-refresh & improve developer experience**

| Week | Focus | Outcome |
|------|-------|---------|
| 1 | Remove remaining hard-coded paths, centralise config | One-command book build |
| 2 | Finish unit-tests for Crossword Engine v3 & QA validator | 80 %+ test coverage |
| 3 | Automate SERPAPI/Claude usage logging | Daily cost report |
| 4 | Publish updated documentation & video walkthrough | On-boarding in <30 min |

### Month 2 – Feature Growth (August 2025)
**Goal**: Expand product offering & monetisation insights**

| Week | Focus | Outcome |
|------|-------|---------|
| 1 | Integrate Sudoku & Word-Search into book-layout bot | Multi-puzzle books |
| 2 | Implement cover-template CLI (Inkscape/SVG) | Repeatable, brand-consistent covers |
| 3 | Sales CSV parser + local dashboard (Streamlit) | Daily revenue snapshot |
| 4 | Beta “batch generator” CLI (create 5 books in one run) | Throughput ↑ 3× |

### Month 3 – Scale Prep (September 2025)
**Goal**: Prepare for light automation & multi-series output**

| Week | Focus | Outcome |
|------|-------|---------|
| 1-2 | Remote storage option (S3 or Backblaze) for generated assets | Cloud archive toggle |
| 3 | Production checklist GitHub Action (opens PR with TODOs) | Fewer human errors |
| 4 | Pilot 2nd puzzle-book series, measure per-book time | Sustain 10 books / week |

## Technical Debt to Address

1. **Configuration Cleanup**  
   • Finalise `.env` & `config.yaml` usage, remove inline constants  
2. **Test Coverage**  
   • Unit & integration tests for Sudoku / Word-Search engines  
   • Mock KDP validator in CI  
3. **Performance**  
   • Profile Crossword Engine v3 backtracking (target <10 s per puzzle)  
4. **Documentation**  
   • Keep README & PLAN in sync (add doc-linter)  
   • Record 2-min “generate book” screencast

## Cost Reality Check

### Current Costs (Estimated)
- GitHub Actions: Free tier
- SERPAPI: $0-50/month
- Claude API: $20/month (via Claude Max)
- Total: ~$20-70/month

### Break-even Analysis
- Need 2-3 book sales/month to cover costs
- Each book: ~$3-5 profit
- Target: 10 books live by end of Q3
 - Target: 20 books live by end of Q3

## What We're NOT Building (Yet)

1. **Full Automation** - KDP doesn't allow it
2. **AWS Infrastructure** - Overkill for current scale
3. **Complex AI** - Current approach works fine
4. **Revenue API** - KDP doesn't provide one

## Success Metrics

### Q3 2025 Goals
- [ ] 3 puzzle types supported (Crossword, Sudoku, Word-Search)
- [ ] <20 min automated work per book
- [ ] 2 active series

### Q4 2025 Goals
- [ ] $750 / month net revenue
- [ ] 5 active series
- [ ] 2 external contributors

## Next Immediate Steps

1. **Today**: Tag v3.0 release, update CHANGELOG ✅  
2. **This Week**: Run `deploy_fixes.py test` on all existing books  
3. **This Month**: Publish Vol 4-5 of Crossword Masters (quality-refreshed)  
4. **Next Month**: Merge Sudoku generator into main workflow

## Notes

- Keep it simple - complexity killed v1
- Manual processes are OK if documented
- Focus on book quality over automation
- Track actual time savings, not theoretical

---

Last Updated: June 25 2025