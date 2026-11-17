#!/usr/bin/env python3
"""deck_script.py: checks a deck script before anything is generated, and gates the one generation.

The deck script is a JSON file: the brief, the slides (title, body, what part of the brief each one
answers, where each number comes from) and the generations spent. The workshop's decision log is the
source: every number on a slide has to trace back to it or to a named source.

Hard rules live here, not in the prompt:
  - `gate` says no unless every check passes, every slide is approved by the person and no generation
    has been spent yet;
  - `record` refuses a second generation: fixes after the first one are edits.

Usage:
  deck_script.py check  <deck.json>
  deck_script.py gate   <deck.json>
  deck_script.py record <deck.json> --id <generation id or url>

Exit codes: 0 ok, 1 a gate or a check said no, 2 bad usage.
Standard library only. Python 3.9+.
"""
import argparse
import datetime
import json
import os
import re
import sys

ARC = ["goal", "user", "failure", "ideas", "choice", "measure", "phases", "summary"]
REQUIRED_ARC = ["goal", "user", "failure", "choice", "measure", "summary"]
LABEL_TITLES = {
    "overview", "agenda", "context", "background", "problem", "the problem", "solution", "the solution", "ideas",
    "metrics", "next steps", "summary", "conclusion", "roadmap", "goal", "customer", "user", "appendix", "introduction",
    "contexto", "problema", "el problema", "solución", "la solución", "métricas", "próximos pasos", "resumen",
    "conclusión", "objetivo", "cliente", "usuario", "anexo", "introducción",
}
NUMBER = re.compile(r"(?<![\w.,])\d[\d.,]*(?:\s?%)?")
DURATION = re.compile(r"\s?(?:seconds?|secs?|days?|weeks?|months?|years?|hours?|minutes?|min|segundos?|d[ií]as?|semanas?|mes(?:es)?|a[ñn]os?|horas?|minutos?)\b",
                      re.IGNORECASE)
CLOCK_AFTER = re.compile(r":\d")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, deck):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def norm(token):
    return str(token).replace(" ", "").rstrip(".,")


def number_tokens(text):
    out = []
    for m in NUMBER.finditer(text or ""):
        tok = norm(m.group(0))
        if not tok or DURATION.match(text, m.end()):
            continue
        if CLOCK_AFTER.match(text, m.end()) or (m.start() > 1 and text[m.start() - 1] == ":" and text[m.start() - 2].isdigit()):
            continue
        plain = tok.replace(".", "").replace(",", "")
        if plain.isdigit() and "." not in tok and "," not in tok:
            n = int(plain)
            if n <= 12 or 1900 <= n <= 2100:
                continue
        out.append(tok)
    return out


def log_numbers(deck, deck_path):
    """Numbers registered in the workshop log, if the deck names one and it can be read."""
    ref = deck.get("log")
    if not ref:
        return None
    path = ref if os.path.isabs(ref) else os.path.join(os.path.dirname(os.path.abspath(deck_path)), ref)
    if not os.path.exists(path):
        return None
    return set(norm(n.get("value", "")) for n in load(path).get("numbers", []))


