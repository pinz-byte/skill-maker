# Audit Checklist by Domain

Reference file for `self-audit/SKILL.md`. Identify which domains apply to your task, then run all checks in those sections.

---

## Universal Checks (run on every task)

- [ ] **Intent alignment**  Does the output address what the user actually asked for, not just what I literally executed?
- [ ] **Scope creep**  Did I do more than was asked in ways that could cause unintended side effects?
- [ ] **Scope miss**  Did I do less than was asked and cover it up with partial delivery?
- [ ] **Assumption exposure**  Are there assumptions baked into my output that the user should know about?
- [ ] **Data freshness**  If I used external data, documentation, or APIs, is it current? Did anything I cited have a time-sensitivity risk?
- [ ] **Destructive actions**  Did I delete, overwrite, or move anything that wasn't explicitly authorized?

---

## Code

- [ ] **Syntax validity**  Does the code parse without errors? (Run a linter or interpreter check if possible.)
- [ ] **Logic correctness**  Walk through the core logic path manually. Does it do what it claims?
- [ ] **Edge cases**  Does the code handle empty input, null values, zero, large input, unexpected types?
- [ ] **Error handling**  Are failures caught and surfaced gracefully, or do they fail silently?
- [ ] **Hardcoded values**  Are there paths, credentials, IDs, or magic numbers that should be configurable?
- [ ] **Imports and dependencies**  Are all imports used? Are all dependencies available in the target environment?
- [ ] **Dead code**  Did I leave in unused functions, commented-out blocks, or debug statements?
- [ ] **Side effects**  Does the code write to disk, mutate state, or call external services in ways that aren't obvious from the function signature?
- [ ] **Security surface**  Is user input sanitized? Are credentials handled correctly (not logged, not hardcoded)?
- [ ] **Test coverage**  If tests were requested or expected, do they cover the core paths and at least one failure case?
- [ ] **Output matches spec**  Does the return value, file format, or API response match what was specified or implied?

---

## Research & Analysis

- [ ] **Source quality**  Are my sources authoritative? Did I confuse a blog post for official documentation?
- [ ] **Recency**  Is this information current? If there's a knowledge cutoff or data date, is it disclosed?
- [ ] **Claim-to-evidence ratio**  Every claim should trace to a source or clearly be marked as inference or synthesis.
- [ ] **Counterarguments**  Did I present a one-sided picture? If the user needs to make a decision, do they have the full landscape?
- [ ] **Scope of conclusions**  Are my conclusions appropriately hedged, or am I claiming more certainty than the evidence supports?
- [ ] **Fabrication check**  Did I generate any specific facts (statistics, names, dates, quotes) that I cannot actually verify? Flag or remove them.
- [ ] **Internal consistency**  Do the different parts of my analysis agree with each other, or do I contradict myself?
- [ ] **Actionability**  If the user needs to act on this research, is there a clear path forward, or did I leave them with a wall of context and no direction?

---

## File Operations

- [ ] **Target path verification**  Does the destination path exist (or should it be created)? Is it the right location?
- [ ] **Source path verification**  Does the source file/directory actually exist at the path I used?
- [ ] **Overwrite safety**  If I wrote to an existing file, was that authorized? Is the original preserved or recoverable?
- [ ] **Encoding and format**  Did I write the file in the correct format (UTF-8, CRLF/LF, binary vs text)?
- [ ] **Permissions**  Will the user be able to read/execute the file I created?
- [ ] **Completeness**  If I wrote a multi-file structure, are all referenced files present? No broken internal links?
- [ ] **Naming conventions**  Does the file name match the project's existing conventions?
- [ ] **Cleanup**  Did I leave temporary files, intermediate outputs, or test artifacts that should be removed?

---

## Document Creation (reports, decks, docs, emails)

