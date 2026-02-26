"""
CAT Tool (Computer-Assisted Translation) - Streamlit App
=========================================================
A lightweight, web-based CAT tool for translation students and professionals.

To run:
    pip install streamlit
    streamlit run app.py

TAG SYSTEM
──────────
Use inline tags in your source text to mark formatting:

    <b>text</b>    → negrita / bold
    <i>text</i>    → cursiva / italic
    <u>text</u>    → subrayado / underline
    <br/>          → salto de línea / line break
    {variable}     → variable / placeholder
    [etiqueta]     → etiqueta genérica / generic tag

To change the tag regex, edit TAG_PATTERN below.
"""

import re
import streamlit as st
import html as html_lib

# ─────────────────────────────────────────────
# TAG CONFIGURATION
# ─────────────────────────────────────────────
# Edit this regex to match your tag format.
TAG_PATTERN = r"(<[^>]+>|\{[^}]+\}|\[[^\]]+\])"

# These HTML tags will be RENDERED (not just highlighted) in previews.
RENDER_TAGS = {"b", "i", "u", "br", "br/", "strong", "em"}

# Formatting tag buttons shown in the toolbar
FORMAT_TAGS = [
    ("B",  "<b>",  "</b>",  "Negrita",    "#2563EB"),
    ("I",  "<i>",  "</i>",  "Cursiva",    "#7C3AED"),
    ("U",  "<u>",  "</u>",  "Subrayado",  "#059669"),
    ("↵",  "<br/>","",      "Salto línea","#DC2626"),
]


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def segment_text(text: str) -> list[str]:
    """Split text into segments on blank lines and sentence boundaries."""
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
    return re.findall(TAG_PATTERN, text)


def highlight_tags_html(text: str) -> str:
    """Highlight tags in amber; escape all other text."""
    parts = re.split(TAG_PATTERN, text)
    out = []
    for part in parts:
        if re.fullmatch(TAG_PATTERN, part):
            out.append(f'<span class="tag-chip">{html_lib.escape(part)}</span>')
        else:
            out.append(html_lib.escape(part))
    return "".join(out)


def render_translation_html(text: str) -> str:
    """Render known formatting tags as real HTML; wrap others as chips."""
    parts = re.split(TAG_PATTERN, text)
    out = []
    for part in parts:
        if re.fullmatch(TAG_PATTERN, part):
            inner = part.strip("<>/").split()[0].lower().rstrip("/")
            if inner in RENDER_TAGS:
                out.append(part)
            else:
                out.append(f'<span class="tag-chip">{html_lib.escape(part)}</span>')
        else:
            out.append(html_lib.escape(part))
    return "".join(out)


def check_missing_tags(source: str, translation: str) -> list[str]:
    src_copy = extract_tags(source)
    tgt_copy = extract_tags(translation)
    missing = []
    for t in src_copy:
        if t in tgt_copy:
            tgt_copy.remove(t)
        else:
            missing.append(t)
    return missing


def build_download_content(segments: list[str], translations: dict) -> str:
    return "\n\n".join(translations.get(i, "") for i in range(len(segments)))


# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

