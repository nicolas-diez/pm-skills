#!/usr/bin/env python3
"""workshop_log.py: the decision log of a product workshop, and the gates that keep the person in the loop.

The board is the view; this log is the record. For every frame it keeps what the AI drafted, the
question put to the person, the person's answer in their own words, and what changed.

Hard rules live here, not in the prompt:
  - a frame cannot be opened until every earlier question frame has the person's answer (`open`);
  - a frame cannot be decided without an answer, nor marked "changed" without saying what changed (`decide`);
  - `check` fails if a solution shows up before the ideas frame, if a number has no source and is not
    marked as an assumption, or if a frame is missing what the method asks for.

Usage (payloads always come from a file, never inline):
  workshop_log.py new     <log.json> --case "..." [--type design|diagnosis] [--lang en] [--board URL]
  workshop_log.py draft   <log.json> <frame> --from <payload.json>   # {"question","proposal","fields":{...}}
  workshop_log.py number  <log.json> --from <payload.json>           # [{"value","frame","source"|"assumption":true}]
  workshop_log.py open    <log.json> <frame>
  workshop_log.py decide  <log.json> <frame> --from <payload.json>   # {"answer","outcome","change","fields":{...}}
  workshop_log.py check   <log.json> [--draft | --close]
  workshop_log.py summary <log.json>

`check --draft` runs before the workshop, over the AI's own draft of every frame. Plain `check` looks
only at decided frames. `check --close` also fails while a frame is waiting.

Exit codes: 0 ok, 1 a gate or a check said no, 2 bad usage.
Standard library only. Python 3.9+.
"""
import argparse
import datetime
import json
import os
import re
import sys

# --- The method, as data -------------------------------------------------------------------------
# id, name, has_question. Order is the method: it is checked, not suggested.
DESIGN = [
    ("0", "Start here", False),
    ("1", "Goal", True),
    ("2", "Customer", True),
    ("3", "Their moment and what they use it for", True),
    ("4", "Where it fails today", True),
    ("5", "Ideas", True),
    ("6", "Choose, hypothesis and metrics", True),
    ("7", "Growth and vision", True),
    ("A", "Assumptions", True),
    ("E", "Evidence", False),
]
DIAGNOSIS = [
    ("0", "Start here", False),
    ("D1", "Isolate", True),
    ("D2", "Diagnose", True),
    ("D3", "Resolve", True),
    ("A", "Assumptions", True),
    ("E", "Evidence", False),
]
ROWS = {"design": DESIGN, "diagnosis": DIAGNOSIS}
# Frames that must stay free of solutions, and the frame where solutions are first allowed.
BEFORE_IDEAS = {"design": ["1", "2", "3", "4"], "diagnosis": ["D1", "D2"]}
ROLES = {"pays", "uses", "lives_with"}
SIZES = {"small", "habit", "bold"}


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, log):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def frame(log, fid):
    for fr in log["frames"]:
        if fr["id"] == fid:
            return fr
    raise SystemExit("Unknown frame '%s'. Frames in this log: %s" % (fid, ", ".join(f["id"] for f in log["frames"])))


def strings(obj):
    """Every string inside a nested structure."""
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


def current_fields(fr):
    """What the board says now: the decided version if there is one, else the draft."""
    if fr.get("final") is not None:
        return fr["final"]
    return (fr.get("draft") or {}).get("fields") or {}


# --- Numbers --------------------------------------------------------------------------------------
NUMBER = re.compile(r"(?<![\w.,])\d[\d.,]*(?:\s?%)?")


# A duration is a decision ("in six weeks", "en 90 días"), not a claim that needs a source.
DURATION = re.compile(r"\s?(?:seconds?|secs?|days?|weeks?|months?|years?|hours?|minutes?|min|segundos?|d[ií]as?|semanas?|mes(?:es)?|a[ñn]os?|horas?|minutos?)\b",
                      re.IGNORECASE)
CLOCK_AFTER = re.compile(r":\d")


def norm_number(token):
    return token.replace(" ", "").rstrip(".,")


