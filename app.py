st.markdown("""
<style>
    /* Global Reset */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0e1117 !important;
        color: #f1f5f9 !important;
    }

    .main .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }

    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Streamlit Native Tab Bar Container */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: #11151c !important;
        padding: 6px 8px !important;
        border-radius: 10px !important;
        border: 1px solid #222734 !important;
        margin-bottom: 16px !important;
    }

    /* KILL STREAMLIT DEFAULT RED UNDERLINE HIGHLIGHT & BORDER */
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
        height: 0px !important;
        background-color: transparent !important;
    }

    /* UNSELECTED TABS - BOLD PURE WHITE TEXT */
    .stTabs [data-baseweb="tab"] {
        height: 44px !important;
        border-radius: 8px !important;
        border: 1px solid #2a324b !important;
        padding: 0 20px !important;
        background-color: #161a22 !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* Force text to bold pure white on all inner tab elements */
    .stTabs [data-baseweb="tab"] *,
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] button {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    /* Hover State for Unselected Tabs */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #1c212c !important;
        border-color: #3b4252 !important;
    }

    /* SELECTED TAB - Dark Slate + Green Bottom Border ONLY */
    .stTabs [aria-selected="true"] {
        background-color: #222734 !important;
        border: 1px solid #3b4252 !important;
        border-bottom: 3px solid #22c55e !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }

    .stTabs [aria-selected="true"] *,
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Section Headers styling */
    .section-header {
        font-size: 15px;
        color: #cbd5e1;
        font-weight: 700;
        margin-top: 28px;
        margin-bottom: 10px;
    }

    /* Metric Cards */
    .metric-card {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    
    .metric-title {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 2px;
    }

    .metric-value {
        font-size: 20px;
        font-weight: 700;
    }

    .metric-positive { color: #4ade80; }
    .metric-negative { color: #fb7185; }
    .metric-neutral  { color: #38bdf8; }

    /* Goal Cards */
    .goal-card {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 6px;
    }

    .goal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }

    .goal-title {
        font-size: 14px;
        font-weight: 700;
        color: #f8fafc;
    }

    .goal-badge {
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 12px;
        text-transform: uppercase;
    }

    .badge-saved { background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid #16522c; }
    .badge-progress { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #1d4ed8; }
    .badge-waiting { background: rgba(250, 204, 21, 0.15); color: #facc15; border: 1px solid #713f12; }

    .progress-bar-bg {
        background: #222734;
        height: 7px;
        border-radius: 4px;
        overflow: hidden;
        margin: 6px 0;
    }

    .progress-bar-fill {
        height: 100%;
        border-radius: 4px;
    }

    .goal-footer {
        display: flex;
        justify-content: space-between;
        font-size: 11px;
        color: #94a3b8;
    }

    /* Cashflow Containers */
    .cashflow-card {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
    }

    .cf-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        border-bottom: 1px solid #1c212c;
        font-size: 12px;
    }

    .cf-row:last-child {
        border-bottom: none;
    }

    /* Streamlit Expander Dark Theme Overrides */
    .stExpander {
        background: #161a22 !important;
        border: 1px solid #222734 !important;
        border-radius: 10px !important;
        margin-bottom: 6px !important;
        padding: 0px !important;
        overflow: hidden !important;
    }

    .stExpander details {
        background-color: #161a22 !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 10px !important;
    }

    .stExpander summary {
        background-color: #161a22 !important;
        color: #e2e8f0 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        transition: background-color 0.15s ease, color 0.15s ease;
    }

    .stExpander summary:hover,
    .stExpander summary:focus,
    .stExpander summary:active,
    .stExpander details[open] > summary {
        background-color: #1c212c !important;
        color: #ffffff !important;
        outline: none !important;
        box-shadow: none !important;
    }

    .stExpander summary p {
        color: inherit !important;
    }

    .stExpander summary svg {
        fill: #94a3b8 !important;
        color: #94a3b8 !important;
    }

    .stExpander [data-testid="stExpanderDetails"] {
        background-color: #161a22 !important;
        padding: 4px 14px 10px 14px !important;
        border-top: 1px solid #222734 !important;
    }
    
    iframe {
        border: none !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)
