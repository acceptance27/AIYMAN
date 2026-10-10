"""Direction tags: how the character is performed instead of spoken.

A bracket in the output is a *delivery* channel. The voice engine performs what it understands and
ignores what it does not - and in neither case does it read the bracket out. That is the whole
reason this module is short, and it is also the reason its one rule is what it is.

Measured on a real engine, one sentence at a time, plain against tagged (a ~0.2 s noise band, so
anything inside that is not a claim):

    [chuckle]  +1.14 s     [giggle]  +1.79 s    [giggling]  +1.79 s
    [gasping]  +0.72 s     [sighing] +0.35 s    [calm]      -0.46 s
    [pause]    +0.47 s     four tags on one line: +0.98 s

`[giggle]` and `[giggling]` moved by *identical* amounts, which is a sound being inserted rather
than a word being spoken - "giggle" as a word is about 0.5 s of syllables, not 1.8 s.

**Duration cannot judge an emotion.** Emotion changes timbre, not length, so loudness and a pitch
proxy are the instrument: `[whisper in a small voice]` came back 23% quieter and 22% lower,
`[pitch up]` 25% louder. Duration alone called those "ignored" - which is how a whitelist of phrases
came to exist, and why it is gone.

**Unwrapping a bracket is the dangerous operation.** `[forced optimism]` sent as a bracket changed
nothing measurable (3.16 s against a 2.93 s plain line) and was never spoken; the same words
unwrapped were read aloud (4.18 s, +1.25 s). So an unknown bracket travels intact, and the vocabulary
is open on purpose: known means *case-normalised*, never *allowed*.
"""

from __future__ import annotations

import re

#: Tags the engine was measured to perform on this voice.
MEASURED = frozenset({
    "angry", "sad", "embarrassed", "emphasis",
    "whispering", "soft", "breathy", "excited", "laughing",
    "pause",
    "chuckle", "giggle", "giggling", "gasping", "sighing", "calm",
})

#: The engine's documented vocabulary for these models, taken from its documentation rather than
#: measured here. Safe to accept either way: a tag that is performed is delivery, and a tag that is
#: ignored is dropped. Neither is ever spoken.
DOCUMENTED = frozenset({
    # basic emotions
    "happy", "nervous", "confident", "surprised", "satisfied", "delighted", "scared", "worried",
    "upset", "frustrated", "depressed", "empathetic", "disgusted", "moved", "proud", "relaxed",
    "grateful", "curious", "sarcastic",
    # further emotions, documented for an earlier model and accepted here
    "hopeful", "optimistic", "pessimistic", "determined", "resigned", "uncertain", "confused",
    "disappointed", "regretful", "guilty", "ashamed", "sympathetic", "compassionate", "nostalgic",
    "bored", "lonely", "anxious", "indifferent", "hysterical",
    # tone and sound markers
    "shouting", "screaming", "sobbing", "groaning", "panting", "yawning",
    "break", "long-break",
})

#: The vocabulary whose *case* is normalised, so `[SAD]` cannot miss the engine's own tags. It is
#: deliberately not a permission list: every other bracket travels intact.
KNOWN = MEASURED | DOCUMENTED

BRACKET = re.compile(r"\[([^\[\]]{0,60})\]")


def normalise(text: str) -> str:
    """Lower-case a known tag; leave every other bracket exactly as written.

    One rule, and it is the safe one. A known tag is lower-cased so `[SAD]` cannot miss the engine's
    vocabulary. Everything else in brackets - free-form direction like `[whisper in a small voice]`,
    or noise like `[INFO]` - passes through with its brackets *on*, because that is the form the
    engine treats as direction rather than as words to read out.

    Brackets are therefore a direction channel, and the prompts say so: nothing prose-shaped belongs
    in one. That is a far smaller cost than the alternative, which was speaking delivery
    instructions aloud.
    """
    def replace(match: re.Match) -> str:
        inner = " ".join(match.group(1).split())
        lowered = inner.lower()
        return f" [{lowered if lowered in KNOWN else inner}] "

    return " ".join(BRACKET.sub(replace, text or "").split())


def tags_in(text: str) -> list[str]:
    """Every bracketed span in a line, in order. Useful for checking a prompt's examples."""
    return [" ".join(item.split()) for item in BRACKET.findall(text or "")]
