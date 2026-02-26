"""
CAT Tool (Computer-Assisted Translation) - Streamlit App
=========================================================
A lightweight, web-based CAT tool for translation students and professionals.

To run:
    pip install streamlit
    streamlit run app.py

TAG SYSTEM
──────────
This tool uses inline tags to mark up formatting inside the source text.
The translator must copy these tags into the translation — they are preserved
and rendered in the live preview:

    <b>text</b>      → bold
    <i>text</i>      → italic
    <u>text</u>      → underline
    <br/>            → line break
    {1}, {varname}   → variables / placeholders
    [tag], [/tag]    → generic bracket tags

To change the tag regex, edit TAG_PATTERN below.
"""

import re
import streamlit as st
import html as html_lib

# ─────────────────────────────────────────────
# TAG CONFIGURATION
# ─────────────────────────────────────────────
# Modify this regex to match whatever tag format your files use.
# Current pattern matches (in order of priority):
#   <b>, </b>, <br/>, <i>, <u>, <span …>  → XML/HTML formatting tags
#   {1}, {varname}                          → curly-brace variable tags
#   [tag], [/tag]                           → square-bracket tags
TAG_PATTERN = r"(<[^>]+>|\{[^}]+\}|\[[^\]]+\])"

# Tags that carry real formatting and should be RENDERED (not just highlighted)
# in the live preview. Adjust this set freely.
RENDER_TAGS = {"b", "i", "u", "br", "br/", "strong", "em"}


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def segment_text(text: str) -> list[str]:
    """
    Split text into segments (sentences).
    Blank lines are always segment boundaries.
    Within each paragraph, split on . ! ? followed by whitespace.
    """
    paragraphs = re.split(r"\n\s*\n", text.strip())
    segments = []
    for para in paragraphs:
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
    Return an HTML string where tags are visually highlighted in amber.
    Used in the source column to show translators where tags are.
    """
    parts = re.split(TAG_PATTERN, text)
    out = []
    for part in parts:
        if re.fullmatch(TAG_PATTERN, part):
            escaped = html_lib.escape(part)
            out.append(f'<span class="tag-chip">{escaped}</span>')
        else:
            out.append(html_lib.escape(part))
    return "".join(out)


def render_translation_html(text: str) -> str:
    """
    Convert a translation string (with tags) into rendered HTML for the preview.
    Recognised formatting tags (<b>, <i>, <u>, <br/>) are kept as real HTML.
    Unknown tags ({var}, [tag]) are displayed as amber chips.
    Plain text is HTML-escaped.
    """
    parts = re.split(TAG_PATTERN, text)
    out = []
    for part in parts:
        if re.fullmatch(TAG_PATTERN, part):
            # Check if it's a known HTML formatting tag
            inner = part.strip("<>/").split()[0].lower().rstrip("/")
            if inner in RENDER_TAGS:
                out.append(part)   # pass through as real HTML
            else:
                escaped = html_lib.escape(part)
                out.append(f'<span class="tag-chip">{escaped}</span>')
        else:
            out.append(html_lib.escape(part))
    return "".join(out)


def check_missing_tags(source: str, translation: str) -> list[str]:
    """Return a list of tags present in source but absent in translation."""
    src_tags = extract_tags(source)
    tgt_tags = extract_tags(translation)
    src_copy, tgt_copy = src_tags[:], tgt_tags[:]
    missing = []
    for t in src_copy:
        if t in tgt_copy:
            tgt_copy.remove(t)
        else:
            missing.append(t)
    return missing


def build_download_content(segments: list[str], translations: dict) -> str:
    """Assemble the final translated text in segment order."""
    return "\n\n".join(translations.get(i, "") for i in range(len(segments)))


# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

CUSTOM_CSS = """
<style>
/* ── Page base ── */
[data-testid="stAppViewContainer"] {
    background: #F0F2F6;
}

