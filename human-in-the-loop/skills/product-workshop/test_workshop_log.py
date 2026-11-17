#!/usr/bin/env python3
"""Tests for workshop_log.py: the gates, the checks and the invented example.

Run from this folder: python3 test_workshop_log.py
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest

import workshop_log as wl

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE = os.path.join(HERE, "examples", "bike-repair-workshop-log.json")


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            code = wl.main(list(argv))
        except SystemExit as e:
            code = 1 if isinstance(e.code, str) else (e.code or 0)
            out.write(str(e.code))
    return code, out.getvalue()


class Gates(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.log = os.path.join(self.dir, "log.json")
        run("new", self.log, "--case", "Test case")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def payload(self, obj):
        path = os.path.join(self.dir, "payload.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        return path

    def draft(self, fid, question="Is this the goal?", proposal="Yes, because the brief says so."):
        return run("draft", self.log, fid, "--from", self.payload(
            {"question": question, "proposal": proposal, "fields": {"business_goal": "g", "user_problem": "p", "metric": "m"}}))

    def test_a_log_is_never_overwritten(self):
        code, out = run("new", self.log, "--case", "Again")
        self.assertEqual(code, 1)
        self.assertIn("already exists", out)

    def test_cannot_open_a_frame_before_the_previous_answer(self):
        self.draft("1")
        self.draft("2", "Why this customer?")
        code, out = run("open", self.log, "2")
        self.assertEqual(code, 1)
        self.assertIn("Frame 1 is still waiting", out)

    def test_cannot_open_a_frame_without_a_question(self):
        self.draft("1", question="This is the goal.")
        code, out = run("open", self.log, "1")
        self.assertEqual(code, 1)
        self.assertIn("no question", out)

    def test_cannot_open_a_frame_without_a_proposed_answer(self):
        self.draft("1", proposal="")
        code, _ = run("open", self.log, "1")
        self.assertEqual(code, 1)

    def test_cannot_decide_without_opening(self):
        self.draft("1")
        code, out = run("decide", self.log, "1", "--from", self.payload({"answer": "ok", "outcome": "kept"}))
        self.assertEqual(code, 1)
        self.assertIn("never opened", out)

    def test_cannot_decide_without_the_persons_words(self):
        self.draft("1")
        run("open", self.log, "1")
        code, _ = run("decide", self.log, "1", "--from", self.payload({"answer": "  ", "outcome": "kept"}))
        self.assertEqual(code, 1)

    def test_changed_needs_what_changed(self):
        self.draft("1")
        run("open", self.log, "1")
        code, out = run("decide", self.log, "1", "--from", self.payload({"answer": "No, another goal", "outcome": "changed"}))
        self.assertEqual(code, 1)
        self.assertIn("what changed", out)

    def test_happy_path_then_next_frame_opens(self):
        self.draft("1")
        self.draft("2", "Why this customer?")
        self.assertEqual(run("open", self.log, "1")[0], 0)
        code, _ = run("decide", self.log, "1", "--from", self.payload(
            {"answer": "No, the goal is bookings", "outcome": "changed", "change": "Goal moved to bookings",
             "fields": {"business_goal": "bookings", "user_problem": "p", "metric": "m"}}))
        self.assertEqual(code, 0)
        self.assertEqual(run("open", self.log, "2")[0], 0)

    def test_a_decided_draft_is_history(self):
        self.draft("1")
        run("open", self.log, "1")
        run("decide", self.log, "1", "--from", self.payload({"answer": "ok", "outcome": "kept"}))
        code, out = self.draft("1")
        self.assertEqual(code, 1)
        self.assertIn("already decided", out)

    def test_a_number_needs_a_source_or_an_assumption_mark(self):
        code, _ = run("number", self.log, "--from", self.payload([{"value": "38%", "frame": "6"}]))
        self.assertEqual(code, 1)
        code, _ = run("number", self.log, "--from", self.payload([{"value": "38%", "frame": "6", "assumption": True}]))
        self.assertEqual(code, 0)

    def test_close_fails_while_frames_wait(self):
        code, out = run("check", self.log, "--close")
        self.assertEqual(code, 1)
        self.assertIn("pending", out)


class Numbers(unittest.TestCase):
    def test_what_counts_as_a_number(self):
        text = "In 2026 we ran 3 ideas for 90 days; 38% converted, USD 1,761 per unit and 56.78 back. Six weeks."
        self.assertEqual(wl.number_tokens(text), ["38%", "1,761", "56.78"])

    def test_spanish_durations_are_decisions(self):
        self.assertEqual(wl.number_tokens("En 90 días sube de 40% a 55 %"), ["40%", "55%"])

    def test_clock_times_and_seconds_are_not_figures(self):
        self.assertEqual(wl.number_tokens("Quoted at 08:55 and 15:10, refreshed every 15 seconds, fee 3.2%"), ["3.2%"])


class DraftMode(unittest.TestCase):
    """Before the workshop, `check --draft` has to look at the AI's own draft of every frame."""

    def setUp(self):
        self.log = wl.load(EXAMPLE)
        for fr in self.log["frames"]:  # back to the state before the person saw anything
            fr.update({"opened_at": None, "answer": None, "outcome": None, "change": None, "final": None, "decided_at": None})

    def test_plain_check_says_nothing_about_undecided_frames(self):
        self.log["frames"][6]["draft"]["fields"]["hypothesis"]["baseline"] = ""
        self.assertEqual(wl.run_checks(self.log), [])

    def test_draft_check_catches_it(self):
        self.log["frames"][6]["draft"]["fields"]["hypothesis"]["baseline"] = ""
        codes = [(c, f) for c, f, _ in wl.run_checks(self.log, draft=True)]
        self.assertIn(("hypothesis", "6"), codes)

    def test_draft_check_catches_an_unregistered_number(self):
        self.log["frames"][4]["draft"]["fields"]["ranking_criterion"] = "It hits 72% of commuters"
        codes = [(c, f) for c, f, _ in wl.run_checks(self.log, draft=True)]
        self.assertIn(("number", "4"), codes)

    def test_draft_check_wants_every_frame_drafted_with_its_question(self):
        self.log["frames"][3]["draft"] = None
        self.log["frames"][5]["draft"]["question"] = "Three ideas."
        codes = [(c, f) for c, f, _ in wl.run_checks(self.log, draft=True)]
        self.assertIn(("draft", "3"), codes)
        self.assertIn(("draft", "5"), codes)

    def test_the_first_draft_of_the_example_has_one_real_gap(self):
        # The AI's draft picked a customer with no sized reason; the person fixed it in the workshop.
        self.assertEqual([(c, f) for c, f, _ in wl.run_checks(self.log, draft=True)], [("anecdote", "2")])


