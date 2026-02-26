"""
CAT Tool (Computer-Assisted Translation) - Streamlit App
=========================================================
A lightweight, web-based CAT tool for translation students and professionals.

To run:
    pip install streamlit
    streamlit run app.py

To change the Tag regex pattern, find the TAG_PATTERN constant below and update it.
"""

import re
import streamlit as st

# ─────────────────────────────────────────────
# TAG CONFIGURATION
# ─────────────────────────────────────────────
# Modify this regex to match whatever tag format your files use.
# Current pattern matches:
#   {1}, {tag_name}        → curly-brace tags
#   [tag], [/tag]          → square-bracket tags
#   <b>, </b>, <br/>       → XML/HTML tags
TAG_PATTERN = r"(\{[^}]+\}|\[[^\]]+\]|<[^>]+>)"


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def segment_text(text: str) -> list[str]:
    """
    Split text into segments (sentences).
    Strategy: split on sentence-ending punctuation followed by whitespace/newline.
    Blank lines also act as segment boundaries.
    """
    # First split on blank lines
    paragraphs = re.split(r"\n\s*\n", text.strip())
    segments = []
    for para in paragraphs:
        # Split on . ! ? followed by a space or end-of-string
        # Keep the delimiter attached to the preceding sentence
        sents = re.split(r"(?<=[.!?])\s+", para.strip())
        for s in sents:
            s = s.strip()
            if s:
                segments.append(s)
    return segments


def extract_tags(text: str) -> list[str]:
    """Return all tags found in a text string."""
    return re.findall(TAG_PATTERN, text)


def highlight_tags_html(text: str) -> str:
    """
    Return an HTML string where tags are wrapped in a styled <span>.
    Used to visually highlight tags in the source column.
    """
    def replacer(m):
        tag = m.group(0)
        return (
            f'<span style="background:#FFF3CD;color:#856404;'
            f'border:1px solid #FFEEBA;border-radius:3px;'
            f'padding:0 4px;font-family:monospace;font-size:0.85em;">'
            f'{tag}</span>'
        )
    return re.sub(TAG_PATTERN, replacer, text)


def check_missing_tags(source: str, translation: str) -> list[str]:
    """Return a list of tags present in source but absent in translation."""
    src_tags = extract_tags(source)
    tgt_tags = extract_tags(translation)
    missing = []
    # Check each source tag occurrence
    src_copy = src_tags[:]
    tgt_copy = tgt_tags[:]
    for t in src_copy:
        if t in tgt_copy:
            tgt_copy.remove(t)
        else:
            missing.append(t)
    return missing


def build_download_content(segments: list[str], translations: dict) -> str:
    """Assemble the final translated text in segment order."""
    lines = []
    for i, seg in enumerate(segments):
        lines.append(translations.get(i, ""))
    return "\n\n".join(lines)


# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