CUSTOM_CSS = """
<style>
/* ── Page ── */
[data-testid="stAppViewContainer"] { background: #F0F2F6; }

/* ── Sidebar dark theme ── */
[data-testid="stSidebar"] {
    background: #1A1A2E !important;
    border-right: 1px solid #0F3460;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stMarkdown { color: #E0E0E0 !important; }
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] textarea {
    background: #16213E !important;
    color: #F0F0F0 !important;
    border: 1px solid #4A90E2 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] button {
    background: #0F3460 !important;
    color: #FFFFFF !important;
    border: 1px solid #4A90E2 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] button:hover { background: #4A90E2 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label span { color: #D0D0D0 !important; }
[data-testid="stSidebar"] [data-testid="stToggle"] span { color: #D0D0D0 !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #16213E !important;
    border: 1px dashed #4A90E2 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
[data-testid="stSidebar"] [data-testid="stFileUploader"] p { color: #ADB5BD !important; }
[data-testid="stSidebar"] hr { border-color: #0F3460 !important; opacity:1 !important; }
[data-testid="stSidebar"] code,
[data-testid="stSidebar"] pre {
    background: #0D1B2A !important;
    color: #7EC8E3 !important;
    border: 1px solid #0F3460 !important;
}

/* ── Header ── */
.cat-header {
    background: linear-gradient(135deg,#1A1A2E 0%,#0F3460 100%);
    padding:1.4rem 2rem; border-radius:12px; margin-bottom:1.5rem;
}
.cat-header h1 { margin:0; font-size:1.6rem; font-weight:700; color:#fff; }
.cat-header p  { margin:.3rem 0 0; font-size:.85rem; opacity:.7; color:#fff; }

/* ── Column headers ── */
.col-header {
    font-size:.72rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.1em; color:#6C757D;
    padding:.4rem .6rem; border-bottom:2px solid #DEE2E6; margin-bottom:.5rem;
}

/* ── Segment row wrapper ── */
.segment-row {
    background:#FFFFFF;
    border:1px solid #DEE2E6;
    border-radius:10px;
    margin-bottom:.8rem;
    overflow:hidden;
}
.segment-row-header {
    background:#F8F9FA;
    border-bottom:1px solid #DEE2E6;
    padding:.35rem .8rem;
    font-size:.68rem; font-weight:700; color:#6C757D;
    letter-spacing:.05em;
    display:flex; align-items:center; gap:.6rem;
}
.segment-row-header .seg-confirmed {
    background:#D1FAE5; color:#065F46;
    border-radius:4px; padding:1px 7px; font-size:.65rem; font-weight:700;
}
.segment-row-body {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:0;
}
.seg-source {
    padding:.8rem 1rem;
    border-right:1px solid #DEE2E6;
    line-height:1.7; font-size:.9rem; color:#212529;
    position:relative;
}
.seg-source-pending { background:#FAFAFA; }
.seg-source-confirmed { background:#F0FFF4; }
.seg-target-area { padding:.6rem .8rem; }

/* ── Tag chip ── */
.tag-chip {
    background:#FFF3CD; color:#856404;
    border:1px solid #FFEEBA; border-radius:4px;
    padding:0 5px; font-family:monospace; font-size:.8em; white-space:nowrap;
}

/* ── Warning badge ── */
.tag-warning {
    background:#FFF3CD; color:#856404;
    border:1px solid #FFEEBA; border-radius:4px;
    font-size:.73rem; padding:3px 8px; margin-top:3px; display:inline-block;
}

/* ── Tag toolbar ── */
.tag-toolbar {
    display:flex; flex-wrap:wrap; gap:5px;
    margin-bottom:6px;
}

/* ── Stats bar ── */
.stats-bar {
    background:#FFFFFF; border:1px solid #DEE2E6; border-radius:8px;
    padding:.65rem 1.2rem; display:flex; flex-wrap:wrap; gap:1.5rem;
    margin-bottom:1rem; font-size:.82rem; color:#495057;
}
.stat-item strong { color:#1A1A2E; }

/* ──────────────────────────────────────────
   FIX: Force textarea text to be BLACK
   Streamlit injects its own dark-mode vars;
   we override all relevant colour properties.
─────────────────────────────────────────── */
.stTextArea textarea,
.stTextArea > div > div > textarea,
[data-testid="stTextArea"] textarea,
[data-testid="stTextAreaRootElement"] textarea,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] textarea {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    background-color: #FFFFFF !important;
    caret-color: #111111 !important;
    font-size: .9rem !important;
    line-height: 1.6 !important;
    border-radius: 6px !important;
    border: 1px solid #CED4DA !important;
}
.stTextArea textarea:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #4A90E2 !important;
    box-shadow: 0 0 0 3px rgba(74,144,226,.18) !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
}

/* ── Confirm button styling ── */
.stButton button[kind="secondary"] {
    background: #F8F9FA !important;
    color: #374151 !important;
    border: 1px solid #D1D5DB !important;
    border-radius:6px !important;
    font-size:.78rem !important;
    padding:.2rem .7rem !important;
}
button[data-confirm="true"],
.confirm-btn button {
    background: #065F46 !important;
    color: #FFFFFF !important;
    border: none !important;
}

/* ── Preview panel ── */
.preview-panel {
    background:#FFFFFF; border:1px solid #DEE2E6; border-radius:10px;
    padding:1.5rem 2rem; line-height:1.9; font-size:.95rem; color:#212529;
    min-height:100px;
}
.preview-panel-title {
    font-size:.72rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.1em; color:#6C757D;
    border-bottom:2px solid #DEE2E6; padding-bottom:.5rem; margin-bottom:1rem;
}
.preview-segment { margin-bottom:.9rem; }
.preview-seg-src {
    font-size:.78rem; color:#9CA3AF; font-style:italic;
    margin-bottom:.15rem; text-decoration:line-through;
}
.preview-seg-src-pending {
    font-size:.78rem; color:#9CA3AF; font-style:italic; margin-bottom:.15rem;
}
.preview-seg-tgt { font-size:.95rem; color:#111827; }
.preview-placeholder { color:#ADB5BD; font-style:italic; }

/* ── Section title ── */
.section-title {
    font-size:.85rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.07em; color:#495057; margin:1.4rem 0 .8rem;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background:#1A1A2E !important; color:#FFFFFF !important;
    border:none !important; border-radius:6px !important; font-weight:600 !important;
}
[data-testid="stDownloadButton"] button:hover { background:#0F3460 !important; }
</style>
"""

