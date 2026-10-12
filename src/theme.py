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
    """Style actual Streamlit controls without adding borders to their children."""
    colors = theme_tokens(mode)
    variables = "\n".join(f"--ms-{key.replace('_', '-')}: {value};" for key, value in colors.items() if isinstance(value, str))
    return "<style>:root { color-scheme: " + str(colors["scheme"]) + ";" + variables + "}" + """
    [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"] {
      background: var(--ms-background); color: var(--ms-text);
    }
    [data-testid="stHeader"] { background: var(--ms-background); }
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
      background: var(--ms-sidebar); color: var(--ms-text);
    }
    [data-testid="stSidebar"] { border-right: 1px solid var(--ms-border); }
    .block-container { max-width: 1500px; padding: 4.5rem 2rem 3rem; }
    .hero { padding: 0 0 0.7rem; }
    .eyebrow { color: var(--ms-accent); font-size: .72rem; letter-spacing: .13em; font-weight: 700; }
    .hero h1 { color: var(--ms-text); font-size: clamp(2rem, 4vw, 3rem); line-height: 1.12;
      margin: .45rem 0 .65rem; letter-spacing: -.045em; }
    .hero p { color: var(--ms-muted); max-width: 780px; margin: 0; line-height: 1.6; }
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5, [data-testid="stWidgetLabel"] { color: var(--ms-text); }
    [data-testid="stCaptionContainer"] { opacity: 1 !important; }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .source-note {
      color: var(--ms-muted) !important; line-height: 1.6;
    }
    .hero p { color: var(--ms-muted) !important; }
    a { color: var(--ms-link) !important; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; margin: .3rem 0 1.5rem; }
    .kpi-card { background: var(--ms-panel); border: 1px solid var(--ms-border);
      border-radius: 14px; padding: 1.1rem; min-width: 0; }
    .kpi-label { color: var(--ms-muted); font-size: .84rem; line-height: 1.4; }
    .kpi-value { color: var(--ms-text); font-size: clamp(1.6rem, 3vw, 2rem); font-weight: 650;
      line-height: 1.2; margin-top: .55rem; overflow-wrap: anywhere; }
    /* React Aria paints the field wrapper; inputs and arrow buttons stay transparent. */
    :is([data-testid="stSelectbox"], [data-testid="stMultiSelect"]) .react-aria-ComboBox > [role="group"] {
      background: var(--ms-control) !important; color: var(--ms-text) !important;
      border: 1px solid var(--ms-border) !important; border-radius: 10px !important;
    }
    :is([data-testid="stSelectbox"], [data-testid="stMultiSelect"]) input,
    :is([data-testid="stSelectbox"], [data-testid="stMultiSelect"]) button {
      color: var(--ms-text) !important; background: transparent !important; border: 0 !important;
      box-shadow: none !important; border-radius: 0 !important;
    }
    [data-testid="stMultiSelect"] [data-tag] {
      background: var(--ms-accent) !important; color: var(--ms-on-accent) !important;
      border-radius: 5px;
    }
    [data-testid="stMultiSelect"] [data-tag] *, [data-testid="stMultiSelect"] [data-tag] button {
      color: var(--ms-on-accent) !important;
    }
    [data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"] {
      background: var(--ms-control) !important; border-color: var(--ms-border) !important; border-radius: 10px;
    }
    [data-testid="stTextInputRootElement"] input, [data-testid="stNumberInputContainer"] input {
      background: transparent !important;
    }
    [data-testid="stTooltipIcon"] button, [data-testid="stNumberInputContainer"] button {
      color: var(--ms-muted) !important; background: transparent !important;
    }
    [data-testid="stTooltipIcon"] svg { stroke: var(--ms-muted) !important; }
    [data-testid="stSlider"] [data-rac][style*="position: relative"] {
      background: var(--ms-border) !important;
    }
    [data-testid="stSlider"] [data-rac][style*="position: relative"] > div:first-child,
    [data-testid="stSlider"] div[data-rac]:has(> div > input[type="range"]) {
      background: var(--ms-accent) !important;
    }
    [data-testid="stDownloadButton"] button {
      background: var(--ms-panel); color: var(--ms-text); border-color: var(--ms-border);
    }
    input, textarea { color: var(--ms-text) !important; }
    input::placeholder, textarea::placeholder { color: var(--ms-muted) !important; opacity: 1 !important; }
    [role="listbox"] { background: var(--ms-panel) !important; color: var(--ms-text) !important;
      border: 1px solid var(--ms-border); border-radius: 10px; }
    [role="option"] { color: var(--ms-text) !important; }
    [role="option"][data-focused="true"], [role="option"][aria-selected="true"] {
      background: var(--ms-sidebar) !important;
    }
    .st-key-appearance_mode [role="radiogroup"] { gap: .5rem; }
    .st-key-appearance_mode [data-testid="stRadioOption"] { border: 1px solid var(--ms-border); background: var(--ms-panel);
      border-radius: 8px; padding: .4rem .8rem; margin: 0; }
    .st-key-appearance_mode [data-testid="stRadioOption"]:has(input:checked) { background: var(--ms-accent); border-color: var(--ms-accent); }
    .st-key-appearance_mode [data-testid="stRadioOption"]:has(input:checked) p { color: var(--ms-on-accent) !important; font-weight: 650; }
    .st-key-appearance_mode [data-testid="stRadioOption"] > div > div:first-child { display: none; }
    button:focus-visible, input:focus-visible, .st-key-appearance_mode [data-testid="stRadioOption"]:has(input:focus-visible) {
      outline: 2px solid var(--ms-accent) !important; outline-offset: 3px;
    }
    [data-testid="stSidebarCollapseButton"] { opacity: 1 !important; visibility: visible !important; }
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapseButton"] span, [data-testid="stExpandSidebarButton"] span,
    [data-testid="stToolbar"] button, [data-testid="stToolbar"] span {
      color: var(--ms-muted) !important;
    }
    [data-testid="stExpander"] details { border-color: var(--ms-border); background: var(--ms-sidebar); }
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color: var(--ms-text) !important; }
    [data-testid="stTabs"] [role="tab"] { color: var(--ms-muted) !important; }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: var(--ms-accent) !important; }
    [data-testid="stTabsScrollRight"], [data-testid="stTabsScrollLeft"] {
      background: var(--ms-background) !important; color: var(--ms-text) !important;
    }
    .ms-table { overflow: auto; max-height: 520px; border: 1px solid var(--ms-border); border-radius: 12px; }
    .ms-table table { width: 100%; border-collapse: collapse; background: var(--ms-panel); color: var(--ms-text); font-size: .88rem; }
    .ms-table th { position: sticky; top: 0; background: var(--ms-sidebar); color: var(--ms-text); text-align: left; z-index: 1; }
    .ms-table td, .ms-table th { padding: .75rem 1rem; border-bottom: 1px solid var(--ms-border); white-space: nowrap; }
    .ms-table tbody tr:hover { background: var(--ms-sidebar); }
    hr { border-color: var(--ms-border) !important; }
    @media (max-width: 1150px) { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 1000px) { .block-container { padding-left: 1.25rem; padding-right: 1.25rem; } }
    @media (max-width: 640px) { .block-container { padding: 4rem 1rem 2rem; }
      .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .65rem; }
      .kpi-card { padding: .9rem; } .hero h1 { font-size: 2rem; }
    }
    </style>
    """
