# FactCheck AI — PDF Fact-Checking Web App

## What it does
- Accepts a text-based PDF.
- Extracts candidate sentences containing numbers, percentages, currencies or dates.
- Searches the live web using the public DuckDuckGo search interface (no API key).
- Shows a preliminary status: Verified, Inaccurate, or False / Unsupported.
- Displays source links and lets users download a CSV report.

## Files
- `app.py` — Streamlit interface.
- `factcheck.py` — PDF claim extraction and evidence-based search logic.
- `requirements.txt` — Python dependencies.
- `README.md` — this guide.
- `DEMO_SCRIPT.md` — 30-second recording guide.
- `SUBMISSION_TEMPLATE.md` — final submission email/document template.
- `sample_trap_document.pdf` — sample document for a basic test.

## Deploy (no API key)
1. Download and unzip this project.
2. Sign in to https://github.com/ and create a **public** repository named `factcheck-ai`.
3. Open the repository and choose **Add file → Upload files**.
4. Upload all files from this folder (including `app.py`, `factcheck.py`, `requirements.txt`, and `README.md`).
5. Commit the upload to the `main` branch.
6. Visit https://share.streamlit.io/ and choose **Continue with GitHub**.
7. Authorize Streamlit to access your GitHub repository.
8. Click **Create app**.
9. Select repository `your-username/factcheck-ai`, branch `main`, and main file path `app.py`.
10. Click **Deploy**. Wait for the build to finish.
11. Copy the public `https://....streamlit.app` URL and test it in an incognito/private browser window.

No API key or Streamlit Secrets are required for this version.

## Test
Upload `sample_trap_document.pdf`. It contains deliberately invented figures. The app should extract the sentences with figures and search for evidence. Do not expect every result to be classified correctly: the current no-key version uses search-result text and numeric matching, not an LLM or a full research-grade fact-checker.

## Important limitations
- Scanned/image-only PDFs are not supported; the PDF must contain selectable text.
- Extraction is rule-based and may miss claims written without numbers or dates.
- Search is a public, keyless search interface and can be rate-limited or temporarily unavailable.
- A numeric match in a search snippet does not prove the full claim is true.
- A missing result does not prove a claim is false. The app labels this "False / Unsupported" and explains the uncertainty.
- Search snippets may omit source dates or context. Open source links and review authority, publication date, units, geography and methodology.
- This is an assessment prototype, not a production-grade legal, financial or scientific verification system.

## Troubleshooting
- **App says ModuleNotFoundError:** confirm all packages are in `requirements.txt`, commit the file, and wait for Streamlit to rebuild.
- **App fails during build:** open the app's Manage app / Logs view in Streamlit Cloud and read the first dependency or Python error.
- **Search returns no results:** retry after a short wait; the public search provider may be throttling.
- **No claims found:** try a PDF with selectable text and clear numerical/date statements. Scanned PDFs need OCR.
- **Repository not visible:** reconnect/authorize GitHub in Streamlit Cloud. You need admin access to the repository.

## Security
Do not upload confidential PDFs to a public demo unless you have permission. Do not commit passwords, tokens or private API keys.
