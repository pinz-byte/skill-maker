# Source mapping and worked examples

## Provenance

Source: *Terence Tao Teaches Mathematical Thinking*, MasterClass, English
class guide, PDF metadata dated January 20, 2022. Supplied filename:
`TT_classguide_en-US.pdf`.

Printed page numbers below are one less than the PDF viewer's page index:

| Printed pages | Source theme | Adaptation in this skill |
| --- | --- | --- |
| 25-27 | Problem selection, abstraction, analogies, motivation, questioning methods, patience and incremental progress | Define success; retain essentials; learn from related problems; accept partial progress |
| 31-32 | Start an attempt, simplify, reuse familiar tools, change approach and collaborate | Smaller cases, explicit obstruction and a different next move |
| 33-34 | Group testing: reason about possible scenarios | Choose informative tests over equal-size groups of people |
| 35-38 | Twelve coins, matrices and compressed sensing | Choose a representation that extracts more information from measurements |
| 40-42 | Scheduling, bus arrivals and wheel circumference | Respect constraints, model sampling and separate exact from approximate |
| 45 | Collaboration, getting stuck, letting go and shared progress | Complementary perspectives and a useful stopping condition |

This is an original operational adaptation, not a reproduction of the guide.
Explicit success criteria, assumption labels, verification checks, probability
and test-cost qualifications, authorization boundaries and the response format
are editorial implementation choices. Do not attribute them as quotations or
as a formal algorithm created by Tao. The guide's exercises are teaching models;
they do not establish performance guarantees in real clinical settings.

## Example: partition hypotheses rather than objects

Suppose exactly two of 100 people have a property. An ideal, noiseless pooled
test is positive if at least one person in the pool has it. There are
`C(100, 2) = 4,950` possible pairs. Assume each pair is equally likely.

Testing 50 people leaves `C(50, 2) = 1,225` possible pairs after a negative
result and `4,950 - 1,225 = 3,725` after a positive result. The groups of people
are equal, but the possible outcomes are poorly balanced.

Testing 29 people leaves `C(71, 2) = 2,485` pairs after a negative result and
`4,950 - 2,485 = 2,465` after a positive result. This first test divides the
hypotheses nearly evenly. Later tests must be designed against the hypotheses
still possible; repeatedly testing groups of 29 is not the solution.

Transfer: for debugging or diagnosis, list competing explanations and choose
a check that separates them. With unequal probabilities, noisy tests, different
costs or different consequences, balance alone is not sufficient.

## Example: equal frequencies do not imply equal selection probabilities

Two bus routes each run every 15 minutes. Route E arrives at minutes
0, 15, 30 and 45; route W at 4, 19, 34 and 49. A person arrives uniformly
at random over time and boards the next bus.

In every 15-minute cycle, W is next for 4 minutes and E for 11. Thus
`P(W) = 4/15 = 26.666...%`. Equal service frequency does not imply equal
probability of catching a route; the time windows determine the answer.

The guide calls this roughly 25%, consistent with an approximate story, but
not exactly one quarter. An offset of 3.75 minutes would give exactly 25%.
This calculation also depends on uniform arrival times and punctual service.

## Example: eliminate an unknown before estimating

Two circular tires differ in circumference by 12 millimeters. If their outer
radii are `R` and `R + D`, then:

`2*pi*(R + D) - 2*pi*R = 12`, so `D = 6/pi mm`, approximately `1.91 mm`.

The unknown original radius cancels, so measuring it adds no information
needed for this question. The exact answer is `6/pi`, not the rounded `1.91`.
Check by substitution: increasing radius by `6/pi` increases circumference
by exactly 12. This assumes circular geometry, not tire deformation under load.
