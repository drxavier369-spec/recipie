"""Assemble a vertical 1080x1920 Short: gradient background + burned-in captions + voiceover.

Requires ffmpeg and ffprobe installed on PATH.

Usage:
    python scripts/build_video.py --script output/script.json --audio output/voice.mp3 --out output/final.mp4
"""
import argparse
import json
import os
import subprocess
import textwrap

from PIL import Image, ImageDraw

W, H = 1080, 1920


def ffprobe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def make_background(out_path: str, top_color=(20, 20, 35), bottom_color=(60, 30, 90)):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    img.save(out_path)


def escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "’")
        .replace("%", "\\%")
    )


def wrap_caption(text: str, width: int = 24) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def build_drawtext_filters(captions, total_duration: float, font_path: str | None):
    word_counts = [max(1, len(c.split())) for c in captions]
    total_words = sum(word_counts)
    filters = []
    t = 0.0
    font_opt = f":fontfile='{font_path}'" if font_path else ""
    for caption, wc in zip(captions, word_counts):
        dur = total_duration * (wc / total_words)
        start, end = t, t + dur
        wrapped = escape_drawtext(wrap_caption(caption))
        filters.append(
            f"drawtext=text='{wrapped}'{font_opt}:fontcolor=white:fontsize=64:"
            f"box=1:boxcolor=black@0.55:boxborderw=24:line_spacing=10:"
            f"x=(w-text_w)/2:y=h*0.72-text_h/2:"
            f"enable='between(t,{start:.3f},{end:.3f})'"
        )
        t = end
    return filters


def find_font() -> str | None:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--out", default="output/final.mp4")
    parser.add_argument("--title-text", default=None, help="Optional big title shown for first 2s")
    args = parser.parse_args()

    with open(args.script) as f:
        script = json.load(f)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    bg_path = os.path.join(os.path.dirname(args.out) or ".", "_bg.png")
    make_background(bg_path)

    duration = ffprobe_duration(args.audio)
    captions = script.get("on_screen_captions") or [script["full_voiceover_text"]]
    font_path = find_font()
    filters = build_drawtext_filters(captions, duration, font_path)
    filter_str = ",".join(filters) if filters else "null"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", bg_path,
        "-i", args.audio,
        "-vf", filter_str,
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        args.out,
    ]
    subprocess.run(cmd, check=True)
    os.remove(bg_path)
    print(f"Video written to {args.out}")


if __name__ == "__main__":
    main()