# ─────────────────────────────────────────────
# Ctrl+Enter JS injection
# ─────────────────────────────────────────────
# This injects a document-level keydown listener.
# When Ctrl+Enter is pressed, it finds the confirm button
# that sits next to the currently focused textarea and clicks it.
CTRL_ENTER_JS = """
<script>
(function() {
  if (window._catCtrlEnterBound) return;
  window._catCtrlEnterBound = true;
  document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      // Walk up from the focused element to find the nearest confirm button
      var focused = document.activeElement;
      if (!focused || focused.tagName !== 'TEXTAREA') return;
      // Streamlit wraps each textarea in several divs; the confirm button
      // is a sibling of the textarea's stTextArea wrapper inside the column.
      var parent = focused;
      for (var d = 0; d < 10; d++) {
        parent = parent.parentElement;
        if (!parent) break;
        var btn = parent.querySelector('button[data-cat-confirm]');
        if (btn) { btn.click(); break; }
      }
    }
  });
})();
</script>
"""

# ─────────────────────────────────────────────
# SIDEBAR TAG GUIDE
# ─────────────────────────────────────────────

TAG_GUIDE_HTML = """
<div style="background:#0D1B2A;border:1px solid #0F3460;border-radius:8px;
            padding:.9rem 1rem;font-size:.78rem;line-height:1.8;margin-top:.3rem;">
  <div style="color:#7EC8E3;font-weight:700;margin-bottom:.5rem;">🏷️ Etiquetas soportadas</div>
  <table style="width:100%;border-collapse:collapse;color:#C8D6E5;">
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">&lt;b&gt;…&lt;/b&gt;</td>
      <td>Negrita</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">&lt;i&gt;…&lt;/i&gt;</td>
      <td>Cursiva</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">&lt;u&gt;…&lt;/u&gt;</td>
      <td>Subrayado</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">&lt;br/&gt;</td>
      <td>Salto de línea</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">{variable}</td>
      <td>Variable</td>
    </tr>
    <tr>
      <td style="padding:2px 8px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">[etiqueta]</td>
      <td>Etiqueta genérica</td>
    </tr>
  </table>
  <div style="color:#8899AA;margin-top:.7rem;font-size:.71rem;line-height:1.6;">
    ⚠️ Copia las etiquetas tal cual en tu traducción.<br>
    Usa los botones <b style="color:#C8D6E5">B / I / U / ↵</b> en cada fila para insertarlas.
  </div>
</div>
"""


