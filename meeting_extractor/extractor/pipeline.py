from datetime import date
from typing import List
from .preprocess import parse_transcript
from .rule_extractor import extract_rules
from .validate import validate
from .schema import ActionItem


def run(transcript: str, meeting_date: date, mode: str = "rule") -> List[ActionItem]:
    """mode = 'rule' (offline) or 'llm' (needs API key)."""
    sentences = parse_transcript(transcript)
    if mode == "llm":
        from .llm_extractor import extract_llm
        items = extract_llm(sentences, meeting_date)
    else:
        items = extract_rules(sentences, meeting_date)
    return validate(items, meeting_date)
