"""Upload a finished Short to YouTube using the YouTube Data API v3.

First-time setup (see README for details):
  1. Create a Google Cloud project, enable "YouTube Data API v3".
  2. Create an OAuth client ID (Desktop app), download as secrets/client_secret.json.
  3. Run this script once interactively to complete the OAuth consent flow; it caches
     a refresh token in secrets/token.json for future unattended runs.

Usage:
    python scripts/upload_youtube.py --script output/script.json --video output/final.mp4
"""
import argparse
import json
import os

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_credentials(client_secret_file: str, token_file: str) -> Credentials:
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(token_file) or ".", exist_ok=True)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return creds


def upload(video_path: str, script: dict, privacy_status: str, client_secret_file: str, token_file: str):
    creds = get_credentials(client_secret_file, token_file)
    youtube = build("youtube", "v3", credentials=creds)

    title = script["title"]
    description = script.get("description", "")
    tags = script.get("tags", [])

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "28",  # Science & Technology
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"Upload complete: https://youtube.com/shorts/{video_id}")
    return video_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--video", required=True)
    parser.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    parser.add_argument("--client-secret", default=os.environ.get("YOUTUBE_CLIENT_SECRET_FILE", "secrets/client_secret.json"))
    parser.add_argument("--token-file", default=os.environ.get("YOUTUBE_TOKEN_FILE", "secrets/token.json"))
    args = parser.parse_args()

    with open(args.script) as f:
        script = json.load(f)

    upload(args.video, script, args.privacy, args.client_secret, args.token_file)


if __name__ == "__main__":
    main()
