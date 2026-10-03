# AI Meeting Action-Item Extractor

Converts meeting transcripts into structured action items: **task, owner, deadline, confidence, status**.

## Setup
    pip install -r requirements.txt

## Run
    streamlit run app.py                                   # web interface (upload -> results)
    python run_extract.py data/meeting_01.txt --date 2026-10-01   # command line, JSON output
    python evaluate.py                                     # precision / recall / F1 on data/
    python tests/test_pipeline.py                          # unit tests for dates + validation

LLM mode: `export ANTHROPIC_API_KEY=...` then `python evaluate.py --llm` or choose "LLM" in the app.

## Structure (maps to the 6 project steps)
| Step | File |
|---|---|
| 1 Gather annotated transcripts | `data/meeting_*.txt` + `meeting_*.json` (ground truth) |
| 2 Clean and segment | `extractor/preprocess.py` |
| 3 Extraction (rules or LLM) | `extractor/rule_extractor.py`, `extractor/llm_extractor.py` |
| 4 Output schema | `extractor/schema.py` |
| 5 Validation rules | `extractor/validate.py`, `extractor/dates.py` |
| 6 Evaluation + interface | `evaluate.py`, `app.py` |

## Transcript format
    Speaker: sentence text
Optional timestamps like `[10:02] Priya: ...` are accepted.
