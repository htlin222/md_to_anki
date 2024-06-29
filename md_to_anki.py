#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# title: md_to_anki
# author: Hsieh-Ting Lin, the Lizard 🦎
# description: md_to_anki is a script about...
# date: "2024-06-29"
# --END-- #

import json

import markdown
import requests
import argparse

# Constants for Anki
ANKI_DECK_NAME = "00_Inbox"
ANKI_NOTE_TYPE = "Basic"
ANKI_FRONT_FIELD = "Front"
ANKI_BACK_FIELD = "Back"
ANKICONNECT_ENDPOINT = "http://localhost:8765"


def load_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()


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
    # print(response.content.decode())


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


def check_response_for_success(response):
    response_content = response.text
    if '"error": null' in response_content:
        print("\033[92mSuccess\033[0m")
    else:
        print(response.content.decode())


def main():
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

    markdown_lines = load_markdown(markdown_file_path)

    if not markdown_lines:
        print("Markdown file is empty.")
        return

    # Extract 'front' and 'back'
    front = markdown_lines[0].strip().replace("#", "").strip()
    back = (
        "".join(markdown_lines[1:]).strip().replace("[[", "__📜 ").replace("]]", "__")
    )
    back_html = markdown.markdown(back)

    # print(back_html)

    # Send to Anki
    send_to_anki(front, back_html, deck_name)


if __name__ == "__main__":
    main()
