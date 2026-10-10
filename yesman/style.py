"""Choosing a register: a file you can edit while the thing is still running.

The register is read from a file rather than fixed in code so it can be changed without a restart,
and so the wording of the character is never buried somewhere you have to go looking for it.

One lesson is baked into the reading, and it cost real debugging time: **read the file as
`utf-8-sig`.** PowerShell's `Set-Content -Encoding UTF8` and Notepad both write a byte-order mark,
plain `utf-8` keeps it, and `strip()` does not remove it. So a file containing `gush` arrives as
`\ufeffgush`, matches no register, and the character silently stays on the default. Silently is the
whole problem: nothing anywhere says a word about it.
"""

from __future__ import annotations

import os
from pathlib import Path

from . import voices

#: Where the register is written down, inside the config directory.
STYLE_FILE = "style.txt"

#: An environment override, for when a file is inconvenient.
STYLE_ENV = "YESMAN_STYLE"


def config_dir() -> Path:
    """Where settings live. Override with ``YESMAN_HOME``."""
    override = (os.environ.get("YESMAN_HOME") or "").strip()
    return Path(override) if override else Path.home() / ".yesman"


def from_file(path: Path | None = None) -> str:
    """The register named in the file, or "" - including when the file says something impossible.

    A name that is not a register falls through rather than raising. A typo should not break the
    voice; it should just not take effect.
    """
    target = Path(path) if path else config_dir() / STYLE_FILE
    try:
        # utf-8-sig: see the module docstring. A BOM here is invisible and matches nothing.
        chosen = target.read_text(encoding="utf-8-sig").strip().lower()
    except OSError:
        return ""
    return chosen if chosen in voices.REGISTERS else ""


def active(register: str | None = None, *, path: Path | None = None) -> str:
    """Which register to use: the argument, then the file, then the environment, then the default."""
    if register in voices.REGISTERS:
        return register
    chosen = from_file(path)
    if chosen:
        return chosen
    chosen = (os.environ.get(STYLE_ENV) or "").strip().lower()
    if chosen in voices.REGISTERS:
        return chosen
    return voices.DEFAULT_REGISTER
