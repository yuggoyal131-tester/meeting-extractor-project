"""Command-line use: python run_extract.py data/meeting_01.txt --date 2026-10-01 [--llm]"""
import argparse, json
from datetime import date
from extractor.pipeline import run

ap = argparse.ArgumentParser()
ap.add_argument("file"); ap.add_argument("--date", required=True, help="meeting date YYYY-MM-DD")
ap.add_argument("--llm", action="store_true")
a = ap.parse_args()
items = run(open(a.file, encoding="utf-8").read(), date.fromisoformat(a.date), "llm" if a.llm else "rule")
print(json.dumps([i.to_dict() for i in items], indent=2))