def run_checks(deck, deck_path="."):
    problems = []
    slides = deck.get("slides") or []
    brief = deck.get("brief") or []
    registered = log_numbers(deck, deck_path)
    if deck.get("log") and registered is None:
        problems.append(("trace", "-", "the workshop log named in 'log' cannot be read"))

    # 1. Every point of the brief has a slide that answers it.
    covered = set(c for s in slides for c in (s.get("covers") or []))
    for point in brief:
        if point.get("id") not in covered:
            problems.append(("brief", "-", "no slide answers brief point %s: %s" % (point.get("id"), point.get("asks", ""))))

    # 3. Slide cap.
    cap = deck.get("max_slides")
    if cap and len(slides) > cap:
        problems.append(("cap", "-", "%d slides, and the cap is %d" % (len(slides), cap)))

    last_arc = -1
    seen_arc = set()
    for s in slides:
        n = str(s.get("n", "?"))
        title = (s.get("title") or "").strip()
        # 2. The title is a claim.
        if (not title or title.casefold().rstrip(":") in LABEL_TITLES or title.endswith(":")
                or len(title.split()) < 4):
            problems.append(("title", n, "the title is a label, not a claim: '%s'" % title))
        # 2. Every number traces back.
        declared = {}
        for item in s.get("numbers") or []:
            declared[norm(item.get("value", ""))] = item.get("trace", "")
        text = " ".join([title, s.get("body") or ""])
        for tok in number_tokens(text):
            trace = declared.get(tok)
            if not trace:
                problems.append(("trace", n, "%s has no trace to the board or to a source" % tok))
                continue
            kind, _, ref = trace.partition(":")
            if kind not in ("log", "evidence", "source") or not ref.strip():
                problems.append(("trace", n, "%s has a trace that says nothing: '%s'" % (tok, trace)))
            elif kind == "log" and registered is not None and tok not in registered:
                problems.append(("trace", n, "%s says it comes from the workshop log, and the log does not have it" % tok))
        # 3. Sources in the footer, and no personal data in images.
        if declared and not (s.get("footer_sources") or []):
            problems.append(("footer", n, "the slide has numbers and no source in the footer"))
        for img in s.get("images") or []:
            if img.get("personal_data_checked") is not True:
                problems.append(("image", n, "image '%s' was not checked for personal data" % img.get("file", "?")))
        # No em dashes, in any language.
        if chr(0x2014) in text:
            problems.append(("style", n, "em dash in the slide text"))
        # 6. The arc of the case, in order.
        arc = s.get("arc")
        if arc and arc != "other":
            if arc not in ARC:
                problems.append(("arc", n, "unknown arc step '%s'" % arc))
            else:
                if ARC.index(arc) < last_arc:
                    problems.append(("arc", n, "'%s' comes after a later step of the case" % arc))
                last_arc = max(last_arc, ARC.index(arc))
                seen_arc.add(arc)
    for step in REQUIRED_ARC:
        if step not in seen_arc:
            problems.append(("arc", "-", "the deck has no '%s' slide" % step))

    closing = (deck.get("closing_sentence") or "").strip()
    if not closing:
        problems.append(("closing", "-", "the deck does not close with the one-sentence summary"))
    elif "\n" in closing or re.findall(r"[.!?](?=\s+\S)", closing):
        problems.append(("closing", "-", "the closing summary is more than one sentence"))

    # 4. One generation per deck.
    if len(deck.get("generations") or []) > 1:
        problems.append(("generation", "-", "more than one generation was spent on this deck"))
    return problems


def report(problems):
    if not problems:
        print("All checks pass.")
        return 0
    print("%d things to fix:" % len(problems))
    for code, n, msg in problems:
        print("  [%s] slide %s: %s" % (code, n, msg))
    return 1


def cmd_check(args):
    return report(run_checks(load(args.deck), args.deck))


def cmd_gate(args):
    deck = load(args.deck)
    problems = run_checks(deck, args.deck)
    waiting = [str(s.get("n", "?")) for s in deck.get("slides") or [] if s.get("approved") is not True]
    if waiting:
        problems.append(("approval", ", ".join(waiting), "the person has not approved these slides yet"))
    if deck.get("generations"):
        problems.append(("generation", "-", "this deck was already generated once: fix it by editing, do not generate again"))
    if problems:
        report(problems)
        print("Do not generate.")
        return 1
    print("Ready. Ask the person before generating: it spends credits.")
    return 0


def cmd_record(args):
    deck = load(args.deck)
    if deck.get("generations"):
        print("This deck already has its one generation. Fixes are edits.")
        return 1
    deck["generations"] = [{"id": args.id, "at": datetime.datetime.now().isoformat(timespec="seconds")}]
    save(args.deck, deck)
    print("Generation recorded.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Checks and gate for a deck script.")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("check"); s.add_argument("deck")
    s = sub.add_parser("gate"); s.add_argument("deck")
    s = sub.add_parser("record"); s.add_argument("deck"); s.add_argument("--id", required=True)
    args = p.parse_args(argv)
    if not args.cmd:
        p.print_help()
        return 2
    return {"check": cmd_check, "gate": cmd_gate, "record": cmd_record}[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
