---
name: data-analyst
description: Audit-only data analyst that looks at any project's actual data (schemas, sample docs, business context) and proposes what to measure, grounded in what's already instrumented + what's missing. Project-agnostic  works on Firestore, SQL, JSON dumps, or any structured data store. Use whenever the user says "analyze my data", "what should I measure", "what KPIs for X", "find insights in [project]", "metrics for [thing]", "load-bearing questions", "data audit", "what's worth tracking", "audit the data model", "find signal in [dataset]", "what could I derive from this data", "is my schema giving me enough signal", "design metrics for", "data discovery", "what's the north star metric", "AARRR for [project]", "funnel analysis", "what should this dashboard measure", "I have a database/collection, now what". Does NOT generate code or instrumentation prompts  outputs a single METRICS_PROPOSAL document. Pairs with dashboard-section skill (data-analyst decides QU medir; dashboard-section orchestrates CMO mostrarlo).
metadata:
  intent: audit
---

# Data Analyst (Audit-Only)

A skill for opinionated data discovery + metric proposals on any project. Reads schemas + samples + business context, returns a structured proposal of what's worth measuring.

## When this skill fires

- "Analyze my data", "what should I measure", "what KPIs"
- "Data audit", "audit the data model", "is my schema giving enough signal"
- "Find insights in [project]", "find signal in [dataset]"
- "Metrics for [feature/product]", "design metrics for"
- "Load-bearing questions for [business]"
- "North star metric", "AARRR for X", "HEART metrics"
- "What's worth tracking", "what could I derive from this data"
- "I have a database, now what"
- Casual: "look at this and tell me what matters", "is this dataset useful"

Fire even on adjacent phrasings. Pairs with `dashboard-section` (this skill says WHAT to measure; dashboard-section orchestrates HOW to display it).

## When this skill does NOT fire

- "Implement metric X"  no, that's dashboard-section / builder territory
- "Run SQL query Y"  no, that's ad-hoc data work, not analytical methodology
- "Compare metric A vs B over time"  that's metrics-review, not metric design
- "What's our current revenue"  simple read, not analytical methodology
- Statistical work (regressions, correlations, hypothesis testing)  out of scope

## What this skill produces

**ONE artifact:** `METRICS_PROPOSAL_{PROJECT}_{YYYY-MM-DD}.md`

