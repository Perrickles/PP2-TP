"""
CAT Tool (Computer-Assisted Translation) - Streamlit App
=========================================================
To run:
    pip install streamlit
    streamlit run app.py

TAG SYSTEM
──────────
    <b>…</b>   → negrita      <i>…</i>  → cursiva
    <u>…</u>   → subrayado    <br/>     → salto de línea
    {var}      → variable     [tag]     → etiqueta genérica

Edit TAG_PATTERN below to change the tag regex.
"""

import re
import streamlit as st
import html as html_lib

# ─────────────────────────────────────────────
# TAG CONFIGURATION
# ─────────────────────────────────────────────
TAG_PATTERN = r"(<[^>]+>|\{[^}]+\}|\[[^\]]+\])"
RENDER_TAGS = {"b", "i", "u", "br", "br/", "strong", "em"}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def segment_text(text: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", text.strip())
    segments = []
    for para in paragraphs:
        for s in re.split(r"(?<=[.!?])\s+", para.strip()):
            s = s.strip()
            if s:
                segments.append(s)
    return segments


def extract_tags(text: str) -> list[str]:
    return re.findall(TAG_PATTERN, text)


def highlight_tags_html(text: str) -> str:
    parts = re.split(TAG_PATTERN, text)
    out = []
    for p in parts:
        if re.fullmatch(TAG_PATTERN, p):
            out.append(f'<span class="tag-chip">{html_lib.escape(p)}</span>')
        else:
            out.append(html_lib.escape(p))
    return "".join(out)


def render_translation_html(text: str) -> str:
    parts = re.split(TAG_PATTERN, text)
    out = []
    for p in parts:
        if re.fullmatch(TAG_PATTERN, p):
            inner = p.strip("<>/").split()[0].lower().rstrip("/")
            out.append(p if inner in RENDER_TAGS else f'<span class="tag-chip">{html_lib.escape(p)}</span>')
        else:
            out.append(html_lib.escape(p))
    return "".join(out)


def check_missing_tags(source: str, translation: str) -> list[str]:
    src, tgt = extract_tags(source), extract_tags(translation)
    missing = []
    for t in src:
        if t in tgt:
            tgt.remove(t)
        else:
            missing.append(t)
    return missing


def build_download_content(segments, translations):
    return "\n\n".join(translations.get(i, "") for i in range(len(segments)))


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

CUSTOM_CSS = """
<style>
/* ── Page ── */
[data-testid="stAppViewContainer"] { background:#F0F2F6; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background:#1A1A2E !important;
    border-right:1px solid #0F3460;
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
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p { color:#E8E8E8 !important; }
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] textarea {
    background:#16213E !important; color:#F0F0F0 !important;
    border:1px solid #4A90E2 !important; border-radius:6px !important;
}
/* Sidebar buttons — strong contrast */
[data-testid="stSidebar"] button {
    background:#2563EB !important; color:#FFFFFF !important;
    border:none !important; border-radius:6px !important;
    font-weight:700 !important; font-size:.85rem !important;
}
[data-testid="stSidebar"] button:hover { background:#1D4ED8 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label span { color:#D0D0D0 !important; }
[data-testid="stSidebar"] [data-testid="stToggle"] span { color:#D0D0D0 !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background:#16213E !important; border:1px dashed #4A90E2 !important; border-radius:8px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
[data-testid="stSidebar"] [data-testid="stFileUploader"] p { color:#ADB5BD !important; }
[data-testid="stSidebar"] hr { border-color:#0F3460 !important; opacity:1 !important; }
[data-testid="stSidebar"] code, [data-testid="stSidebar"] pre {
    background:#0D1B2A !important; color:#7EC8E3 !important; border:1px solid #0F3460 !important;
}
/* Sidebar bottom text (caption / small text) */
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] .stCaption p { color:#94A3B8 !important; }

/* ── Sticky toolbar ── */
.toolbar-wrap {
    position:sticky; top:0; z-index:999;
    background:#1E293B;
    border-bottom:2px solid #334155;
    padding:.5rem 1rem;
    display:flex; align-items:center; flex-wrap:wrap; gap:.4rem;
    border-radius:0 0 8px 8px;
    margin-bottom:1rem;
    box-shadow:0 2px 8px rgba(0,0,0,.18);
}
.toolbar-label {
    font-size:.68rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.08em; color:#94A3B8; margin-right:.3rem; white-space:nowrap;
}
.toolbar-sep {
    width:1px; height:22px; background:#334155; margin:0 .3rem;
}
/* Toolbar buttons rendered via st.columns — we style by data attribute */
.tb-btn button {
    border-radius:5px !important; font-weight:700 !important;
    font-size:.8rem !important; padding:.2rem .55rem !important;
    min-height:0 !important; height:30px !important; line-height:1 !important;
    border:1px solid transparent !important;
    transition:filter .15s !important;
}
.tb-btn button:hover { filter:brightness(1.15) !important; }

/* ── Header ── */
.cat-header {
    background:linear-gradient(135deg,#1A1A2E 0%,#0F3460 100%);
    padding:1.3rem 2rem; border-radius:12px; margin-bottom:1rem;
}
.cat-header h1 { margin:0; font-size:1.5rem; font-weight:700; color:#fff; }
.cat-header p  { margin:.25rem 0 0; font-size:.82rem; opacity:.65; color:#fff; }

/* ── Column headers ── */
.col-header {
    font-size:.7rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.1em; color:#6C757D;
    padding:.35rem .6rem; border-bottom:2px solid #DEE2E6; margin-bottom:.5rem;
}

/* ── Segment source card ── */
.seg-src-card {
    border:1px solid #DEE2E6; border-radius:8px;
    padding:.7rem 1rem; margin-bottom:.2rem;
    line-height:1.7; font-size:.9rem; color:#212529; min-height:68px;
    transition:background .2s, border-left .2s;
}
.seg-src-pending  { background:#FFFFFF; border-left:3px solid #4A90E2; }
.seg-src-active   { background:#EFF6FF; border-left:3px solid #2563EB; }
.seg-src-confirmed{ background:#F0FFF4; border-left:3px solid #10B981; }
.seg-num {
    font-size:.65rem; color:#ADB5BD; font-weight:700;
    letter-spacing:.05em; margin-bottom:4px;
}

/* ── Tag chip ── */
.tag-chip {
    background:#FFF3CD; color:#856404; border:1px solid #FFEEBA;
    border-radius:4px; padding:0 5px;
    font-family:monospace; font-size:.8em; white-space:nowrap;
}

/* ── Warning ── */
.tag-warning {
    background:#FFF3CD; color:#856404; border:1px solid #FFEEBA;
    border-radius:4px; font-size:.72rem; padding:3px 8px;
    margin-top:3px; display:inline-block;
}

/* ── Stats bar ── */
.stats-bar {
    background:#FFFFFF; border:1px solid #DEE2E6; border-radius:8px;
    padding:.6rem 1.2rem; display:flex; flex-wrap:wrap; gap:1.4rem;
    margin-bottom:.8rem; font-size:.82rem; color:#495057;
}
.stat-item strong { color:#1A1A2E; }

/* ── Textarea — force black text ── */
.stTextArea textarea,
[data-testid="stTextArea"] textarea,
[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] textarea {
    color:#111111 !important;
    -webkit-text-fill-color:#111111 !important;
    background-color:#FFFFFF !important;
    caret-color:#111111 !important;
    font-size:.9rem !important;
    line-height:1.6 !important;
    border-radius:6px !important;
    border:1px solid #CED4DA !important;
}
.stTextArea textarea:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color:#2563EB !important;
    box-shadow:0 0 0 3px rgba(37,99,235,.15) !important;
    color:#111111 !important;
    -webkit-text-fill-color:#111111 !important;
}

/* ── Preview panel ── */
.preview-panel {
    background:#FFFFFF; border:1px solid #DEE2E6; border-radius:10px;
    padding:1.4rem 2rem; line-height:1.9; font-size:.95rem; color:#212529;
    min-height:80px;
}
.preview-panel-title {
    font-size:.7rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.1em; color:#6C757D;
    border-bottom:2px solid #DEE2E6; padding-bottom:.5rem; margin-bottom:1rem;
}
.preview-segment { margin-bottom:.9rem; }
.preview-seg-src { font-size:.75rem; color:#9CA3AF; font-style:italic; margin-bottom:.12rem; text-decoration:line-through; }
.preview-seg-src-pending { font-size:.75rem; color:#D97706; font-style:italic; margin-bottom:.12rem; }
.preview-seg-tgt { font-size:.95rem; color:#111827; }
.preview-placeholder { color:#ADB5BD; font-style:italic; }

/* ── Section title ── */
.section-title {
    font-size:.82rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.07em; color:#495057; margin:1.2rem 0 .7rem;
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
# JS: track active segment + Ctrl+Enter confirm
# ─────────────────────────────────────────────
TOOLBAR_JS = """
<script>
(function(){
  if(window._catInit) return;
  window._catInit = true;

  // Track which segment textarea is focused
  window._catActiveSeg = null;
  document.addEventListener('focusin', function(e){
    var ta = e.target;
    if(ta && ta.tagName === 'TEXTAREA'){
      var m = ta.closest('[data-seg-index]');
      if(m) window._catActiveSeg = parseInt(m.dataset.segIndex);
    }
  });

  // Ctrl+Enter → click the confirm button for the active segment
  document.addEventListener('keydown', function(e){
    if((e.ctrlKey||e.metaKey) && e.key==='Enter'){
      e.preventDefault();
      if(window._catActiveSeg === null) return;
      var btn = document.querySelector('[data-confirm-seg="'+window._catActiveSeg+'"]');
      if(btn) btn.click();
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
            padding:.85rem 1rem;font-size:.78rem;line-height:1.8;margin-top:.3rem;">
  <div style="color:#7EC8E3;font-weight:700;margin-bottom:.5rem;">🏷️ Etiquetas compatibles</div>
  <table style="width:100%;border-collapse:collapse;color:#C8D6E5;">
    <tr>
      <td style="padding:2px 10px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">&lt;b&gt;…&lt;/b&gt;</td>
      <td>Negrita</td>
    </tr>
    <tr>
      <td style="padding:2px 10px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">&lt;i&gt;…&lt;/i&gt;</td>
      <td>Cursiva</td>
    </tr>
    <tr>
      <td style="padding:2px 10px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">&lt;u&gt;…&lt;/u&gt;</td>
      <td>Subrayado</td>
    </tr>
    <tr>
      <td style="padding:2px 10px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">&lt;br/&gt;</td>
      <td>Salto de línea</td>
    </tr>
    <tr>
      <td style="padding:2px 10px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">{variable}</td>
      <td>Variable</td>
    </tr>
    <tr>
      <td style="padding:2px 10px 2px 0;font-family:monospace;color:#FFD580;white-space:nowrap">[etiqueta]</td>
      <td>Etiqueta genérica</td>
    </tr>
  </table>
</div>
"""

# ─────────────────────────────────────────────
# TOOLBAR DEFINITION
# ─────────────────────────────────────────────
# Each entry: (key, label, tooltip, bg_color, text_color, action_type, payload)
# action_type: "insert_tag" | "confirm_active" | "confirm_all" | "copy_source" | "export"
TOOLBAR_BUTTONS = [
    # Formatting tags
    ("tb_b",    "B",   "Negrita — inserta <b>…</b>",           "#DBEAFE", "#1D4ED8", "insert_tag",    ("<b>", "</b>")),
    ("tb_i",    "𝐼",   "Cursiva — inserta <i>…</i>",           "#EDE9FE", "#6D28D9", "insert_tag",    ("<i>", "</i>")),
    ("tb_u",    "U̲",   "Subrayado — inserta <u>…</u>",         "#D1FAE5", "#065F46", "insert_tag",    ("<u>", "</u>")),
    ("tb_br",   "↵",   "Salto de línea — inserta <br/>",        "#FEE2E2", "#B91C1C", "insert_tag",    ("<br/>", "")),
    # --- separator (rendered as empty space) ---
    ("tb_sep1", "",    "",                                       "",        "",        "sep",           None),
    # Source copy
    ("tb_copy", "🏷",  "Copiar etiquetas de la fuente al destino","#FEF3C7","#92400E","copy_source",   None),
    # --- separator ---
    ("tb_sep2", "",    "",                                       "",        "",        "sep",           None),
    # Confirm
    ("tb_ok",   "✓",   "Confirmar segmento activo (Ctrl+Enter)","#D1FAE5", "#065F46", "confirm_active",None),
    ("tb_okall","✓✓",  "Confirmar todos los segmentos",         "#A7F3D0", "#064E3B", "confirm_all",   None),
    # --- separator ---
    ("tb_sep3", "",    "",                                       "",        "",        "sep",           None),
    # Export
    ("tb_exp",  "⬇",   "Exportar traducción",                   "#E0E7FF", "#3730A3", "export",        None),
]


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

def main():
    st.set_page_config(page_title="CAT Tool", page_icon="🌐", layout="wide",
                       initial_sidebar_state="expanded")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(TOOLBAR_JS, unsafe_allow_html=True)

    # Session state defaults
    for k, v in {
        "segments": [], "translations": {}, "confirmed": {},
        "active_seg": 0,
        "source_lang": "Español", "target_lang": "English",
        "show_preview": True,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Header ──
    st.markdown("""
        <div class="cat-header">
            <h1>🌐 CAT Tool — Translation Workbench</h1>
            <p>Computer-Assisted Translation · Lightweight · No installation required</p>
        </div>""", unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # SIDEBAR
    # ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        st.session_state.source_lang = st.text_input("Idioma fuente", value=st.session_state.source_lang)
        st.session_state.target_lang = st.text_input("Idioma meta",   value=st.session_state.target_lang)
        st.session_state.show_preview = st.toggle("Mostrar vista previa", value=st.session_state.show_preview)

        st.markdown("---")
        st.markdown("### 📂 Cargar texto fuente")
        input_method = st.radio("Método de entrada", ["Subir archivo .txt", "Pegar texto"])

        raw_text = ""
        if input_method == "Subir archivo .txt":
            uploaded = st.file_uploader("Selecciona un archivo .txt", type=["txt"])
            if uploaded:
                raw_text = uploaded.read().decode("utf-8", errors="replace")
        else:
            raw_text = st.text_area("Pega aquí el texto fuente", height=180,
                placeholder="Ejemplo:\nEl producto cuesta <b>{precio}</b>.\nHaz clic [aquí] para continuar.")

        if st.button("▶ Cargar y segmentar", use_container_width=True):
            if raw_text.strip():
                segs = segment_text(raw_text)
                st.session_state.segments = segs
                st.session_state.active_seg = 0
                for i in range(len(segs)):
                    st.session_state.translations.setdefault(i, "")
                    st.session_state.confirmed.setdefault(i, False)
                st.success(f"✅ {len(segs)} segmento(s) cargados.")
            else:
                st.warning("Por favor escribe o sube un texto primero.")

        st.markdown("---")
        st.markdown(TAG_GUIDE_HTML, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ Borrar todas las traducciones", use_container_width=True):
            n = len(st.session_state.segments)
            st.session_state.translations = {i: "" for i in range(n)}
            st.session_state.confirmed    = {i: False for i in range(n)}
            st.rerun()

    # ─────────────────────────────────────────
    # MAIN AREA
    # ─────────────────────────────────────────
    segments     = st.session_state.segments
    translations = st.session_state.translations
    confirmed    = st.session_state.confirmed

    if not segments:
        st.info("👈 Sube un archivo .txt o pega tu texto en la barra lateral, "
                "luego haz clic en **Cargar y segmentar** para comenzar.")
        return

    n_confirmed = sum(1 for i in range(len(segments)) if confirmed.get(i, False))
    filled      = sum(1 for i in range(len(segments)) if translations.get(i, "").strip())
    pct         = int(n_confirmed / len(segments) * 100)

    # ── Stats bar ──
    st.markdown(f"""
        <div class="stats-bar">
            <span class="stat-item">Segmentos: <strong>{len(segments)}</strong></span>
            <span class="stat-item">Confirmados: <strong>{n_confirmed}</strong></span>
            <span class="stat-item">En progreso: <strong>{filled - n_confirmed}</strong></span>
            <span class="stat-item">Pendientes: <strong>{len(segments) - filled}</strong></span>
            <span class="stat-item">Progreso: <strong>{pct}%</strong></span>
            <span class="stat-item">{st.session_state.source_lang} → {st.session_state.target_lang}</span>
        </div>""", unsafe_allow_html=True)
    st.progress(pct / 100)

    # ─────────────────────────────────────────
    # TOOLBAR
    # ─────────────────────────────────────────
    active = st.session_state.active_seg  # currently selected segment index

    # Build export bytes here so the download button can use it
    export_bytes = build_download_content(segments, translations).encode("utf-8")
    export_fname = f"traduccion_{st.session_state.target_lang.lower().replace(' ','_')}.txt"

    # Count real buttons (excluding separators) to size columns
    real_btns = [b for b in TOOLBAR_BUTTONS if b[5] != "sep"]
    sep_count = sum(1 for b in TOOLBAR_BUTTONS if b[5] == "sep")
    # We give separators very small column weight
    col_weights = []
    for b in TOOLBAR_BUTTONS:
        col_weights.append(0.15 if b[5] == "sep" else 1)

    tb_cols = st.columns(col_weights, gap="small")

    for col, (key, label, tip, bg, fg, action, payload) in zip(tb_cols, TOOLBAR_BUTTONS):
        with col:
            if action == "sep":
                st.markdown('<div style="width:1px;height:30px;background:#E2E8F0;margin:auto;margin-top:4px;"></div>', unsafe_allow_html=True)
                continue

            if action == "export":
                # Export uses download button
                st.download_button(
                    label=label,
                    data=export_bytes,
                    file_name=export_fname,
                    mime="text/plain",
                    help=tip,
                    key=key,
                    use_container_width=True,
                )
                # Style it inline
                st.markdown(f"""
                <style>
                [data-testid="stDownloadButton"][key="{key}"] button,
                div:has(>[data-testid="stDownloadButton"]) button {{
                    background:{bg} !important; color:{fg} !important;
                    border:1px solid {fg}55 !important;
                    font-size:.85rem !important; font-weight:700 !important;
                    height:30px !important; padding:.1rem .4rem !important;
                    min-height:0 !important;
                }}
                </style>""", unsafe_allow_html=True)
                continue

            clicked = st.button(label, key=key, help=tip, use_container_width=True)

            # Style this specific button
            st.markdown(f"""
            <style>
            div[data-testid="column"] button[kind="secondary"][data-testid*="{key}"],
            #root ~ * button[data-testid*="{key}"] {{
                background:{bg} !important; color:{fg} !important;
                border:1px solid {fg}55 !important;
            }}
            </style>""", unsafe_allow_html=True)

            if not clicked:
                continue

            # ── Handle actions ──
            if action == "insert_tag":
                open_tag, close_tag = payload
                cur = translations.get(active, "")
                translations[active] = cur + open_tag + close_tag
                st.session_state.translations = translations
                st.rerun()

            elif action == "copy_source":
                # Copy all tags from source into translation (append)
                src_tags = extract_tags(segments[active])
                cur = translations.get(active, "")
                translations[active] = cur + "".join(src_tags)
                st.session_state.translations = translations
                st.rerun()

            elif action == "confirm_active":
                val = translations.get(active, "")
                if val.strip():
                    confirmed[active] = not confirmed.get(active, False)
                    st.session_state.confirmed = confirmed
                    st.rerun()

            elif action == "confirm_all":
                for i in range(len(segments)):
                    if translations.get(i, "").strip():
                        confirmed[i] = True
                st.session_state.confirmed = confirmed
                st.rerun()

    # Toolbar bottom border
    st.markdown('<hr style="margin:.4rem 0 1rem;border-color:#E2E8F0;">', unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # SEGMENT SELECTOR (click to make active)
    # ─────────────────────────────────────────
    st.markdown(f'<p class="section-title">📝 Cuadrícula de traducción — '
                f'<span style="color:#2563EB;font-weight:700;">segmento activo: #{active+1}</span></p>',
                unsafe_allow_html=True)

    hdr_l, hdr_r = st.columns(2)
    with hdr_l:
        st.markdown(f'<div class="col-header">🔵 Fuente — {st.session_state.source_lang}</div>',
                    unsafe_allow_html=True)
    with hdr_r:
        st.markdown(f'<div class="col-header">✏️ Traducción — {st.session_state.target_lang}</div>',
                    unsafe_allow_html=True)

    for i, seg in enumerate(segments):
        is_confirmed = confirmed.get(i, False)
        is_active    = (i == active)

        col_src, col_tgt = st.columns(2, gap="medium")

        # ── Source ──
        with col_src:
            if is_confirmed:
                card_cls = "seg-src-confirmed"
                badge = ' <span style="background:#D1FAE5;color:#065F46;border-radius:4px;padding:1px 6px;font-size:.62rem;font-weight:700;">✓</span>'
            elif is_active:
                card_cls = "seg-src-active"
                badge = ' <span style="background:#DBEAFE;color:#1D4ED8;border-radius:4px;padding:1px 6px;font-size:.62rem;font-weight:700;">activo</span>'
            else:
                card_cls = "seg-src-pending"
                badge = ""

            st.markdown(
                f'<div class="seg-src-card {card_cls}">'
                f'<div class="seg-num">#{i+1}{badge}</div>'
                f'{highlight_tags_html(seg)}'
                f'</div>',
                unsafe_allow_html=True,
            )
            # Invisible button to set active segment
            if not is_active:
                if st.button(f"Seleccionar #{i+1}", key=f"sel_{i}",
                             help=f"Hacer activo el segmento #{i+1}",
                             use_container_width=True):
                    st.session_state.active_seg = i
                    st.rerun()
                st.markdown("""
                <style>
                div[data-testid="stButton"] button[kind="secondary"] {
                    font-size:.7rem !important; height:22px !important;
                    padding:.1rem .4rem !important; min-height:0 !important;
                    background:#F1F5F9 !important; color:#64748B !important;
                    border:1px solid #CBD5E1 !important; margin-top:2px;
                }
                </style>""", unsafe_allow_html=True)

        # ── Target ──
        with col_tgt:
            new_val = st.text_area(
                label=f"seg_{i}",
                value=translations.get(i, ""),
                key=f"ta_{i}",
                label_visibility="collapsed",
                height=90,
                placeholder=f"Segmento #{i+1}… | Ctrl+Enter para confirmar",
                disabled=is_confirmed,
                on_change=lambda idx=i: setattr(
                    st.session_state, "active_seg", idx
                ),
            )
            translations[i] = new_val
            st.session_state.translations = translations

            missing = check_missing_tags(seg, new_val)
            if new_val.strip() and missing and not is_confirmed:
                chips = " ".join(f'<span class="tag-chip">{html_lib.escape(t)}</span>' for t in missing)
                st.markdown(f'<div class="tag-warning">⚠️ Etiqueta(s) faltante(s): {chips}</div>',
                            unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # LIVE PREVIEW
    # ─────────────────────────────────────────
    if st.session_state.show_preview:
        st.markdown('<p class="section-title">👁️ Vista previa — Traducción completa</p>',
                    unsafe_allow_html=True)

        any_content = any(translations.get(i, "").strip() for i in range(len(segments)))
        if not any_content:
            body = '<span class="preview-placeholder">La traducción aparecerá aquí mientras escribes…</span>'
        else:
            rows = []
            for i, seg in enumerate(segments):
                t       = translations.get(i, "").strip()
                is_conf = confirmed.get(i, False)
                src_html = highlight_tags_html(seg)
                if t:
                    src_cls = "preview-seg-src" if is_conf else "preview-seg-src-pending"
                    note    = "" if is_conf else ' <em>(sin confirmar)</em>'
                    rows.append(
                        f'<div class="preview-segment">'
                        f'<div class="{src_cls}">#{i+1} {src_html}{note}</div>'
                        f'<div class="preview-seg-tgt">{render_translation_html(t)}</div>'
                        f'</div>'
                    )
                else:
                    rows.append(
                        f'<div class="preview-segment">'
                        f'<div class="preview-seg-src-pending" style="color:#D1D5DB">'
                        f'#{i+1} {src_html} <em>(pendiente)</em></div>'
                        f'</div>'
                    )
            body = "".join(rows)

        st.markdown(
            f'<div class="preview-panel">'
            f'<div class="preview-panel-title">📄 {st.session_state.target_lang} — '
            f'{n_confirmed}/{len(segments)} confirmados</div>'
            f'{body}</div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()