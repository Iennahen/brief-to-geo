# check.py — checks a draft against the sources in its brief.
#
# Run it with:
#   python check.py briefs/payment-orchestration-vs-gateway.yaml output/faq-draft-XXXX.json
#
# Two stages. First it splits the copy into individual claims. Then it checks
# each claim on its own against the evidence pack.
#
# The two stages are separate calls on purpose. The checker never sees the
# drafting instructions, so it can't inherit their assumptions — the same reason
# a newsroom doesn't let a reporter fact-check their own piece.

import json
import os
import sys
import time

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

MODEL = "claude-sonnet-5"


def load_prompt(filename):
    """Read a prompt file and split it into its two halves."""
    text = open("prompts/" + filename, encoding="utf-8").read()
    system_part, user_part = text.split("## USER")
    return system_part.replace("## SYSTEM", "").strip(), user_part.strip()


def fill(template, values):
    """Replace every {{blank}} with a real value, and stop if one is left over."""
    for name, value in values.items():
        template = template.replace("{{" + name + "}}", value)
    if "{{" in template:
        sys.exit("A blank in the prompt was never filled.")
    return template


def ask(client, system_part, user_part):
    """Send one message to Claude and return the text of the reply."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=system_part,
        messages=[{"role": "user", "content": user_part}],
    )
    reply = "".join(b.text for b in response.content if b.type == "text")
    if not reply.strip():
        sys.exit(f"Claude sent no text back. stop_reason={response.stop_reason}")
    if reply.strip().startswith("```"):          # strip code fences if it added them
        reply = reply.split("```")[1]
        if reply.startswith("json"):
            reply = reply[4:]
    return json.loads(reply)


# --- read the brief and the draft -------------------------------------------

brief = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
draft = json.load(open(sys.argv[2], encoding="utf-8"))

evidence = "\n\n".join(
    f"[{s['id']}] {s['title']} (kind: {s['kind']})\n" + " ".join(s["evidence"].split())
    for s in brief["sources"]
)

load_dotenv()
client = Anthropic()


# --- stage one: split the copy into claims ----------------------------------
# Only answered questions go in. A question that came back empty has no copy to
# check.

copy_to_check = "\n\n".join(
    f"[q{number}] {item['a']}"
    for number, item in enumerate(draft["items"], start=1)
    if item["a"]
)

print("Splitting the draft into claims...")
system_part, user_part = load_prompt("extract_claims.v1.md")
claims = ask(client, system_part, fill(user_part, {"draft": copy_to_check}))["claims"]
print(f"Found {len(claims)} claims.\n")


# --- stage two: check each claim on its own ---------------------------------
# One call per claim. Checking them in a batch lets the model settle into a
# rhythm and wave the last few through.

system_part, user_part = load_prompt("verify_claim.v2.md")
results = []

for claim in claims:
    filled = fill(user_part, {
        "claim_text": claim["text"],
        "claim_type": claim["type"],
        "evidence": evidence,
    })
    verdict = ask(client, system_part, filled)
    results.append({**claim, **verdict})
    print(f"  {claim['id']}  {verdict['verdict']:<12} {claim['text'][:70]}")


# --- save and summarise -----------------------------------------------------

os.makedirs("output", exist_ok=True)
stamp = time.strftime("%Y%m%d-%H%M%S")
path = f"output/claims-{stamp}.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nSummary:")
for verdict in ["supported", "partial", "unsupported", "contradicted"]:
    count = len([r for r in results if r["verdict"] == verdict])
    if count:
        print(f"  {verdict:<14} {count}")

print(f"\nSaved to {path}")
