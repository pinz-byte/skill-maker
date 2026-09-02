---
name: human-reactor
description: >
  Human reactor for text: reviews, rewrites, or generates prose so it reads as
  written by a specific person, not assembled by a model. Kills three layers of AI
  tells -- lexical (dashes as clause glue, "not X but Y" / "no es X, es Y" false
  contrasts, framers like "cabe destacar", stock vocabulary), structural (uniform
  sentence length, rule-of-three everywhere, synthesis closers, framing openers,
  bolded list lead-ins) and voice (no concrete detail, no stake, flat register).
  Anchors on a pasted sample, the project's Voice Lock, or LFP's default register.
  Ships a scanner that measures before/after. Use on "humaniza", "reactor
  humano", "human reactor", "suena a IA", "suena a robot", "quita lo de IA", "de-AI
  this", "make this sound human", "reads like ChatGPT", "mata los dashes", "quita
  los contrastes", "pasa esto por el reactor", or any request to write text a
  person will sign (email, post, memo, reply, bio). NOT patel-tone-converter
  (persuasive rewrite) or inpositive-language (affirmative framing): run first.
metadata:
  intent: write
---

# Human Reactor

Text that a model wrote carries a signature. Most people only strip the obvious part
(the dashes, the "not X but Y") and ship something that still reads as machine output,
because the signature lives mostly in structure and in the absence of a person behind
the words. This skill treats the problem as three layers and works all three, then
measures the result instead of trusting the feeling that it "sounds better now".

Three modes:

- **REVIEW** (default when the user pastes text): scan, report the tells, rewrite,
  re-scan, deliver text plus a before/after tell count.
- **GENERATE** (user gives a brief, no draft): write with the tells never entering,
  then run the same scan on your own output before delivering.
- **SCAN** (user asks "does this sound like AI?" or "revisa"): report only, with the
  exact sentences flagged. No rewrite unless asked.

## Step 0 -- Resolve the voice anchor (never skip)

"Human" is undefined until you know which human. Resolve in this order; the anchor
you used is stated as the first line of the Reactor report, nowhere else:

1. **Sample in the request.** The user pasted 2+ paragraphs of their own writing, or
   named a file with it. Extract: average sentence length and its spread, how they
   open a paragraph, whether they use fragments, which connectors they actually use,
   ES/EN mix, level of formality, favorite verbs, how they close (usually they just
   stop). Mirror those, do not caricature them.
2. **Project voice reference.** A Voice Lock section, style guide, CLAUDE.md voice
   rules, or an approved prior piece in the same project. Read it verbatim.
3. **LFP default register** (when the author is LFP and 1 and 2 are absent): direct,
   dense, short imperatives, positions instead of menus, precise naming of things,
   Spanish and English coexisting inside the same paragraph when the concept is
   better in one of them, no filler, no motivational language, no closing
   encouragement. Cuts before it decorates.
4. **Nothing available and the author is not LFP:** ask for a sample in one line.
   Do not rewrite into a generic "friendly human" register; that is just a second
   template.

Facts that arrive with the request (product name, city, a figure, a date) are user
material even when the draft never mentions them. In REVIEW mode you are authorized
to inject them; the report lists which ones you injected. They are not the anchor;
the anchor is the voice, the facts are layer 3 material.

## Step 1 -- Scan: the three layers

Run `references/scan_tells.py` on the text when a shell is available (it counts layer 1
patterns and measures sentence-length variance). Read the text yourself regardless.
The script is a floor, never the target: when the scanner says clean and your reading
says a sentence still carries the shape of a tell, your reading wins. When the scanner
flags something your reading says is legitimate (a required negation, a dash the
anchor author actually uses), keep it and say so in the report. Never insert a
fragment, a short sentence, or a fourth item to move a number; text engineered to
pass a detector is the signature this skill exists to remove. On pieces under about
80 words the spread number is advisory only.

### Layer 1 -- Lexical and typographic tells (mechanical, must reach zero)