/* ── Sidebar — dark theme for full contrast ── */
[data-testid="stSidebar"] {
    background: #1A1A2E !important;
    border-right: 1px solid #0F3460;
}
/* Force all text inside sidebar to be light */
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stMarkdown {
    color: #E0E0E0 !important;
}
/* Sidebar text inputs */
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] textarea {
    background: #16213E !important;
    color: #F0F0F0 !important;
    border: 1px solid #4A90E2 !important;
    border-radius: 6px !important;
}
/* Sidebar buttons */
[data-testid="stSidebar"] button {
    background: #0F3460 !important;
    color: #FFFFFF !important;
    border: 1px solid #4A90E2 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] button:hover {
    background: #4A90E2 !important;
}
/* Sidebar radio dots and labels */
[data-testid="stSidebar"] [data-testid="stRadio"] label span {
    color: #D0D0D0 !important;
}
/* Sidebar toggle */
[data-testid="stSidebar"] [data-testid="stToggle"] span {
    color: #D0D0D0 !important;
}
/* Sidebar file uploader */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #16213E !important;
    border: 1px dashed #4A90E2 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
[data-testid="stSidebar"] [data-testid="stFileUploader"] p {
    color: #ADB5BD !important;
}
/* Sidebar horizontal rule */
[data-testid="stSidebar"] hr {
    border-color: #0F3460 !important;
    opacity: 1 !important;
}
/* Sidebar code / pre */
[data-testid="stSidebar"] code,
[data-testid="stSidebar"] pre {
    background: #0D1B2A !important;
    color: #7EC8E3 !important;
    border: 1px solid #0F3460 !important;
}
/* Sidebar success/warning messages */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: #16213E !important;
    color: #D0E8FF !important;
}