class Example(unittest.TestCase):
    def setUp(self):
        self.log = wl.load(EXAMPLE)

    def test_the_invented_example_passes_every_check(self):
        self.assertEqual(wl.run_checks(self.log, close=True), [])

    def test_it_counts_four_changed_decisions(self):
        self.assertEqual([f["id"] for f in wl.changed_frames(self.log)], ["1", "2", "5", "6"])

    def test_summary_is_a_table(self):
        code, out = run("summary", EXAMPLE)
        self.assertEqual(code, 0)
        self.assertIn("4 of 8 decisions changed", out)
        self.assertIn("| 6. Choose, hypothesis and metrics |", out)

    def test_a_solution_in_the_goal_is_caught(self):
        self.log["frames"][1]["final"]["business_goal"] = "Ship the open-slot calendar"
        codes = [c for c, _, _ in wl.run_checks(self.log)]
        self.assertIn("early_solution", codes)

    def test_an_unregistered_number_is_caught(self):
        self.log["frames"][4]["final"]["ranking_criterion"] = "It hits 72% of commuters"
        problems = wl.run_checks(self.log)
        self.assertIn(("number", "4", "72% is on the board with no source and no assumption mark"), problems)

    def test_opening_out_of_order_is_caught(self):
        self.log["frames"][3]["opened_at"] = "2026-01-12T10:10:00"
        codes = [(c, f) for c, f, _ in wl.run_checks(self.log)]
        self.assertIn(("order", "3"), codes)

    def test_a_frame_sent_as_text_to_approve_is_caught(self):
        self.log["frames"][2]["draft"]["question"] = "Here is the customer."
        codes = [(c, f) for c, f, _ in wl.run_checks(self.log)]
        self.assertIn(("closed_text", "2"), codes)

    def test_a_two_sentence_summary_is_caught(self):
        self.log["frames"][7]["final"]["one_sentence_summary"] = "Show open slots. Then count bookings."
        codes = [(c, f) for c, f, _ in wl.run_checks(self.log)]
        self.assertIn(("structure", "7"), codes)


