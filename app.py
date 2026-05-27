"""AI Meeting Notes Summariser — Flask application entry point."""

import uuid
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
import database
from auth import User, authenticate_user, load_user, register_user
from config import (
    ALLOWED_AUDIO_EXTENSIONS,
    ENABLE_AUTH,
    MAX_AUDIO_BYTES,
    SECRET_KEY,
    SUMMARY_STYLES,
    UPLOAD_DIR,
)
from summarizer import SummaryGenerationError, generate_summary, normalize_style
from transcription import TranscriptionError, transcribe_audio

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_AUDIO_BYTES

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@app.context_processor
def inject_template_globals():
    return {"enable_auth": ENABLE_AUTH}


@login_manager.user_loader
def user_loader(user_id: str):
    return load_user(user_id)


def _file_suffix(filename: str) -> str:
    """Return lowercase extension from a client-provided filename."""
    clean = Path(filename.replace("\\", "/")).name
    return Path(clean).suffix.lower()


def _allowed_audio(filename: str) -> bool:
    return _file_suffix(filename) in ALLOWED_AUDIO_EXTENSIONS


def _get_uploaded_audio_file():
    """Return the first valid uploaded audio file (supports legacy field name)."""
    for key in ("audio_file", "audio"):
        upload = request.files.get(key)
        if upload and upload.filename and upload.filename.strip():
            return upload
    return None


def _get_form_field(name: str) -> str:
    value = request.form.get(name, "").strip()
    if value:
        return value
    payload = request.get_json(silent=True) or {}
    return str(payload.get(name, "")).strip()


def _save_uploaded_audio(audio_file) -> Path:
    if not audio_file or not audio_file.filename:
        raise TranscriptionError("No audio file provided.")

    original_name = Path(audio_file.filename.replace("\\", "/")).name
    suffix = _file_suffix(original_name)
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
        raise TranscriptionError(f"Unsupported file type. Allowed: {allowed}")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    audio_file.save(destination)
    return destination


def _get_input_text() -> str:
    """
    Resolve input text from meeting notes or uploaded audio.
    Meeting notes take priority when both are provided.
    """
    notes = request.form.get("meeting_notes", "")
    if notes is not None:
        notes = notes.strip()
    else:
        notes = ""

    if notes:
        return notes

    audio_file = _get_uploaded_audio_file()
    if audio_file is None:
        return ""

    audio_path = None
    try:
        audio_path = _save_uploaded_audio(audio_file)
        return transcribe_audio(audio_path)
    finally:
        if audio_path and audio_path.exists():
            audio_path.unlink(missing_ok=True)


@app.before_request
def ensure_database():
    if not getattr(app, "_db_initialized", False):
        database.init_db()
        app._db_initialized = True


@app.route("/")
def index():
    return render_template(
        "index.html",
        summary_styles=SUMMARY_STYLES,
        enable_auth=ENABLE_AUTH,
    )


@app.route("/summarize", methods=["POST"])
def summarize():
    style = normalize_style(_get_form_field("style"))

    try:
        meeting_notes = _get_input_text()
    except TranscriptionError as exc:
        return jsonify({"error": exc.message}), 400

    if not meeting_notes:
        return jsonify(
            {"error": "Please provide either meeting notes or audio."}
        ), 400

    try:
        summary = generate_summary(meeting_notes, style=style)
    except SummaryGenerationError as exc:
        return jsonify({"error": exc.message}), 503

    summary_id = None
    if current_user.is_authenticated:
        summary_id = database.save_summary(
            user_id=current_user.id,
            original_text=meeting_notes,
            summary_text=summary,
            style=style,
        )

    return jsonify(
        {
            "summary": summary,
            "style": style,
            "style_label": SUMMARY_STYLES[style],
            "saved": summary_id is not None,
            "summary_id": summary_id,
        }
    )


@app.route("/history")
def history():
    if not ENABLE_AUTH:
        flash("History is available when authentication is enabled.", "info")
        return redirect(url_for("index"))
    if not current_user.is_authenticated:
        return redirect(url_for("login", next=request.url))

    rows = database.get_summaries_for_user(current_user.id)
    return render_template(
        "history.html",
        summaries=rows,
        summary_styles=SUMMARY_STYLES,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if not ENABLE_AUTH:
        flash("Authentication is disabled.", "warning")
        return redirect(url_for("index"))

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            user = register_user(
                request.form.get("username", ""),
                request.form.get("password", ""),
            )
            login_user(user)
            flash("Account created. You are now logged in.", "success")
            return redirect(url_for("index"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if not ENABLE_AUTH:
        flash("Authentication is disabled.", "warning")
        return redirect(url_for("index"))

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        user = authenticate_user(
            request.form.get("username", ""),
            request.form.get("password", ""),
        )
        if user is None:
            flash("Invalid username or password.", "danger")
        else:
            login_user(user)
            flash("Welcome back!", "success")
            next_page = request.args.get("next") or url_for("index")
            return redirect(next_page)

    return render_template("login.html")


@app.route("/logout")
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    database.init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.run(host="127.0.0.1", port=5000, debug=False)