/* ── Header ── */
.cat-header {
    background: linear-gradient(135deg, #1A1A2E 0%, #0F3460 100%);
    color: #FFFFFF;
    padding: 1.4rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.cat-header h1 { margin:0; font-size:1.6rem; font-weight:700; color:#fff; }
.cat-header p  { margin:.3rem 0 0; font-size:.85rem; opacity:.7; color:#fff; }

/* ── Column headers ── */
.col-header {
    font-size: .72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: #6C757D;
    padding: .4rem .6rem;
    border-bottom: 2px solid #DEE2E6;
    margin-bottom: .5rem;
}

/* ── Segment card (source) ── */
.segment-card {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-left: 3px solid #4A90E2;
    border-radius: 8px;
    padding: .75rem 1rem;
    margin-bottom: .6rem;
    line-height: 1.7;
    font-size: .9rem;
    color: #212529;
    min-height: 68px;
    transition: box-shadow .15s ease;
}
.segment-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,.08); }
.segment-number {
    font-size: .68rem;
    color: #ADB5BD;
    font-weight: 700;
    letter-spacing: .05em;
    margin-bottom: 5px;
}

/* ── Tag chip ── */
.tag-chip {
    background: #FFF3CD;
    color: #856404;
    border: 1px solid #FFEEBA;
    border-radius: 4px;
    padding: 0 5px;
    font-family: 'SFMono-Regular', Consolas, monospace;
    font-size: .8em;
    white-space: nowrap;
}

/* ── Warning badge ── */
.tag-warning {
    background: #FFF3CD;
    color: #856404;
    border: 1px solid #FFEEBA;
    border-radius: 4px;
    font-size: .75rem;
    padding: 3px 8px;
    margin-top: 4px;
    display: inline-block;
}

/* ── Stats bar ── */
.stats-bar {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 8px;
    padding: .65rem 1.2rem;
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 1rem;
    font-size: .82rem;
    color: #495057;
}
.stat-item strong { color: #1A1A2E; }

/* ── Textarea override ── */
textarea {
    font-size: .9rem !important;
    line-height: 1.6 !important;
    border-radius: 6px !important;
    border: 1px solid #CED4DA !important;
    background: #FDFDFD !important;
    transition: border-color .15s, box-shadow .15s !important;
}
textarea:focus {
    border-color: #4A90E2 !important;
    box-shadow: 0 0 0 3px rgba(74,144,226,.18) !important;
}

/* ── Preview panel ── */
.preview-panel {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    line-height: 1.9;
    font-size: .95rem;
    color: #212529;
    min-height: 100px;
}
.preview-panel-title {
    font-size: .72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: #6C757D;
    border-bottom: 2px solid #DEE2E6;
    padding-bottom: .5rem;
    margin-bottom: 1rem;
}
.preview-placeholder { color: #ADB5BD; font-style: italic; }

/* ── Section title ── */
.section-title {
    font-size: .85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .07em;
    color: #495057;
    margin: 1.4rem 0 .8rem;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #1A1A2E !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #0F3460 !important;
}
</style>
"""


# ─────────────────────────────────────────────
# TAG GUIDE HTML (rendered inside sidebar)
# ─────────────────────────────────────────────

TAG_GUIDE_HTML = """
<div style="background:#0D1B2A;border:1px solid #0F3460;border-radius:8px;
            padding:.9rem 1rem;font-size:.78rem;line-height:1.8;margin-top:.3rem;">
  <div style="color:#7EC8E3;font-weight:700;margin-bottom:.5rem;">🏷️ Etiquetas soportadas</div>
  <table style="width:100%;border-collapse:collapse;color:#C8D6E5;">
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">
        &lt;b&gt;…&lt;/b&gt;
      </td>
      <td style="padding:2px 4px;">Negrita</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">
        &lt;i&gt;…&lt;/i&gt;
      </td>
      <td style="padding:2px 4px;">Cursiva</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">
        &lt;u&gt;…&lt;/u&gt;
      </td>
      <td style="padding:2px 4px;">Subrayado</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">
        &lt;br/&gt;
      </td>
      <td style="padding:2px 4px;">Salto de línea</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">
        {variable}
      </td>
      <td style="padding:2px 4px;">Variable / placeholder</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">
        [etiqueta]
      </td>
      <td style="padding:2px 4px;">Etiqueta genérica</td>
    </tr>
  </table>
  <div style="color:#8899AA;margin-top:.7rem;font-size:.71rem;line-height:1.6;">
    ⚠️ Copia las etiquetas tal cual en tu traducción.<br>
    &lt;b&gt;, &lt;i&gt;, &lt;u&gt; se <em style="color:#C8D6E5">renderizarán</em> en la vista previa.
  </div>
</div>
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
    defaults = {
        "segments": [],
        "translations": {},
        "source_lang": "Español",
        "target_lang": "English",
        "show_preview": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Header ──
    st.markdown(
        """
        <div class="cat-header">
            <h1>🌐 CAT Tool — Translation Workbench</h1>
            <p>Computer-Assisted Translation · Lightweight · No installation required</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ─────────────────────────────────────────
    # SIDEBAR
    # ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        st.session_state.source_lang = st.text_input(
            "Idioma fuente", value=st.session_state.source_lang
        )
        st.session_state.target_lang = st.text_input(
            "Idioma meta", value=st.session_state.target_lang
        )
        st.session_state.show_preview = st.toggle(
            "Mostrar vista previa", value=st.session_state.show_preview
        )

        st.markdown("---")
        st.markdown("### 📂 Cargar texto fuente")
        input_method = st.radio("Método de entrada", ["Subir archivo .txt", "Pegar texto"])

        raw_text = ""
        if input_method == "Subir archivo .txt":
            uploaded = st.file_uploader("Selecciona un archivo .txt", type=["txt"])
            if uploaded:
                raw_text = uploaded.read().decode("utf-8", errors="replace")
        else:
            raw_text = st.text_area(
                "Pega aquí el texto fuente",
                height=200,
                placeholder="Ejemplo:\nEl producto cuesta <b>{precio}</b>.\nHaz clic [aquí] para continuar.",
            )

        if st.button("▶ Cargar y segmentar", use_container_width=True):
            if raw_text.strip():
                segs = segment_text(raw_text)
                st.session_state.segments = segs
                for i in range(len(segs)):
                    if i not in st.session_state.translations:
                        st.session_state.translations[i] = ""
                st.success(f"✅ {len(segs)} segmento(s) cargados.")
            else:
                st.warning("Por favor escribe o sube un texto primero.")

        st.markdown("---")
        st.markdown(TAG_GUIDE_HTML, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ Borrar todas las traducciones", use_container_width=True):
            st.session_state.translations = {
                i: "" for i in range(len(st.session_state.segments))
            }
            st.rerun()

    # ─────────────────────────────────────────
    # MAIN AREA
    # ─────────────────────────────────────────
    segments     = st.session_state.segments
    translations = st.session_state.translations

    if not segments:
        st.info(
            "👈 Sube un archivo .txt o pega tu texto en la barra lateral, "
            "luego haz clic en **Cargar y segmentar** para comenzar."
        )
        return

    # ── Stats bar ──
    filled = sum(1 for i in range(len(segments)) if translations.get(i, "").strip())
    pct    = int(filled / len(segments) * 100)

    st.markdown(
        f"""
        <div class="stats-bar">
            <span class="stat-item">Segmentos: <strong>{len(segments)}</strong></span>
            <span class="stat-item">Traducidos: <strong>{filled}</strong></span>
            <span class="stat-item">Pendientes: <strong>{len(segments) - filled}</strong></span>
            <span class="stat-item">Progreso: <strong>{pct}%</strong></span>
            <span class="stat-item">
                {st.session_state.source_lang} → {st.session_state.target_lang}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(pct / 100)

    # ── Translation grid ──
    st.markdown(
        '<p class="section-title">📝 Cuadrícula de traducción</p>',
        unsafe_allow_html=True,
    )

    hdr_l, hdr_r = st.columns(2)
    with hdr_l:
        st.markdown(
            f'<div class="col-header">🔵 Fuente — {st.session_state.source_lang}</div>',
            unsafe_allow_html=True,
        )
    with hdr_r:
        st.markdown(
            f'<div class="col-header">✏️ Traducción — {st.session_state.target_lang}</div>',
            unsafe_allow_html=True,
        )

    for i, seg in enumerate(segments):
        col_src, col_tgt = st.columns(2, gap="medium")

        # Source column
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

        # Target column
        with col_tgt:
            new_val = st.text_area(
                label=f"Segmento {i + 1}",
                value=st.session_state.translations.get(i, ""),
                key=f"ta_{i}",
                label_visibility="collapsed",
                height=80,
                placeholder=f"Traduce el segmento #{i + 1}…  (usa <b>, <i>, <u> para formato)",
            )
            st.session_state.translations[i] = new_val

            # Tag protection warning
            missing = check_missing_tags(seg, new_val)
            if new_val.strip() and missing:
                chips = " ".join(
                    f'<span class="tag-chip">{html_lib.escape(t)}</span>'
                    for t in missing
                )
                st.markdown(
                    f'<div class="tag-warning">⚠️ Etiqueta(s) faltante(s): {chips}</div>',
                    unsafe_allow_html=True,
                )

    # ─────────────────────────────────────────
    # LIVE PREVIEW PANEL
    # ─────────────────────────────────────────
    if st.session_state.show_preview:
        st.markdown(
            '<p class="section-title">👁️ Vista previa — Traducción completa</p>',
            unsafe_allow_html=True,
        )

        rendered_segments = []
        for i in range(len(segments)):
            t = translations.get(i, "").strip()
            if t:
                rendered_segments.append(render_translation_html(t))

        if rendered_segments:
            body = "<br><br>".join(rendered_segments)
            title = f"📄 {st.session_state.target_lang} — Resultado renderizado"
        else:
            body  = '<span class="preview-placeholder">Tu traducción aparecerá aquí mientras escribes…</span>'
            title = "📄 Vista previa"

        st.markdown(
            f"""
            <div class="preview-panel">
                <div class="preview-panel-title">{title}</div>
                {body}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ─────────────────────────────────────────
    # EXPORT
    # ─────────────────────────────────────────
    st.markdown("---")
    ex_col1, ex_col2 = st.columns([3, 1])
    with ex_col1:
        st.markdown(
            "**Exportar** la traducción como archivo `.txt` "
            "(las etiquetas se conservan; segmentos separados por líneas en blanco)."
        )
    with ex_col2:
        export_content = build_download_content(segments, translations)
        st.download_button(
            label="⬇️ Exportar traducción",
            data=export_content.encode("utf-8"),
            file_name=f"traduccion_{st.session_state.target_lang.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
