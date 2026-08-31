# gate.py — decides whether a checked draft can be published.
#
# Run it with:
#   python gate.py briefs/<brief>.yaml output/faq-draft-XXXX.json output/claims-XXXX.json
#
# There is no Claude in this file, on purpose. The same inputs always produce the
# same verdict, and changing a standard means changing a line of code that
# someone can argue with — not a judgement call that drifts between runs.

import json
import sys
import time

import yaml

# How many claims may come back partially supported before the piece needs a
# human read. A policy choice, not a law. Raise it and you publish more, with
# thinner sourcing behind it.
PARTIAL_TOLERANCE = 0.20


brief = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
draft = json.load(open(sys.argv[2], encoding="utf-8"))
claims = json.load(open(sys.argv[3], encoding="utf-8"))

blocks = []      # reasons the piece cannot be published
warnings = []    # things an editor should look at


# --- rule 1: a contradicted claim is a factual error -------------------------

for claim in claims:
    if claim["verdict"] == "contradicted":
        blocks.append(f"{claim['id']} contradicts {claim['source_id']}: {claim['text']}")


# --- rule 2: an unsupported claim has nothing behind it ----------------------
# This is the rule that catches invented sentences. It does not care how
# reasonable the sentence sounds.

for claim in claims:
    if claim["verdict"] == "unsupported":
        blocks.append(f"{claim['id']} unsupported ({claim['type']}): {claim['text']}")


# --- rule 3: too many partials means thin sourcing throughout ----------------
# One partial is a sentence to tighten. A third of the piece being partial means
# the copy has drifted away from the evidence, even if no single claim is wrong.

partials = [c for c in claims if c["verdict"] == "partial"]
if claims and len(partials) / len(claims) > PARTIAL_TOLERANCE:
    share = len(partials) / len(claims)
    blocks.append(f"{share:.0%} of claims only partially supported (limit {PARTIAL_TOLERANCE:.0%})")
else:
    for claim in partials:
        warnings.append(f"{claim['id']} partially supported: {claim['text']}")


# --- rule 4: banned phrases -------------------------------------------------
# A plain text search, not a model call. Cheaper, and it never has an off day.

published_text = " ".join(item["a"] for item in draft["items"] if item["a"]).lower()
for phrase in brief["voice"]["banned_phrases"]:
    if phrase.lower() in published_text:
        blocks.append(f"banned phrase in copy: {phrase}")


# --- rule 5: declared gaps are not failures ---------------------------------
# A question the drafter refused to answer is the system working. Closing the
# gap is an editor's job: find a source, or drop the question.

for number, item in enumerate(draft["items"], start=1):
    if not item["a"]:
        warnings.append(f"q{number} returned no answer: {item['unsupported']}")


# --- the verdict ------------------------------------------------------------

if blocks:
    status = "BLOCKED"
elif warnings:
    status = "REVIEW"
else:
    status = "SHIPPABLE"


# --- write the report -------------------------------------------------------

counts = {}
for claim in claims:
    counts[claim["verdict"]] = counts.get(claim["verdict"], 0) + 1

report = [f"# {brief['title']}", "", f"**{status}**", ""]

if blocks:
    report += ["## Blocking", ""] + [f"- {b}" for b in blocks] + [""]
if warnings:
    report += ["## For review", ""] + [f"- {w}" for w in warnings] + [""]

report += ["## Claims", "", "| id | type | verdict | source | claim |", "|---|---|---|---|---|"]
for claim in claims:
    text = claim["text"].replace("|", "/")
    if len(text) > 80:
        text = text[:77] + "..."
    report.append(
        f"| {claim['id']} | {claim['type']} | {claim['verdict']} "
        f"| {claim.get('source_id') or '—'} | {text} |"
    )

report += ["", "## Counts", ""] + [f"- {k}: {v}" for k, v in sorted(counts.items())]

stamp = time.strftime("%Y%m%d-%H%M%S")
path = f"output/report-{stamp}.md"
open(path, "w", encoding="utf-8").write("\n".join(report) + "\n")


# --- tell the human ---------------------------------------------------------

print(f"\n  {status}\n")
for b in blocks:
    print(f"  BLOCK   {b}")
for w in warnings:
    print(f"  review  {w}")
print(f"\n  Report: {path}")

# Exit code 1 on a block, so this can run automatically as a publishing check.
sys.exit(1 if status == "BLOCKED" else 0)
