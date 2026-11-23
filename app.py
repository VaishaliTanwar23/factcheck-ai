import streamlit as st
import pandas as pd
import fitz
from factcheck import extract_claims, verify_claim

st.set_page_config(page_title="FactCheck AI", page_icon="🔎", layout="wide")
st.title("🔎 FactCheck AI")
st.write("**Your PDF truth layer** — extract checkable claims, search live web evidence, and review the findings.")

with st.sidebar:
    st.header("How it works")
    st.write("1. Upload a text-based PDF")
    st.write("2. Extract claims containing figures or dates")
    st.write("3. Search the live web for each claim")
    st.write("4. Review source links and download a report")
    st.divider()
    st.caption("No paid AI/search API key is required. Public search can be rate-limited.")

st.info("This tool is an evidence assistant. It does not treat missing search results as proof that a statement is false. Always open and review the cited sources.")

uploaded = st.file_uploader("Choose a PDF", type=["pdf"])
max_claims = st.slider("Maximum claims to check", min_value=5, max_value=30, value=15)

if uploaded:
    if st.button("Extract claims and fact-check", type="primary", use_container_width=True):
        try:
            pdf = fitz.open(stream=uploaded.getvalue(), filetype="pdf")
            pages = [p.get_text("text") for p in pdf]
            text = "\n".join(pages)
            if not text.strip():
                st.error("No selectable text found. This appears to be a scanned PDF. OCR is not included in this version.")
                st.stop()

            claims = extract_claims(text)[:max_claims]
            if not claims:
                st.warning("No candidate claims containing numbers, percentages, currency or dates were detected.")
                st.stop()

            st.write(f"Found **{len(claims)} candidate claims** across **{len(pages)} pages**.")
            results = []
            progress = st.progress(0)
            for idx, claim in enumerate(claims):
                result = verify_claim(claim)
                results.append(result)
                progress.progress((idx + 1) / len(claims))
            st.session_state["results"] = results
            st.session_state["filename"] = uploaded.name
        except Exception as exc:
            st.error(f"Could not process this PDF: {exc}")

if "results" in st.session_state:
    results = st.session_state["results"]
    df = pd.DataFrame([{
        "Claim": r["claim"],
        "Status": r["status"],
        "Finding": r["finding"],
        "Suggested correction": r["correction"],
        "Sources": " | ".join(s["url"] for s in r["sources"] if s.get("url"))
    } for r in results])

    st.subheader("Verification summary")
    a, b, c = st.columns(3)
    a.metric("Verified", int((df["Status"] == "Verified").sum()))
    b.metric("Inaccurate", int((df["Status"] == "Inaccurate").sum()))
    c.metric("False / unsupported", int((df["Status"] == "False / Unsupported").sum()))

    for n, r in enumerate(results, 1):
        status = r["status"]
        icon = "🟢" if status == "Verified" else "🟠" if status == "Inaccurate" else "🔴"
        with st.expander(f"{icon} {status} — {r['claim'][:125]}"):
            st.markdown("**Claim found in PDF**")
            st.write(r["claim"])
            st.markdown("**Finding**")
            st.write(r["finding"])
            st.markdown("**Possible correction / context**")
            st.write(r["correction"])
            st.markdown("**Web evidence**")
            if r["sources"]:
                for src in r["sources"]:
                    st.markdown(f"- [{src['title'] or src['url']}]({src['url']})")
                    if src.get("snippet"):
                        st.caption(src["snippet"])
            else:
                st.write("No usable results were returned. This does not prove the claim is false.")

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Download results as CSV", csv, "factcheck_report.csv", "text/csv")
    st.caption("Review publication date, source authority, geography, definitions and methodology before accepting any finding.")
else:
    st.markdown("### What you get")
    st.write("- Candidate claims extracted from the PDF")
    st.write("- A status for each claim")
    st.write("- Search-result evidence and clickable source links")
    st.write("- Downloadable CSV report")
