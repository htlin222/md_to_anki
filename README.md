# md_to_anki

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

You can run the script

```bash
python md_to_anki.py -f YOUR_MARKDOWN_FILE.md -d DECK_NAME`
```

The script will use Heading 1 as the Anki card front and place the subsequent content as the Anki card back. It will ignore any content before Heading 1, such as YAML front matter.

## Build

`pyinstaller --onedir md_to_anki.py`

you will find your binary file in `./dist/md_to_anki/`
