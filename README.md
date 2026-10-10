# Simple Tech Hacks — Faceless Shorts Channel Automation

Automates one video = one simple tech hack, end-to-end:

1. **Idea** — pulled from `config/ideas.json` (or passed directly).
2. **Script** — Claude writes a verified Hook → Result → Steps → Payoff script (`scripts/generate_script.py`).
   Anything it can't verify is flagged `"verified": false` instead of being made up.
3. **Voiceover** — free TTS via `edge-tts` (`scripts/tts.py`).
4. **Video** — vertical 1080x1920 gradient background with synced burned-in captions, built with
   Pillow + ffmpeg (`scripts/build_video.py`).
5. **Upload** — pushes the finished Short to YouTube via the Data API (`scripts/upload_youtube.py`).

Run the whole thing with `scripts/pipeline.py`.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY, pick a TTS_VOICE
```

You also need `ffmpeg` and `ffprobe` on your PATH (`apt install ffmpeg` / `brew install ffmpeg`).

### YouTube upload credentials

1. In Google Cloud Console, create a project and enable **YouTube Data API v3**.
2. Create an OAuth client ID of type **Desktop app**, download the JSON, save it as
   `secrets/client_secret.json`.
3. The first upload run opens a browser for consent and caches a refresh token at
   `secrets/token.json`. After that, uploads run unattended.
4. New YouTube API projects start with a **daily upload quota** that may limit you to a
   handful of uploads per day until you request a quota increase — plan your posting
   schedule around that.

## Usage

Generate and upload one video from the idea bank (as a private video, for review first).
Pick an idea by its launch day, id, or plain list position:

```bash
python scripts/pipeline.py --from-ideas config/ideas.json --launch-day 1 --upload --privacy private
python scripts/pipeline.py --from-ideas config/ideas.json --id 6 --upload --privacy private
python scripts/pipeline.py --from-ideas config/ideas.json --index 0 --upload --privacy private
```

Generate a video from a custom idea, without uploading:

```bash
python scripts/pipeline.py --topic "Win+Shift+S instant screenshot" --category Windows
```

Each stage can also be run standalone (`generate_script.py`, `tts.py`, `build_video.py`,
`upload_youtube.py`) — see each file's `--help` / usage docstring.

## Content rules this pipeline enforces

- One trick per video. No combining multiple tips.
- Every script is checked for a `verified` flag — review `output/script.json` before uploading
  anything marked `false`, or any trick you're not personally sure still works on the current
  OS/app version.
- Script length targets 20–40 seconds of spoken audio (~55–110 words).
- No "hey guys welcome back" intros, no like/subscribe begging.

## The idea bank

`config/ideas.json` holds a 100-idea content calendar across five categories: Smartphone,
Windows, Chrome, Google & Internet, and AI & Productivity. Each entry has:

```json
{"id": 1, "category": "Smartphone", "topic": "Copy text from a photo",
 "status": "unverified", "launch_day": 3, "hook": "“You don't have to type this.”"}
```

`launch_day` and `hook` are only set for the first 10 videos — a deliberately small,
high-confidence launch batch to test before committing to the full 100. Pick one by
`--launch-day N`, `--id N`, or plain `--index N` (see Usage above). When a `hook` is set,
it's passed to Claude as a suggested starting point, not a locked script. Add new entries
as `{"category": "...", "topic": "...", "status": "unverified", "launch_day": null, "hook": null}`
and they're ready to run through the pipeline.

**Launch plan (days 1–10):** reopen a closed Chrome tab, Windows clipboard history, copy text
from a photo, partial screenshot, turn a website into an app, Google image search, Windows
screen recording, phone document scanner, find a lost phone, instantly lock Windows. Treat the
other 90 as a backlog to pull from based on how these 10 perform — don't batch-produce all 100
blind.

## Notes / limitations

- The video background is a plain gradient with burned-in captions — it demonstrates the
  trick through narration and on-screen text rather than a screen recording. Swap in real
  screen-recorded B-roll in `scripts/build_video.py` once you start capturing footage; the
  caption-timing logic is independent of the background source.
- Caption timing is estimated by splitting the voiceover duration proportionally by word
  count per caption chunk (word-level timestamps from edge-tts are saved to
  `output/word_timings.json` if you want tighter sync later).
