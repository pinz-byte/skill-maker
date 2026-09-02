#!/usr/bin/env python3
"""scan_tells.py -- count layer-1 AI tells and measure layer-2 rhythm in a text.

Usage:
    python3 scan_tells.py FILE            # human-readable report
    python3 scan_tells.py FILE --json     # machine-readable
    cat text.md | python3 scan_tells.py - # from stdin

Exit code 0 always; the numbers are the verdict. Layer 1 target: 0.
Layer 2 target: sentence-length spread (stdev/mean) >= 0.40, triads <= 1 per 300 words.
This script catches patterns, not judgment. Layer 3 is read by a person.
"""
import json
import re
import statistics
import sys
import unicodedata

L1 = {
    "dash_glue": [
        r"\s[\u2014\u2013]\s", r"[A-Za-z][\u2014\u2013][A-Za-z]", r"(?<=\S)\s-\s(?=(?-i:[a-z]))",
    ],
    "false_contrast": [
        r"\bnot\s+(?:just\s+|only\s+|about\s+)?[^.,;:]{1,40}?,?\s+but\s+(?:rather\s+|about\s+|also\s+)?",
        r"\bit'?s not (?:about|that)\b",
        r"\bnot because\b[^.]{1,60}\bbut because\b",
        r"\bno es (?:solo |solamente |cuestion de |cuesti[o\u00f3]n de )?[^.,;:]{1,40}?,\s*(?:es|sino)\b",
        r"\bno se trata de\b[^.]{1,60}\bsino\b",
        r"\bno (?:es|era) un[a]? [^.,;:]{1,30}, (?:es|sino) un[a]?\b",
    ],
    "framer": [
        r"\bit'?s worth (?:noting|mentioning)\b", r"\bimportantly\b", r"\bnotably\b",
        r"\bin today'?s\b", r"\bin an era (?:where|of)\b", r"\bhere'?s the thing\b",
        r"\blet'?s dive in\b", r"\bat its core\b", r"\bwhen it comes to\b",
        r"\bcabe (?:destacar|mencionar|se[n\u00f1]alar)\b", r"\bes importante (?:mencionar|destacar|se[n\u00f1]alar)\b",
        r"\bvale la pena (?:se[n\u00f1]alar|destacar|mencionar)\b", r"\ben un mundo (?:donde|en el que)\b",
        r"\bhoy en d[i\u00ed]a\b", r"\bm[a\u00e1]s que nunca\b", r"\bsin duda\b", r"\ba nivel de\b",
    ],
    "closer": [
        r"\bin conclusion\b", r"\bultimately\b", r"\bthe bottom line\b", r"\bat the end of the day\b",
        r"\bthe (?:key )?takeaway\b", r"\bin summary\b",
        r"\ben resumen\b", r"\ben conclusi[o\u00f3]n\b", r"\bal final del d[i\u00ed]a\b",
        r"\ben pocas palabras\b", r"\blo cierto es que\b", r"\ben definitiva\b",
    ],
    "stock_word": [
        r"\bdelv(?:e|es|ing)\b", r"\btapestry\b", r"\blandscape\b", r"\bnavigat(?:e|es|ing)\b",
        r"\bleverag(?:e|es|ing)\b", r"\brobust\b", r"\bseamless(?:ly)?\b", r"\bunlock(?:s|ing)?\b",
        r"\belevat(?:e|es|ing)\b", r"\bempower(?:s|ing)?\b", r"\bfoster(?:s|ing)?\b", r"\bharness(?:es|ing)?\b",
        r"\bgame-?changer\b", r"\bcutting-edge\b", r"\bcrucial\b", r"\bvital\b", r"\bjourney\b",
        r"\brealm\b", r"\btestament to\b", r"\bstreamline\b",
        r"\bsumergir(?:se|nos)\b", r"\babanico de\b", r"\bpanorama\b", r"\bpotenciar\b", r"\brobust[oa]s?\b",
        r"\bfluid[oa]\b", r"\bdesbloquear\b", r"\bempoderar\b", r"\bfomentar\b",
        r"\baprovechar al m[a\u00e1]ximo\b", r"\bun antes y un despu[e\u00e9]s\b",
    ],
    "colon_reveal": [
        r"\b(?:The|El|La) (?:result|resultado|problem|problema|answer|respuesta|catch|truth|verdad)\??:\s",
        r"\b(?:One|Una) (?:word|palabra):\s",
    ],
    "rhetorical_q": [
        r"\?\s+(?:Because|Porque)\b",
    ],
    "bold_leadin": [
        r"^\s*[-*\u2022]\s*\*\*[^*]{1,40}\*\*\s*[:\u2013\u2014-]",
    ],
    "emoji_structure": [
        r"^\s*[\U0001F300-\U0001FAFF\u2600-\u27bf]",
    ],
    "hedge_stack": [
        r"\bmay potentially\b", r"\bcould possibly\b", r"\bmight perhaps\b",
        r"\bpodr[i\u00ed]a eventualmente\b", r"\bquiz[a\u00e1]s tal vez\b",
    ],
}

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\u00c1\u00c9\u00cd\u00d3\u00da\u00d1\u00bf\u00a1\"'(])")
TRIAD = re.compile(r"\b\w+(?:\s\w+){0,2},\s+\w+(?:\s\w+){0,2},?\s+(?:and|y|e|or|o)\s+\w+", re.I)