def number_tokens(text):
    out = []
    for m in NUMBER.finditer(text):
        tok = norm_number(m.group(0))
        if not tok:
            continue
        if DURATION.match(text, m.end()):
            continue
        # A time of day ("08:55") is not a figure either.
        if CLOCK_AFTER.match(text, m.end()) or (m.start() > 1 and text[m.start() - 1] == ":" and text[m.start() - 2].isdigit()):
            continue
        plain = tok.replace(".", "").replace(",", "")
        if plain.isdigit():
            n = int(plain)
            if "." not in tok and "," not in tok:
                if n <= 12:  # "3 ideas", "phase 2": counting, not evidence
                    continue
                if 1900 <= n <= 2100:  # a year
                    continue
        out.append(tok)
    return out


def registry(log):
    reg = {}
    for item in log.get("numbers", []):
        reg[norm_number(str(item.get("value", "")))] = item
    return reg


# --- Commands -------------------------------------------------------------------------------------
def cmd_new(args):
    if os.path.exists(args.log):
        raise SystemExit("That log already exists. Pick another path; a log is never overwritten.")
    row = ROWS[args.type]
    log = {
        "case": args.case,
        "type": args.type,
        "lang": args.lang,
        "board": args.board or "",
        "created_at": now(),
        "frames": [
            {"id": fid, "name": name, "has_question": q, "draft": None, "opened_at": None,
             "answer": None, "outcome": None, "change": None, "final": None, "decided_at": None}
            for fid, name, q in row
        ],
        "numbers": [],
        "solution_terms": [],
    }
    save(args.log, log)
    print("Log created with %d frames (%s row)." % (len(row), args.type))


def cmd_draft(args):
    log = load(args.log)
    fr = frame(log, args.frame)
    if fr.get("decided_at"):
        raise SystemExit("Frame %s is already decided. The draft is history now; it does not change." % fr["id"])
    payload = load(args.payload)
    fr["draft"] = {
        "question": payload.get("question", ""),
        "proposal": payload.get("proposal", ""),
        "fields": payload.get("fields", {}),
        "drafted_at": now(),
    }
    save(args.log, log)
    print("Draft saved for frame %s." % fr["id"])


def cmd_number(args):
    log = load(args.log)
    payload = load(args.payload)
    if isinstance(payload, dict):
        payload = [payload]
    reg = registry(log)
    for item in payload:
        if not filled(item.get("value")):
            raise SystemExit("A number needs a 'value'.")
        if not filled(item.get("source")) and item.get("assumption") is not True:
            raise SystemExit("Number %s needs a source, or \"assumption\": true." % item["value"])
        reg[norm_number(str(item["value"]))] = item
    log["numbers"] = list(reg.values())
    save(args.log, log)
    print("%d numbers in the registry." % len(log["numbers"]))


def pending_before(log, fid):
    out = []
    for fr in log["frames"]:
        if fr["id"] == fid:
            return out
        if fr["has_question"] and not fr.get("decided_at"):
            out.append(fr["id"])
    return out


def cmd_open(args):
    log = load(args.log)
    fr = frame(log, args.frame)
    waiting = pending_before(log, fr["id"])
    if waiting:
        print("Not yet. Frame %s is still waiting for the person's answer." % waiting[0])
        return 1
    if fr["has_question"]:
        if not fr.get("draft") or "?" not in (fr["draft"].get("question") or ""):
            print("Frame %s has no question for the person. Write the draft with its question first." % fr["id"])
            return 1
        if not filled(fr["draft"].get("proposal")):
            print("Frame %s has no proposed answer. Say what you would answer and why, then open it." % fr["id"])
            return 1
    if not fr.get("opened_at"):
        fr["opened_at"] = now()
        save(args.log, log)
    print("Frame %s open: %s" % (fr["id"], fr["name"]))
    if fr["has_question"]:
        print("Question: %s" % fr["draft"]["question"])
        print("Proposed answer: %s" % fr["draft"]["proposal"])
    return 0


