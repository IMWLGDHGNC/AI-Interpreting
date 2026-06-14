"""Custom CSS and display helpers for the AI+ Interpreting Training Platform."""

import streamlit as st

# ── icon / accent colour maps for result cards ──────────────────────────
ICON_MAP = {
    "transcription": "🎙️",
    "translation": "🌐",
    "paraphrase": "🔄",
    "notes": "📝",
    "default": "📋",
}
ACCENT_COLORS = {
    "transcription": "#3B82F6",  # blue
    "translation": "#10B981",    # green
    "paraphrase": "#F59E0B",     # amber
    "notes": "#8B5CF6",          # purple
    "default": "#6B7280",        # gray
}


def inject_custom_css() -> None:
    """Inject all custom CSS into the Streamlit app.  Call once at startup."""

    css = """
    <style>
    /* ── Global typography ─────────────────────────────────────── */
    .stApp {
        font-feature-settings: "kern" 1, "liga" 1;
        text-rendering: optimizeLegibility;
    }
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1280px;
    }
    h1 { font-weight: 700; letter-spacing: -0.02em; font-size: 2rem; }
    h2 { font-weight: 600; letter-spacing: -0.01em; }
    h3 { font-weight: 600; }
    h5 { font-weight: 600; margin-top: 0.75rem; }

    /* ── Buttons ───────────────────────────────────────────────── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stButton > button[kind="primary"] {
        font-weight: 600;
        letter-spacing: 0.01em;
    }

    /* ── Cards (bordered containers) ───────────────────────────── */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    }

    /* ── Result cards ──────────────────────────────────────────── */
    .result-card-header {
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }
    .result-card-accent {
        display: inline-block;
        width: 4px;
        height: 1.2em;
        border-radius: 2px;
        margin-right: 0.5rem;
        vertical-align: middle;
    }

    /* ── Sidebar ───────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(
            180deg,
            rgba(79, 70, 229, 0.03) 0%,
            transparent 30%
        );
    }
    [data-testid="stSidebar"] hr {
        margin: 1rem 0;
    }
    [data-testid="stSidebar"] .stTextInput label {
        font-weight: 500;
        font-size: 0.875rem;
    }

    /* ── Tabs ──────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.25rem;
        font-weight: 500;
        margin-right: 2px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        font-weight: 600;
    }

    /* ── Expanders / history ───────────────────────────────────── */
    [data-testid="stExpander"] {
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.12);
        margin-bottom: 0.5rem;
    }
    [data-testid="stExpander"] details summary {
        font-weight: 500;
        padding: 0.5rem 0.75rem;
    }

    /* ── Select boxes & inputs ─────────────────────────────────── */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    input[type="text"], input[type="password"] {
        border-radius: 8px !important;
    }

    /* ── Audio player spacing ──────────────────────────────────── */
    .stAudio {
        padding: 0.5rem 0;
        margin: 0.5rem 0;
    }

    /* ── Footer ────────────────────────────────────────────────── */
    footer { visibility: hidden; }
    .app-footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(128,128,128,0.15);
        text-align: center;
    }

    /* ── General utility ───────────────────────────────────────── */
    hr { margin: 1.25rem 0; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_result_card(title: str, content: str, card_type: str = "default") -> None:
    """Render a styled result card with a colored left accent bar and emoji icon.

    Parameters
    ----------
    title : str
        Card title (e.g. "转写文本", "翻译结果").
    content : str
        The body text to display inside the card.
    card_type : str
        One of ``"transcription"``, ``"translation"``, ``"paraphrase"``,
        ``"notes"``, or ``"default"``.  Determines the accent colour and icon.
    """
    icon = ICON_MAP.get(card_type, ICON_MAP["default"])
    accent = ACCENT_COLORS.get(card_type, ACCENT_COLORS["default"])

    with st.container(border=True):
        st.markdown(
            f'<div class="result-card-header">'
            f'<span class="result-card-accent" style="background-color:{accent};"></span>'
            f'{icon} {title}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(content)


def render_section_header(emoji: str, title: str, subtitle: str | None = None) -> None:
    """Render a consistent section header with an emoji and optional subtitle."""
    st.markdown(f"### {emoji} {title}")
    if subtitle:
        st.caption(subtitle)


def render_status_badge(label: str, badge_type: str = "info") -> None:
    """Render a small coloured pill badge.

    badge_type may be ``"info"``, ``"success"``, ``"warning"``, or ``"error"``.
    """
    colors = {
        "info": "#3B82F6",
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444",
    }
    color = colors.get(badge_type, colors["info"])
    st.markdown(
        f'<span style="display:inline-block;padding:2px 10px;border-radius:12px;'
        f'font-size:0.8rem;font-weight:500;'
        f'background:{color}20;color:{color};'
        f'border:1px solid {color}40;margin-right:0.5rem;">'
        f'{label}</span>',
        unsafe_allow_html=True,
    )
