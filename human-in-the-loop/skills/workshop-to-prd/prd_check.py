#!/usr/bin/env python3
"""prd_check.py: checks a short, test-first PRD built from a workshop's decision log, and renders it.

The PRD is a JSON file (the record) that renders to Markdown (the view). It starts from the test:
the hypothesis, the cheapest test, the threshold and what gets decided if the threshold is missed.
Every requirement says which failure from the board it answers, so the document cannot grow with
things nobody decided.

Hard rules live here, not in the prompt:
  - `check` fails when a requirement answers nothing or does not say how we will know it is met, when a
    number is not on the board or in a named
    source, when an idea the workshop discarded comes back without the person reopening it, or when
    the test that comes first is incomplete;
  - `gate` says "ready" only when the three sections that belong to the person carry their own words
    and every open question has an owner and a date.

Usage:
  prd_check.py check  <prd.json>
  prd_check.py gate   <prd.json>
  prd_check.py render <prd.json>          (Markdown to stdout)

Exit codes: 0 ok, 1 a gate or a check said no, 2 bad usage.
Standard library only. Python 3.9+.
"""
import argparse
import json
import os
import re
import sys

NUMBER = re.compile(r"(?<![\w.,])\d[\d.,]*(?:\s?%)?")
DURATION = re.compile(r"\s?(?:seconds?|secs?|days?|weeks?|months?|years?|hours?|minutes?|min|segundos?|d[ií]as?|semanas?|mes(?:es)?|a[ñn]os?|horas?|minutos?)\b",
                      re.IGNORECASE)
CLOCK_AFTER = re.compile(r":\d")
PERSON_SECTIONS = ("scope_v1", "out_of_scope", "edge_cases")
PRIORITIES = ("P0", "P1", "P2")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            for s in strings(v):
                yield s
    elif isinstance(obj, list):
        for v in obj:
            for s in strings(v):
                yield s


