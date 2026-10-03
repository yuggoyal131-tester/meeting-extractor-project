"""Step 3 (LLM version): uses the Anthropic API. Needs `pip install anthropic` and ANTHROPIC_API_KEY."""
import json, re
from datetime import date
from typing import List
from .schema import ActionItem
from .preprocess import Sentence

SYSTEM = """You are a meeting assistant. From the transcript, extract every ACTION ITEM
(a task someone committed to or was asked to do). Return ONLY a JSON list, no prose, no markdown.
Each element: {"task": str, "owner": str|null, "deadline": "YYYY-MM-DD"|null,
"confidence": number 0-1, "source_sentence": str}.
Rules: resolve relative dates (e.g. "next Friday") using the meeting date given.
Use null when the owner or deadline is not stated. Do not invent owners or dates.
Do not include discussion, opinions or decisions that are not tasks."""

CHUNK, OVERLAP = 40, 5


def _chunks(sentences):
    i = 0
    while i < len(sentences):
        yield sentences[i:i + CHUNK]
        if i + CHUNK >= len(sentences):
            break
        i += CHUNK - OVERLAP


def extract_llm(sentences: List[Sentence], ref: date, model: str = "claude-sonnet-4-6") -> List[ActionItem]:
    import anthropic
    client = anthropic.Anthropic()
    items = []
    for chunk in _chunks(sentences):
        transcript = "\n".join(f"{s.speaker}: {s.text}" for s in chunk)
        msg = client.messages.create(
            model=model, max_tokens=2000, system=SYSTEM,
            messages=[{"role": "user",
                       "content": f"Meeting date: {ref.isoformat()} ({ref.strftime('%A')})\n\nTranscript:\n{transcript}"}])
        text = re.sub(r"^```(?:json)?|```$", "", msg.content[0].text.strip(), flags=re.M).strip()
        try:
            for d in json.loads(text):
                items.append(ActionItem(
                    task=str(d.get("task", "")).strip(), owner=d.get("owner"),
                    deadline=d.get("deadline"), confidence=float(d.get("confidence", 0.5)),
                    source_sentence=d.get("source_sentence", "")))
        except (json.JSONDecodeError, TypeError, AttributeError):
            continue          # bad JSON from the model: skip this chunk instead of crashing
    return items