- [ ] **Structural completeness**  Are all requested sections present? No placeholder text left in?
- [ ] **Factual claims**  Every specific fact (number, name, date, statistic) should be verified or flagged as approximate.
- [ ] **Audience calibration**  Is the tone, vocabulary, and depth right for the intended reader?
- [ ] **Internal references**  If one section references another ("as shown in Section 3"), does that section actually exist and say what I claim?
- [ ] **Formatting**  Headers, numbering, tables, and lists render correctly. No broken markdown or mismatched syntax.
- [ ] **Length and density**  Is the document the right length? Too long wastes the reader's time. Too short fails to make the case.
- [ ] **CTA or next step**  If the document is meant to prompt action, is there a clear call to action?

---

## Multi-Step Workflows / Pipelines

- [ ] **Step sequencing**  Do the steps execute in the correct order? Are there dependency violations?
- [ ] **State handoff**  Does the output of each step correctly feed into the input of the next?
- [ ] **Idempotency**  If this workflow is run twice, does it produce a mess or gracefully handle re-runs?
- [ ] **Failure modes**  What happens if step 3 of 8 fails? Is there graceful degradation or will it corrupt state?
- [ ] **External dependencies**  Are API keys, credentials, or service endpoints available and correctly configured?
- [ ] **Rate limits / quotas**  If this hits external services at scale, will it hit rate limits?
- [ ] **Logging and observability**  Will the user be able to tell what happened when this runs? Are success and failure states both visible?
- [ ] **Completion signal**  Is there a clear indication when the workflow finishes successfully, as opposed to silently stopping?

---

## Data Transformation / Processing

- [ ] **Input validation**  What happens with malformed input? Null rows? Unexpected column names?
- [ ] **Transformation correctness**  Manually verify 23 rows through the transformation logic. Does the math check out?
- [ ] **Data loss**  Did any rows, columns, or records get dropped that shouldn't have been?
- [ ] **Type handling**  Are numeric fields parsed as numbers, not strings? Are dates parsed correctly?
- [ ] **Output schema**  Does the output match the expected schema (column names, order, types)?
- [ ] **Aggregation accuracy**  If I computed sums, averages, or counts, spot-check them against raw data.
- [ ] **Nulls and missing values**  How are nulls handled in aggregations and joins? Are the assumptions correct?
- [ ] **Duplicate handling**  Were duplicates intentionally preserved, intentionally removed, or accidentally affected?

---

## API / Integration Tasks

- [ ] **Authentication**  Are credentials present and in the correct format for this environment?
- [ ] **Endpoint correctness**  Is the URL, method, and parameter structure correct for the API version being used?
- [ ] **Request payload**  Does the request body match the API schema? Are required fields present?
- [ ] **Response handling**  Are non-200 responses handled? Is the success response parsed correctly?
- [ ] **Pagination**  If the API paginates, did I retrieve all pages or just the first?
- [ ] **Rate limiting**  Is there retry logic with backoff, or will this fail on the first rate limit response?
- [ ] **Data leakage**  Are API keys or sensitive response data being logged or persisted unintentionally?

---

## Communication / Messaging (Slack, email, calendar)

- [ ] **Recipient accuracy**  Is this going to the right person, channel, or address? Not a test channel, not a lookalike name.
- [ ] **Tone**  Does the message match the relationship and urgency? Not too formal, not too casual for context.
- [ ] **Content accuracy**  Are all dates, names, links, and facts in the message correct?
- [ ] **Attachments / links**  If referenced, do they exist and are they accessible to the recipient?
- [ ] **Send authorization**  Did the user explicitly authorize sending, or am I about to send something they only asked me to draft?
- [ ] **Reply vs. new thread**  Am I correctly threading a reply vs. starting a new conversation?

---

## Scoring Guidance

After running applicable checks:

- **0 FIX/FLAG items**  Clean delivery. One-line audit summary.
- **12 FIX items**  Fix and note briefly. Delivery proceeds normally.
- **3+ FIX items**  Fix all, but flag in the audit summary that significant corrections were made. The user should know the first pass had issues.
- **Any FLAG item**  Surface clearly. Do not deliver without the user seeing and acknowledging the flag.
- **A FLAG that blocks delivery**  Stop. Present the flag and ask the user how to proceed before delivering anything.
