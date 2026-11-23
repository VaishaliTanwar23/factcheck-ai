import re
from urllib.parse import urlparse
from ddgs import DDGS

NUMBER = re.compile(r'(?<!\w)(?:[$€£₹]\s*)?\d[\d,]*(?:\.\d+)?\s*(?:%|percent|billion|million|trillion|thousand|k|m|bn)?', re.I)
DATE = re.compile(r'\b(?:19|20)\d{2}\b|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,\s*\d{4})?\b', re.I)
STOP = set("the a an and or but of in on at to for from by with is are was were be been being this that these those it its as per than more most less about around approximately".split())

def extract_claims(text):
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    found, seen = [], set()
    for s in sentences:
        s = s.strip(" \n\t•-")
        if len(s) < 28 or len(s) > 550:
            continue
        if NUMBER.search(s) or DATE.search(s):
            key = re.sub(r'\W+', '', s.lower())
            if key not in seen:
                seen.add(key)
                found.append(s)
    return found

def tokens(text):
    return {w for w in re.findall(r'[a-zA-Z]{3,}', text.lower()) if w not in STOP}

def search_claim(claim):
    # Public DuckDuckGo search; no key. May be throttled by provider.
    with DDGS() as ddgs:
        return list(ddgs.text(claim, max_results=5))

def verify_claim(claim):
    try:
        raw = search_claim(claim)
    except Exception as e:
        return {
            "claim": claim, "status": "False / Unsupported",
            "finding": f"Live search could not be completed ({type(e).__name__}). Treat this as unverified, not false.",
            "correction": "Retry the search or check a trusted primary source manually.",
            "sources": []
        }

    claim_tokens = tokens(claim)
    claim_numbers = {x.replace(",", "").strip().lower() for x in NUMBER.findall(claim)}
    candidates = []
    for item in raw:
        title = str(item.get("title", "") or "")
        body = str(item.get("body", "") or "")
        url = str(item.get("href", "") or "")
        combined = title + " " + body
        result_tokens = tokens(combined)
        overlap = len(claim_tokens & result_tokens) / max(1, len(claim_tokens))
        result_numbers = {x.replace(",", "").strip().lower() for x in NUMBER.findall(combined)}
        number_match = bool(claim_numbers & result_numbers)
        candidates.append({
            "title": title, "snippet": body, "url": url,
            "domain": urlparse(url).netloc, "overlap": overlap,
            "number_match": number_match
        })

    # Keep only results that share meaningful subject terms with the claim.
    relevant = [x for x in candidates if x["overlap"] >= 0.18]
    if not relevant:
        status = "False / Unsupported"
        finding = "No sufficiently relevant evidence was found in the returned search results. This is not proof that the claim is false."
        correction = "No reliable corrected figure could be established. Check an authoritative source manually."
    elif any(x["number_match"] for x in relevant):
        status = "Verified"
        finding = "A relevant search result contains at least one numeric value also present in the claim. This is a preliminary match, not full proof of the entire statement."
        correction = "The matching figure appears in the evidence below. Confirm the date, units, population and context in the original source."
    else:
        status = "Inaccurate"
        finding = "Relevant results were found, but the same numeric value was not found in their snippets. The claim may be outdated or inconsistent; inspect the sources before deciding."
        correction = next((x["snippet"] for x in relevant if x["snippet"]), "Search results did not provide a clear replacement figure.")

    relevant.sort(key=lambda x: (x["number_match"], x["overlap"]), reverse=True)
    return {
        "claim": claim, "status": status, "finding": finding,
        "correction": correction, "sources": relevant[:5]
    }