def cmd_decide(args):
    log = load(args.log)
    fr = frame(log, args.frame)
    if not fr["has_question"]:
        raise SystemExit("Frame %s has no question, so there is nothing to decide." % fr["id"])
    if not fr.get("opened_at"):
        print("Frame %s was never opened. Open it and ask before recording an answer." % fr["id"])
        return 1
    payload = load(args.payload)
    answer = (payload.get("answer") or "").strip()
    outcome = payload.get("outcome")
    if not answer:
        print("No answer from the person. Their own words go in 'answer'.")
        return 1
    if outcome not in ("kept", "changed"):
        print("'outcome' must be \"kept\" or \"changed\".")
        return 1
    if outcome == "changed" and not filled(payload.get("change")):
        print("The outcome is \"changed\": say what changed and why in 'change'.")
        return 1
    fr["answer"] = answer
    fr["outcome"] = outcome
    fr["change"] = payload.get("change") or ""
    fr["final"] = payload.get("fields") or (fr.get("draft") or {}).get("fields") or {}
    fr["decided_at"] = now()
    save(args.log, log)
    print("Frame %s decided (%s)." % (fr["id"], outcome))
    return 0


# --- Checks ---------------------------------------------------------------------------------------
def need(problems, code, fid, fields, keys):
    for key in keys:
        cur = fields
        for part in key.split("."):
            cur = cur.get(part) if isinstance(cur, dict) else None
        if not filled(cur):
            problems.append((code, fid, "'%s' is empty" % key))


def check_structure(log, problems, draft=False):
    by_id = {fr["id"]: fr for fr in log["frames"]}

    def done(fid):
        fr = by_id.get(fid)
        if not fr:
            return None
        if fr["has_question"] and not fr.get("decided_at"):
            # Before the workshop, --draft checks the AI's own draft of every frame.
            if not draft or not fr.get("draft"):
                return None
        return current_fields(fr)

    reg = registry(log)
    f = done("1")
    if f is not None:
        need(problems, "structure", "1", f, ["business_goal", "user_problem", "metric"])
    f = done("2")
    if f is not None:
        segs = f.get("segments") or []
        if len(segs) < 2:
            problems.append(("structure", "2", "fewer than two customer segments to choose from"))
        for seg in segs:
            roles = seg.get("role") or []
            if isinstance(roles, str):
                roles = [roles]
            if not roles or not set(roles) <= ROLES:
                problems.append(("structure", "2", "segment '%s' does not say who pays, uses or lives with the product"
                                 % seg.get("name", "?")))
        need(problems, "structure", "2", f, ["chosen", "chosen_why"])
        if filled(f.get("chosen")) and f["chosen"] not in [s.get("name") for s in segs]:
            problems.append(("structure", "2", "the chosen customer is not one of the segments"))
        cited = [norm_number(str(v)) for v in (f.get("chosen_why_numbers") or [])]
        if not cited or not all(c in reg for c in cited):
            problems.append(("anecdote", "2", "the choice of customer is not sized: cite at least one number from the "
                                              "registry (a source or a stated assumption)"))
    f = done("3")
    if f is not None:
        need(problems, "structure", "3", f, ["persona", "moment", "deeper_want", "use_cases", "prioritized_use_case"])
    fails = []
    f = done("4")
    if f is not None:
        fails = f.get("failures") or []
        if len(fails) < 2:
            problems.append(("structure", "4", "fewer than two failures"))
        for item in fails:
            if not filled(item.get("alternative_today")):
                problems.append(("alternative", "4", "failure '%s' does not say how the person solves it today"
                                 % item.get("name", "?")))
            if not filled(item.get("cause")):
                problems.append(("structure", "4", "failure '%s' has no cause" % item.get("name", "?")))
        if not filled(f.get("ranking_criterion")):
            problems.append(("criterion", "4", "the failures are ranked without saying by which criterion"))
    ideas = []
    f = done("5")
    if f is not None:
        ideas = f.get("ideas") or []
        if len(ideas) < 3:
            problems.append(("structure", "5", "fewer than three ideas"))
        sizes = set(i.get("size") for i in ideas)
        if not sizes <= SIZES or "small" not in sizes or "bold" not in sizes:
            problems.append(("structure", "5", "the ideas need at least one small fix and one bold bet, labeled"))
        names = [x.get("name") for x in fails]
        for idea in ideas:
            if fails and idea.get("attacks") not in names:
                problems.append(("structure", "5", "idea '%s' is not tied to a failure from frame 4" % idea.get("name", "?")))
    f = done("6")
    if f is not None:
        need(problems, "structure", "6", f, ["chosen_idea", "why_vs_goal", "cheap_test", "weak_spot"])
        need(problems, "hypothesis", "6", f, ["hypothesis.statement", "hypothesis.baseline", "hypothesis.target",
                                              "hypothesis.timeframe"])
        need(problems, "metrics", "6", f, ["metrics.north_star", "metrics.primary", "metrics.secondary",
                                           "metrics.guardrails"])
        if ideas and filled(f.get("chosen_idea")) and f["chosen_idea"] not in [i.get("name") for i in ideas]:
            problems.append(("structure", "6", "the chosen idea is not one of the ideas in frame 5"))
    f = done("7")
    if f is not None:
        need(problems, "structure", "7", f, ["growth", "phases", "company_strategy_fit", "one_sentence_summary"])
        summary = (f.get("one_sentence_summary") or "").strip()
        if summary and ("\n" in summary or len(re.findall(r"[.!?](?=\s+\S)", summary)) > 0):
            problems.append(("structure", "7", "the closing summary is more than one sentence"))
    f = done("D1")
    if f is not None:
        need(problems, "structure", "D1", f, ["metric", "branch_that_moved"])
        if len(f.get("tree") or []) < 2:
            problems.append(("structure", "D1", "the metric tree has fewer than two branches"))
    f = done("D2")
    if f is not None:
        cuts = f.get("cuts") or []
        if len(cuts) < 2 or not all(filled(c.get("finding")) for c in cuts):
            problems.append(("structure", "D2", "fewer than two cuts with a finding each"))
        need(problems, "structure", "D2", f, ["cause_hypothesis"])
    f = done("D3")
    if f is not None:
        need(problems, "structure", "D3", f, ["goal", "chosen", "how_measured"])
        if len(f.get("options") or []) < 2:
            problems.append(("structure", "D3", "fewer than two options"))
    f = done("A")
    if f is not None:
        need(problems, "structure", "A", f, ["assumptions", "most_worrying"])
    ev = by_id.get("E")
    if ev is not None:
        for item in current_fields(ev).get("items") or []:
            if item.get("type") == "anecdote":
                problems.append(("anecdote", "E", "a personal anecdote is listed as evidence: '%s'" % item.get("ref", "?")))
            elif not filled(item.get("source")):
                problems.append(("source", "E", "evidence '%s' has no source" % item.get("ref", "?")))