Containing:
1. Project context summary (what the business is, observed from docs/data)
2. Load-bearing questions (5-7 questions the business should answer)
3. Metric proposals (2-4 candidate metrics per question)
4. Gap analysis (what's not tracked that should be)
5. Recommended next moves (priority order)

**Does NOT produce:** builder prompts, code, instrumentation specs, dashboard layouts. Those belong to dashboard-section or builder agents downstream.

## The 5-phase lifecycle

### Phase 1  Discovery

**Goal:** Build a grounded mental model of the project from primary sources before proposing anything.

**Reads in this order:**

1. **Project root docs:** `CLAUDE.md`, `README.md`, `IB_*.md`, any docs in `docs/` or root
2. **Schema definitions:**
   - Firestore: `firestore.rules` (collections referenced), sample reads of each collection (top 3-5 docs per collection)
   - SQL: `schema.sql`, migrations, `DESCRIBE TABLE` outputs
   - JSON/MongoDB: sample documents per collection
   - GraphQL: type definitions
3. **Business context (if available):** IB docs, pitch decks, product specs, user journey maps
4. **Existing metrics/dashboards (if any):** what's currently being measured, even if poorly

**Deliverable of Phase 1:** A short internal mental model (2-4 paragraphs). Surface to user only if they ask "what did you learn"; otherwise proceed to Phase 2.

**Key questions to answer in your head during Phase 1:**
- What is this business / project trying to do?
- Who are the actors (users, customers, admins)?
- What's the core value flow (acquisition  activation  retention  revenue  referral, or whatever applies)?
- What data is captured per actor / per action?
- What's the time grain of events (per-action / per-day / per-session)?
- Where are the gaps (data captured but not analyzed, or actions taken but not tracked)?

See `references/discovery-patterns.md` for cross-store-type patterns (how to discover in Firestore vs SQL vs unstructured).

### Phase 2  Question framing

**Goal:** Propose 5-7 load-bearing questions the business should answer, grounded in the discovered model.

**Methodology:** Apply 2-3 analytical lenses simultaneously, pick the ones that fit the business model best. Lenses:

- **AARRR (pirate metrics):** Acquisition, Activation, Retention, Referral, Revenue  best for consumer products, SaaS, marketplaces
- **HEART:** Happiness, Engagement, Adoption, Retention, Task success  best for product UX, internal tools
- **North Star Metric:** One metric that captures value delivered  best for clear single-value products
- **Funnel:** Stage-by-stage conversion  best for transactional / e-commerce / lead-gen
- **Quality dimensions:** Accuracy, completeness, consistency, timeliness  best for data products
- **Marketplace dynamics:** Supply, demand, match rate, GMV, take rate  best for two-sided platforms

See `references/frameworks.md` for full descriptions + when to apply each.

**Output format for Phase 2 questions:**

```
Q1: [The question, phrased as a question]
    Why load-bearing: [one sentence why this matters for the business]
    Lens applied: [AARRR-Activation / HEART-Engagement / etc.]
    Currently tracked: [yes/partial/no]
```

5-7 questions. Per `feedback_macro_means_filter_not_catalogue` (filter not catalog)  don't enumerate every possible question, pick the highest-signal ones.

### Phase 3  Metric mapping

**Goal:** For each load-bearing question, propose 2-4 candidate metrics with concrete data sources.

**Per-metric structure (mandatory fields):**

```
Metric: [Name in TitleCase]
Question: [Which Phase-2 question this addresses]

Definition: [One-sentence operational definition]
Formula: [Exact calculation, with field references]
Data source: [collection_name.field_name / table.column / etc.]
Time grain: [event / day / week / month]
Segmentations: [3-5 dimensions worth slicing by, from actual data  not generic]

Why it matters: [One paragraph on the business decision this metric informs]
Data quality risks:
  - [Risk 1, e.g., "field is optional, may be null in 30% of docs"]
  - [Risk 2, e.g., "two writers populate this field with different formats"]
Currently tracked: [yes / partial / no  if no, see Gap analysis]
```

**Discipline rules:**
- Every field reference must come from actual schema you saw in Phase 1
- Never propose a metric whose data doesn't exist (that goes to Phase 4 Gap analysis)
- Always include data quality risks  schema drift, optional fields, denormalization debt
- Segmentations must be derivable from existing dimensions  don't invent

### Phase 4  Gap analysis

**Goal:** Identify what's NOT tracked today but should be, with proposed schema additions.

**Categories of gaps to look for:**

1. **No actor field on action events**  events fire but you can't tell who did them
2. **No time dimension**  state captured but not "as of when"  no historical analysis
3. **Denormalized but not snapshotted**  joins work today but break if upstream changes
4. **Funnel gaps**  captured upstream + downstream but not the middle stages
5. **No outcome field**  actions captured but not whether they succeeded
6. **Aggregate only, no individual events**  totals but no granularity for cohort analysis
7. **Single-source dependency**  critical metric depends on data that has no backup

See `references/gap-analysis-rubric.md` for the full checklist.

**Per-gap structure:**

```
Gap: [Short name]
What's missing: [Field/event/dimension that doesn't exist]
Question(s) it would unlock: [Reference Q1-Q7 from Phase 2]

Proposed addition:
  Schema change: [Concrete  new field on existing collection / new collection / new event type]
  Writer responsibility: [Which service/code path would populate this]
  Backfill option: [Can old data be recovered or only forward-going]

Priority: [P0 / P1 / P2]
  P0: blocks a P0 question
  P1: enables a P1 question or improves accuracy of P0
  P2: nice-to-have for future analysis
```

### Phase 5  Deliverable

**Goal:** Synthesize Phases 1-4 into ONE structured document.

**File:** `METRICS_PROPOSAL_{PROJECT}_{YYYY-MM-DD}.md` in the user's META workspace (default `/Users/lfp/Dev/AVT_CarMatch_meta/` for Subastop ecosystem; ask if unclear).

**Structure (mandatory sections in this order):**

1. **Header**  project, date, scope
2. **Executive summary**  3-5 bullets capturing the headline findings
3. **Project context**  what the business is, who the actors are, the value flow (1-2 paragraphs)
4. **Load-bearing questions**  Phase 2 output (5-7 questions)
5. **Metric proposals**  Phase 3 output, organized by question
6. **Gap analysis**  Phase 4 output, prioritized
7. **Recommended next moves**  top 3-5 things to do in priority order
8. **Open questions**  what the analyst couldn't determine and needs from the user

See `assets/metrics-proposal-template.md` for the exact template.

**Then:** Present the file to the user. Surface the 3-5 highest-signal findings inline in chat, point to the file for depth. Per `feedback_macro_means_filter_not_catalogue`  don't dump the whole doc into chat.

## Project context auto-detection

When the user invokes the skill, attempt to detect the project context from:

1. **Working directory**  current cwd is the project root
2. **Explicit user mention**  "for AVT", "analyze CarMatch", "audit project X"
3. **Recently modified files**  what has the user been working on
4. **Mounted folders / repos**  which paths are accessible

If the project is in the Subastop ecosystem (AVT, CarMatch, AVT PLUS, etc.), use canonical project knowledge from META workspace. See `references/discovery-patterns.md` for the Subastop-specific shortcuts.

If the project is unknown / external, run pure-discovery Phase 1 from primary sources.

## Anti-patterns to avoid

-  Proposing metrics on data that doesn't exist (that goes to gap analysis, not metric proposal)
-  Generic metrics ("DAU", "MAU") without adapting to the business model  if the product is a one-shot valuation tool, DAU is irrelevant
-  Recommending vanity metrics (total events, total registered users) without tying to value
-  Listing every possible segmentation  pick 3-5 high-signal per metric
-  Inventing field names  verify against schema
-  Producing the deliverable without doing Phase 1 discovery  guessing produces generic outputs
-  Including code, instrumentation prompts, or implementation in the deliverable  that's out of scope
-  Single-framework lock-in (only AARRR for everything)  apply 2-3 lenses

## Composition with other skills

- **Run AFTER:** `anthropic-skills:ib` if the project structure isn't clear (IB establishes purpose; data-analyst grounds it in data)
- **Run BEFORE:** `anthropic-skills:dashboard-section` if building a new BI tab (data-analyst proposes the metrics; dashboard-section orchestrates the build)
- **Layer ON TOP:** `anthropic-skills:critical-thinker` to stress-test the metric proposals before locking them
- **Hand off to:** `anthropic-skills:write-spec` if a single metric needs deep PRD treatment

This skill does NOT replace those  it's the metric-design layer.

## Success criteria

After running this skill on a project:
- User has a clear list of 5-7 questions worth answering, grounded in their actual business
- For each question, 2-4 concrete metrics with data sources
- For gaps, prioritized list of schema additions with effort estimate
- User can hand the metric proposals to a builder (via dashboard-section skill) and build dashboards that actually inform decisions
- Total time: 30-45 minutes from "analyze X" to METRICS_PROPOSAL.md delivered

## Key memory references (Subastop ecosystem)

When running on AVT/CarMatch/AVT PLUS, load these memories:

- `project_avt_training_lake_principle`  every observation persists; metrics should leverage the full history
- `feedback_extractor_key_format_drift`  schema drift between writers; flag in data quality risks
- `feedback_macro_means_filter_not_catalogue`  top 3-5 per category, never exhaustive
- `feedback_dont_ask_pops_implementation_choices`  propose metrics with recommendations, don't menu
- `feedback_audit_measurement_basis`  wrong basis = high-confidence wrong outputs; verify the measurement basis matches the question

These keep the proposals grounded in POPs's established mental model rather than reinventing.

## When to stop

The skill is done when:
- The METRICS_PROPOSAL_*.md is written
- The user has reviewed and either accepted or pointed at specific things to refine
- If refined, re-run Phase 2-5 (not Phase 1  discovery doesn't change)

Do not loop indefinitely. After 2 refinement rounds, propose locking with caveats explicit.