def filled(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return value is not None


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


def read_log(prd, prd_path):
    ref = prd.get("log")
    if not ref:
        return None
    path = ref if os.path.isabs(ref) else os.path.join(os.path.dirname(os.path.abspath(prd_path)), ref)
    return load(path) if os.path.exists(path) else None


def board(log):
    """What the checks need from the decision log: failures, ideas, the chosen idea, registered numbers."""
    out = {"failures": [], "ideas": [], "chosen": "", "numbers": set()}
    if not log:
        return out
    for fr in log.get("frames", []):
        fields = fr.get("final") if fr.get("final") is not None else ((fr.get("draft") or {}).get("fields") or {})
        if fr["id"] == "4":
            out["failures"] = [f.get("name", "") for f in fields.get("failures") or []]
        elif fr["id"] == "5":
            out["ideas"] = [i.get("name", "") for i in fields.get("ideas") or []]
        elif fr["id"] == "6":
            out["chosen"] = fields.get("chosen_idea", "")
    out["numbers"] = set(norm(n.get("value", "")) for n in log.get("numbers", []))
    return out


def run_checks(prd, prd_path="."):
    problems = []
    log = read_log(prd, prd_path)
    if prd.get("log") and log is None:
        problems.append(("trace", "the workshop log named in 'log' cannot be read"))
    b = board(log)

    # The test comes first: hypothesis, cheapest test, threshold, and the decision if it is missed.
    test = prd.get("test_first") or {}
    for key in ("hypothesis", "test", "threshold", "decision_if_missed"):
        if not filled(test.get(key)):
            problems.append(("test_first", "the test that comes first has no '%s'" % key))

    for key in ("problem", "for_whom", "what_we_build"):
        if not filled(prd.get(key)):
            problems.append(("structure", "'%s' is empty" % key))
    if not filled(prd.get("goals")):
        problems.append(("structure", "no goals"))

    # Every requirement answers a failure from the board, or the goal.
    reqs = prd.get("requirements") or []
    if not any(r.get("priority") == "P0" for r in reqs):
        problems.append(("structure", "no P0 requirement: say what the first version cannot ship without"))
    seen = set()
    discarded_names = [d.get("idea", "") for d in prd.get("discarded") or []]
    for r in reqs:
        rid = r.get("id", "?")
        if rid in seen:
            problems.append(("structure", "requirement id %s is used twice" % rid))
        seen.add(rid)
        if r.get("priority") not in PRIORITIES:
            problems.append(("structure", "requirement %s has no priority (P0, P1 or P2)" % rid))
        if not filled(r.get("acceptance")):
            problems.append(("acceptance", "requirement %s does not say how we will know it is met" % rid))
        answers = (r.get("answers") or "").strip()
        kind, _, ref = answers.partition(":")
        if kind == "goal":
            pass
        elif kind == "failure" and ref.strip():
            if b["failures"] and ref.strip() not in b["failures"]:
                problems.append(("trace", "requirement %s answers a failure that is not on the board: '%s'" % (rid, ref.strip())))
        else:
            problems.append(("trace", "requirement %s does not say which failure or goal it answers" % rid))
        # An idea the workshop discarded does not come back on its own.
        text = (r.get("text") or "").casefold()
        for name in discarded_names:
            if len(name) >= 4 and name.casefold() in text and not filled(r.get("reopened_by")):
                problems.append(("discarded", "requirement %s brings back '%s', which the workshop discarded, "
                                              "without the person reopening it" % (rid, name)))

    # The ideas the workshop did not choose are listed as discarded alternatives, each with its reason.
    for idea in b["ideas"]:
        if idea and idea != b["chosen"] and idea not in discarded_names:
            problems.append(("discarded", "the idea '%s' was on the board and is not among the discarded alternatives" % idea))
    for d in prd.get("discarded") or []:
        if not filled(d.get("reason")):
            problems.append(("discarded", "'%s' is discarded without a reason" % d.get("idea", "?")))
    for key, label in (("non_goals", "non-goal"), ("out_of_scope", "out-of-scope item")):
        for item in prd.get(key) or []:
            if not filled(item.get("reason")):
                problems.append(("reason", "%s '%s' has no reason" % (label, item.get("text", "?"))))

    # No new numbers.
    sources = dict((norm(s.get("value", "")), s.get("source", "")) for s in prd.get("sources") or [])
    seen_numbers = set()
    body = dict((k, v) for k, v in prd.items() if k not in ("sources", "log", "person_answers"))
    for text in strings(body):
        for tok in number_tokens(text):
            if tok in seen_numbers:
                continue
            seen_numbers.add(tok)
            if tok in b["numbers"] or filled(sources.get(tok)):
                continue
            problems.append(("number", "%s is not on the board and has no named source" % tok))
        if chr(0x2014) in text:
            problems.append(("style", "em dash in the text"))

    # What is not known is an open question, not a guess.
    open_q = [q for q in prd.get("open_questions") or [] if (q.get("status") or "open") != "closed"]
    tbd = sum(text.count("[TBD]") for text in strings(body))
    if tbd > len(open_q):
        problems.append(("open", "%d [TBD] marks in the text and only %d open questions: every unknown needs its question" % (tbd, len(open_q))))
    return problems


def gate_problems(prd, prd_path="."):
    problems = run_checks(prd, prd_path)
    answers = prd.get("person_answers") or {}
    for key in PERSON_SECTIONS:
        if not filled(answers.get(key)):
            problems.append(("person", "'%s' has no answer from the person: that section is theirs to decide" % key))
    if not filled(prd.get("edge_cases")):
        problems.append(("person", "no edge cases written"))
    # The threshold and the decision if it is missed are the person's: a [TBD] there keeps the PRD a draft.
    for key, value in (prd.get("test_first") or {}).items():
        if "[TBD]" in str(value):
            problems.append(("test_first", "'%s' of the test that comes first is still [TBD]: the person decides it" % key))
    for q in prd.get("open_questions") or []:
        if (q.get("status") or "open") == "closed":
            continue
        if not filled(q.get("owner")) or not filled(q.get("due")):
            problems.append(("open", "open question without an owner and a date: '%s'" % q.get("question", "?")))
    return problems


def report(problems, closing=None):
    if not problems:
        print("All checks pass.")
        return 0
    print("%d things to fix:" % len(problems))
    for code, msg in problems:
        print("  [%s] %s" % (code, msg))
    if closing:
        print(closing)
    return 1


def cmd_check(args):
    return report(run_checks(load(args.prd), args.prd))


def cmd_gate(args):
    prd = load(args.prd)
    problems = gate_problems(prd, args.prd)
    if problems:
        return report(problems, "Not ready for engineering.")
    open_q = [q for q in prd.get("open_questions") or [] if (q.get("status") or "open") != "closed"]
    print("Ready for engineering, with %d open questions, each with an owner and a date." % len(open_q))
    return 0


def render(prd, prd_path="."):
    open_q = [q for q in prd.get("open_questions") or [] if (q.get("status") or "open") != "closed"]
    ready = not gate_problems(prd, prd_path)
    t = prd.get("test_first") or {}
    o = ["# %s" % prd.get("title", "PRD"), ""]
    o.append("**Status:** %s. %d open questions." % ("ready for engineering" if ready else "draft, not ready", len(open_q)))
    o += ["", "## The problem, and for whom", "", prd.get("problem", ""), "", prd.get("for_whom", ""), ""]
    o += ["## The test that comes first", ""]
    o += ["- **Hypothesis:** %s" % t.get("hypothesis", ""), "- **Cheapest test:** %s" % t.get("test", ""),
          "- **Threshold:** %s" % t.get("threshold", ""), "- **If we miss it:** %s" % t.get("decision_if_missed", ""), ""]
    o += ["## Goals", ""] + ["- %s" % g for g in prd.get("goals") or []] + [""]
    if prd.get("non_goals"):
        o += ["**Not a goal:**", ""] + ["- %s. %s" % (n["text"], n.get("reason", "")) for n in prd["non_goals"]] + [""]
    o += ["## What we build", "", prd.get("what_we_build", ""), ""]
    if prd.get("discarded"):
        o += ["| Alternative we discarded | Why |", "|---|---|"]
        o += ["| %s | %s |" % (d.get("idea", ""), d.get("reason", "")) for d in prd["discarded"]] + [""]
    o += ["## Requirements", "", "| Id | Priority | Requirement | Done when | Answers |", "|---|---|---|---|---|"]
    for r in prd.get("requirements") or []:
        answers = (r.get("answers") or "").replace("failure:", "Failure: ").replace("goal", "The goal")
        o.append("| %s | %s | %s | %s | %s |" % (r.get("id", ""), r.get("priority", ""), r.get("text", ""),
                                               r.get("acceptance", ""), answers))
    o += ["", "## Edge cases and errors", ""]
    o += ["- **%s:** %s" % (e.get("case", ""), e.get("behavior", "")) for e in prd.get("edge_cases") or []] + [""]
    m = prd.get("metrics") or {}
    if m:
        o += ["## How we measure it", ""] + ["- **%s:** %s" % (k.replace("_", " ").capitalize(), v) for k, v in m.items()] + [""]
    o += ["## Phases, and what is left out", ""] + ["%d. %s" % (i, p) for i, p in enumerate(prd.get("phases") or [], 1)] + [""]
    if prd.get("out_of_scope"):
        o += ["**Left out:**", ""] + ["- %s. %s" % (x["text"], x.get("reason", "")) for x in prd["out_of_scope"]] + [""]
    o += ["## Open questions", ""]
    if prd.get("open_questions"):
        o += ["| Question | Owner | Due | Status |", "|---|---|---|---|"]
        o += ["| %s | %s | %s | %s |" % (q.get("question", ""), q.get("owner", ""), q.get("due", ""), q.get("status") or "open")
              for q in prd["open_questions"]]
    else:
        o.append("None.")
    return "\n".join(o) + "\n"


def cmd_render(args):
    sys.stdout.write(render(load(args.prd), args.prd))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Checks, gate and Markdown view of a test-first PRD.")
    sub = p.add_subparsers(dest="cmd")
    for name in ("check", "gate", "render"):
        s = sub.add_parser(name)
        s.add_argument("prd")
    args = p.parse_args(argv)
    if not args.cmd:
        p.print_help()
        return 2
    return {"check": cmd_check, "gate": cmd_gate, "render": cmd_render}[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
