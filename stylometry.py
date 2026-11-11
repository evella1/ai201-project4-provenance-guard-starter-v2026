"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies. ← TODO

    Returns:
        A float. Decide yourself what scale it's on and which direction means
        "more human" — then write that down, because your combining rule
        depends on knowing it.

    A hint on what you're reaching for: the standard deviation of sentence
    lengths, probably divided by the mean so a long text and a short one are
    comparable. `statistics.stdev` is imported for you.

    Watch the edge case: a one-sentence submission has no spread at all, and
    `stdev` raises on fewer than two values. Decide what that should return
    before the attack set decides for you.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    # One sentence has no spread. Returns 0.0, but style_signal never uses it:
    # texts under 3 sentences get 0.5 ("can't tell") there.
    if len(lengths) < 2:
        return 0.0
    # Higher = more human. In testing: AI essay 0.26, edited AI 0.35, my plain
    # text 0.39, forum post 0.51. Fooled by AI told to "sound casual" (0.73).
    return statistics.stdev(lengths) / statistics.mean(lengths)


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words. ← TODO

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.

    Fix: average the ratio over 50-word windows.

    Direction: higher = more AI. I first assumed the opposite, but in testing
    all three AI texts scored higher (0.92, 0.92, 0.89) than both human texts
    (0.87, 0.80). AI picks a wide, polished vocabulary; people repeat plain
    words. It is the only measure that separated my plain text from the
    edited AI, but only by 0.05 — five samples is not much evidence.
    """
    ws = words(text)
    if not ws:
        return 0.0
    window = 50
    if len(ws) <= window:
        return len(set(ws)) / len(ws)
    ratios = [len(set(ws[i:i + window])) / window for i in range(len(ws) - window + 1)]
    return statistics.mean(ratios)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length. ← TODO

    Returns:
        A float. Whether you count all punctuation or only some kinds — commas,
        semicolons, dashes — is a real choice. Semicolons and em dashes are
        more interesting than full stops, because they vary more between
        writers.

    Measures variety only: how many different punctuation marks, out of 6.
    Returns 0–1, flipped so that higher = more AI (few kinds of marks).

    Why no comma count: I tried it, but a real human forum post had more
    commas (8.5 per 100 words) than an AI essay (about 5.5). Comma habits
    depend on the writer, not on whether it's AI. Same for dashes and
    semicolons, which were 0 in every sample.

    Why variety: the AI essay used 3 kinds of marks (. , -), the forum post
    used 6 (! " # ' , .).

    Weakness: plain human writing also uses few marks. My plain text scored
    0.50, the same as the AI essay. This only spots lively writing.
    """
    if not text.strip():
        return 0.0
    marks = set(re.findall(r"[^\w\s]", text))
    return 1 - min(len(marks) / 6, 1.0)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.

    My rule: put each measure on 0–1 (higher = more AI), then average them.
    The limits below come from my five calibration texts, so they fit those
    texts better than they will fit new ones. Re-check them on new samples.
    """
    # Too short to judge: answer "can't tell" instead of guessing.
    if len(sentences(text)) < 3 or len(words(text)) < 40:
        return 0.5

    # Even sentences = AI. 0.20 or less counts as fully AI, 0.60 or more as fully human.
    spread_part = _scale(sentence_length_spread(text), human=0.60, ai=0.20)
    # Wide, polished vocabulary = AI. 0.93 or more fully AI, 0.78 or less fully human.
    variety_part = _scale(type_token_ratio(text), human=0.78, ai=0.93)
    # Already 0–1 with higher = AI.
    punct_part = punctuation_density(text)

    # Equal weights: with only five test texts, I have no good reason to favour one.
    return (spread_part + variety_part + punct_part) / 3


def _scale(value: float, human: float, ai: float) -> float:
    """Map value onto 0–1: the `human` limit gives 0, the `ai` limit gives 1."""
    score = (value - human) / (ai - human)
    return max(0.0, min(1.0, score))


if __name__ == "__main__":
    import sys

    # Text can come from arguments, or piped in: $text | python stylometry.py
    # Piping keeps quote marks that PowerShell strips from arguments.
    piped = "" if sys.stdin.isatty() else sys.stdin.read().strip()
    text = " ".join(sys.argv[1:]) or piped or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
