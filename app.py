from urllib.parse import quote

import streamlit as st
from scraper import scrape_article
from analyzer import analyze
from scoring import compute_score, grade_from_score, explain_score
from ratelimit import check_limits
from db import save_analysis, load_history

st.set_page_config(page_title="Overwatch", page_icon="🔍")

# ---------- Look and feel ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Space+Grotesk:wght@400;500&family=JetBrains+Mono:wght@500&display=swap');

html, body, [class*="css"], .stMarkdown, p, li {
    font-family: 'Space Grotesk', sans-serif;
}
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
h1 { color: #ff2fa0; }
h2, h3 { color: #e8d9ff; }
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    color: #ff2fa0;
}
[data-testid="stMetricLabel"] {
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.stButton button {
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.1em;
    border: 1px solid #ff2fa0;
    color: #ff2fa0;
    background: transparent;
}
.stButton button:hover {
    background: #ff2fa0;
    color: #0e1117;
}
</style>
""", unsafe_allow_html=True)

st.title("🔍 Overwatch")
st.caption("Open-source intelligence for the truth. Writing, sourcing, and manipulation patterns.")
if not st.user.is_logged_in:
    st.write("Sign in to use Overwatch.")
    if st.button("Sign in with Google"):
        st.login()
    st.stop()

st.sidebar.write(f"Signed in as {st.user.email}")
st.sidebar.button("Log out", on_click=st.logout)

# ---------- Show results ----------
def show_results(article, r):
    score = compute_score(r)

    st.subheader(article["title"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score}/100")
    col2.metric("Grade", grade_from_score(score))
    col3.metric("Confidence", r["confidence"])
    st.caption("This grades writing and sourcing only. Facts are not verified.")
    with st.expander("How this score was calculated"):
        for label, pts in explain_score(r)[1]:
            st.write(f"**{pts:+d}**  {label}")

    st.info(r["summary"])

    st.subheader("Sources")
    st.write(r["source_quality"])

    st.subheader("Bias")
    st.write(r["bias_assessment"])

    st.subheader("Manipulation flags")
    if not r["manipulation_flags"]:
        st.success("None found")
    for f in r["manipulation_flags"]:
        st.warning(f"**{f['type']}**: {f['example']}")

    st.subheader("What to check next")
    for item in r["what_to_check_next"]:
        st.write("•", item)

    images = article.get("images", [])
    if images:
        st.subheader("Image check")
        st.caption(
            "Overwatch cannot detect fakes. These links let you check whether a photo "
            "is old or from a different event. Look at where else it appears and when."
        )
        for img in images:
            try:
                st.image(img, width=220)
            except Exception:
                pass
            lens = "https://lens.google.com/uploadbyurl?url=" + quote(img, safe="")
            tineye = "https://tineye.com/search?url=" + quote(img, safe="")
            st.markdown(f"[Google Lens]({lens})  |  [TinEye]({tineye})")


# ---------- Two ways in ----------
tab_link, tab_text, tab_history = st.tabs(["Paste a link", "Paste the text", "My history"])

with tab_link:
    url = st.text_input("Article link").strip().strip("[]()<>\"' ")
    go_link = st.button("Analyze link") 

with tab_history:
    rows, err = load_history(st.user.email)
    if err:
        st.error(f"Couldn't load history: {err}")
    elif not rows:
        st.write("No saved analyses yet. Analyze an article and it will appear here.")
    for row in rows:
        when = (row.get("created_at") or "")[:10]
        with st.expander(f"{row['grade']} ({row['score']}/100) · {row['title']} · {when}"):
            st.write(row["result"].get("summary", ""))
            st.caption(row.get("url") or "")

with tab_text:
    st.caption("Use this for paywalled sites or sites that block scrapers.")
    pasted = st.text_area("Article text", height=200)
    go_text = st.button("Analyze text")

article = None

try:
    if go_link and url:
        with st.spinner("Scraping the article..."):
            article = scrape_article(url)
    elif go_text and pasted.strip():
        article = {
            "url": "(pasted text)",
            "title": "Pasted text",
            "author": "not found",
            "images": [],
            "text": pasted.strip()[:15000],
        }

    if article:
        allowed, msg = check_limits(st.user.email)
        if not allowed:
            st.warning(msg)
        else:

            with st.spinner("Analyzing... this can take a minute if the AI is busy"):
                r = analyze(article)
            score = compute_score(r)
            saved, save_err = save_analysis(
                st.user.email, article, r, score, grade_from_score(score)
            )
            show_results(article, r)
            if not saved:
                st.caption("This result couldn't be saved to your history.")
except Exception as e:
    st.error(f"Couldn't analyze that: {e}")