def sentences(text):
    body = re.sub(r"^\s*(#+|[-*\u2022]|\d+\.)\s+", "", text, flags=re.M)
    out = []
    for para in re.split(r"\n\s*\n", body):
        para = " ".join(para.split())
        if not para:
            continue
        out.extend(s for s in SENT_SPLIT.split(para) if len(s.split()) >= 2)
    return out


def scan(text):
    hits = {}
    total = 0
    for name, pats in L1.items():
        found, seen = [], []
        for p in pats:
            for m in re.finditer(p, text, flags=re.I | re.M):
                if any(m.start() < e and m.end() > b for b, e in seen):
                    continue
                seen.append((m.start(), m.end()))
                start = max(0, m.start() - 40)
                found.append(text[start:m.end() + 40].replace("\n", " ").strip())
        if found:
            hits[name] = found
            total += len(found)

    sents = sentences(text)
    lengths = [len(s.split()) for s in sents]
    words = sum(lengths)
    mean = statistics.mean(lengths) if lengths else 0
    stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0
    spread = (stdev / mean) if mean else 0
    triads = len(TRIAD.findall(text))
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    semis = text.count(";")

    return {
        "layer1_total": total,
        "layer1": hits,
        "layer2": {
            "sentences": len(sents),
            "words": words,
            "len_mean": round(mean, 1),
            "len_stdev": round(stdev, 1),
            "len_spread": round(spread, 2),
            "len_spread_ok": spread >= 0.40,
            "len_spread_advisory": words < 80,
            "shortest": min(lengths) if lengths else 0,
            "longest": max(lengths) if lengths else 0,
            "triads": triads,
            "triads_ok": triads <= max(1, words // 300),
            "paragraphs": len(paras),
            "semicolons": semis,
        },
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    src = args[0] if args else "-"
    raw = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    text = unicodedata.normalize("NFC", raw)
    r = scan(text)
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    l2 = r["layer2"]
    print(f"LAYER 1 tells: {r['layer1_total']}  (target 0)")
    for name, found in r["layer1"].items():
        print(f"  {name} x{len(found)}")
        for f in found[:5]:
            print(f"     ...{f}...")
        if len(found) > 5:
            print(f"     (+{len(found) - 5} more)")
    print("LAYER 2 rhythm:")
    print(f"  sentences {l2['sentences']}, words {l2['words']}, paragraphs {l2['paragraphs']}")
    print(f"  length mean {l2['len_mean']}  stdev {l2['len_stdev']}  spread {l2['len_spread']}  "
          f"[{'ok' if l2['len_spread_ok'] else 'UNIFORM - vary sentence length'}"
          f"{'; advisory only, text under 80 words' if l2['len_spread_advisory'] else ''}]  "
          f"range {l2['shortest']}-{l2['longest']}")
    print(f"  triads {l2['triads']}  [{'ok' if l2['triads_ok'] else 'too many rule-of-three'}]")
    print(f"  semicolons {l2['semicolons']}" + ("  [suspicious: dash swapped for semicolon?]" if l2["semicolons"] >= 2 else ""))
    print("LAYER 3: read it. Concrete nouns? A stake? A register shift? Anchor voice present?")


if __name__ == "__main__":
    main()
