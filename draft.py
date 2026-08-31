# draft.py — turns a brief into a first draft of an FAQ.
#
# Run it with:   python draft.py briefs/payment-orchestration-vs-gateway.yaml
#
# It does four things: reads the brief, fills the blanks in the prompt file,
# sends the result to Claude, saves what comes back.

import json
import os
import sys
import time

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

MODEL = "claude-sonnet-5"


# --- 1. read the brief ------------------------------------------------------
# yaml.safe_load turns the brief file into something Python can look things up
# in. brief["title"] then gives you the title, and so on.

brief_path = sys.argv[1]          # the filename you typed after "python draft.py"
brief = yaml.safe_load(open(brief_path, encoding="utf-8"))


# --- 2. build the pieces that go into the blanks ----------------------------
# The brief holds lists. The prompt needs text. These three lines turn one into
# the other.

voice_rules = "\n".join("- " + rule for rule in brief["voice"]["rules"])

do_not_cover = "\n".join("- " + item for item in brief["do_not_cover"])

questions = "\n".join(
    f"{number}. {question}"
    for number, question in enumerate(brief["must_cover"], start=1)
)

# The evidence pack is the important one. Each source becomes a labelled block,
# so the model can refer back to it by id.
evidence = "\n\n".join(
    f"[{source['id']}] {source['title']} (kind: {source['kind']})\n"
    + " ".join(source["evidence"].split())      # collapse the line breaks
    for source in brief["sources"]
)


# --- 3. fill the blanks in the prompt file ----------------------------------

prompt_file = open("prompts/draft_faq.v4.md", encoding="utf-8").read()

# The file has two parts, separated by the "## USER" line.
system_part, user_part = prompt_file.split("## USER")
system_part = system_part.replace("## SYSTEM", "").strip()
user_part = user_part.strip()

for name, value in {
    "audience": " ".join(brief["audience"].split()),
    "search_intent": brief["search_intent"],
    "voice_rules": voice_rules,
    "do_not_cover": do_not_cover,
    "evidence": evidence,
    "questions": questions,
}.items():
    user_part = user_part.replace("{{" + name + "}}", value)

# Safety check: if a blank is still sitting there unfilled, stop now rather than
# send Claude a prompt with a hole in it.
if "{{" in user_part:
    sys.exit("A blank in the prompt was never filled. Check the brief for a missing field.")


# --- 4. send it to Claude ---------------------------------------------------

load_dotenv()                      # reads your key out of the .env file
client = Anthropic()               # picks up ANTHROPIC_API_KEY from there

print(f"Drafting {len(brief['must_cover'])} answers with {MODEL}...")

response = client.messages.create(
    model=MODEL,
    max_tokens=8000,
    system=system_part,
    messages=[{"role": "user", "content": user_part}],
)

reply = "".join(block.text for block in response.content if block.type == "text")


# --- 5. save it -------------------------------------------------------------
# The reply is supposed to be JSON. Sometimes a model wraps it in ``` fences
# anyway, so trim those before trying to read it.

if reply.strip().startswith("```"):
    reply = reply.split("```")[1]
    if reply.startswith("json"):
        reply = reply[4:]

if not reply.strip():
    sys.exit(f"Claude sent no text back. stop_reason={response.stop_reason}")
draft = json.loads(reply)

os.makedirs("output", exist_ok=True)
import time
stamp = time.strftime("%Y%m%d-%H%M%S")
with open(f"output/faq-draft-{stamp}.json", "w", encoding="utf-8") as f:
    json.dump(draft, f, indent=2, ensure_ascii=False)


# --- 6. show it ------------------------------------------------------------

for item in draft["items"]:
    print("\n" + item["q"])
    if item["a"]:
        print(item["a"])
        print("sources: " + ", ".join(item["sources"]))
    else:
        print("NO ANSWER — " + item["unsupported"])

cost = (
    response.usage.input_tokens * 3 / 1_000_000
    + response.usage.output_tokens * 15 / 1_000_000
)
print(f"\nSaved to output/faq-draft.json. Cost: about ${cost:.3f}")