| Tell | EN forms | ES forms |
|---|---|---|
| Dash as clause glue | em dash / en dash / spaced hyphen joining two clauses | raya, guion largo, " - " entre clausulas |
| False contrast | "not X, but Y", "it's not about X, it's about Y", "not because X but because Y" | "no es X, es Y", "no se trata de X, sino de Y", "no es un problema, es una oportunidad" |
| Framing filler | "it's worth noting", "importantly", "notably", "in today's fast-paced world", "in an era where", "here's the thing", "let's dive in", "at its core" | "cabe destacar", "es importante mencionar", "vale la pena senalar", "en un mundo donde", "hoy en dia mas que nunca", "en definitiva", "sin duda", "a nivel de" |
| Summary closers | "in conclusion", "ultimately", "the bottom line", "at the end of the day", "the takeaway" | "en resumen", "en conclusion", "al final del dia", "en pocas palabras", "lo cierto es que" |
| Stock vocabulary | delve, tapestry, landscape, navigate, leverage, robust, seamless, unlock, elevate, empower, foster, harness, game-changer, cutting-edge, crucial, vital, journey, realm, testament | sumergirse, abanico, panorama, potenciar, robusto, fluido, desbloquear, elevar, empoderar, fomentar, aprovechar al maximo, clave (as filler), fundamental (as filler), viaje (metaphorical), un antes y un despues |
| Colon reveal | "The result: ...", "The problem? ...", "One word: ..." | "El resultado: ...", "El problema? ...", "Una palabra: ..." |
| Rhetorical Q + self-answer | "Why does this matter? Because..." | "Por que importa? Porque..." |
| Bolded lead-ins on list items | **Speed:** ..., **Cost:** ... | **Velocidad:** ..., **Costo:** ... |
| Emoji as structure | bullets or headers carrying emoji | same |
| Hedge stacking | "may potentially", "could possibly", "it seems that it might" | "podria eventualmente", "quizas tal vez", "en cierta medida podria" |

### Layer 2 -- Structural tells (statistical, must drop below thresholds)

These survive every blacklist and are what a careful reader actually detects.

- **Uniform sentence length.** Machine prose sits around 15-22 words with low
  spread. Human prose has a 4-word sentence next to a 38-word one. Target: standard
  deviation of sentence length above 40% of the mean.
