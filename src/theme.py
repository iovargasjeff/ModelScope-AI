"""Shared color tokens and app styling for light and dark appearance modes."""

from __future__ import annotations

THEMES: dict[str, dict[str, object]] = {
    "Dark": {
        "scheme": "dark",
        "background": "#0B1220",
        "sidebar": "#0E1828",
        "panel": "#121F32",
        "control": "#0B1627",
        "text": "#E7EEF8",
        "muted": "#91A2B9",
        "border": "#26374E",
        "accent": "#61D2C2",
        "on_accent": "#0B1220",
        "link": "#8AB5FF",
        "grid": "rgba(148,163,184,0.13)",
        "plot_template": "plotly_dark",
        "chart_colors": [
            "#75A7FF", "#56D6B1", "#F5C451", "#AA8BFF",
            "#53C5D9", "#F28E6B", "#E879B9", "#96C36B",
        ],
    },
    "Light": {
        "scheme": "light",
        "background": "#F3F6FB",
        "sidebar": "#EAF0F7",
        "panel": "#FFFFFF",
        "control": "#FFFFFF",
        "text": "#17263B",
        "muted": "#5D6D82",
        "border": "#D7E1ED",
        "accent": "#147B73",
        "on_accent": "#FFFFFF",
        "link": "#285CC5",
        "grid": "rgba(71,84,103,0.14)",
        "plot_template": "plotly_white",
        "chart_colors": [
            "#315FBB", "#13816F", "#A96A00", "#7652B5",
            "#167F9B", "#C45D26", "#BA427B", "#5F8126",
        ],
    },
}


def theme_tokens(mode: str) -> dict[str, object]:
    """Return the shared tokens for a known appearance mode."""
    return THEMES.get(mode, THEMES["Dark"])


