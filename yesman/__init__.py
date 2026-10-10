"""yesman - the voice, portable.

Two registers of one character: the structured one that carries a list in its shape, and the gushing
one that praises first and confesses second. Plus the mechanics that keep a spoken line speakable -
a word budget that ignores tags, markdown that a voice would otherwise read out, and a sentinel for
"nothing to say".

The character is the part worth having; everything else here is the small print that stops it
producing something you would not want read aloud. Nothing in this package knows about a model, a
provider or a network.

    import yesman

    system = yesman.prompt("gush")          # the whole system prompt for one register
    system = yesman.prompt("gush", name="Ada", hands="a build server is your hands")
    yesman.rules("gush")                    # just the rules that outrank the voice

    yesman.spoken(reply)                    # what to hand an engine: tags kept, markdown gone
    yesman.words(reply)                     # what will actually be heard
    yesman.is_nothing(reply)                # drop the line instead of speaking it
"""

from __future__ import annotations

from . import lines, style, tags, voices

__all__ = [
    "lines", "style", "tags", "voices",
    "NOTHING", "prompt", "register", "rules", "voice",
    "is_nothing", "normalise", "spoken", "words",
]

__version__ = "0.1.0"

#: The exact line a register replies with when there is nothing to say. Drop it; do not speak it.
NOTHING = lines.NOTHING


def register(register: str | None = None, *, path=None) -> str:
    """Which register is in force: the argument, then the file, then the environment, then default."""
    return style.active(register, path=path)


def voice(register: str | None = None, **kwargs) -> str:
    """The in-character half of the system prompt."""
    return voices.voice(style.active(register), **kwargs)


def rules(register: str | None = None) -> str:
    """The out-of-character half. Worth sending again late in a long context."""
    return voices.rules(style.active(register))


def prompt(register: str | None = None, **kwargs) -> str:
    """Voice then rules - the whole system prompt for one register."""
    return voices.prompt(style.active(register), **kwargs)


def spoken(text: str) -> str:
    """The form to hand an engine: known tags normalised, unknown brackets intact, markdown gone."""
    return lines.spoken(text)


def words(text: str) -> int:
    """How many words will actually be heard - tags are performed, so they do not count."""
    return lines.words(text)


def is_nothing(text: str) -> bool:
    """Is this the "nothing to say" sentinel? Tolerant of case, spacing and a stray full stop."""
    return lines.is_nothing(text)


def normalise(text: str) -> str:
    """Normalise known tag case; leave every other bracket exactly as written."""
    return tags.normalise(text)
