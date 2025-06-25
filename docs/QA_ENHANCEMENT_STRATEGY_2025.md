# QA ENHANCEMENT STRATEGY 2025  
_AI KindleMint Engine_

---

## 1. Executive Summary  
The current single-model workflow (Claude Code → PDF/EPUB) produces books with >40 critical defects per volume (duplicate clues, page-cut text, mis-aligned grids). Rejections and negative reviews threaten brand credibility and stall revenue. A 2025-grade QA program is required to:

* Drive reject rate < 2 %  
* Lift average review rating > 4.4 stars  
* Enable scale to 5 books / week without line-by-line human edits

---

## 2. Research-Backed Solutions  
| Pillar | Key Findings (2025 papers & industry benchmarks) | Improvement vs single-model |
|--------|--------------------------------------------------|-----------------------------|
| **Multi-LLM Ensemble** (“LLM-as-a-Judge”, Weaver 2025, Patronus AI) | 70-85 % error reduction through majority-vote & weighted verifier ensembles | ★★★ |
| **Claude Artifacts QA Workspace** (Anthropic 3.5) | Real-time side-by-side editing, traceability, team collaboration | ★★☆ |
| **Specialized QA Models** (AGENT-X 0-shot text detector, domain small-models) | 40-55 % defect catch at 1/3 cost of large models | ★★☆ |

---

## 3. Implementation Options  

| Option | Architecture | Quality Gain | Monthly Cost* | When to Choose |
|--------|--------------|--------------|---------------|----------------|
| **A. Full Ensemble** | Claude 3.5 Sonnet + GPT-4o + Gemini 1.5 Pro generation; validation by 4-model judge (Opus, GPT-4o, Gemini Flash, Llama-3 70B) with 80 % consensus | 70-85 % | **$1 250** | Zero rejections / premium brand |
| **B. Hybrid Artifacts** | Current Claude generation; Claude Artifacts workspace; QA judged by GPT-4o + small Glider verifier | 50-65 % | **$480** | Balanced quality / cost |
| **C. Specialist QA** | Claude generation; single 13B QA model (AGENT-X fork) + regex rule set | 40-55 % | **$220** | Budget runs / early drafts |

\*Assumes 20 books / mo, 10-page sample slices for ensemble validation.

---

## 4. Detailed Technical Architecture (Option A reference)

```
┌──────────────┐
│ Claude 3.5   │──┐
└──────────────┘  │
┌──────────────┐  │  candidate PDFs/EPUBs
│ GPT-4o        │──┼──► Artifact Store (S3/LFS)
└──────────────┘  │
┌──────────────┐  │
│ Gemini 1.5   │──┘
└──────────────┘

             ▼
      ╔════════════╗
      ║  VERIFIER   ║  (Weaver-style)
      ╠════════════╣
      ║ Claude Opus║ weight 0.35
      ║ GPT-4o judge weight 0.25
      ║ Gemini Pro weight 0.25
      ║ Llama 3 70B RM weight 0.15
      ╚════════════╝
             ▼
  Consensus ≥80 %? ──► PASS
             │
             └──► FAIL → Regenerate or send to Claude Artifacts for human-in-the-loop fixes.

Monitoring & logs pushed to Slack BI dashboard + Sentry events.
```

---

## 5. Implementation Timeline

| Phase | Duration | Milestones |
|-------|----------|------------|
| **P0 – Foundation (Week 1)** | 1 wk | • Add QA data schema to `book_results` • Enable Sentry breadcrumbs for QA events |
| **P1 – Specialist QA (Month 1)** | 3 wks | • Integrate AGENT-X small model • Achieve 40 % defect catch • Slack QA block live |
| **P2 – Artifacts Workspace (Month 2-3)** | 6 wks | • Deploy Claude Artifacts project • Inline edit → re-validate loop • Duplicate-content detector |
| **P3 – Ensemble & Consensus (Month 4-5)** | 8 wks | • Wire GPT-4o/Gemini APIs • Implement weighted verifier (Weaver) • Reach 80 % consensus pass |
| **P4 – Autopilot Scale (Month 6)** | 4 wks | • Auto-regeneration on fail • Automatic KDP-ready flag • SLA: <2 % reject rate |

---

## 6. API Key Strategy

| Purpose | Model | Provider | Key Scope |
|---------|-------|----------|-----------|
| **Generation** | Claude 3.5 Sonnet | Anthropic | `CLAUDE_GEN_KEY` |
| Backup Gen | GPT-4o | OpenAI | `OPENAI_GEN_KEY` |
| **Validation** | GPT-4o Judge | OpenAI | `OPENAI_JUDGE_KEY` (rate-limited) |
|  | Claude Opus Judge | Anthropic | `CLAUDE_JUDGE_KEY` |
|  | Gemini 1.5 Pro | Google | `GEMINI_VALIDATION_KEY` |
| Specialized QA | AGENT-X (13B) | Bedrock SLM | `BEDROCK_QA_KEY` |

Keys isolated per role -> blast-radius limited, easier cost attribution.

---

## 7. Cost & ROI Projection (Option B baseline)

| Metric | Current | After QA Upgrade | Delta |
|--------|---------|------------------|-------|
| Defects / book | 40 | 12 | -70 % |
| KDP rejections | 3 / mo | 0.4 / mo | -87 % |
| Manual fix hrs | 6 hrs | 1.5 hrs | -75 % |
| QA API cost | $45/mo | $180/mo | +$135 |
| **Net Profit** | $540 → $840 | **+55 % ROI** (3 mo payback) |

---

## 8. Standard QA Criteria (minimum pass scores)

| Dimension | Threshold |
|-----------|-----------|
| Duplicate text/clues | <10 % |
| Font embedding | 100 % embedded |
| Page trim safety | 0 text cut-off flags |
| Puzzle-grid integrity | 100 % clue-answer match |
| White-space ratio | <92 % for >95 % pages |
| Kindle EPUB validation | EPUB 3 valid, TOC OK |
| QA Score | ≥85/100 |

---

## 9. Testing & Validation Approach

1. **Unit Tests** – Parse PDF, check puzzle counts, font subsets  
2. **Synthetic Golden Set** – 10 gold-standard interiors compared by hash  
3. **LLM-as-Judge Regression** – Weekly eval dataset (100 pages) scored; alert if <90 % agreement  
4. **Sandbox Publish Test** – Upload to KDP previewer (CLI) and scrape validation warnings  
5. **Human Spot-Check** – 1 in 5 books manual skim until reject rate < 2 %

---

## 10. Success Metrics & Monitoring

| KPI | Target | Source |
|-----|--------|--------|
| KDP Reject Rate | **<2 %** | KDP status scraper |
| Avg QA Score | **≥85** | Verifier ensemble |
| Duplicate Content | **<10 %** | AGENT-X semantic diff |
| Time/Book | **<5 min** | Batch logs |
| Profit/Book | **>$3** | Cost tracker |
| Customer Rating | **≥4.4** | Amazon reviews API |
| SLA Alerts | <2 critical / month | Sentry |

Weekly Slack digest + Grafana dashboard tracks all KPIs.

---

### 🌟 **Recommended Path**

Start with **Option B** (Hybrid Artifacts) for fastest ROI, then graduate to **Option A** once profit funds increased model spend. This roadmap delivers **executive-level quality assurance** while preserving scalability and profit growth.  