def solution_terms(log):
    terms = list(log.get("solution_terms") or [])
    by_id = {fr["id"]: fr for fr in log["frames"]}
    if log["type"] == "design":
        f5 = by_id.get("5")
        if f5:
            for src in (current_fields(f5), (f5.get("draft") or {}).get("fields") or {}):
                terms += [i.get("name", "") for i in (src.get("ideas") or [])]
    else:
        d3 = by_id.get("D3")
        if d3:
            for src in (current_fields(d3), (d3.get("draft") or {}).get("fields") or {}):
                for opt in src.get("options") or []:
                    terms.append(opt.get("name", "") if isinstance(opt, dict) else str(opt))
    return sorted(set(t.strip().casefold() for t in terms if len(t.strip()) >= 4))


def check_no_early_solution(log, problems):
    terms = solution_terms(log)
    by_id = {fr["id"]: fr for fr in log["frames"]}
    for fid in BEFORE_IDEAS[log["type"]]:
        fr = by_id.get(fid)
        if not fr:
            continue
        text = " ".join(strings([(fr.get("draft") or {}).get("fields"), fr.get("final")])).casefold()
        for term in terms:
            if term in text:
                problems.append(("early_solution", fid, "the solution '%s' is written before the ideas frame" % term))


def check_order(log, problems, close):
    last_decided = None
    for fr in log["frames"]:
        if not fr["has_question"]:
            continue
        if fr.get("opened_at"):
            waiting = [p for p in pending_before(log, fr["id"])]
            if waiting:
                problems.append(("order", fr["id"], "opened while frame %s had no answer" % waiting[0]))
            if last_decided and fr["opened_at"] < last_decided:
                problems.append(("order", fr["id"], "opened before the previous frame was decided"))
        if fr.get("decided_at"):
            if not filled(fr.get("answer")):
                problems.append(("order", fr["id"], "decided without the person's answer"))
            if not fr.get("opened_at"):
                problems.append(("order", fr["id"], "decided without ever being opened"))
            if "?" not in ((fr.get("draft") or {}).get("question") or ""):
                problems.append(("closed_text", fr["id"], "the frame went to the person as text to approve, not as a question"))
            last_decided = fr["decided_at"]
        elif close:
            problems.append(("pending", fr["id"], "still waiting for the person's answer"))


