#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# title: add_md_to_anki
# date: "2023-10-06"
# author: Hsieh-Ting Lin, the Lizard 🦎
import json
import subprocess
import argparse
import markdown
import requests
import yaml

# Constants for Anki
ANKI_DECK_NAME = "00_Inbox"
ANKI_NOTE_TYPE = "Basic"
ANKI_FRONT_FIELD = "Front"
ANKI_BACK_FIELD = "Back"
ANKICONNECT_ENDPOINT = "http://localhost:8765"


def load_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def parse_front_matter_and_content(markdown_content):
    # TODO: how to handle if no front matter
    parts = markdown_content.split("---")
    if len(parts) < 3:
        return None, None

    front_matter = yaml.safe_load(parts[1])
    content = parts[2]
    return front_matter, content


def find_existing_note(front):
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {"query": f'{ANKI_FRONT_FIELD}:"{front}"'},
    }
    response = requests.post(ANKICONNECT_ENDPOINT, json=payload)
    return json.loads(response.content.decode()).get("result", [])


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
    response = requests.post(ANKICONNECT_ENDPOINT, json=payload)
    print(f"Updated 🔃: {front}")
    check_response_for_success(response)


def check_response_for_success(response):
    response_content = response.text
    if '"error": null' in response_content:
        print("\033[92mSuccess\033[0m")
    else:
        print(response.content.decode())


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

        response = requests.post(ANKICONNECT_ENDPOINT, json=payload)
        print(f"Added ✅ {front}")
        check_response_for_success(response)


def is_process_running(process_name):
    try:
        output = subprocess.check_output(["pgrep", "-f", process_name])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False


def main():
    process_name = "/Applications/Anki.app/Contents/MacOS/anki"
    if is_process_running(process_name):
        print("Anki is running")
    else:
        print("Anki is not running, starting it now...")
        subprocess.run(["open", "/Applications/Anki.app"])
        return

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

    # Step 1: Load Markdown content
    markdown_content = load_markdown(markdown_file_path)

    content = "NA"
    # Step 2: Parse front matter and content
    front_matter, content = parse_front_matter_and_content(markdown_content)

    front = content.split("# ", 1)[1].split("\n", 1)[0].strip()
    back = content.split("# ", 1)[1].split("\n", 1)[1].strip()
    back_html = markdown.markdown(back)

    # Step 4: Open Anki app
    #
    # print(front)
    # print(back_html)

    # Step 5: Send to Anki
    send_to_anki(front, back_html, deck_name)


if __name__ == "__main__":
    main()
