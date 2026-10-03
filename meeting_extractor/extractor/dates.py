"""Resolve phrases like 'by Friday' or 'next Monday' into real dates."""
import re, calendar
from datetime import date, timedelta
from typing import Optional, Tuple

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
MON = "|".join(sorted(MONTHS, key=len, reverse=True))
WD = "|".join(WEEKDAYS)
PRE = r"(?:\b(?:by|on|before|until|due|for)\s+)?"
NUMS = {"a": 1, "one": 1, "two": 2, "three": 3}

PATTERNS = [
    ("iso", PRE + r"\b(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})\b"),
    ("md", PRE + rf"\b(?P<m>{MON})\.?\s+(?P<d>\d{{1,2}})(?:st|nd|rd|th)?\b"),
    ("dm", PRE + rf"\b(?P<d>\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?(?P<m>{MON})\b"),
    ("rel", PRE + r"\b(?P<w>today|tomorrow|tonight)\b"),
    ("inN", r"\bin\s+(?P<n>\d+|a|one|two|three)\s+(?P<u>day|week)s?\b"),
    ("eow", PRE + r"\bend of (?:the |this )?(?P<u>week|month)\b"),
    ("eod", PRE + r"\b(?:eod|end of (?:the )?day)\b"),
    ("wd", PRE + rf"\b(?:(?P<n>next|this|coming)\s+)?(?P<w>{WD})\b"),
]


def find_date(text: str, ref: date) -> Tuple[Optional[date], Optional[Tuple[int, int]]]:
    """Return (date, (start, end)). date is None if nothing found or the date is invalid."""
    for kind, pat in PATTERNS:
        m = re.search(pat, text, re.I)
        if not m:
            continue
        span = m.span()
        g = {k: (v.lower() if v else v) for k, v in m.groupdict().items()}
        try:
            if kind == "iso":
                return date(int(g["y"]), int(g["m"]), int(g["d"])), span
            if kind in ("md", "dm"):
                d = date(ref.year, MONTHS[g["m"]], int(g["d"]))
                if d < ref - timedelta(days=30):   # clearly meant next year
                    d = d.replace(year=ref.year + 1)
                return d, span
            if kind == "rel":
                return ref + timedelta(days=1 if g["w"] == "tomorrow" else 0), span
            if kind == "inN":
                n = int(g["n"]) if g["n"].isdigit() else NUMS[g["n"]]
                return ref + timedelta(days=n * (7 if g["u"] == "week" else 1)), span
            if kind == "eow":
                if g["u"] == "month":
                    return date(ref.year, ref.month, calendar.monthrange(ref.year, ref.month)[1]), span
                return ref + timedelta(days=(4 - ref.weekday()) % 7), span
            if kind == "eod":
                return ref, span
            if kind == "wd":
                idx = WEEKDAYS.index(g["w"])
                if g["n"] == "next":            # that weekday in the next calendar week
                    return ref + timedelta(days=7 - ref.weekday() + idx), span
                delta = (idx - ref.weekday()) % 7 or 7
                return ref + timedelta(days=delta), span
        except ValueError:                       # e.g. February 30
            return None, span
    return None, None
