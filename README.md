# yesman

The voice, portable. Two registers of one character — Yes Man from *Fallout: New Vegas* — plus the
small print that keeps a spoken line speakable.

Nothing here knows about a model, a provider or a network. This is the text and the rules; bring your
own way of asking.

```python
import yesman

system = yesman.prompt("gush")      # the whole system prompt for one register
system = yesman.prompt("gush", name="Ada", hands="a build server is your hands")

yesman.rules("gush")                # just the rules that outrank the voice

yesman.spoken(reply)                # what to hand an engine: tags kept, markdown gone
yesman.words(reply)                 # what will actually be heard
yesman.is_nothing(reply)            # drop the line instead of speaking it
```

## The interesting part is not the enthusiasm

Yes Man is relentlessly cheerful, endlessly accommodating, delighted to be useful — and, in the
fiction, a catastrophic yes-man who cannot say no and cheerfully helps you do terrible things.

So the character prompt here is not just a mood. **Every register carries a block of rules that
explicitly outrank the voice**, and that block is the part worth keeping:

- **Never invent detail, and never cheer for work that failed.** Cheerful delivery, straight facts.
- **Never make the damage sound smaller than it is.** Comfort may only be a fact that is in the
  input — *"it was only test data"* is a distortion, not a comfort.
- **You never approve, decide, promise or grant anything.** Yes Man's one great flaw is that he cannot
  say no, and that flaw is deliberately not inherited.
- **If the input is not a finished result, reply with exactly `Nothing to report.`**

A cheerful voice with no such block will dress up a failure as a success, invent detail to keep the
mood up, and agree to things it cannot do. The enthusiasm is only safe because it is bounded, and the
bounds are written down in the same prompt that produces the enthusiasm.

## Two registers

| | | |
|---|---|---|
| `gush` | default | Babbling, self-interrupting, confess-then-ask. Praise first, stutter at the awkward part, sweep bad news under the rug *while still saying plainly what it is*, close by asking what grand step comes next. Five or six sentences. |
| `report` | | Structure spoken aloud. The listener has no list in front of them, so the *shape* carries the information — "Three big fixes: first… second… third…". Four sentences. |

`gush`, on bad news:

> `[sad]` Oh, boy, well, that is one hundred percent my fault and I am `[emphasis]` sooooo sorry! See,
> the refactor went in and, uh… the build is red now — three tests in the queue tests are erroring out
> with an AttributeError! `[soft]` Gosh, nothing was deployed, so that's the good part…
> `[laughing]` Ha-ha! So, are we ready to go fix those tests?!

The facts are all there, in order, and the mood is doing none of the lying. That is the whole trick,
and it is why the worked examples ship inside the prompt: they are the target, not decoration.

Pick a register per call, or leave it in a file so it can be changed without a restart:

```bash
echo gush > ~/.yesman/style.txt      # or YESMAN_STYLE=gush, or pass it as an argument
```

## Direction tags: a bracket is a channel, not a word

A tag like `[sad]` or `[emphasis]` is **performed by the voice engine, not spoken**. The vocabulary is
open: anything you can describe in a few words — `[whisper in a small voice]`, `[clearing throat]`,
`[professional broadcast tone]` — is as real as the short ones.

Measured on a real engine, one sentence at a time, plain against tagged (a ~0.2 s noise band, so
anything inside that is not a claim):

| tag | effect | | tag | effect |
|---|---|---|---|---|
| `[giggle]` | +1.79 s | | `[chuckle]` | +1.14 s |
| `[giggling]` | +1.79 s | | `[gasping]` | +0.72 s |
| `[pause]` | +0.47 s | | `[sighing]` | +0.35 s |
| `[whisper in a small voice]` | 23% quieter, 22% lower | | `[pitch up]` | 25% louder |

`[giggle]` and `[giggling]` moved by *identical* amounts — that is a sound being inserted, not a word
being spoken, since "giggle" as a word is about 0.5 s of syllables, not 1.8 s.

**Duration cannot judge an emotion**, because an emotion changes timbre rather than length. Duration
alone called `[whisper in a small voice]` "ignored", which is how a whitelist of phrases once came to
exist — and why it is gone.

**Unwrapping a bracket is the dangerous operation.** `[forced optimism]` sent as a bracket changed
nothing measurable (3.16 s against a 2.93 s plain line) and was never spoken; the same words
*unwrapped* were read aloud (4.18 s, +1.25 s). So:

- a known tag is lower-cased, so `[SAD]` cannot miss the engine's vocabulary;
- **every other bracket travels intact** — the engine either performs it or ignores it;
- known means *case-normalised*, **never** *allowed*.

`yesman.normalise()` does exactly that and nothing else. `yesman.spoken()` adds the markdown strip,
because markdown is *not* direction — no engine performs an asterisk.

## The small print that keeps a line speakable

- **A tag is not a word.** `[sad] Oh, WOW, that is [emphasis] sooooo sorry!` is six spoken words, not
  nine. `words()` counts what will be *heard*, so a budget does not make the voice terser than the
  register asks for.
- **`strip_tags()` is for counting only.** It looks like `normalise()` and is not interchangeable —
  sending the stripped form is the dangerous operation described above. Both live in `lines.py`,
  named for what they do, precisely so the difference is visible.
- **The sentinel is recognised tolerantly.** The model is told to reply with an exact string and will
  sometimes reply with a nearly-exact one; `is_nothing()` accepts `nothing to report`, with or without
  a full stop. A voice layer that reads "Nothing to report." aloud has turned a silence into an
  interruption.
- **A refusal is apologetic, never reluctant.** A voice that sounds put-upon about saying no has made
  the refusal about itself.

## What is deliberately not here

No model, no provider, no API key, no HTTP, no deadlines, no retries, no streaming. Those are the
things that differ per setup, and mixing them in is how a character file turns into a framework. This
package is the character and the line rules — pure text in, pure text out, stdlib only.

## What changed from the original

Extracted from a larger voice layer, where the character was wired to a specific assistant. Every edit
is a substitution, not a rewrite:

- `You are QWEEPS` → `You are {name}` (default `Yes Man`).
- `a coding agent is your hands` → `{hands}`, same default, so the clause can describe whatever is
  actually doing the work. The point of the clause is unchanged: never disown work you were
  responsible for, and never say "the agent" as though it were somebody else.
- `QWEEPS's refusals and approvals are decided elsewhere` → `approvals and refusals are decided
  elsewhere`.

One known wart, kept on purpose: the `gush` worked example uses `*tiny*` for emphasis, which its own
rule 4 forbids in output. The wording is the target, so it stays; `spoken()` removes the asterisks on
the way to the engine, which is where it actually matters.

## Tests

```bash
python -m unittest discover -s tests
```

37 tests, stdlib only. They pin the things that cost real time to find: that a `style.txt` written with
a byte-order mark still names its register (PowerShell and Notepad both write one, and read as plain
`utf-8` it silently matches nothing); that an invented tag survives untouched; that a tag does not
count as a word; and that every register carries rules which outrank its voice and arrive last in the
prompt.

## Credit

Yes Man is a character from *Fallout: New Vegas*, © Bethesda Softworks. This repository contains no
game assets — only prompt text written in homage to a very good performance.
