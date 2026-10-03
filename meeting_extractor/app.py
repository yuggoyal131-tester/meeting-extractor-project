"""Step 6b: upload-to-results interface.  Run:  streamlit run app.py"""
from datetime import date
import pandas as pd
import streamlit as st
from extractor.pipeline import run

st.set_page_config(page_title="Meeting Action-Item Extractor", layout="wide")
st.title("AI Meeting Action-Item Extractor")
st.caption("Upload a transcript and get structured action items: task, owner, deadline, confidence.")

with st.sidebar:
    meeting_date = st.date_input("Meeting date", value=date.today(),
                                 help="Used to turn 'next Friday' into a real date")
    mode_label = st.radio("Extraction engine", ["Rule-based (offline)", "LLM (needs API key)"])
    st.markdown("Transcript format: `Speaker: sentence`")

up = st.file_uploader("Upload transcript (.txt)", type=["txt"])
text = up.read().decode("utf-8", errors="ignore") if up else st.text_area("...or paste it here", height=220)

if st.button("Extract action items", type="primary") and text.strip():
    try:
        items = run(text, meeting_date, "llm" if mode_label.startswith("LLM") else "rule")
    except Exception as e:
        st.error(f"Extraction failed: {e}"); st.stop()
    if not items:
        st.warning("No action items found."); st.stop()
    df = pd.DataFrame([i.to_dict() for i in items])
    df["flags"] = df["flags"].apply(", ".join)
    c1, c2, c3 = st.columns(3)
    c1.metric("Action items", len(df))
    c2.metric("Need review", int((df.status == "needs_review").sum()))
    c3.metric("Avg confidence", f"{df.confidence.mean():.2f}")
    show = df[["task", "owner", "deadline", "confidence", "status", "flags", "source_sentence"]]
    st.dataframe(show.style.apply(
        lambda r: ["background-color:#FFF3CD" if r.status == "needs_review" else "" for _ in r], axis=1),
        use_container_width=True, hide_index=True)
    st.download_button("Download CSV", show.to_csv(index=False), "action_items.csv", "text/csv")
