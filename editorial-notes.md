# Editorial notes

The first run of the pipeline was blocked. The fact-check step found four sentences in
the draft that no source in the brief supported. Below is what I did about each one and
why.

## "Test it against your own transaction data before using it in a business case."

I deleted this sentence: it looks like reasonable advice, but doesn't really say anything of real use with the sole purpose of being clever. None of my four sources give it, so the model added it on its own. Such sentences are easy to publish by mistake, because the content sounds
like it follows from what came before it, so a reader skimming the page has no reason to
question it. This case was innocent enough, but it can get dangerous within a more specific context. 

## Two sentences about merchants below Solidgate's $400,000 threshold

I deleted both, and deliberately left the question unanswered.

Solidgate says that orchestration pays for itself above roughly $400,000 processed per
month across multiple markets. The draft turned that into advice for merchants below
that level, and for merchants selling in a single market. My chosen sources don't really say
anything about either group. Knowing when something starts to pay off does not tell you
what happens below that point, and Solidgate is a vendor with an interest in where this
line is drawn.

I simply couldn't answer the question from this evidence pack. To answer
it properly, I'd need a source about smaller or single-market merchants. Until I have
one, I'd rather skip than lie on this account.

## The sentence comparing gateways and orchestration

I split it in two.

The claim was accurate, but it combined two sources into one sentence, and the checker
only accepts one source per claim. Splitting it means each sentence can be traced to the
source it came from. The copy reads a bit less smoothly, but the sourcing is now
clear.

## "Treat the figure as a vendor estimate rather than a verified benchmark."

I rewrote this as a statement about the source instead of advice to the reader.

It now says that the figure is a vendor claim rather than a measured benchmark. The
information is the same, but the sentence that used to look like an instruction that came from nowhere is now something my sources support directly.


## What the first run caught

Three of the four blocked sentences were advice instead of facts. The model didn't hallucinate any
statistics, but invented guidance, and put that guidance inside answers that were
otherwise accurate and well sourced.

That's harder to catch by reading than a wrong number would be, and that's why the pipeline checks one claim at a time against the source list, instead of asking a model
whether the article as a whole looks neat.
