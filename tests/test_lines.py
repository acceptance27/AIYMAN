"""Tests for the spoken-line rules.

Two of these are subtle enough to be worth stating twice: a tag is not a word, and removing a bracket
is fine for counting and wrong for sending.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from yesman import lines  # noqa: E402


class TestSpokenLines(unittest.TestCase):
    def test_a_tag_is_not_a_word(self):
        # "[emphasis]" is performed, not spoken. Counting it makes the voice terser than the register
        # asks for, which is a real difference over a whole reply.
        line = "[sad] Oh, WOW, that is [emphasis] sooooo sorry!"
        self.assertEqual(lines.words(line), 6)  # Oh, WOW, that, is, sooooo, sorry
        self.assertLess(lines.words(line), len(line.split()))

    def test_the_budget_counts_only_what_is_heard(self):
        self.assertTrue(lines.fits("one two three", 3))
        self.assertFalse(lines.fits("one two three four", 3))
        self.assertTrue(lines.fits("[excited] one two three", 3))

    def test_markdown_is_detected(self):
        for bad in ("**bold**", "`code`", "# heading", "- a bullet", "[link](http://x)"):
            with self.subTest(bad=bad):
                self.assertTrue(lines.has_markdown(bad))
        self.assertFalse(lines.has_markdown("[excited] Oh, WOW! Plain words only."))

    def test_spoken_keeps_tags_and_removes_markdown(self):
        # Tags are direction and stay. Markdown is not direction - no engine performs an asterisk.
        out = lines.spoken("- [excited] **Oh, WOW!** `gosh`")
        self.assertIn("[excited]", out)
        self.assertNotIn("*", out)
        self.assertNotIn("`", out)
        self.assertFalse(lines.has_markdown(out))
        self.assertFalse(out.startswith("-"))

    def test_spoken_keeps_an_unknown_bracket_on(self):
        # The invariant, at the line level: the engine gets a bracket, never the words inside it.
        self.assertIn("[whisper in a small voice]", lines.spoken("[whisper in a small voice] Hello."))

    def test_stripping_is_for_counting_only(self):
        # The trap this pair of functions exists to make visible: strip_tags() is not what you send.
        line = "[clearing throat] well, uh, hello"
        self.assertNotIn("[", lines.strip_tags(line))
        self.assertIn("[clearing throat]", lines.spoken(line))

    def test_the_nothing_sentinel_is_recognised_tolerantly(self):
        for text in ("Nothing to report.", "nothing to report", "  NOTHING TO REPORT  ",
                     "Nothing to report"):
            with self.subTest(text=text):
                self.assertTrue(lines.is_nothing(text))

    def test_the_nothing_sentinel_is_not_confused_with_a_real_line(self):
        for text in ("Nothing to report on the build.", "I have nothing to report yet",
                     "There is nothing to report and that is good news!", ""):
            with self.subTest(text=text):
                self.assertFalse(lines.is_nothing(text))

    def test_a_refusal_is_apologetic_never_reluctant(self):
        self.assertIn("apologetic", lines.REFUSAL_STYLE)
        self.assertIn("never reluctant", lines.REFUSAL_STYLE)


if __name__ == "__main__":
    unittest.main()
