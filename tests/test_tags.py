"""Tests for the direction-tag rule, which is one rule and has to stay that way.

The invariant: a known tag is lower-cased, and **every other bracket travels intact**. There is
deliberately no vocabulary constraint, because unwrapping a bracket is the dangerous operation - the
same words sent unwrapped were read aloud (+1.25 s of audio), while sent as a bracket they were never
spoken. So the test that matters most here is the one asserting that an invented tag survives.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from yesman import tags  # noqa: E402


class TestDirectionTags(unittest.TestCase):
    def test_a_known_tag_is_lower_cased(self):
        self.assertEqual(tags.normalise("[SAD] I could not."), "[sad] I could not.")
        self.assertEqual(tags.normalise("[EMPHASIS] yes"), "[emphasis] yes")

    def test_a_free_form_bracket_is_kept_exactly(self):
        # The measurement that deleted the whitelist: this is obeyed by the engine, and unwrapping it
        # would make it words instead of direction.
        line = "[whisper in a small voice] I have something to say."
        self.assertEqual(tags.normalise(line), line)

    def test_an_invented_tag_survives_untouched(self):
        # There is no vocabulary constraint, and this is what that means: the engine performs it or
        # ignores it, and either way it is never spoken.
        for invented in ("[eager]", "[flibbertigibbet]", "[forced optimism]"):
            with self.subTest(invented=invented):
                self.assertIn(invented, tags.normalise(f"{invented} Hello."))

    def test_an_unclosed_or_overlong_bracket_is_left_alone(self):
        # `[` with no `]` is not a tag; it is just a character, and rewriting it would be a guess.
        self.assertEqual(tags.normalise("costs [10"), "costs [10")
        long_one = "[" + "x" * 80 + "]"
        self.assertIn(long_one, tags.normalise(long_one))

    def test_normalising_twice_changes_nothing(self):
        line = "[EXCITED] Oh, WOW! [whisper in a small voice] Gosh."
        once = tags.normalise(line)
        self.assertEqual(tags.normalise(once), once)

    def test_the_measured_and_documented_sets_do_not_overlap_by_accident(self):
        self.assertTrue(tags.MEASURED)
        self.assertTrue(tags.DOCUMENTED)
        self.assertEqual(tags.KNOWN, tags.MEASURED | tags.DOCUMENTED)
        # "emphasis" is the one the prompts lean on hardest, so it must be in the measured set.
        self.assertIn("emphasis", tags.MEASURED)

    def test_tags_in_lists_what_is_there(self):
        self.assertEqual(tags.tags_in("[sad] oh no [soft] gosh"), ["sad", "soft"])
        self.assertEqual(tags.tags_in("no tags here"), [])

    def test_no_tag_vocabulary_is_enforced_anywhere(self):
        # A guard against this module growing a whitelist again: the only thing that ever rejects a
        # bracket is the length limit in the pattern, and that is about parsing, not permission.
        source = (Path(__file__).resolve().parent.parent / "yesman" / "tags.py").read_text(
            encoding="utf-8")
        self.assertNotIn("if lowered not in", source)
        self.assertIn("known means *case-normalised*, never *allowed*", source)


if __name__ == "__main__":
    unittest.main()
