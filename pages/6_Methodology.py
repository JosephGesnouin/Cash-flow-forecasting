"""In-app rendering of the methodology document."""
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Methodology", page_icon="📘", layout="wide")
st.title("📘 Methodology")

doc = Path(__file__).resolve().parents[1] / "docs" / "METHODOLOGY.md"
st.markdown(doc.read_text(encoding="utf-8"))
