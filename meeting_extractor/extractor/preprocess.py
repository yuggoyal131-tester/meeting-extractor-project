"""Step 2: clean the transcript and split it by speaker and sentence."""
import re
from dataclasses import dataclass
from typing import List

LINE = re.compile(
    r"^\s*(?:\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*)?"   # optional timestamp
    r"(?P<sp>[A-Z][\w .'-]{0,30}?)\s*:\s*(?P<tx>.+)$"
)
FILLERS = re.compile(r"\b(?:um+|uh+|erm|er|you know|i mean)\b[,]?\s*", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")


@dataclass
class Sentence:
    speaker: str
    text: str


def parse_transcript(raw: str) -> List[Sentence]:
    raw = raw.replace("\u2019", "'").replace("\u2018", "'")
    turns = []  # (speaker, text)
    for line in raw.splitlines():
        if not line.strip():
            continue
        m = LINE.match(line)
        if m:
            turns.append([m["sp"].strip(), m["tx"].strip()])
        elif turns:                       # continuation of previous turn
            turns[-1][1] += " " + line.strip()
    out = []
    for speaker, text in turns:
        text = FILLERS.sub("", text)
        text = re.sub(r"\s+", " ", text).strip()
        for s in SENT_SPLIT.split(text):
            s = s.strip()
            if s:
                out.append(Sentence(speaker, s[0].upper() + s[1:]))
    return out
