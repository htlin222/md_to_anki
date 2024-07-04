#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# title: add_md_to_anki
# date: "2023-10-06"
# #!/usr/bin/env python3
# -*- coding: utf-8 -*-
# title: add_md_to_anki
# date: "2023-10-06"
# author: Hsieh-Ting Lin, the Lizard 🦎

import argparse
import json
import re
import subprocess
import sys
import time

import markdown
import requests
from markdown.extensions.fenced_code import FencedCodeExtension

# Constants for Anki
ANKI_DECK_NAME = "00_Inbox"
ANKI_NOTE_TYPE = "Basic"
ANKI_FRONT_FIELD = "Front"
ANKI_BACK_FIELD = "Back"
ANKICONNECT_ENDPOINT = "http://localhost:8765"


def load_markdown(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Failed to read the markdown file: {e}")
        sys.exit(1)


def parse_front_matter_and_content(markdown_content):
    parts = markdown_content.split("---")
    if len(parts) < 3:
        return markdown_content, None
    front_matter = parts[1]
    content = parts[2]
    return front_matter, content


def find_existing_note(front):
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {"query": f'{ANKI_FRONT_FIELD}:"{front}"'},
    }
    try:
        response = requests.post(ANKICONNECT_ENDPOINT, json=payload)
        response.raise_for_status()
        return json.loads(response.content.decode()).get("result", [])
    except requests.RequestException as e:
        print(f"Failed to find existing note: {e}")
        return []


def update_note(note_id, front, back):
    payload = {
        "action": "updateNoteFields",
        "version": 6,
        "params": {
            "note": {
                "id": note_id,
                "fields": {ANKI_FRONT_FIELD: front, ANKI_BACK_FIELD: back},
            }
        },
    }
    try:
        response = requests.post(ANKICONNECT_ENDPOINT, json=payload)
        check_response_for_success(response)
        print(f"Updated 🔃: {front}")
    except requests.RequestException as e:
        print(f"Failed to update note: {e}")


def check_response_for_success(response):
    try:
        response.raise_for_status()
        if '"error": null' in response.text:
            print("Success✨")
        else:
            print(f"Error in response: {response.content.decode()}")
    except requests.RequestException as e:
        print(f"Response error: {e}")


def send_to_anki(front, back, deck_name):
    existing_notes = find_existing_note(front)
    if existing_notes:
        update_note(existing_notes[0], front, back)
    else:
        payload = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": ANKI_NOTE_TYPE,
                    "fields": {ANKI_FRONT_FIELD: front, ANKI_BACK_FIELD: back},
                    "options": {"allowDuplicate": False},
                    "tags": ["from_mymarkdown"],
                }
            },
        }
        try:
            response = requests.post(ANKICONNECT_ENDPOINT, json=payload)
            check_response_for_success(response)
            print(f"Added ✅ {front}")
        except requests.RequestException as e:
            print(f"Failed to add note: {e}")


def is_process_running(process_name):
    try:
        output = subprocess.check_output(["pgrep", "-f", process_name])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False


def start_anki():
    try:
        subprocess.run(["open", "/Applications/Anki.app"])
        time.sleep(5)  # Wait for Anki to start
    except Exception as e:
        print(f"Failed to start Anki: {e}")
        sys.exit(1)


def add_language_class(html):
    def replacer(match):
        language = match.group(1)
        code_content = match.group(2)
        return f'<pre><code class="language-{language}">{code_content}</code></pre>'

    pattern = re.compile(r"<code>(.*?)\n(.*?)</code>", re.DOTALL)
    return pattern.sub(replacer, html)


def main():
    process_name = "/Applications/Anki.app/Contents/MacOS/anki"
    if not is_process_running(process_name):
        print("Anki is not running, starting it now...")
        start_anki()

    parser = argparse.ArgumentParser(description="Add markdown to Anki")
    parser.add_argument("--file", "-f", required=True, help="Path to markdown file")
    parser.add_argument(
        "--deck", "-d", default=ANKI_DECK_NAME, help="Name of the Anki deck"
    )
    args = parser.parse_args()

    markdown_file_path = args.file
    deck_name = args.deck

    if not markdown_file_path.endswith(".md"):
        print("Error: The file must end with .md")
        return

    markdown_content = load_markdown(markdown_file_path)
    front_matter, content = parse_front_matter_and_content(markdown_content)

    if content:
        try:
            front = content.split("# ", 1)[1].split("\n", 1)[0].strip()
            back = content.split("# ", 1)[1].split("\n", 1)[1].strip()
            back_html = markdown.markdown(back, extensions=[FencedCodeExtension()])
            back_html = add_language_class(back_html)
            send_to_anki(front, back_html, deck_name)
        except IndexError:
            print("Error: Unable to parse the content")
    else:
        print("Empty content")


if __name__ == "__main__":
    main()
