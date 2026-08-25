---
name: dependency-audit
description: >-
  Pre-build viability gate that audits external dependencies before code ships. Triggers when
  reviewing or writing builder prompts, technical specs, implementation plans, or any document
  that specifies HOW something will be built. Fire on "builder prompt", "build this",
  "implement this", "ship this to builder", "technical spec", "implementation plan", or when
  you see a builder prompt being drafted. Also trigger on "audit dependencies", "check
  viability", "cost analysis", "what breaks if X goes down", "dependency check", "is this
  sustainable", or any discussion about whether a technical choice scales economically.
  Trigger proactively when you detect an external API, paid service, or rate-limited resource
  being specified for a bulk/recurring operation in any builder context. This skill exists
  because the wrong moment to discover a cost-scaling problem is after the code ships and the
  credits run out. NOT auditor-general (reviews a build after it lands): this prices external
  dependencies BEFORE any code ships.
metadata:
  intent: audit
---

# Dependency Audit — Pre-Build Viability Gate

## Why This Exists

Technical decisions about implementation — which API to call, which service to use, whether to run something locally or remotely — are made at the builder prompt layer, not at the architectural intention layer. The IB defines WHAT to build and WHY. The builder prompt defines HOW. Bad HOW decisions create systems that work in prototype and collapse at scale.

This skill catches those decisions before code ships.

## When to Trigger

The gate activates at the transition between intention and implementation — specifically when:

1. A builder prompt is being written or reviewed
2. A technical spec specifies an external dependency for a core operation
3. An implementation plan routes bulk/recurring operations through paid APIs
4. Someone says "use [service X] for [operation Y]" in a build context

The key signal: **any time a paid, rate-limited, or externally-hosted service is specified for an operation that runs per-record, per-ingest, or on a recurring schedule.**

One-time operations (initial setup, migration) are lower risk. Per-record operations are where cost scaling kills viability.

## The Audit

For every external dependency identified in the builder prompt or technical spec, answer these five questions:

### 1. FREQUENCY — How often does this operation run?

- **Once** (setup, migration) → low risk
- **Per batch** (daily job, weekly reindex) → medium risk
- **Per record** (every vector, every ingest, every query) → high risk

Per-record dependencies are the critical ones. They're what turn a $5/month prototype into a $500/month single-user system.

### 2. ALTERNATIVE — Is there a local/deterministic/free way to achieve the same outcome?

For each dependency, evaluate alternatives in this order:

| Operation Type | LLM Alternative | Local Alternative | Rule-Based Alternative |
|---|---|---|---|
| Entity extraction (NER) | Claude Haiku | spaCy, local Llama | Regex + dictionary |
| Text classification | Claude Haiku | local classifier, embeddings clustering | Keyword rules |
| Summarization | Claude Sonnet | local Llama/Mistral | Extractive (TextRank) |
| Embedding generation | OpenAI API | sentence-transformers (local) | TF-IDF (if quality allows) |
| Re-ranking | Claude Haiku | cross-encoder (local) | BM25 + heuristics |
| Evolution descriptions | Claude Haiku | template + diff | Omit (structural edge is sufficient) |
| Salience scoring | Claude Haiku | Graph algorithms (PageRank, betweenness) | Degree count + rules |
| Metadata tagging | Claude Haiku | Zero-shot classifier (local) | Source-based rules |

The question is never "is the LLM better?" — it almost always is. The question is: **does the quality delta justify the cost delta at N users × M records × daily frequency?**

### 3. FAILURE MODE — What happens when this dependency is unavailable?

- Credits exhausted → system stops enriching (PARALLAX Task B scenario)
- API rate limited → pipeline backs up
- Service deprecated → rewrite required
- Price increase → unit economics shift

If the answer is "core functionality degrades or stops," the dependency is structural, not optional. Structural dependencies on external paid services are architectural risks.

### 4. COST PROJECTION — What does this cost at scale?

Calculate: `cost_per_call × calls_per_record × records_per_user × users × frequency`

Example from PARALLAX:
- Entity extraction via Haiku: ~$0.001 per call
- 11,200 vectors × 1 call each = $11.20 for initial build
- But: every new voice memo triggers extraction = ongoing cost
- At 100 users × 10 memos/week × 52 weeks = 52,000 calls/year = $52/year just for extraction
- Add temporal linking, salience recalc, metadata backfill → multiply by 4-5x

This isn't catastrophic, but it's also not zero — and it compounds with every enrichment layer added.

### 5. VERDICT — Keep, Replace, or Defer?

- **KEEP** — The LLM adds irreplaceable value and the cost is justified (e.g., Symbios sessions, complex cross-domain synthesis)
- **REPLACE** — A local/deterministic alternative achieves 80%+ of the quality at 0% of the marginal cost (e.g., NER via spaCy, salience via PageRank)
- **DEFER** — The operation is nice-to-have, not core. Skip it in the build, add it as optional enrichment later (e.g., evolution descriptions on EVOLVED_INTO edges)

## Output Format

When the audit runs, produce a dependency table:

```
DEPENDENCY AUDIT — [Project Name]
Date: [date]

| Operation | Current Impl | Frequency | Alternative | Cost @ 1K users | Verdict |
|-----------|-------------|-----------|-------------|-----------------|---------|
| [op]      | [service]   | [freq]    | [alt]       | [$/month]       | [K/R/D] |

STRUCTURAL RISKS:
- [List any operation where Verdict = Keep but Frequency = per-record]

RECOMMENDED CHANGES:
- [Specific replacement instructions for each Replace verdict]

DEFERRED ITEMS:
- [Items marked Defer with explanation of when they become worth adding]
```

## Integration with Builder Prompts

When this skill triggers during builder prompt creation or review:

1. Scan the prompt for external service references (API calls, paid services, cloud endpoints)
2. For each, run the 5-question audit
3. Present the dependency table before the builder prompt ships
4. If any per-record operation has Verdict = Replace, modify the builder prompt to specify the local alternative
5. If any structural risk exists with Verdict = Keep, flag it explicitly in the builder prompt so the builder knows the tradeoff

The builder prompt should never specify an external paid service for a bulk operation without the audit having confirmed it's the right choice.

## Philosophy

The base and middle of any system pyramid should run without external paid dependencies. Free and infinite. The intelligence layer — the apex — is where LLM spend belongs, because that's where the quality delta is irreplaceable and the frequency is low (sessions, not per-record operations).

Graph operations are free. Vector operations are nearly free (after initial embedding). LLM calls are not free. Route accordingly.
