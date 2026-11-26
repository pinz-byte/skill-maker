# Interaction decisions

Read only the relevant pattern. Adapt to the product and the supplied evidence.
These are working design judgments, not a mandatory inventory for every screen.

## Forms and consequential transactions

Ask for information needed at this stage; explain unusual or sensitive requests.
Use persistent labels, appropriate input types, autocomplete, and clear required
status. Instructions appear before a predictable mistake; actionable validation
appears at the relevant field without erasing valid work. Avoid announcing an
error while someone is still entering an incomplete but normal value.

For submission, keep status understandable and prevent unintended duplicates.
On failure, retain entered values and provide a retry or correction path. A
timeout after a transaction may mean an unknown result: reconcile status before
offering another potentially duplicate transaction. Show the actual total and
consequences before commitment. A confirmation needs a useful receipt or next
step rather than an unexplained success toast.

Example: a booking flow should retain dates and guest details after an invalid
phone number. A payment timeout needs a pending/status check path; clearing the
form or declaring payment failed without evidence would increase uncertainty.

## Search, collections, comparison, and expert work

Choose table, list, or cards according to the attributes people compare, their
volume, and the actions they repeat. Keep comparable values aligned and units
clear. A dense interface can serve experts when hierarchy remains legible.
Expose the active query, filters, sort, result count where useful, and a reset
path. Preserve list context when opening and returning from details.

Separate first-use emptiness, zero search results, and loading failure; each has
a different next action. Specify selection scope for bulk actions, particularly
across pagination. Keep destructive action scope visible. Do not hide essential
columns on mobile without an accessible detail or comparison alternative.

Example: an inventory table needs price, stock, and selected-item actions close
to the comparison task. Oversized image cards may make repeated price checks
slower; that hypothesis should be checked with representative work.

## Navigation, disclosure, and overlays

Use labels that predict destination or outcome. Show location and keep back
behavior understandable. Distinguish tabs that switch adjacent views from
navigation to another area. Deep-link and preserve view state when the workflow
depends on returning or sharing.

Use disclosure for secondary detail without hiding decision-critical content.
A modal suits a bounded interruption; a complex sustained task may deserve a
page. For a modal, specify initial focus, keyboard containment, close behavior,
and focus return using the appropriate APG pattern. Do not require hover for
essential information. Avoid stacks of nested overlays.

## Onboarding, engagement, and feedback

Let people experience useful value promptly. Explain an unfamiliar interaction
at the point of use; do not make a tour substitute for understandable controls.
Show progress only when it represents real state. Offer skip, resume, or dismiss
when appropriate. Do not optimize time spent when the desired outcome is a fast
completed task.

Distinguish status from instruction: a background save indicator, field error,
blocking failure, and completed task need different prominence and persistence.
Use motion to clarify change or spatial continuity; preserve the final meaning
without animation. Feedback must remain available to assistive technologies
without repeatedly interrupting people.

## Choosing a validation method

Use a task walkthrough to identify likely friction; label it expert judgment.
Use tree testing or card sorting when findability or grouping is uncertain.
Use moderated or unmoderated task testing to observe actual interaction.
Use analytics to locate abandonment, then investigate its cause rather than
inventing motivation from a funnel. An A/B test needs an appropriate hypothesis,
sample, analysis plan, and guardrail metrics; do not promise significance from
a fixed small usability sample.

Worked measurement example: for an application form, goal = complete an eligible
submission with confidence; signals = completion, repeated errors, help requests;
metrics = completion rate with a defined denominator, errors per submission,
and reported ease. Specify the population and time window. Do not fabricate
a baseline, target uplift, or completed study.