- **Rule of three everywhere.** Three adjectives, three examples, three bullet
  points, three-part parallel clauses. One triad per piece is normal; one per
  paragraph is a signature. Default fix is to break the parallelism (different
  grammar for each member, or one member expanded into its own sentence), which
  keeps every claim. Dropping a member removes a claim; do it only when that
  member has nothing behind it (no fact in the brief supports "clientes mas
  satisfechos"), and list the dropped claim in the report as unsupported, never
  silently. Extending to four is allowed only when a fourth real item exists.
- **Paragraph template.** Claim, two supports, synthesis sentence. Every paragraph.
  Humans end paragraphs mid-thought, on a detail, on a question they leave open, or
  just stop.
- **Framing opener.** First sentence restates the topic instead of saying something
  ("When it comes to X, there are several factors to consider"). Delete it; start on
  the second sentence.
- **Summary closer.** Final paragraph restates the piece. Delete it. If the user
  needs a call to action, one sentence, concrete.
- **Anaphora and perfect parallelism.** "We build. We ship. We learn." Fine once;
  a tell when it recurs.
- **Balanced concession.** "While X is true, Y also matters" applied to every claim,
  so nothing is ever asserted. Take a side where the author would.
- **One-line punch paragraph after a long paragraph.** "And it worked." This is a
  rhythm trick models overuse. Allow at most one per piece.
- **Header for every three lines / list-ification.** Prose turned into bullets when
  the ideas are not parallel. Merge back into paragraphs.
- **Symmetric contrast pairs.** "Old way / new way", "before / after" laid out in
  matching sentences. Break the symmetry or drop one side.
- **Semicolon and colon spam.** The lazy fix for dashes. Test: if the original had
  a dash at that spot, a semicolon there is a swap, and it goes. A semicolon the
  author would have written joining two clauses the draft never dashed is fine, one
  per piece.

### Layer 3 -- Voice absence (qualitative, the part that makes it human)

- **No concrete nouns.** "Stakeholders", "solutions", "outcomes" where a person
  would say the name of the thing, the number, the date, the city.
- **No stake.** The author never says what they think, what they got wrong, what
  they are unsure about, what annoys them. A person with an opinion writes
  differently from an explainer.
- **Single register.** Same formality from first word to last. Humans shift: a
  precise paragraph, then a blunt aside, then back.
- **No dialect.** Nothing that places the writer. For LFP: Colombian and Peruvian
  Spanish idiom, ES/EN mixing, business shorthand ("V.B.", "el expediente",
  "la licitacion").
- **No friction.** Every sentence is smooth. Humans leave a fragment. A sentence
  that starts with "And". A parenthetical that runs long.
- **Over-humanized.** The opposite failure: injected slang, fake typos, forced
  jokes, "honestly", "look,". That is a model imitating a human, and it reads as
  such. Restraint.

## Step 2 -- Rewrite, by layer, in this order

1. **Layer 1 to zero.** Every dash sentence gets restructured (split into two
   sentences, subordinate clause, or a parenthesis when the aside is a real aside).
   Every false contrast becomes a direct statement, a real question, or a concrete
   implication. Every framer and closer is deleted, not paraphrased. Stock words are
   replaced with the specific word the sentence actually needed, or the phrase is
   cut if it needed nothing.
2. **Layer 2 to threshold.** Read the sentence lengths aloud in your head. Merge two
   short ones. Cut one long one in half at an unexpected place. Find each triad and
   decide. Delete the opener and closer paragraphs, then check the piece still lands
   without them (it almost always does). Unbold list lead-ins or turn the list into
   a paragraph.
3. **Layer 3 by anchor.** Add the concrete noun, the number, the name -- **only from
   material the user gave or the project holds. Never invent a fact, a figure, or a
   quote to make text feel specific.** If specificity needs a fact you do not have,
   leave a bracketed slot `[dato: ...]` and flag it. Insert stake where the anchor
   voice would (LFP: a position, a named weakness, a "this is the part I would
   cut"). Shift register once or twice. Let one sentence stay rough.

Constraints on the rewrite:

- Meaning is preserved. Claims are not strengthened, softened, or added.
- Negations required for legal, safety, or factual accuracy stay. The false-contrast
  tell is the reframe shape: "no es X, es Y" where Y is X relabeled and no reason is
  given. A plain negation that limits a claim ("la escala fuera de Lima todavia no
  se probo") is a person being precise, and it stays.
- Length moves for two reasons only: deleting framers and closers (shorter) and
  injecting brief facts (longer). Both are required, so the result may land up to
  about 20% either side of the original. Anything beyond that means you rewrote
  the argument, which is a different task; stop and say so.
- Do not swap dashes for semicolons or colons as a mechanical substitution.
- In Subastop, SubasCars, SubasBlog, and archive contexts, the InPositive rule
  applies after this skill. Run human-reactor first, then inpositive-language; the
  two do not conflict, because false contrasts are negations InPositive would also
  remove.

## Step 3 -- Re-scan and deliver

Run the scan again on the rewrite. Deliver:

1. The rewritten text (or the generated text), nothing else above it.
2. A **Reactor report**, short:
   - Anchor used (sample / project voice / LFP default).
   - Layer 1 count before and after (after must be 0; if it is not, say which
     instance you kept and why, e.g. a legally required negation).
   - Layer 2: sentence-length mean and spread before and after; triads found and
     what you did with them; opener/closer removed yes/no.
   - Layer 3: which facts you injected and from which source (brief, project file,
     prior approved piece); any claim dropped as unsupported; any `[dato: ...]`
     slots left for the user.
3. **Weakest point** of the rewrite: the sentence you are least sure reads as the
   author. One sentence. Not a caveat, an honest assessment.

In SCAN mode deliver only items 2 and the flagged sentences quoted verbatim, each
with its layer and tell name.

## Generate mode specifics

When writing from a brief instead of a draft, resolve the anchor first, then write
with these habits so the scan comes back clean instead of needing surgery:

- Start on the substance. The first sentence carries a fact, a position, or the
  thing the reader needs to do.
- Decide sentence lengths on purpose. Before writing a paragraph, know that it will
  have one long sentence and one very short one.
- Pick two examples, or four. Notice when you reach for three.
- End when the point is made. The last sentence is a detail or an instruction, never
  a summary.
- Say one thing you are unsure about, if the author would.
- Keep every fact traceable to the brief or project material; the voice-bench-gate
  grounding rule applies to generated prose too.

## Worked example

Input (EN, machine draft):

> In today's fast-paced business environment, data is not just an asset -- it's the
> foundation of every decision. Our platform offers robust, seamless, and scalable
> tools that empower teams to unlock insights. The result: faster decisions, better
> outcomes, and happier customers. Ultimately, the organizations that leverage data
> effectively will be the ones that thrive.

Scan: L1 = 11 (framer, dash, false contrast, stock x6, colon reveal, closer).
L2: four sentences, 16-19 words each, two triads, opener and closer present.
L3: zero concrete nouns, zero stake.

Rewrite (anchor: LFP default; facts from the brief: Firestore, 40k listings, the
comparables pipeline):

> The comparables pipeline reads 40k listings a night into Firestore. That is the
> asset. What a dealer does with it the next morning is the product, and right now
> that part takes them longer than it should. The fix is in the query layer, and it
> ships next week.

Report: L1 0. Sentence lengths 11 / 4 / 21 / 12, spread well above threshold. Triads
removed (2). Opener and closer removed. Specificity from the brief only. Weakest
point: "That is the asset" is a punch line, and the piece has only one, but it is
still the sentence closest to a model rhythm.

## Failure modes to watch in yourself

- Declaring the text "clean" after layer 1 only. The scan exists so you cannot.
- Replacing one template with another (the "warm human" template with "honestly"
  and "look, here's the deal"). Voice comes from the anchor, never from a stock
  humanity kit.
- Adding facts to feel specific. Bracket and flag instead.
- Over-cutting the author's own rhetorical devices because they resemble a tell. If
  the sample shows the author uses dashes, the author keeps some dashes. The anchor
  wins over the table.
