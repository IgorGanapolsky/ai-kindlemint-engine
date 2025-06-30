# AI KindleMint Engine – GAP Analysis
*(Repository snapshot: 24 June 2025)*

## 1 · Executive Summary
Igor’s **AI KindleMint Engine** is a semi-automated pipeline that reliably produces KDP-compliant puzzle books, but several roadmap items and README aspirations remain unimplemented.
The core engine is technically sound for small-scale production (≈1–2 books / week) and can plausibly reach break-even with modest sales volumes. Scaling to the fully-automated, multi-series vision will require closing key functional gaps (cover automation, QA depth, sales analytics) and—critically—solving the distribution problem (manual KDP upload, market visibility).

## 2 · Scope of Comparison
| Source | Type | Key Promises / Goals |
|--------|------|----------------------|
| **plan.md** (last updated Jun 24 2024) | 90-day roadmap | • Stabilise core scripts<br>• Add Sudoku & Word Search<br>• Build local dashboard & batch support<br>• Publish 10 books, 3 puzzle types by Q3 |
| **README.md / README_HONEST.md** (Jun 2024) | Project status & marketing | • 60 % automation, 1 book published<br>• Market research via GitHub Actions<br>• “Zero-touch” publishing **not** available |
| **Repository implementation** | Code & data | • Crossword, PDF/EPUB, market research scripts present & working<br>• Quality checks via GH Actions<br>• No AWS / revenue automation<br>• 1 active series, volume 2 WIP |

## 3 · Detailed GAP Matrix

| Capability | Plan Target | README Claim | **Observed Reality** | GAP & Impact |
|------------|-------------|--------------|----------------------|--------------|
| Crossword generation | ✅ (already) | ✅ | ✅ scripts/crossword_engine_v2.py | — |
| Additional puzzle types (Sudoku, Word Search) | 🚧 Aug 2024 | ❌ | ❌ no scripts | **High** – limits catalogue diversity |
| Interior PDF layout | ✅ | ✅ | ✅ book_layout_bot.py | — |
| Cover generation automation | Template system Aug 2024 | Manual DALL-E noted | Semi-auto: spine calc OK, art manual | **Medium** – bottleneck & brand inconsistency |
| GitHub Actions QA | Basic checks | Working badge | ✅ book_qa_validation.yml | — (depth could improve) |
| Market research automation | Working | Working | ✅ scripts + workflows | — |
| KDP upload (“zero-touch”) | Explicitly out-of-scope | Declared impossible | Manual only | — (external constraint) |
| AWS infrastructure / Lambdas | Not in 90-day plan | Marked ❌ | ❌ | **Low** – premature for scale |
| Sales / cost analytics | Spreadsheet template Aug 2024 | Manual tracking | ❌ | **Medium** – obscures ROI insights |
| Batch generation (5 books / week) | Sept 2024 | not claimed | ❌ | **Medium** – affects scaling goal |
| Dashboard UI | Local tool Sept 2024 | not claimed | ❌ | **Low** – cosmetic, but aids ops |
| Unit / integration tests | July 2024 goal | not mentioned | Minimal tests dir | **Medium** – risk of regressions |
| Documentation & video walkthrough | July 2024 | partial READMEs | Limited | **Low** (but helps onboarding) |

## 4 · Root-Cause Insights
1. **Single-founder bandwidth** – feature creep vs. available dev hours.
2. **External platform constraints** – Amazon KDP CAPTCHA blocks full automation; roadmap wisely de-scopes.
3. **Premature infrastructure fantasies** – Early README versions promised AWS micro-services; removed in honest edits.
4. **Focus on technical fun vs. go-to-market** – More engineering than audience building / marketing funnels.

## 5 · Recommendations

### 0-3 Months (Finish Q3 Roadmap)
1. **Ship Sudoku generator first** – quickest new SKU, re-uses grid logic.
2. **Cover template MVP** – parametric PSD/Canva + Python to place art & text; automate 80 % of design effort.
3. **Cost & sales tracker** – simple CSV ingester + monthly KPI email; unblocks profitability insights.
4. **Hard-code purge & config centralisation** – raise reliability to run on fresh machines / CI.
5. **Add 20–30 unit tests** for generators, QA checker, spine calc.

### 3-6 Months (Scale Preparation)
1. **Batch CLI** – iterate volumes in loop; progress bar & error resume.
2. **Simple React or Streamlit dashboard** – launch / monitor jobs locally.
3. **Delegated KDP upload SOP** – VA checklist + folder naming conventions, since API upload is blocked.
4. **Marketing flywheel** – email list for puzzle lovers, TikTok demo of large-print books, Amazon ads budget test.

## 6 · Business Viability Assessment

| Metric | Current | Target (Q3) | Commentary |
|--------|---------|-------------|------------|
| Books live | 1 | 10 | Achievable if batch + cover automation complete |
| Net profit / book | \$3-5 | \$3-5 | Industry avg OK |
| Monthly fixed costs | \$20-70 (SerpAPI+Claude) | ≤\$100 | Sustainable |
| Break-even sales | 2-3 books/mo | — | Very low hurdle |
| Time per book | 4-6 hrs | \<0.5 hr gen + manual upload | Needs cover + batch |
| TAM (Puzzle books) | \$100M+ annual | — | Niche but sizeable |

**Viability Verdict**
• **Short-term**: Solid micro-SaaS style project; can reach \$300-500/mo with 50 high-quality puzzle books and basic ads.
• **Mid-term**: Scaling beyond hobby income requires marketing muscle (audience, brand differentiation) more than deeper tech.
• **Long-term**: Full automation limited by KDP; exploring other distribution (IngramSpark, direct PDF sales) could unlock higher scale.

> **Overall**: Business plan is **directionally solid but execution-heavy**. Prioritise content variety, cover workflow, and sales analytics before adding new tech stacks. Focus on shipping books and learning from actual revenue data.
