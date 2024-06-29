# md_to_anki

> A minimalist method to create cards in Anki from a Markdown file.

This python script will add a piece of markdown file `.md` file to anki via [AnkiConnect - AnkiWeb](https://ankiweb.net/shared/info/2055492159)

## Installation

> I use [uv: Python packaging in Rust](https://astral.sh/blog/uv) BTW

- `uv venv`
- `source .venv/bin/activate`
- `uv pip sync requirements.txt`

## Usage

If you have a markdown file looks like

```markdown
---
title: Title
date: "2024-06-29"
tag: whatever
---

# What is Anki?

- Anki is a digital flashcard tool that uses spaced repetition to help users effectively memorize and learn various information.
```

You can run the script, with anki.app opened in the background

```bash
python md_to_anki.py -f YOUR_MARKDOWN_FILE.md -d DECK_NAME
```

The script will use Heading 1 as the Anki card front and place the subsequent content as the Anki card back. It will ignore any content before Heading 1, such as YAML front matter.

## Why use this method

I personally use a markdown-based personal knowledge management system. The Zettelkasten note-taking method is atomic, meaning each card contains only one unit of simple information, making it suitable for a single Anki card. Many projects aim to pipeline markdown files to Anki, but they are generally suited for batch generation and not for single markdown files.

My need arises when I finish a permanent note and want to review it regularly. Instead of batch-creating notes, I want the ability to easily add a single markdown file as a note into an Anki deck and update the content as needed. I prefer not to create too many APKG files and instead use Anki-connect to add notes directly.

## Build

`pyinstaller --onedir md_to_anki.py`

you will find your binary file in `./dist/md_to_anki/`
