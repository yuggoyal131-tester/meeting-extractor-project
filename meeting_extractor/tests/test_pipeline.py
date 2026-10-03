import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date
from extractor.dates import find_date
from extractor.schema import ActionItem
from extractor.validate import validate

REF = date(2026, 10, 1)  # a Thursday


def test_dates():
    assert find_date("by Friday", REF)[0] == date(2026, 10, 2)
    assert find_date("next Monday", REF)[0] == date(2026, 10, 5)
    assert find_date("tomorrow", REF)[0] == date(2026, 10, 2)
    assert find_date("on October 9", REF)[0] == date(2026, 10, 9)
    assert find_date("by February 30", REF)[0] is None      # invalid date


def test_missing_owner_and_past_date():
    out = validate([ActionItem("Send the report", None, "2026-09-01", 0.9)], REF)
    assert out[0].status == "needs_review"
    assert {"missing_owner", "past_deadline"} <= set(out[0].flags)


def test_duplicates_merged():
    a = ActionItem("Update the website pricing", None, None, 0.6)
    b = ActionItem("Update the pricing page", "Rohan", "2026-10-05", 0.9)
    out = validate([a, b], REF)
    assert len(out) == 1 and out[0].owner == "Rohan" and out[0].deadline == "2026-10-05"


if __name__ == "__main__":
    test_dates(); test_missing_owner_and_past_date(); test_duplicates_merged()
    print("all 3 tests passed")
