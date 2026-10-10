"""Generate voiceover audio + word-timing data using free Microsoft edge-tts.

Usage:
    python scripts/tts.py --script output/script.json --out output/voice.mp3
"""
import argparse
import asyncio
import json
import os

import edge_tts
from dotenv import load_dotenv

load_dotenv()

DEFAULT_VOICE = os.environ.get("TTS_VOICE", "en-US-GuyNeural")


async def synthesize(text: str, voice: str, audio_out: str, timing_out: str):
    communicate = edge_tts.Communicate(text, voice)
    word_boundaries = []
    with open(audio_out, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word_boundaries.append(
                    {
                        "text": chunk["text"],
                        "start_s": chunk["offset"] / 10_000_000,
                        "duration_s": chunk["duration"] / 10_000_000,
                    }
                )
    with open(timing_out, "w") as f:
        json.dump(word_boundaries, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, help="Path to script.json from generate_script.py")
    parser.add_argument("--out", default="output/voice.mp3")
    parser.add_argument("--timing-out", default="output/word_timings.json")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    args = parser.parse_args()

    with open(args.script) as f:
        script = json.load(f)
    text = script["full_voiceover_text"]

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    asyncio.run(synthesize(text, args.voice, args.out, args.timing_out))
    print(f"Voiceover: {args.out}")
    print(f"Word timings: {args.timing_out}")


if __name__ == "__main__":
    main()
