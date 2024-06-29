import argparse
import requests
import json
import markdown

# Constants
ANKICONNECT_ENDPOINT = "http://localhost:8765"
ANKI_FRONT_FIELD = "Front"
ANKI_BACK_FIELD = "Back"
ANKI_NOTE_TYPE = "Basic"
ANKI_DECK_NAME = "Default"


def load_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


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


def parse_front_matter_and_content(markdown_content):
    parts = markdown_content.split("---")
    if len(parts) < 3:
        return markdown_content
    content = parts[2].strip()
    return content


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

    markdown_content = load_markdown(markdown_file_path)

    if not markdown_content:
        print("Markdown file is empty.")
        return

    content = "NA"
    front = ""
    back = ""
    back_html = ""
    # Step 2: Parse front matter and content
    content = parse_front_matter_and_content(markdown_content)
    # Extract 'front' and 'back'
    if isinstance(content, str) and "# " in content:
        sections = content.split("# ", 1)[1].split("\n", 1)
        front = sections[0].strip()
        back = sections[1].strip()
        back_html = markdown.markdown(back)

    # print(back_html)

    # Send to Anki
    send_to_anki(front, back_html, deck_name)


if __name__ == "__main__":
    main()
