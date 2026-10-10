"""Line rules: what a spoken line may contain, and what will actually be heard.

Everything here exists because the output is read aloud by a machine. Two of these rules are less
obvious than they look:

**A tag is not a word.** `[emphasis]` is performed, not spoken, so it must not count against a word
budget. `[sad] Oh, WOW, that is [emphasis] sooooo sorry!` is five spoken words, not eight - and a
counter that says eight will make the voice terser than the register asks for. So `words()` counts
the *spoken* form, with brackets removed.

**Removing a bracket is fine for counting and wrong for sending.** `strip_tags()` exists for
measurement only. What you hand to an engine is `tags.normalise()`, which keeps every bracket on -
because an unwrapped direction becomes words, and words get read out (measured: +1.25 s of audio for
one unwrapped phrase). The two functions look similar and are not interchangeable; that is exactly
why they are both here, named for what they do.

And the sentinel: a line that is not a finished result must be recognisable as *nothing to say*, so
it can be dropped instead of spoken. A voice layer that reads "Nothing to report." aloud has turned a
silence into an interruption.
"""

from __future__ import annotations

import re

from . import tags

#: The exact line a register replies with when the input is not a finished result.
NOTHING = "Nothing to report."

#: How a refusal sounds. The wording is the point: apologetic, never reluctant. A voice that sounds
#: put-upon about saying no has made the refusal about itself.
REFUSAL_STYLE = "A refusal is apologetic, never reluctant to refuse."

#: Default spoken-word budget for one line, when a register does not say otherwise.
DEFAULT_WORDS = 25

#: The shapes the prompts forbid, because a voice reads them out: `**bold**` becomes a pause or the
#: word "asterisk", `#` becomes "hash", a leading dash becomes "dash".
_MARKDOWN = re.compile(r"[`*_#]|\]\(|^\s*[-•]\s+", re.M)


def strip_tags(text: str) -> str:
    """Remove brackets entirely. For *counting* only - never send this to an engine.

    Sending this is the dangerous operation: an unwrapped direction becomes plain words, and plain
    words are read aloud. See `tags.normalise` for what to send.
    """
    return " ".join(tags.BRACKET.sub(" ", text or "").split())


def words(text: str) -> int:
    """How many words will actually be heard. Tags are performed, so they do not count."""
    return len(strip_tags(text).split())


def fits(text: str, limit: int = DEFAULT_WORDS) -> bool:
    """Is the line inside its budget, counting only what is spoken?"""
    return words(text) <= limit


def has_markdown(text: str) -> bool:
    """Does the line contain anything a voice would read out as punctuation?"""
    return bool(_MARKDOWN.search(text or ""))


def spoken(text: str) -> str:
    """The form to hand an engine: tags kept, markdown gone, whitespace collapsed.

    Tags are normalised rather than removed - that is the whole invariant. Markdown is removed
    because it is *not* direction: there is no engine that performs an asterisk.
    """
    out = tags.normalise(text)
    out = re.sub(r"^\s*#{1,6}\s*", "", out, flags=re.M)
    out = re.sub(r"^\s*[-•]\s+", "", out, flags=re.M)
    out = out.replace("`", "").replace("*", "").replace("_", " ")
    return " ".join(out.split())


def is_nothing(text: str) -> bool:
    """Is this the "nothing to say" sentinel? Tolerant of case, spacing and a stray full stop.

    Tolerant on purpose: the model is told to reply with an exact string, and it will sometimes reply
    with a nearly-exact one. Treating `nothing to report` as a real line means speaking it aloud,
    which is the failure this exists to prevent.
    """
    body = " ".join((text or "").split()).strip().lower()
    return body.rstrip(".!") == NOTHING.rstrip(".!").lower()