class Board(unittest.TestCase):
    """board_svg.py has to produce well-formed SVG with one frame per frame of the method."""

    def parse(self, svg):
        import xml.dom.minidom
        return xml.dom.minidom.parseString(svg.encode("utf-8"))

    def frames(self, svg):
        return [g.getAttribute("data-frame") for g in self.parse(svg).getElementsByTagName("g")]

    def test_the_template_has_ten_design_frames_and_three_diagnosis_frames(self):
        import board_svg
        titles = self.frames(board_svg.template("both", "en"))
        self.assertEqual(len(titles), 13)
        self.assertEqual([t.split(" ")[0] for t in titles], ["0", "1", "2", "3", "4", "5", "6", "7", "A", "E", "D1", "D2", "D3"])

    def test_every_field_the_checks_ask_for_has_a_box(self):
        import board_svg
        boxes = {spec[0]: [name for b in spec[5] for name in b[0].split("+")] for spec in board_svg.DESIGN + board_svg.DIAGNOSIS}
        for fid, fields in {"1": ["business_goal", "user_problem", "metric"], "2": ["segments", "chosen", "chosen_why"],
                            "4": ["failures", "ranking_criterion"], "6": ["chosen_idea", "hypothesis", "metrics", "cheap_test", "weak_spot"],
                            "7": ["company_strategy_fit", "one_sentence_summary"], "D2": ["cuts", "cause_hypothesis"]}.items():
            for field in fields:
                self.assertIn(field, boxes[fid])

    def test_a_filled_board_carries_the_decisions_and_survives_an_ampersand(self):
        import board_svg
        log = wl.load(EXAMPLE)
        log["frames"][1]["final"]["business_goal"] = "Riders & shops <both> win"
        svg = board_svg.from_log(log, "en")
        self.assertEqual(len(self.frames(svg)), 10)
        contents = [r.getAttribute("data-content") for r in self.parse(svg).getElementsByTagName("rect")]
        # After XML parsing the box body is HTML: the label keeps its tags, the person's text is escaped.
        self.assertTrue(any("<b>Business goal</b><br>Riders &amp; shops &lt;both&gt; win" in c for c in contents))
        self.assertIn("Changed", contents)
        self.assertTrue(any("Daily commuter" in c for c in contents))


class SecondExample(unittest.TestCase):
    """The exercise on a real product. Its draft follows a public walkthrough; the review is a reconstruction."""

    PATH = os.path.join(HERE, "examples", "chrome-workshop-log.json")

    def test_it_passes_every_check(self):
        self.assertEqual(wl.run_checks(wl.load(self.PATH), close=True), [])

    def test_it_says_where_it_comes_from(self):
        case = wl.load(self.PATH)["case"]
        self.assertIn("youtube.com/watch", case)
        self.assertIn("reconstruction", case)

    def test_two_examples_two_colors(self):
        import board_svg
        blue = board_svg.from_log(wl.load(EXAMPLE), "en")
        purple = board_svg.from_log(wl.load(self.PATH), "en", family="purple")
        self.assertIn("#f0f5fd", blue)
        self.assertNotIn("#f4f2fd", blue)
        self.assertIn("#f4f2fd", purple)
        self.assertNotIn("#f0f5fd", purple)


class Source(unittest.TestCase):
    def test_the_tool_only_touches_the_log(self):
        with open(os.path.join(HERE, "workshop_log.py"), encoding="utf-8") as f:
            src = f.read()
        for banned in ("import subprocess", "import urllib", "import requests", "import socket", "os.remove", "shutil"):
            self.assertNotIn(banned, src)

    def test_no_em_dashes(self):
        for name in ("workshop_log.py", "SKILL.md", "TEMPLATE.md"):
            path = os.path.join(HERE, name)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    self.assertNotIn(chr(0x2014), f.read(), name)


if __name__ == "__main__":
    unittest.main()
