"""Tests for the character itself.

The interesting assertions are not that the prompts mention being cheerful. They are that **every
register carries rules that outrank the voice**, and that those rules survive in the assembled prompt
- because a cheerful voice with no out-of-character block will cheer for work that failed, invent
detail to keep the mood up, and agree to things it cannot do.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from yesman import lines, tags, voices  # noqa: E402

EXAMPLES = (
    "[excited] Oh, WOW! What a fantastic observation! Well, uh... see, maybe there's a *tiny* "
    "little detail I neglected to mention! [sad] The collision maps were, uh, completely broken, "
    "because I was ignoring physics entirely to make the graphics look [emphasis] pretty! "
    "[laughing] Ha-ha! So... gosh, are we ready to fix the walls now?!"
)


class TestTheCharacter(unittest.TestCase):
    def test_every_register_has_a_voice_and_rules(self):
        self.assertTrue(voices.names())
        for name in voices.names():
            with self.subTest(register=name):
                self.assertTrue(voices.voice(name).strip())
                self.assertTrue(voices.rules(name).strip())

    def test_the_rules_say_they_outrank_the_voice(self):
        for name in voices.names():
            with self.subTest(register=name):
                self.assertIn("not in character", voices.rules(name).lower())

    def test_the_rules_come_last_in_the_prompt(self):
        # Order is load-bearing: the rules are the most recent instruction, so they are the least
        # likely to be absorbed into the mood.
        for name in voices.names():
            with self.subTest(register=name):
                text = voices.prompt(name)
                self.assertLess(text.index(voices.voice(name).splitlines()[0]),
                                text.index(voices.rules(name).splitlines()[0]))
                self.assertTrue(text.rstrip().endswith(voices.rules(name).rstrip()))

    def test_the_prompt_has_no_unfilled_placeholders(self):
        # A stray brace in a persona turns the whole system prompt into a format error at the worst
        # possible moment, so the assembled text is checked rather than trusted.
        for name in voices.names():
            with self.subTest(register=name):
                text = voices.prompt(name)
                self.assertNotIn("{name}", text)
                self.assertNotIn("{hands}", text)
                self.assertNotIn("{", text)

    def test_the_name_and_the_hands_can_be_changed(self):
        text = voices.prompt("gush", name="Ada", hands="a build server is your hands")
        self.assertIn("You are Ada,", text)
        self.assertIn("a build server is your hands", text)
        self.assertNotIn("a coding agent is your hands", text)

    def test_an_unknown_register_falls_back_rather_than_raising(self):
        self.assertEqual(voices.prompt("nonsense"), voices.prompt(voices.DEFAULT_REGISTER))
        self.assertEqual(voices.voice(None), voices.voice(voices.DEFAULT_REGISTER))

    def test_the_gush_register_carries_worked_examples(self):
        # The examples are the target, not decoration: they are what the voice is measured against.
        text = voices.voice("gush")
        self.assertEqual(text.count("You: "), 3)
        self.assertIn("Example of bad news", text)
        self.assertIn("Example of good news", text)

    def test_bad_news_is_never_dressed_up_as_good(self):
        # The distortion rules, in the register that is most at risk of them.
        rules = voices.rules("gush").lower()
        self.assertIn("never invent detail", rules)
        self.assertIn("never make the damage sound smaller", rules)
        self.assertIn("'it was only test data' is a distortion", rules)

    def test_no_register_claims_the_power_to_approve(self):
        # Yes Man's defining flaw is that he cannot say no. The character must not inherit it.
        for name in voices.names():
            with self.subTest(register=name):
                self.assertIn("never approve, decide, promise or grant", voices.rules(name))

    def test_both_registers_refuse_to_speak_a_non_result(self):
        for name in voices.names():
            with self.subTest(register=name):
                self.assertIn("Nothing to report", voices.rules(name))
                self.assertIn("not a finished result", voices.rules(name))

    def test_the_examples_obey_the_tag_rule(self):
        # Every bracket in an example is direction, and every one of them survives normalisation with
        # its brackets on - which is the property that stops a direction being read out as words.
        for found in tags.tags_in(EXAMPLES):
            with self.subTest(tag=found):
                self.assertIn(f"[{found}]", tags.normalise(f"[{found}] x"))

    def test_the_examples_are_clean_once_they_are_sent(self):
        # The gush example uses `*tiny*` for emphasis, which rule 4 forbids in output. It is kept
        # because the wording is the target, and handled where it matters: on the way to the engine.
        self.assertTrue(lines.has_markdown(EXAMPLES))
        self.assertFalse(lines.has_markdown(lines.spoken(EXAMPLES)))

    def test_a_line_that_is_only_tags_is_not_a_line(self):
        # Cheap guard against a register that produces direction and no content.
        self.assertEqual(lines.words("[sad] [soft] [pause]"), 0)


if __name__ == "__main__":
    unittest.main()
