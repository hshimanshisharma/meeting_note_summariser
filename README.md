# AI Meeting Notes Summariser

A Flask app that summarises meeting notes locally with **Ollama Mistral**, optional **Whisper** transcription, summary styles, SQLite history, and user accounts.

## Prerequisites

- **Python 3.14** at `/usr/local/bin/python3.14` (verify: `ls /usr/local/bin | grep python`)
- [Ollama](https://ollama.com/) with Mistral: `ollama pull mistral`
- **ffmpeg** (for audio): `brew install ffmpeg` on macOS
- Xcode Command Line Tools (macOS) if `python3` / `venv` are not available

## Setup

```bash
cd ~/meeting-notes-summariser
/usr/local/bin/python3.14 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
/usr/local/bin/python3.14 app.py
```

Or use the helper scripts:

```bash
chmod +x setup.sh run.sh
./setup.sh    # first time, or to rebuild the venv on 3.14
./run.sh      # start the app
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

### Shell aliases (~/.zshrc)

After opening a **new** Terminal window, `python3` points to 3.14:

```bash
python3 --version   # Python 3.14.5
meeting-notes       # cd to project, activate venv, run app
```

Reload aliases in the current window: `source ~/.zshrc`

## Features

- **Summary styles:** Executive Summary, Bullet Points, Action Items
- **Audio / video:** Upload `.mp3`, `.wav`, or `.mp4` → Whisper transcription → summary
- **History:** SQLite-backed saved summaries (when logged in)
- **Auth:** Register / log in with Flask-Login (disable with `ENABLE_AUTH=false`)
- **UI:** Bootstrap cards, loading bar, copy-to-clipboard

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | dev secret | Flask session secret (set in production) |
| `ENABLE_AUTH` | `true` | Set to `false` to disable login/register |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `mistral` | Model name |
| `WHISPER_MODEL` | `base` | Whisper model size (`tiny`, `base`, `small`, …) |
| `MAX_AUDIO_MB` | `25` | Max upload size |

## Project structure

```text
meeting-notes-summariser/
├── app.py              # Routes and app factory
├── auth.py             # User registration / login helpers
├── config.py           # Settings
├── database.py         # SQLite (users, summaries)
├── summarizer.py       # Ollama + style prompts
├── transcription.py    # Whisper audio → text
├── templates/
├── data/               # SQLite DB (created at runtime)
└── uploads/            # Temp audio files
```

## Usage tips

1. **Register** and log in to save summaries to **History**.
2. Choose a **summary style** before clicking Summarize.
3. Paste notes, upload audio, or both.
4. First Whisper run downloads the model and may take a minute.

## Deactivate venv

```bash
deactivate
```
