#!/usr/bin/env python3
"""Tests for prd_check.py. Run from this folder: python3 test_prd_check.py"""
import contextlib
import io
import os
import unittest

import prd_check as pc

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE = os.path.join(HERE, "examples", "bike-repair-prd.json")


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = pc.main(list(argv))
    return code, out.getvalue()


class Checks(unittest.TestCase):
    def setUp(self):
        self.prd = pc.load(EXAMPLE)

    def codes(self):
        return [c for c, _ in pc.run_checks(self.prd, EXAMPLE)]

    def said(self):
        return " | ".join(m for _, m in pc.run_checks(self.prd, EXAMPLE))

    def test_the_invented_example_passes(self):
        self.assertEqual(pc.run_checks(self.prd, EXAMPLE), [])

    def test_a_requirement_says_how_we_know_it_is_met(self):
        self.prd["requirements"][1]["acceptance"] = ""
        self.assertIn("requirement R2 does not say how we will know it is met", self.said())

    def test_a_requirement_that_answers_nothing_is_caught(self):
        self.prd["requirements"].append({"id": "R9", "priority": "P1", "text": "Dark mode.", "acceptance": "A switch exists."})
        self.assertIn("requirement R9 does not say which failure or goal it answers", self.said())

    def test_a_requirement_for_a_failure_the_board_does_not_have_is_caught(self):
        self.prd["requirements"][0]["answers"] = "failure:Slow checkout"
        self.assertIn("not on the board", self.said())

    def test_a_discarded_idea_does_not_come_back_alone(self):
        self.prd["requirements"].append({"id": "R9", "priority": "P2", "text": "Offer a loaner bike with every booking.",
                                         "acceptance": "A rider leaves the shop with a bike.",
                                         "answers": "failure:A day without the bike"})
        self.assertIn("discarded", self.codes())
        self.prd["requirements"][-1]["reopened_by"] = "Bring the loaner back for the two biggest shops."
        self.assertEqual(pc.run_checks(self.prd, EXAMPLE), [])

    def test_an_idea_from_the_board_cannot_vanish(self):
        self.prd["discarded"] = self.prd["discarded"][:-1]
        self.assertIn("'Office pickup' was on the board and is not among the discarded alternatives", self.said())

    def test_everything_left_out_has_a_reason(self):
        self.prd["out_of_scope"][0]["reason"] = ""
        self.prd["discarded"][0]["reason"] = " "
        codes = self.codes()
        self.assertIn("reason", codes)
        self.assertIn("discarded", codes)

    def test_a_new_number_is_caught_unless_it_has_a_source(self):
        self.prd["what_we_build"] += " It should cut calls by 70%."
        self.assertIn("70% is not on the board and has no named source", self.said())
        self.prd["sources"] = [{"value": "70%", "source": "Shop survey, spring"}]
        self.assertEqual(pc.run_checks(self.prd, EXAMPLE), [])

    def test_the_test_comes_first_and_complete(self):
        self.prd["test_first"]["decision_if_missed"] = ""
        self.assertIn("test_first", self.codes())

    def test_a_prd_needs_a_p0(self):
        for r in self.prd["requirements"]:
            r["priority"] = "P1"
        self.assertIn("no P0 requirement", self.said())

    def test_an_unknown_needs_its_open_question(self):
        self.prd["edge_cases"].append({"case": "The shop closes for a holiday", "behavior": "[TBD]"})
        self.prd["what_we_build"] += " Pricing for shops is [TBD]. Notifications are [TBD]."
        self.assertIn("open", self.codes())

    def test_em_dash_is_caught(self):
        self.prd["problem"] = "Riders " + chr(0x2014) + " and shops."
        self.assertIn("style", self.codes())


class Gate(unittest.TestCase):
    def setUp(self):
        self.prd = pc.load(EXAMPLE)

    def test_the_example_is_ready_with_its_open_questions_owned(self):
        code, out = run("gate", EXAMPLE)
        self.assertEqual(code, 0)
        self.assertIn("Ready for engineering, with 2 open questions", out)

    def test_not_ready_without_the_persons_answers(self):
        for key in pc.PERSON_SECTIONS:
            prd = pc.load(EXAMPLE)
            prd["person_answers"][key] = ""
            self.assertIn(("person", "'%s' has no answer from the person: that section is theirs to decide" % key),
                          pc.gate_problems(prd, EXAMPLE))

    def test_a_draft_may_leave_the_decision_open_but_it_is_not_ready(self):
        self.prd["test_first"]["decision_if_missed"] = "[TBD]"
        self.prd["open_questions"].append({"question": "What do we decide if we miss the threshold?", "owner": "Product",
                                           "due": "Before the pilot", "status": "open"})
        self.assertEqual(pc.run_checks(self.prd, EXAMPLE), [])
        self.assertIn("test_first", [c for c, _ in pc.gate_problems(self.prd, EXAMPLE)])

    def test_not_ready_with_an_open_question_nobody_owns(self):
        self.prd["open_questions"][0]["owner"] = ""
        self.assertIn("open", [c for c, _ in pc.gate_problems(self.prd, EXAMPLE)])
        self.prd["open_questions"][0]["status"] = "closed"
        self.assertEqual(pc.gate_problems(self.prd, EXAMPLE), [])


class Render(unittest.TestCase):
    def test_the_view_starts_from_the_test(self):
        code, out = run("render", EXAMPLE)
        self.assertEqual(code, 0)
        self.assertIn("**Status:** ready for engineering. 2 open questions.", out)
        self.assertLess(out.index("## The test that comes first"), out.index("## Requirements"))
        self.assertIn("| R1 | P0 |", out)
        self.assertIn("| Done when |", out)
        self.assertIn("| Loaner bike |", out)
        self.assertNotIn(chr(0x2014), out)


class Source(unittest.TestCase):
    def test_the_tool_only_reads_and_prints(self):
        with open(os.path.join(HERE, "prd_check.py"), encoding="utf-8") as f:
            src = f.read()
        for banned in ("import subprocess", "import urllib", "import requests", "import socket", "smtplib", "open(args.prd, \"w\""):
            self.assertNotIn(banned, src)

    def test_no_em_dashes_in_the_skill(self):
        path = os.path.join(HERE, "SKILL.md")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
