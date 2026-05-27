"""Ollama-powered meeting notes summarization."""

from ollama import Client, ResponseError

from config import DEFAULT_SUMMARY_STYLE, OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT, SUMMARY_STYLES

STYLE_PROMPTS = {
    "executive": (
        "You are an expert executive assistant. Summarize the meeting notes as a "
        "concise executive summary in 1–3 short paragraphs. Highlight outcomes and "
        "next steps."
    ),
    "bullet_points": (
        "You are an expert meeting note taker. Summarize the meeting notes as clear "
        "bullet points grouped by topic. Keep each bullet short and scannable."
    ),
    "action_items": (
        "You are an expert project coordinator. Extract action items from the meeting "
        "notes. For each item include: task, owner (if known), and deadline (if known). "
        "Use a numbered or bulleted list."
    ),
}


class SummaryGenerationError(Exception):
    """Raised when Ollama cannot produce a summary."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def normalize_style(style: str) -> str:
    style = (style or DEFAULT_SUMMARY_STYLE).strip().lower()
    if style not in SUMMARY_STYLES:
        return DEFAULT_SUMMARY_STYLE
    return style


def _ollama_client() -> Client:
    return Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)


def generate_summary(text: str, style: str = DEFAULT_SUMMARY_STYLE) -> str:
    """Generate a meeting-notes summary using Ollama Mistral."""
    notes = text.strip()
    if not notes:
        raise SummaryGenerationError("No meeting notes provided.")

    style = normalize_style(style)
    system_prompt = STYLE_PROMPTS[style]

    try:
        response = _ollama_client().chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Summarize the following meeting notes:\n\n{notes}",
                },
            ],
        )
    except ConnectionError:
        raise SummaryGenerationError(
            "Cannot reach Ollama. Make sure Ollama is running "
            "(open the Ollama app or run `ollama serve`), then try again."
        ) from None
    except ResponseError as exc:
        error_text = str(exc).lower()
        if exc.status_code == 404 or "not found" in error_text:
            raise SummaryGenerationError(
                f"Model '{OLLAMA_MODEL}' is not available. "
                f"Run: ollama pull {OLLAMA_MODEL}"
            ) from exc
        raise SummaryGenerationError(f"Ollama error: {exc}") from exc
    except Exception as exc:
        raise SummaryGenerationError(
            f"Failed to generate summary: {exc}"
        ) from exc

    content = (response.message.content or "").strip()
    if not content:
        raise SummaryGenerationError(
            "Ollama returned an empty summary. Please try again."
        )
    return content
