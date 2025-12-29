"""
fetch_logo.py

Download a logo from a URL into ./assets/ and update config.json so the Streamlit app
(presented earlier) will pick it up automatically as the persisted logo.

Usage:
  python fetch_logo.py --url "https://.../logo.png"

What it does:
  - Downloads the file (requests)
  - Detects simple image type by Content-Type or URL extension
  - Saves it as assets/swift_logo.<ext>
  - Updates config.json {"logo_path": "assets/swift_logo.<ext>"} (creating config.json if missing)

Notes:
  - You must have rights to use the logo you download.
  - Requires requests: pip install requests
"""

import os
import sys
import argparse
import requests
import json

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


def choose_extension(url: str, content_type: str) -> str:
    content_type = (content_type or "").lower()
    if "svg" in content_type or url.lower().endswith(".svg"):
        return ".svg"
    if "png" in content_type or url.lower().endswith(".png"):
        return ".png"
    if "jpeg" in content_type or "jpg" in content_type or url.lower().endswith(".jpg") or url.lower().endswith(".jpeg"):
        return ".jpg"
    # default to png
    return ".png"


def download_logo(url: str) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    ext = choose_extension(url, r.headers.get("content-type", ""))
    fname = os.path.join(ASSETS_DIR, "swift_logo" + ext)
    with open(fname, "wb") as f:
        f.write(r.content)
    return fname


def update_config_with_logo(path: str):
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
    cfg = cfg or {}
    cfg["logo_path"] = path
    # preserve schema_path if present
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print("Failed to write config.json:", e, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Download a logo into ./assets and update config.json")
    parser.add_argument("--url", required=True, help="Logo image URL (png/svg/jpg)")
    args = parser.parse_args()

    try:
        print("Downloading logo from:", args.url)
        saved = download_logo(args.url)
        print("Saved logo to:", saved)
        # store path relative to project root
        relpath = os.path.relpath(saved, os.path.dirname(__file__))
        update_config_with_logo(relpath)
        print("Updated config.json with logo_path:", relpath)
        print("Done. Restart Streamlit app if running; the logo will appear in the UI.")
    except Exception as e:
        print("Error downloading or saving logo:", e, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()