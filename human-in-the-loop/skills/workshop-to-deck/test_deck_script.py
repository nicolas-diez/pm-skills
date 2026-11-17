#!/usr/bin/env python3
"""Tests for deck_script.py. Run from this folder: python3 test_deck_script.py"""
import contextlib
import copy
import io
import json
import os
import shutil
import tempfile
import unittest

import deck_script as ds

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE = os.path.join(HERE, "examples", "bike-repair-deck-script.json")


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ds.main(list(argv))
    return code, out.getvalue()


class Checks(unittest.TestCase):
    def setUp(self):
        self.deck = ds.load(EXAMPLE)

    def codes(self, deck):
        return [(c, n) for c, n, _ in ds.run_checks(deck, EXAMPLE)]

    def test_the_invented_example_passes(self):
        self.assertEqual(ds.run_checks(self.deck, EXAMPLE), [])

    def test_a_brief_point_with_no_slide_is_caught(self):
        self.deck["brief"].append({"id": "B4", "asks": "What does it cost?"})
        self.assertIn(("brief", "-"), self.codes(self.deck))

    def test_a_label_title_is_caught(self):
        self.deck["slides"][0]["title"] = "The problem"
        self.assertIn(("title", "1"), self.codes(self.deck))

    def test_a_number_without_trace_is_caught(self):
        self.deck["slides"][2]["body"] += " It happens to 72% of riders."
        self.assertIn(("trace", "3"), self.codes(self.deck))

    def test_a_number_the_log_does_not_have_is_caught(self):
        s = self.deck["slides"][1]
        s["body"] = s["body"].replace("60%", "65%")
        s["numbers"] = [{"value": "65%", "trace": "log:2"}]
        problems = ds.run_checks(self.deck, EXAMPLE)
        self.assertTrue(any(c == "trace" and "does not have it" in m for c, _, m in problems))

    def test_numbers_need_a_footer(self):
        self.deck["slides"][5]["footer_sources"] = []
        self.assertIn(("footer", "6"), self.codes(self.deck))

    def test_an_unchecked_image_is_caught(self):
        self.deck["slides"][2]["images"] = [{"file": "screen.png", "own": True}]
        self.assertIn(("image", "3"), self.codes(self.deck))

    def test_the_cap_holds(self):
        self.deck["max_slides"] = 6
        self.assertIn(("cap", "-"), self.codes(self.deck))

    def test_the_arc_keeps_its_order(self):
        self.deck["slides"][0]["arc"], self.deck["slides"][4]["arc"] = "choice", "goal"
        self.assertIn(("arc", "5"), self.codes(self.deck))

    def test_a_deck_without_measure_is_caught(self):
        self.deck["slides"][5]["arc"] = "other"
        self.assertIn(("arc", "-"), self.codes(self.deck))

    def test_it_closes_with_one_sentence(self):
        self.deck["closing_sentence"] = ""
        self.assertIn(("closing", "-"), self.codes(self.deck))
        self.deck["closing_sentence"] = "Show slots. Count bookings."
        self.assertIn(("closing", "-"), self.codes(self.deck))

    def test_em_dash_is_caught(self):
        self.deck["slides"][0]["body"] = "Shops pay " + chr(0x2014) + " when a repair gets booked."
        self.assertIn(("style", "1"), self.codes(self.deck))


class Gate(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "deck.json")
        deck = ds.load(EXAMPLE)
        deck["log"] = os.path.join(HERE, "..", "product-workshop", "examples", "bike-repair-workshop-log.json")
        self.base = deck
        self.write(deck)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, deck):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(deck, f)

    def test_gate_opens_when_all_is_approved(self):
        code, out = run("gate", self.path)
        self.assertEqual(code, 0)
        self.assertIn("Ask the person", out)

    def test_gate_stays_shut_with_an_unapproved_slide(self):
        deck = copy.deepcopy(self.base)
        deck["slides"][3]["approved"] = False
        self.write(deck)
        code, out = run("gate", self.path)
        self.assertEqual(code, 1)
        self.assertIn("Do not generate", out)

    def test_only_one_generation(self):
        self.assertEqual(run("record", self.path, "--id", "gen-1")[0], 0)
        self.assertEqual(run("record", self.path, "--id", "gen-2")[0], 1)
        code, out = run("gate", self.path)
        self.assertEqual(code, 1)
        self.assertIn("already generated", out)


class Source(unittest.TestCase):
    def test_the_tool_cannot_generate_or_send(self):
        with open(os.path.join(HERE, "deck_script.py"), encoding="utf-8") as f:
            src = f.read()
        for banned in ("import subprocess", "import urllib", "import requests", "import socket", "smtplib"):
            self.assertNotIn(banned, src)

    def test_no_em_dashes(self):
        for name in ("SKILL.md",):
            path = os.path.join(HERE, name)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    self.assertNotIn(chr(0x2014), f.read(), name)


if __name__ == "__main__":
    unittest.main()
