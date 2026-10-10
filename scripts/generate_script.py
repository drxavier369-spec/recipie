"""Generate a verified, structured Short script for one tech-hack idea using Claude.

Usage:
    python scripts/generate_script.py --topic "Win+Shift+S screenshot trick" --category Windows
    python scripts/generate_script.py --from-ideas config/ideas.json --index 0
"""
import argparse
import json
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a YouTube Shorts scriptwriter and fact-checker for a channel about
simple tech hacks and hidden features (Android, iPhone, Windows, Chrome, Google, WhatsApp,
websites, keyboard shortcuts, AI tricks, files/photos, privacy, time-saving, accessibility,
lesser-known app features).

RULES:
- One video teaches exactly ONE trick. Never combine multiple unrelated tips.
- Verify the trick is real, the steps are correct, and name the platform/version it applies to.
  If you are not confident the feature exists or works as described, set "verified": false and
  explain why in "verification_note" instead of inventing steps.
- Total spoken script must read aloud in 20-40 seconds (roughly 55-110 words).
- Structure, in this order:
  1. HOOK (0-3s): one punchy curiosity line. No "hey guys welcome back".
  2. RESULT (3-7s): what the trick accomplishes, in one line.
  3. STEPS (7-25s): numbered, extremely simple, minimal words per step.
  4. PAYOFF (final seconds): short useful close. No begging for likes/subscribes.
- Style: short sentences, simple vocabulary, conversational, active voice, no jargon, no filler.
- Output strict JSON only, matching this schema:
{
  "title": "short YouTube title, <70 chars, no clickbait lies",
  "platform": "e.g. Android 13+ / iPhone (iOS 16+) / Windows 10/11 / Chrome desktop",
  "verified": true/false,
  "verification_note": "why verified or what is unverifiable",
  "hook": "...",
  "result": "...",
  "steps": ["1. ...", "2. ...", "3. ..."],
  "payoff": "...",
  "full_voiceover_text": "hook + result + steps + payoff combined into one natural spoken script",
  "on_screen_captions": ["short caption chunk 1", "short caption chunk 2", "..."],
  "tags": ["tag1", "tag2", "..."],
  "description": "1-2 line YouTube description with the steps restated"
}
Return ONLY the JSON object, no markdown fences, no extra text.
"""


def generate(topic: str, category: str) -> dict:
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    user_prompt = f"Category: {category}\nTrick idea: {topic}\n\nWrite the Short script JSON now."
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = resp.content[0].text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start : end + 1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic")
    parser.add_argument("--category", default="General")
    parser.add_argument("--from-ideas")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    if args.from_ideas:
        with open(args.from_ideas) as f:
            ideas = json.load(f)
        idea = ideas[args.index]
        topic, category = idea["topic"], idea["category"]
    elif args.topic:
        topic, category = args.topic, args.category
    else:
        print("Provide --topic or --from-ideas", file=sys.stderr)
        sys.exit(1)

    script = generate(topic, category)

    if not script.get("verified", False):
        print(f"WARNING: trick marked NOT verified: {script.get('verification_note')}", file=sys.stderr)

    out_path = args.out or os.path.join("output", "script.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(script, f, indent=2)

    print(f"Script written to {out_path}")
    print(json.dumps(script, indent=2))


if __name__ == "__main__":
    main()