def theme_css(mode: str) -> str:
    """Build responsive Streamlit CSS from the shared appearance tokens."""
    colors = theme_tokens(mode)
    return f"""
    <style>
    :root {{
      color-scheme: {colors['scheme']};
      --ms-bg: {colors['background']};
      --ms-sidebar: {colors['sidebar']};
      --ms-panel: {colors['panel']};
      --ms-control: {colors['control']};
      --ms-text: {colors['text']};
      --ms-muted: {colors['muted']};
      --ms-border: {colors['border']};
      --ms-accent: {colors['accent']};
      --ms-on-accent: {colors['on_accent']};
      --ms-link: {colors['link']};
      --ms-grid: {colors['grid']};
    }}
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
      background: var(--ms-bg) !important;
      color: var(--ms-text) !important;
      transition: background-color 180ms ease, color 180ms ease;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{ background: transparent; }}
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{
      background: var(--ms-sidebar) !important;
      border-right: 1px solid var(--ms-border);
    }}
    .block-container {{
      max-width: 1500px;
      padding-top: 1.35rem;
      padding-bottom: 3rem;
    }}
    .hero {{ padding: 0.2rem 0 0.8rem; }}
    .eyebrow {{
      color: var(--ms-accent);
      font-size: 0.72rem;
      letter-spacing: 0.15em;
      font-weight: 750;
      text-transform: uppercase;
    }}
    .hero h1 {{
      color: var(--ms-text);
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1.05;
      margin: 0.45rem 0 0.4rem;
      font-weight: 740;
      letter-spacing: -0.045em;
    }}
    .hero p {{ color: var(--ms-muted); font-size: 1rem; max-width: 780px; margin: 0; }}
    .section-title {{ color: var(--ms-text); font-weight: 680; letter-spacing: -0.02em; }}
    [data-testid="stMetric"] {{
      background: var(--ms-panel);
      border: 1px solid var(--ms-border);
      padding: 1rem 1.05rem;
      border-radius: 15px;
      box-shadow: 0 7px 20px rgba(17, 29, 47, 0.06);
    }}
    [data-testid="stMetricLabel"] {{ color: var(--ms-muted) !important; }}
    [data-testid="stMetricValue"] {{ color: var(--ms-text) !important; }}
    [data-testid="stCaptionContainer"] p, .source-note {{ color: var(--ms-muted) !important; }}
    [data-testid="stWidgetLabel"] p {{ color: var(--ms-text) !important; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
      color: var(--ms-text);
      letter-spacing: -0.02em;
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color: var(--ms-muted); }}
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"],
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div > div,
    div[data-baseweb="select"] > div {{
      background: var(--ms-control) !important;
      color: var(--ms-text) !important;
      border-color: var(--ms-border) !important;
      border-radius: 10px;
    }}
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stSelectbox"] button[aria-haspopup="listbox"],
    [data-testid="stMultiSelect"] [role="combobox"],
    [data-testid="stMultiSelect"] button[aria-haspopup="listbox"] {{
      background: var(--ms-control) !important;
      color: var(--ms-text) !important;
      border: 1px solid var(--ms-border) !important;
      border-radius: 10px !important;
    }}
    [role="combobox"] {{
      background: var(--ms-control) !important;
      color: var(--ms-text) !important;
      border-color: var(--ms-border) !important;
    }}
    [data-testid="stMultiSelect"] {{
      background: var(--ms-control) !important;
      color: var(--ms-text) !important;
      border: 1px solid var(--ms-border) !important;
      border-radius: 10px !important;
    }}
    [data-testid="stMultiSelect"] input {{
      background: transparent !important;
      color: var(--ms-text) !important;
    }}
    [data-testid="stMultiSelect"] input::placeholder,
    [data-testid="stMultiSelect"] [data-placeholder="true"] {{
      color: var(--ms-muted) !important;
      opacity: 1 !important;
    }}
    [data-testid="stMultiSelect"] div:has(input) {{
      background: var(--ms-control) !important;
      color: var(--ms-text) !important;
      border-color: var(--ms-border) !important;
    }}
    [data-testid="stSelectbox"] [data-baseweb="select"] *,
    [data-testid="stMultiSelect"] [data-baseweb="select"] * {{ color: var(--ms-text); }}
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {{
      background: var(--ms-accent) !important;
      color: var(--ms-on-accent) !important;
      border-color: transparent !important;
    }}
    [data-testid="stMultiSelect"] [data-baseweb="tag"] * {{ color: var(--ms-on-accent) !important; }}
    [data-testid="stSelectbox"] [data-baseweb="select"] svg,
    [data-testid="stMultiSelect"] [data-baseweb="select"] svg {{ fill: var(--ms-muted); }}
    [data-testid="stTextInput"] input::placeholder {{ color: var(--ms-muted) !important; }}
    div[data-baseweb="popover"], div[data-baseweb="popover"] ul {{
      background: var(--ms-panel) !important;
      color: var(--ms-text) !important;
      border-color: var(--ms-border) !important;
    }}
    div[data-baseweb="popover"] li {{ color: var(--ms-text) !important; }}
    [data-testid="stTabs"] button {{ color: var(--ms-muted); }}
    [data-testid="stTabs"] button[aria-selected="true"] {{
      color: var(--ms-accent) !important;
      border-bottom-color: var(--ms-accent) !important;
    }}
    [data-testid="stSegmentedControl"] {{ color: var(--ms-text); }}
    [data-testid="stSegmentedControl"] button {{ color: var(--ms-muted); }}
    [data-testid="stSegmentedControl"] button[aria-pressed="true"] {{
      color: var(--ms-on-accent) !important;
      background: var(--ms-accent) !important;
      border-color: var(--ms-accent) !important;
    }}
    [data-testid="stDataFrame"] {{
      border: 1px solid var(--ms-border);
      border-radius: 12px;
      overflow: hidden;
    }}
    div[data-testid="stAlert"] {{ border-radius: 12px; }}
    a {{ color: var(--ms-link) !important; }}
    hr, [data-testid="stDivider"] {{ border-color: var(--ms-border) !important; }}
    @media (max-width: 760px) {{
      .block-container {{ padding: 1rem 1rem 2rem; }}
      .hero {{ padding-bottom: 0.4rem; }}
    }}
    </style>
    """
