# publish.py — turns a checked draft into the two files a page actually needs.
#
# Run it with:
#   python publish.py briefs/<brief>.yaml output/faq-draft-edited.json
#
# Produces:
#   output/faq-<stamp>.md      the copy, ready for a CMS
#   output/faq-<stamp>.jsonld  FAQPage markup for the page head
#
# The markup is what makes an FAQ legible to search engines and to the systems
# that answer questions by quoting pages. Two rules it follows:
#
#   1. The markup must say exactly what the visible copy says. Markup that
#      claims something the page doesn't show is treated as spam.
#   2. Unanswered questions never reach the markup. A gap belongs in the
#      editorial output, not in a machine-readable claim about the page.

import json
import sys
import time

import yaml

brief = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
draft = json.load(open(sys.argv[2], encoding="utf-8"))

answered = [item for item in draft["items"] if item["a"]]
gaps = [item for item in draft["items"] if not item["a"]]


# --- the copy ---------------------------------------------------------------

lines = [f"## {brief['title']} — frequently asked questions", ""]

for item in answered:
    lines.append(f"### {item['q']}")
    lines.append("")
    lines.append(item["a"].strip())
    lines.append("")
    lines.append(f"*Sources: {', '.join(item['sources'])}*")
    lines.append("")

for item in gaps:
    lines.append(f"### {item['q']}")
    lines.append("")
    lines.append(f"> **Not published.** {item['unsupported']}")
    lines.append("")

markdown = "\n".join(lines)


# --- the markup -------------------------------------------------------------
# schema.org's FAQPage format. Each question becomes a Question with one
# acceptedAnswer, copied character for character from the visible text.

schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": item["q"].strip(),
            "acceptedAnswer": {"@type": "Answer", "text": item["a"].strip()},
        }
        for item in answered
    ],
}


# --- check the markup before writing it -------------------------------------
# A short list of the mistakes a generated pipeline actually makes.

problems = []

if not schema["mainEntity"]:
    problems.append("nothing to publish — every question came back unanswered")

for number, entity in enumerate(schema["mainEntity"], start=1):
    question = entity["name"]
    answer = entity["acceptedAnswer"]["text"]
    if not question.endswith("?"):
        problems.append(f"question {number} doesn't end in a question mark: {question}")
    if not answer:
        problems.append(f"question {number} has an empty answer")
    if "<" in answer and ">" in answer:
        problems.append(f"question {number} has HTML in the answer text")

if problems:
    for problem in problems:
        print(f"  PROBLEM  {problem}")
    sys.exit("\nMarkup not written.")


# --- write ------------------------------------------------------------------

stamp = time.strftime("%Y%m%d-%H%M%S")

open(f"output/faq-{stamp}.md", "w", encoding="utf-8").write(markdown + "\n")
open(f"output/faq-{stamp}.jsonld", "w", encoding="utf-8").write(
    json.dumps(schema, indent=2, ensure_ascii=False) + "\n"
)

print(f"\n  {len(answered)} answers published, {len(gaps)} left as gaps")
print(f"  output/faq-{stamp}.md")
print(f"  output/faq-{stamp}.jsonld\n")
