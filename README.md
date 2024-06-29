# md_to_anki

This python script will add a piece of markdown file `.md` file to anki via [AnkiConnect - AnkiWeb](https://ankiweb.net/shared/info/2055492159)

## Installation

> I use [uv: Python packaging in Rust](https://astral.sh/blog/uv) BTW

- `uv venv`
- `source .venv/bin/activate`
- `uv pip sync requirements.txt`

## Usage

`python md_to_anki.py -f YOUR_MARKDOWN_FILE.md -d DECK_NAME`

## Build

`pyinstaller --onedir md_to_anki.py`

you will find your binary file in `./dist/md_to_anki/`