def check_numbers(log, problems, draft=False):
    reg = registry(log)
    for value, item in reg.items():
        if not filled(item.get("source")) and item.get("assumption") is not True:
            problems.append(("number", str(item.get("frame", "?")), "%s has no source and is not marked as an assumption" % value))
    for fr in log["frames"]:
        if fr["has_question"] and not fr.get("decided_at") and not draft:
            continue
        seen = set()
        for text in strings(current_fields(fr)):
            for tok in number_tokens(text):
                if tok not in reg and tok not in seen:
                    seen.add(tok)
                    problems.append(("number", fr["id"], "%s is on the board with no source and no assumption mark" % tok))


def check_drafted(log, problems):
    for fr in log["frames"]:
        if not fr.get("draft"):
            problems.append(("draft", fr["id"], "not drafted yet"))
        elif fr["has_question"]:
            if "?" not in (fr["draft"].get("question") or ""):
                problems.append(("draft", fr["id"], "the draft has no question for the person"))
            if not filled(fr["draft"].get("proposal")):
                problems.append(("draft", fr["id"], "the draft has no proposed answer"))


def run_checks(log, close=False, draft=False):
    problems = []
    check_order(log, problems, close)
    check_no_early_solution(log, problems)
    check_numbers(log, problems, draft)
    check_structure(log, problems, draft)
    if draft:
        check_drafted(log, problems)
    return problems


def cmd_check(args):
    log = load(args.log)
    problems = run_checks(log, close=args.close, draft=args.draft)
    if not problems:
        print("All checks pass.")
        return 0
    print("%d things to fix:" % len(problems))
    for code, fid, msg in problems:
        print("  [%s] frame %s: %s" % (code, fid, msg))
    return 1


def changed_frames(log):
    return [fr for fr in log["frames"] if fr.get("outcome") == "changed"]


def one_line(obj, limit=160):
    text = "; ".join(s.strip() for s in strings(obj) if s.strip())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def cmd_summary(args):
    log = load(args.log)
    decided = [fr for fr in log["frames"] if fr.get("decided_at")]
    changed = changed_frames(log)
    print("# %s: what the workshop changed" % log["case"])
    print("")
    print("%d of %d decisions changed against the AI's first draft." % (len(changed), len(decided)))
    print("")
    print("| Frame | The AI's draft said | The person said | What changed and why |")
    print("|---|---|---|---|")
    for fr in decided:
        draft = one_line((fr.get("draft") or {}).get("proposal") or (fr.get("draft") or {}).get("fields"))
        change = fr.get("change") or "Kept as drafted"
        row = [fr["id"] + ". " + fr["name"], draft, one_line(fr.get("answer") or ""), one_line(change)]
        print("| " + " | ".join(c.replace("|", "/") for c in row) + " |")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Decision log and gates of a product workshop.")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("new"); s.add_argument("log"); s.add_argument("--case", required=True)
    s.add_argument("--type", choices=sorted(ROWS), default="design"); s.add_argument("--lang", default="en")
    s.add_argument("--board", default="")
    s = sub.add_parser("draft"); s.add_argument("log"); s.add_argument("frame"); s.add_argument("--from", dest="payload", required=True)
    s = sub.add_parser("number"); s.add_argument("log"); s.add_argument("--from", dest="payload", required=True)
    s = sub.add_parser("open"); s.add_argument("log"); s.add_argument("frame")
    s = sub.add_parser("decide"); s.add_argument("log"); s.add_argument("frame"); s.add_argument("--from", dest="payload", required=True)
    s = sub.add_parser("check"); s.add_argument("log"); s.add_argument("--close", action="store_true")
    s.add_argument("--draft", action="store_true")
    s = sub.add_parser("summary"); s.add_argument("log")
    args = p.parse_args(argv)
    if not args.cmd:
        p.print_help()
        return 2
    handler = {"new": cmd_new, "draft": cmd_draft, "number": cmd_number, "open": cmd_open,
               "decide": cmd_decide, "check": cmd_check, "summary": cmd_summary}[args.cmd]
    return handler(args) or 0


if __name__ == "__main__":
    sys.exit(main())
