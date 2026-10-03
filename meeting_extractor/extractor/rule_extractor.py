"""Step 3 (offline version): rule-based information extraction. No API key needed."""
import re
from datetime import date
from typing import List
from .schema import ActionItem
from .preprocess import Sentence
from .dates import find_date

ACTION_VERBS = set("""send share book update prepare review create schedule finish complete fix write call email
check draft submit organize organise test deploy contact arrange collect order confirm make build upload post
circulate plan research publish design set follow present compile finalize finalise assign notify
remind setup clean migrate document merge release approve sign print buy""".split())
NAME = r"[A-Z][a-z]+"


def _candidates(s: str, speaker: str, names: set):
    """Yield (owner, task, pattern_strength) for each pattern that matches the sentence."""
    m = re.search(rf"\b(?P<n>{NAME}),\s+(?:please\s+|(?:can|could|would|will)\s+you\s+(?:please\s+)?)(?P<t>.+)", s)
    if m and m["n"] in names:
        yield m["n"], m["t"], 0.15
    m = re.search(rf"\b(?P<n>{NAME})\s+(?:will|is going to|needs to|should)\s+(?P<t>.+)", s)
    if m and m["n"] in names:
        yield m["n"], m["t"], 0.10
    m = re.search(r"\bI(?:'ll|\s+will|\s+can|\s+need to|\s+have to|\s+am going to|'m going to)\s+(?P<t>.+)", s)
    if m:
        yield speaker.split()[0], m["t"], 0.10
    m = re.search(r"\b(?:we|you all)\s+(?:also\s+)?(?:need to|should|have to|must)\s+(?P<t>.+)", s, re.I)
    if m:
        yield None, m["t"], 0.0


def extract_rules(sentences: List[Sentence], ref: date) -> List[ActionItem]:
    names = {s.speaker.split()[0] for s in sentences}
    items = []
    for sent in sentences:
        for owner, task, bonus in _candidates(sent.text, sent.speaker, names):
            task = re.sub(r"^(also|please|then)\s+", "", task.strip(), flags=re.I)
            if not task or task.split()[0].lower() not in ACTION_VERBS:
                continue                                  # not a real action verb -> try next pattern
            d, _ = find_date(sent.text, ref)              # deadline anywhere in the sentence
            _, span = find_date(task, ref)
            if span:
                task = task[:span[0]] + task[span[1]:]
            task = re.sub(r"\s+", " ", task).strip(" .,!?;:")
            if len(task.split()) < 2:
                continue
            conf = 0.55 + bonus + (0.15 if owner else 0) + (0.15 if d else 0)
            flags = ["invalid_date"] if (span and d is None) else []
            items.append(ActionItem(
                task=task[0].upper() + task[1:], owner=owner,
                deadline=d.isoformat() if d else None,
                confidence=round(min(conf, 0.99), 2),
                source_sentence=sent.text, flags=flags))
            break                                         # one action item per sentence
    return items
