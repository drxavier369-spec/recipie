"""End-to-end: idea -> script -> voiceover -> video -> (optional) YouTube upload.

Usage:
    python scripts/pipeline.py --from-ideas config/ideas.json --index 0 --upload --privacy private
    python scripts/pipeline.py --topic "Win+Shift+S screenshot trick" --category Windows
"""
import argparse
import os
import subprocess
import sys


def run(cmd):
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic")
    parser.add_argument("--category", default="General")
    parser.add_argument("--from-ideas")
    parser.add_argument("--index", type=int, default=None)
    parser.add_argument("--launch-day", type=int, default=None)
    parser.add_argument("--id", type=int, default=None)
    parser.add_argument("--workdir", default="output")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    args = parser.parse_args()

    os.makedirs(args.workdir, exist_ok=True)
    script_path = os.path.join(args.workdir, "script.json")
    audio_path = os.path.join(args.workdir, "voice.mp3")
    video_path = os.path.join(args.workdir, "final.mp4")

    gen_cmd = [sys.executable, "scripts/generate_script.py", "--out", script_path]
    if args.from_ideas:
        gen_cmd += ["--from-ideas", args.from_ideas]
        if args.launch_day is not None:
            gen_cmd += ["--launch-day", str(args.launch_day)]
        elif args.id is not None:
            gen_cmd += ["--id", str(args.id)]
        else:
            gen_cmd += ["--index", str(args.index or 0)]
    elif args.topic:
        gen_cmd += ["--topic", args.topic, "--category", args.category]
    else:
        print("Provide --topic or --from-ideas", file=sys.stderr)
        sys.exit(1)
    run(gen_cmd)

    run([sys.executable, "scripts/tts.py", "--script", script_path, "--out", audio_path,
         "--timing-out", os.path.join(args.workdir, "word_timings.json")])

    run([sys.executable, "scripts/build_video.py", "--script", script_path, "--audio", audio_path, "--out", video_path])

    if args.upload:
        run([sys.executable, "scripts/upload_youtube.py", "--script", script_path, "--video", video_path,
             "--privacy", args.privacy])

    print(f"\nDone. Video: {video_path}")


if __name__ == "__main__":
    main()