# ─────────────────────────────────────────────
# TAG TOOLBAR (per segment)
# ─────────────────────────────────────────────

def render_tag_toolbar(seg_index: int):
    """
    Render a row of small buttons that insert format tags into the textarea
    for segment `seg_index`.  Because Streamlit re-runs on every click, we
    track a pending insertion in session_state and apply it when re-rendering
    the textarea value.
    """
    cols = st.columns(len(FORMAT_TAGS) + 1, gap="small")
    for col_idx, (label, open_tag, close_tag, tooltip, color) in enumerate(FORMAT_TAGS):
        with cols[col_idx]:
            btn_css = f"""
            <style>
            div[data-testid="column"]:nth-child({col_idx+1}) button {{
                background:{color}22 !important;
                color:{color} !important;
                border:1px solid {color}66 !important;
                border-radius:5px !important;
                font-weight:700 !important;
                font-size:.75rem !important;
                padding:.15rem .5rem !important;
                min-height:0 !important;
                height:28px !important;
            }}
            </style>
            """
            if st.button(f"{label}", key=f"tag_btn_{seg_index}_{col_idx}", help=tooltip):
                current = st.session_state.translations.get(seg_index, "")
                st.session_state.translations[seg_index] = current + open_tag + close_tag
                st.rerun()

    # Confirm button (last column)
    with cols[-1]:
        confirmed = st.session_state.confirmed.get(seg_index, False)
        label_txt = "✓ Confirmado" if confirmed else "✓ Confirmar"
        btn_style = "primary" if not confirmed else "secondary"
        if st.button(
            label_txt,
            key=f"confirm_btn_{seg_index}",
            help="Confirmar segmento (Ctrl+Enter)",
            type=btn_style,
            use_container_width=False,
        ):
            val = st.session_state.translations.get(seg_index, "")
            if val.strip():
                st.session_state.confirmed[seg_index] = not confirmed
                st.rerun()


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
    st.markdown(CTRL_ENTER_JS, unsafe_allow_html=True)

    # ── Session state ──
    defaults = {
        "segments": [],
        "translations": {},
        "confirmed": {},        # {seg_index: bool}
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
                    if i not in st.session_state.confirmed:
                        st.session_state.confirmed[i] = False
                st.success(f"✅ {len(segs)} segmento(s) cargados.")
            else:
                st.warning("Por favor escribe o sube un texto primero.")

        st.markdown("---")
        st.markdown(TAG_GUIDE_HTML, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ Borrar todas las traducciones", use_container_width=True):
            st.session_state.translations = {i: "" for i in range(len(st.session_state.segments))}
            st.session_state.confirmed    = {i: False for i in range(len(st.session_state.segments))}
            st.rerun()

    # ─────────────────────────────────────────
    # MAIN AREA
    # ─────────────────────────────────────────
    segments     = st.session_state.segments
    translations = st.session_state.translations
    confirmed    = st.session_state.confirmed

    if not segments:
        st.info(
            "👈 Sube un archivo .txt o pega tu texto en la barra lateral, "
            "luego haz clic en **Cargar y segmentar** para comenzar."
        )
        return

    # ── Stats bar ──
    n_confirmed = sum(1 for i in range(len(segments)) if confirmed.get(i, False))
    filled      = sum(1 for i in range(len(segments)) if translations.get(i, "").strip())
    pct         = int(n_confirmed / len(segments) * 100)

    st.markdown(
        f"""
        <div class="stats-bar">
            <span class="stat-item">Segmentos: <strong>{len(segments)}</strong></span>
            <span class="stat-item">Confirmados: <strong>{n_confirmed}</strong></span>
            <span class="stat-item">En progreso: <strong>{filled - n_confirmed}</strong></span>
            <span class="stat-item">Pendientes: <strong>{len(segments) - filled}</strong></span>
            <span class="stat-item">Progreso: <strong>{pct}%</strong></span>
            <span class="stat-item">{st.session_state.source_lang} → {st.session_state.target_lang}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(pct / 100)

    # ── Translation grid ──
    st.markdown('<p class="section-title">📝 Cuadrícula de traducción</p>', unsafe_allow_html=True)

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
        is_confirmed = confirmed.get(i, False)
        col_src, col_tgt = st.columns(2, gap="medium")

        # ── Source column ──
        with col_src:
            src_bg    = "#F0FFF4" if is_confirmed else "#FFFFFF"
            src_border = "3px solid #10B981" if is_confirmed else "3px solid #4A90E2"
            highlighted = highlight_tags_html(seg)
            confirmed_badge = '<span style="background:#D1FAE5;color:#065F46;border-radius:4px;padding:1px 7px;font-size:.65rem;font-weight:700;margin-left:6px;">✓ CONFIRMADO</span>' if is_confirmed else ""
            st.markdown(
                f"""
                <div style="background:{src_bg};border:1px solid #DEE2E6;
                            border-left:{src_border};border-radius:8px;
                            padding:.75rem 1rem;margin-bottom:.1rem;
                            line-height:1.7;font-size:.9rem;color:#212529;min-height:68px;">
                    <div style="font-size:.68rem;color:#ADB5BD;font-weight:700;
                                letter-spacing:.05em;margin-bottom:5px;">
                        #{i + 1}{confirmed_badge}
                    </div>
                    {highlighted}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Target column ──
        with col_tgt:
            # Tag toolbar + confirm button
            render_tag_toolbar(i)

            # Textarea — use session_state value (may have been modified by toolbar)
            current_val = st.session_state.translations.get(i, "")
            new_val = st.text_area(
                label=f"Segmento {i + 1}",
                value=current_val,
                key=f"ta_{i}",
                label_visibility="collapsed",
                height=80,
                placeholder=f"Traduce el segmento #{i + 1}… | Ctrl+Enter para confirmar",
                disabled=is_confirmed,
            )
            st.session_state.translations[i] = new_val

            # Tag protection warning
            missing = check_missing_tags(seg, new_val)
            if new_val.strip() and missing and not is_confirmed:
                chips = " ".join(
                    f'<span class="tag-chip">{html_lib.escape(t)}</span>' for t in missing
                )
                st.markdown(
                    f'<div class="tag-warning">⚠️ Etiqueta(s) faltante(s): {chips}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # LIVE PREVIEW PANEL
    # ─────────────────────────────────────────
    if st.session_state.show_preview:
        st.markdown(
            '<p class="section-title">👁️ Vista previa — Traducción completa</p>',
            unsafe_allow_html=True,
        )

        any_content = any(translations.get(i, "").strip() for i in range(len(segments)))

        if not any_content:
            body = '<span class="preview-placeholder">Tu traducción aparecerá aquí mientras escribes y confirmas segmentos…</span>'
        else:
            rows = []
            for i, seg in enumerate(segments):
                t = translations.get(i, "").strip()
                is_conf = confirmed.get(i, False)

                if t:
                    # Source text: strikethrough if confirmed, faded if pending
                    src_html = highlight_tags_html(seg)
                    if is_conf:
                        src_line = f'<div class="preview-seg-src">#{i+1} {src_html}</div>'
                    else:
                        src_line = f'<div class="preview-seg-src-pending">#{i+1} {src_html} <em style="color:#D97706">(sin confirmar)</em></div>'

                    tgt_line = f'<div class="preview-seg-tgt">{render_translation_html(t)}</div>'
                    rows.append(f'<div class="preview-segment">{src_line}{tgt_line}</div>')
                else:
                    src_html = highlight_tags_html(seg)
                    rows.append(
                        f'<div class="preview-segment">'
                        f'<div class="preview-seg-src-pending" style="color:#D1D5DB">#{i+1} {src_html} <em>(pendiente)</em></div>'
                        f'</div>'
                    )

            body = "".join(rows)

        lang  = st.session_state.target_lang
        title = f"📄 {lang} — Resultado ({n_confirmed}/{len(segments)} confirmados)"

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
            file_name=f"traduccion_{st.session_state.target_lang.lower().replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()