CUSTOM_CSS = """
<style>
/* ── Page base ── */
[data-testid="stAppViewContainer"] {
    background: #F8F9FA;
}
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E0E0E0;
}

/* ── Header ── */
.cat-header {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%);
    color: #FFFFFF;
    padding: 1.4rem 2rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.cat-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
.cat-header p  { margin: 0; font-size: 0.85rem; opacity: 0.75; }

/* ── Column headers ── */
.col-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6C757D;
    padding: 0.4rem 0.6rem;
    border-bottom: 2px solid #DEE2E6;
    margin-bottom: 0.5rem;
}

/* ── Segment card ── */
.segment-card {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    transition: box-shadow 0.15s ease;
    line-height: 1.6;
    font-size: 0.9rem;
    color: #212529;
    min-height: 60px;
}
.segment-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-color: #ADB5BD;
}
.segment-number {
    font-size: 0.7rem;
    color: #ADB5BD;
    font-weight: 600;
    margin-bottom: 4px;
}

/* ── Warning badge ── */
.tag-warning {
    background: #FFF3CD;
    color: #856404;
    border: 1px solid #FFEEBA;
    border-radius: 4px;
    font-size: 0.75rem;
    padding: 2px 6px;
    margin-top: 4px;
    display: inline-block;
}

/* ── Stats bar ── */
.stats-bar {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
    font-size: 0.82rem;
    color: #495057;
}
.stat-item strong { color: #1A1A2E; }

/* ── Textarea override ── */
textarea {
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    border-radius: 6px !important;
    border: 1px solid #CED4DA !important;
    background: #FDFDFD !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
textarea:focus {
    border-color: #4A90E2 !important;
    box-shadow: 0 0 0 3px rgba(74,144,226,0.15) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #1A1A2E;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1.4rem;
    font-weight: 600;
    transition: background 0.2s;
}
[data-testid="stDownloadButton"] button:hover {
    background: #16213E;
}
</style>
"""


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="CAT Tool",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── Session state initialisation ──
    if "segments" not in st.session_state:
        st.session_state.segments = []
    if "translations" not in st.session_state:
        st.session_state.translations = {}
    if "source_lang" not in st.session_state:
        st.session_state.source_lang = "English"
    if "target_lang" not in st.session_state:
        st.session_state.target_lang = "French"

    # ── Header ──
    st.markdown(
        """
        <div class="cat-header">
            <div>
                <h1>🌐 CAT Tool &nbsp;—&nbsp; Translation Workbench</h1>
                <p>Computer-Assisted Translation · Lightweight · No installation required</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ─────────────────────────────────────────
    # SIDEBAR — Project settings & file upload
    # ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Project Settings")
        st.session_state.source_lang = st.text_input(
            "Source language", value=st.session_state.source_lang
        )
        st.session_state.target_lang = st.text_input(
            "Target language", value=st.session_state.target_lang
        )

        st.markdown("---")
        st.markdown("### 📂 Load Source Text")
        input_method = st.radio("Input method", ["Upload .txt file", "Paste text"])

        raw_text = ""
        if input_method == "Upload .txt file":
            uploaded = st.file_uploader("Choose a .txt file", type=["txt"])
            if uploaded:
                raw_text = uploaded.read().decode("utf-8", errors="replace")
        else:
            raw_text = st.text_area(
                "Paste your source text here",
                height=220,
                placeholder="Enter or paste the text to translate…",
            )

        if st.button("▶ Load & Segment", use_container_width=True):
            if raw_text.strip():
                segs = segment_text(raw_text)
                st.session_state.segments = segs
                # Preserve existing translations; reset only new segment slots
                for i in range(len(segs)):
                    if i not in st.session_state.translations:
                        st.session_state.translations[i] = ""
                st.success(f"✅ {len(segs)} segment(s) loaded.")
            else:
                st.warning("Please provide some source text first.")

        st.markdown("---")
        st.markdown("### 🏷️ Tag Pattern")
        st.code(TAG_PATTERN, language="regex")
        st.caption("Edit `TAG_PATTERN` in the source code to match your tag format.")

        st.markdown("---")
        if st.button("🗑️ Clear all translations", use_container_width=True):
            st.session_state.translations = {
                i: "" for i in range(len(st.session_state.segments))
            }
            st.rerun()

    # ─────────────────────────────────────────
    # MAIN AREA — Stats bar
    # ─────────────────────────────────────────
    segments = st.session_state.segments
    translations = st.session_state.translations

    if segments:
        filled = sum(1 for i in range(len(segments)) if translations.get(i, "").strip())
        pct = int(filled / len(segments) * 100) if segments else 0

        st.markdown(
            f"""
            <div class="stats-bar">
                <span class="stat-item">Segments: <strong>{len(segments)}</strong></span>
                <span class="stat-item">Translated: <strong>{filled}</strong></span>
                <span class="stat-item">Remaining: <strong>{len(segments) - filled}</strong></span>
                <span class="stat-item">Progress: <strong>{pct}%</strong></span>
                <span class="stat-item">
                    {st.session_state.source_lang} → {st.session_state.target_lang}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Progress bar
        st.progress(pct / 100)

    # ─────────────────────────────────────────
    # MAIN AREA — Translation grid
    # ─────────────────────────────────────────
    if not segments:
        st.info(
            "👈 Upload a .txt file or paste text in the sidebar, then click **Load & Segment** to begin."
        )
    else:
        # Column headers
        hdr_left, hdr_right = st.columns(2)
        with hdr_left:
            st.markdown(
                f'<div class="col-header">🔵 Source — {st.session_state.source_lang}</div>',
                unsafe_allow_html=True,
            )
        with hdr_right:
            st.markdown(
                f'<div class="col-header">✏️ Translation — {st.session_state.target_lang}</div>',
                unsafe_allow_html=True,
            )

        # Render each segment row
        for i, seg in enumerate(segments):
            col_src, col_tgt = st.columns(2, gap="medium")

            # ── Source column ──
            with col_src:
                highlighted = highlight_tags_html(seg)
                st.markdown(
                    f"""
                    <div class="segment-card">
                        <div class="segment-number">#{i + 1}</div>
                        {highlighted}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ── Target column ──
            with col_tgt:
                current_val = st.session_state.translations.get(i, "")
                new_val = st.text_area(
                    label=f"seg_{i}",
                    value=current_val,
                    key=f"ta_{i}",
                    label_visibility="collapsed",
                    height=80,
                    placeholder=f"Translate segment #{i + 1} here…",
                )
                # Save to session state on every interaction
                st.session_state.translations[i] = new_val

                # Tag protection warning
                missing = check_missing_tags(seg, new_val)
                if new_val.strip() and missing:
                    missing_str = " ".join(
                        [f'<code style="font-size:0.78em">{t}</code>' for t in missing]
                    )
                    st.markdown(
                        f'<div class="tag-warning">⚠️ Missing tag(s): {missing_str}</div>',
                        unsafe_allow_html=True,
                    )

        # ─────────────────────────────────────
        # EXPORT
        # ─────────────────────────────────────
        st.markdown("---")
        ex_col1, ex_col2 = st.columns([3, 1])
        with ex_col1:
            st.markdown(
                "**Download** your translation as a `.txt` file, with segments separated by blank lines."
            )
        with ex_col2:
            export_content = build_download_content(segments, translations)
            st.download_button(
                label="⬇️ Export Translation",
                data=export_content.encode("utf-8"),
                file_name=f"translation_{st.session_state.target_lang.lower()}.txt",
                mime="text/plain",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
