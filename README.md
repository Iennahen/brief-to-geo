# brief-to-geo

This takes a single editorial brief and produces a fact-checked FAQ along with the
structured markup that lets search engines and language models quote it correctly. When
a claim turns out to have no source behind it, the pipeline stops the piece rather than
publishing it.

That last part is the reason I built it. Getting a model to write an FAQ takes very
little, and what I wanted was something that'd notice the sentences it made up
before any of them reached a page. Most of the prompt work I do is covered by NDA or
belongs to my employers, so I built this one from scratch on a topic I had no stake in,
using the structure I'd use in production: prompts kept as versioned files,
fact-checking as a gate rather than a review step, and every run leaving a record I can
go back through afterwards.

## How it works

```
brief.yaml  →  draft  →  split into claims  →  check each claim  →  gate  →  output
     |                                              |                 |
     |                                              |                 ├─ faq.md
     └── evidence pack ─────────────────────────────┘                 ├─ faq.jsonld
         (the only facts allowed)                                     └─ report.md
```

There are four scripts and they run one after another. `draft.py` reads the brief and
gets a set of answers back from Claude. `check.py` breaks those answers into individual
claims and checks each one against the sources. `gate.py` reads the results and decides
whether the piece can be published. `publish.py` writes the copy along with the markup
that tells a search engine which text is a question and which text is the answer to it.

## The brief and its sources

The brief holds the questions the piece has to answer, the rules for its voice, and a
numbered list of sources, each with a line I wrote saying what that source is allowed to
support. Nothing outside that list is admissible. The drafting step can't reach for
anything else, and the checking step is told plainly that whatever the model happens to
know doesn't count as evidence.

If a question can't be answered from those sources, it comes back empty along with a
note explaining what evidence would be needed to answer it.

That division is the part I care about most, because a model has no way of deciding what
counts as a source, whereas I do, and I make that decision before anything is generated.

## The gate

There's no model anywhere in `gate.py`. The rules are written in code so that the same
inputs always produce the same decision, and so that raising or lowering a standard
means changing a line that somebody can argue with rather than a judgement that quietly
drifts between runs.

A claim that contradicts one of the sources blocks the piece, because that's a factual
error. A claim with nothing behind it blocks as well, however reasonable it happens to
sound. If more than a fifth of the claims are only partly supported, that blocks too:
no individual sentence is wrong in that case, but the copy as a whole has wandered
away from the evidence. Banned phrases are caught by a plain text search rather than by
a model call, since a search never has an off day. A question the drafting step
refused to answer is recorded as a note rather than a failure, because a refusal is the
system doing what I asked of it, and closing that gap is my job rather than its.

The three outcomes are shippable, review and blocked. A block exits with an error code,
which means this can run as an automatic check before anything is published.

## The prompts, and why they changed

The prompts live in `prompts/` as numbered versions, and I don't edit them in place.
When something needs to change, it becomes a new file, and the reason is recorded below.
The drafting prompt went through four versions, and the reasons are more instructive
than the prompts themselves.

The first version attributed everything it wrote, including definitions that nobody
would think to dispute, which made the copy read like a literature review rather than
something a business reader would want. I narrowed attribution down to the claims a
reader could actually argue with.

The second version was told not to answer questions the sources could not support. It
duly stopped answering them and began writing paragraphs about what the evidence did
not contain, inside the published copy, where a reader has no idea what an evidence
pack is and no reason to care. I added a rule that the answer text may never refer to
the sources or to the pack at all, and gave the model something to watch for: if it
finds itself describing what evidence exists, the answer should be empty instead.

The third version repeated the same caveat across three separate answers, echoing the
wording of my own evidence line back at me each time, so the fourth asks it to state a
limitation once, in the answer where that limitation matters most.

The verification prompt went through two versions for a more interesting reason. The
first one reasoned correctly that a source did not carry a claim, wrote that reasoning
out in its own explanation, and then graded the claim as partially supported anyway. The
second version adds a single line: if your reasoning contains the words "does not
explicitly state", the verdict is unsupported.

Something similar was true of every one of these changes. Giving the model a symptom it
can recognise in its own output works better than restating a rule it had already
agreed to and then drifted away from.

## What happened over three runs

All three runs are kept in `samples/`, each with the draft that produced it, every
claim and its verdict, and the report the gate wrote.

The first run, in `run-1-blocked`, was blocked because four of its claims had nothing behind them, and three
of those four turned out to be advice to the reader rather than statements of fact. I
had expected to catch an invented statistic. What the model produced instead was
guidance, written into answers that were otherwise accurate and properly sourced, and
that's considerably harder to notice while reading than a wrong number would be.

Those sentences were harmless enough on their own. However, the same move in a piece on a more
demanding subject would hand a reader something they could act on and be wrong about, and the pipeline already takes that possibility into account. Nothing in the
writing tells those two cases apart, which is why it examines one claim at a time rather
than asking a model whether the article as a whole looks sound.

The second run, in `run-2-fixed`, passed to review after I removed those claims. The file
`editorial-notes.md` records what I changed and why, including the question I left
unanswered rather than fill with a guess that would have sounded plausible.

The third run, in `run-3-final`, is the one I would publish. A draft that survives a
fact-check is not the same thing as a draft anyone wants to read, so I edited it again for
plainness and put that version back through the check rather than trusting my own edits.
Copy that skips the gate would defeat the point of having one. That run also carries the
finished markdown and the FAQPage markup.

One question in the brief can't be answered from its sources, and that's deliberate:
how much approval rates improve after adding orchestration. Vendor pages answer it with
confident figures and no methodology behind any of them. This pipeline reports the
vendor's claim as a claim, and won't state the underlying number as a fact.

## Running it

```
pip install anthropic pyyaml python-dotenv
cp .env.example .env        # add your API key
python draft.py briefs/payment-orchestration-vs-gateway.yaml
python check.py briefs/payment-orchestration-vs-gateway.yaml output/faq-draft-<stamp>.json
python gate.py briefs/payment-orchestration-vs-gateway.yaml output/faq-draft-<stamp>.json output/claims-<stamp>.json
python publish.py briefs/payment-orchestration-vs-gateway.yaml output/faq-draft-<stamp>.json
```

A full run costs a few cents.

## What it doesn't do yet

A claim can only rest on a single source at the moment, so a sentence that is true
because two sources support it together gets marked unsupported. That rule caught a
genuine problem once and produced one false positive in the same evening, and letting a
claim cite more than one source is the obvious fix, which I haven't built.

The checker can't tell a figure of speech from actual advice. The published copy says to
keep in mind that a vendor's figure is an estimate rather than a benchmark, which the
splitter read as an instruction to the reader, and the checker then graded it as only
partly supported because no source tells anyone to keep anything in mind. The verdict is
defensible and the sentence is staying, since the alternative is copy that reads worse in
order to satisfy a rule written for a different problem.

There's only one output type. FAQs work, and comparison pages, glossaries and
statistics roundups would use the same brief, the same stages and the same gate, which
is what I would build next.

The evidence pack is assembled by hand, and I'd keep it that way, since deciding
what counts as a source is the part of this work that genuinely needs judgement.

The four scripts repeat a little code between them, in the loading of a prompt and the
filling of its blanks. I kept them separate so that each one can be read on its own
without having to follow anything into another file.

The numbers in the gate are choices rather than facts. A fifth of the claims being only
partly supported is where I set the line, and someone else would reasonably set it
somewhere else, which is precisely why it sits in code where it can be argued with.
