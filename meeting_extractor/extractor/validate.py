"""Step 5: validation rules: dates, missing owners, duplicate tasks."""
import re
from datetime import date, timedelta
from difflib import SequenceMatcher
from typing import List
from .schema import ActionItem

STOP = set("the a an to of for with and in on at it this that we our your their about by is be".split())
REVIEW_FLAGS = {"missing_owner", "invalid_date", "past_deadline", "far_future", "low_confidence"}
DUP_OVERLAP, DUP_RATIO, LOW_CONF = 0.6, 0.85, 0.6


def _tokens(t: str):
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP}


def is_duplicate(a: str, b: str) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / min(len(ta), len(tb))
    return overlap >= DUP_OVERLAP or SequenceMatcher(None, a.lower(), b.lower()).ratio() >= DUP_RATIO


def _merge(a: ActionItem, b: ActionItem) -> ActionItem:
    best, other = (a, b) if a.confidence >= b.confidence else (b, a)
    best.owner = best.owner or other.owner           # fill gaps from the duplicate
    best.deadline = best.deadline or other.deadline
    best.confidence = max(a.confidence, b.confidence)
    best.flags = sorted(set(best.flags) | set(other.flags) | {"merged_duplicate"})
    return best


def validate(items: List[ActionItem], ref: date) -> List[ActionItem]:
    # 1. normalise + drop junk
    clean = []
    for it in items:
        it.task = it.task.strip()
        if len(it.task.split()) < 2:
            continue
        it.owner = it.owner.strip().title() if it.owner and it.owner.strip() else None
        if it.deadline:
            try:
                date.fromisoformat(it.deadline)
            except (ValueError, TypeError):
                it.deadline = None
                it.flags.append("invalid_date")
        clean.append(it)
    # 2. merge duplicate tasks
    merged: List[ActionItem] = []
    for it in clean:
        for i, kept in enumerate(merged):
            if is_duplicate(it.task, kept.task):
                merged[i] = _merge(kept, it)
                break
        else:
            merged.append(it)
    # 3. flags + status (after merging, so filled-in owners count)
    for it in merged:
        flags = set(it.flags)
        if not it.owner:
            flags.add("missing_owner")
        if it.deadline:
            d = date.fromisoformat(it.deadline)
            if d < ref:
                flags.add("past_deadline")
            elif d > ref + timedelta(days=365):
                flags.add("far_future")
        if it.confidence < LOW_CONF:
            flags.add("low_confidence")
        it.flags = sorted(flags)
        it.status = "needs_review" if flags & REVIEW_FLAGS else "open"
    return merged
