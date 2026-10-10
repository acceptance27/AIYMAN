"""Tests for the register selection - including the bug that cost real debugging time.

The BOM test is the point of this file. A style file written by PowerShell's
`Set-Content -Encoding UTF8` or by Notepad starts with a byte-order mark; read as plain `utf-8` it
arrives as `\\ufeffgush`, matches no register, and the character silently stays on the default. Read as
`utf-8-sig` it works. Nothing anywhere reports the difference, which is why it is pinned here.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yesman  # noqa: E402
from yesman import style, voices  # noqa: E402


class TestChoosingARegister(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.addCleanup(self.home.cleanup)
        self.path = Path(self.home.name) / style.STYLE_FILE

    def test_a_plain_file_names_the_register(self):
        self.path.write_text("gush", encoding="utf-8")
        self.assertEqual(style.from_file(self.path), "gush")

    def test_a_file_written_with_a_bom_still_names_the_register(self):
        # PowerShell's Set-Content -Encoding UTF8 and Notepad both do this. Read as plain utf-8 the
        # value is "\ufeffgush", which matches nothing, and the register silently stays on the default.
        self.path.write_text("report", encoding="utf-8-sig")
        self.assertEqual(self.path.read_bytes()[:3], b"\xef\xbb\xbf")
        self.assertEqual(style.from_file(self.path), "report")

    def test_a_typo_falls_through_instead_of_raising(self):
        self.path.write_text("gussh", encoding="utf-8")
        self.assertEqual(style.from_file(self.path), "")
        self.assertEqual(style.active(path=self.path), voices.DEFAULT_REGISTER)

    def test_the_argument_beats_the_file_and_the_file_beats_the_environment(self):
        self.path.write_text("gush", encoding="utf-8")
        with mock.patch.dict("os.environ", {style.STYLE_ENV: "report"}):
            self.assertEqual(style.active("report", path=self.path), "report")
            self.assertEqual(style.active(path=self.path), "gush")
            self.path.unlink()
            self.assertEqual(style.active(path=self.path), "report")

    def test_a_missing_file_is_not_an_error(self):
        self.assertEqual(style.from_file(self.path), "")
        self.assertEqual(style.active(path=self.path), voices.DEFAULT_REGISTER)

    def test_the_config_directory_can_be_moved(self):
        with mock.patch.dict("os.environ", {"YESMAN_HOME": self.home.name}):
            self.assertEqual(style.config_dir(), Path(self.home.name))
        self.assertEqual(style.config_dir().name, ".yesman")

    def test_the_package_level_call_agrees_with_the_module(self):
        self.path.write_text("report", encoding="utf-8")
        with mock.patch.object(style, "config_dir", return_value=Path(self.home.name)):
            self.assertEqual(yesman.register(), "report")


if __name__ == "__main__":
    unittest.main()
