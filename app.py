import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import datetime

# -----------------------------------------------------------------------------
# 1. Google Sheet Endpoints
# -----------------------------------------------------------------------------
CALENDAR_DATA_URL = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=1456635855"
RAW_DATA_URL = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=528057576"
FINANCES_URL = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=1688426207"

# -----------------------------------------------------------------------------
# 2. Page Configuration & Custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Aura Dashboard 2026",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
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

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: #11151c !important;
        padding: 6px 8px !important;
        border-radius: 10px !important;
        border: 1px solid #222734 !important;
        margin-bottom: 16px !important;
    }

    .stTabs [data-baseweb="tab-border"] { display: none !important; }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; height: 0px !important; background-color: transparent !important; }

    .stTabs [data-baseweb="tab"] {
        height: 44px !important;
        border-radius: 8px !important;
        border: 1px solid #2a324b !important;
        padding: 0 20px !important;
        background-color: #161a22 !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stTabs [data-baseweb="tab"] *, .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #222734 !important;
        border: 1px solid #3b4252 !important;
        border-bottom: 3px solid #22c55e !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }

    .section-header {
        font-size: 15px;
        color: #cbd5e1;
        font-weight: 700;
        margin-top: 28px;
        margin-bottom: 10px;
    }

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

    .metric-value { font-size: 20px; font-weight: 700; }
    .metric-positive { color: #4ade80; }
    .metric-negative { color: #fb7185; }
    .metric-neutral  { color: #38bdf8; }

    .goal-card {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 6px;
    }

    .goal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
    .goal-title { font-size: 14px; font-weight: 700; color: #f8fafc; }
    .goal-badge { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 12px; text-transform: uppercase; }

    .badge-saved { background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid #16522c; }
    .badge-progress { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #1d4ed8; }
    .badge-waiting { background: rgba(250, 204, 21, 0.15); color: #facc15; border: 1px solid #713f12; }

    .progress-bar-bg { background: #222734; height: 7px; border-radius: 4px; overflow: hidden; margin: 6px 0; }
    .progress-bar-fill { height: 100%; border-radius: 4px; }
    .goal-footer { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; }

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
    .cf-row:last-child { border-bottom: none; }

    .stExpander {
        background: #161a22 !important;
        border: 1px solid #222734 !important;
        border-radius: 10px !important;
        margin-bottom: 6px !important;
    }

    .stExpander summary {
        background-color: #161a22 !important;
        color: #e2e8f0 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
    }

    .stExpander [data-testid="stExpanderDetails"] {
        background-color: #161a22 !important;
        padding: 4px 14px 10px 14px !important;
        border-top: 1px solid #222734 !important;
    }
    
    iframe { border: none !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Data Parsers
# -----------------------------------------------------------------------------
def clean_num(val):
    if pd.isna(val): return 0.0
    s = str(val).replace('$', '').replace(',', '').replace('%', '').strip()
    try:
        return float(s)
    except:
        return 0.0

@st.cache_data(ttl=30)
def fetch_calendar_data(calendar_url, raw_url):
    data_map = {}
    category_priority = {"Public Holiday": 5, "Holiday": 4, "Work Trip": 3, "Get-away": 2, "Working": 1}

    try:
        df_cal = pd.read_csv(calendar_url)
        df_cal.columns = df_cal.columns.str.strip()
        for _, row in df_cal.iterrows():
            raw_date = str(row.get("Date", "")).strip()
            if not raw_date or raw_date.lower() == "nan": continue
            try:
                date_key = pd.to_datetime(raw_date).strftime("%Y-%m-%d")
            except Exception: continue

            title = str(row.get("Title", "")).replace("nan", "").strip()
            time_val = str(row.get("Time", "")).replace("nan", "").strip()
            location_val = str(row.get("Location", "")).replace("nan", "").strip()
            category_val = str(row.get("Category", "Working")).replace("nan", "").strip() or "Working"

            if date_key not in data_map:
                data_map[date_key] = {"status": category_val, "events": [], "bills": []}
            else:
                if category_priority.get(category_val, 0) > category_priority.get(data_map[date_key]["status"], 0):
                    data_map[date_key]["status"] = category_val

            if title:
                data_map[date_key]["events"].append({"title": title, "time": time_val, "location": location_val, "category": category_val})
    except Exception as e:
        st.error(f"Error fetching CalendarData: {e}")

    try:
        df_raw = pd.read_csv(raw_url)
        df_raw.columns = df_raw.columns.str.strip()
        for _, row in df_raw.iterrows():
            raw_date = str(row.get("Date", "")).strip()
            if not raw_date or raw_date.lower() == "nan": continue
            try:
                date_key = pd.to_datetime(raw_date, dayfirst=True).strftime("%Y-%m-%d")
            except Exception: continue

            if date_key not in data_map:
                data_map[date_key] = {"status": "Working", "events": [], "bills": []}

            for col in df_raw.columns:
                if col.lower().startswith("bill"):
                    val = str(row.get(col, "")).replace("nan", "").strip()
                    if val: data_map[date_key]["bills"].append({"title": val})
    except Exception as e:
        st.error(f"Error fetching Raw Data: {e}")

    return data_map

@st.cache_data(ttl=30)
def fetch_finances_data(finances_url):
    try:
        df = pd.read_csv(finances_url, header=None)
    except Exception as e:
        st.error(f"Error fetching Finances sheet: {e}")
        return None

    fin_data = {
        "kpis": {"savings": 4937.98, "credit": -26117.95, "assets": 3129.96, "net": -18050.01},
        "income": {"total_wk": 0.0, "salary_wk": 0.0, "transfers_wk": 0.0},
        "expenses": {"total_wk": 0.0, "fixed_wk": 0.0, "variable_wk": 0.0, "holiday_wk": 0.0},
        "net_flow": {"wk": 0.0, "mo": 0.0, "yr": 0.0},
        "goals": [],
        "fixed_bills": [],
        "var_budgets": [],
        "debts": [],
        "assets": []
    }

    try:
        for r in range(len(df)):
            row_vals = [str(x).strip() for x in df.iloc[r].values]
            for c, v in enumerate(row_vals):
                if v == "Savings" and c < len(row_vals)-1:
                    fin_data["kpis"]["savings"] = clean_num(row_vals[c+1])
                elif v == "Credit" and c < len(row_vals)-1:
                    fin_data["kpis"]["credit"] = clean_num(row_vals[c+1])
                elif v == "Assets" and c < len(row_vals)-1:
                    fin_data["kpis"]["assets"] = clean_num(row_vals[c+1])
    except Exception: pass

    fin_data["kpis"]["net"] = fin_data["kpis"]["savings"] + fin_data["kpis"]["credit"] + fin_data["kpis"]["assets"]

    try:
        fin_data["income"]["total_wk"] = clean_num(df.iloc[3, 3])
        fin_data["income"]["salary_wk"] = clean_num(df.iloc[4, 3])
        fin_data["income"]["transfers_wk"] = clean_num(df.iloc[5, 3])

        fin_data["expenses"]["total_wk"] = clean_num(df.iloc[6, 3])
        fin_data["expenses"]["fixed_wk"] = clean_num(df.iloc[7, 3])
        fin_data["expenses"]["variable_wk"] = clean_num(df.iloc[14, 3])
        fin_data["expenses"]["holiday_wk"] = clean_num(df.iloc[18, 3])

        fin_data["net_flow"]["wk"] = clean_num(df.iloc[19, 3])
        fin_data["net_flow"]["mo"] = clean_num(df.iloc[19, 4])
        fin_data["net_flow"]["yr"] = clean_num(df.iloc[19, 6])
    except Exception: pass

    KNOWN_BILLS = {
        "rent": ("$721.25", "Weekly"),
        "electricity": ("$242.00", "Quarterly"),
        "gym": ("$35.20", "Weekly"),
        "credit card": ("$25.00", "Weekly"),
        "rt health": ("$153.15", "Monthly"),
        "internet": ("$49.00", "Monthly"),
    }

    for r in range(8, 14):
        try:
            name = str(df.iloc[r, 2]).strip()
            if name and name.lower() != 'nan':
                wk_impact = f"${clean_num(df.iloc[r, 3]):,.2f}"
                lookup_key = name.lower()
                if lookup_key in KNOWN_BILLS:
                    native_amt, freq = KNOWN_BILLS[lookup_key]
                else:
                    native_amt, freq = wk_impact, "Weekly"
                fin_data["fixed_bills"].append({"item": name, "weekly": wk_impact, "native": native_amt, "freq": freq})
        except: pass

    for r in range(15, 18):
        try:
            name = str(df.iloc[r, 2]).strip()
            if name and name.lower() != 'nan':
                wk_val = clean_num(df.iloc[r, 3])
                fin_data["var_budgets"].append({"item": name, "weekly": f"${wk_val:,.2f}"})
        except: pass

    goal_specs = [
        {"name": "Italy", "target": 7000.00, "end_date": "9-Sep-2026", "rate": 1037.50, "status": "IN PROGRESS"},
        {"name": "New Zealand", "target": 2087.98, "end_date": "", "rate": 0.00, "status": "SAVED"},
        {"name": "Adelaide", "target": 2600.00, "end_date": "30-Sep-2026", "rate": 650.00, "status": "WAITING"},
        {"name": "Emergency Fund", "target": 9000.00, "end_date": "6-Jan-2027", "rate": 692.31, "status": "WAITING"}
    ]

    for spec in goal_specs:
        g_name = spec["name"]
        bal_val = 0.0
        target_val = spec["target"]
        end_date = spec["end_date"]
        rate_val = spec["rate"]
        override_status = spec["status"]

        for r in range(len(df)):
            row_cells = [str(df.iloc[r, c]).strip() for c in range(len(df.columns))]
            for c, cell in enumerate(row_cells):
                if cell.lower() == g_name.lower():
                    if c > 0 and clean_num(row_cells[c-1]) > 0:
                        bal_val = clean_num(row_cells[c-1])

        if g_name == "Italy" and bal_val == 0.0: bal_val = 2850.00
        if g_name == "New Zealand" and bal_val == 0.0: bal_val = 2087.98

        pct = int((bal_val / target_val * 100)) if target_val > 0 else 0
        if pct > 100: pct = 100

        if override_status == "SAVED" or pct >= 100:
            badge = "SAVED"
            badge_class = "badge-saved"
            color = "#4ade80"
            details = "Target Achieved • $0/wk needed"
        elif override_status == "WAITING":
            badge = "WAITING"
            badge_class = "badge-waiting"
            color = "#facc15"
            details = f"Target: {end_date} • Contrib: ${rate_val:,.2f}/wk" if end_date else f"Contrib: ${rate_val:,.2f}/wk"
        else:
            badge = "IN PROGRESS"
            badge_class = "badge-progress"
            color = "#38bdf8"
            details = f"Target: {end_date} • Contrib: ${rate_val:,.2f}/wk" if end_date else f"Contrib: ${rate_val:,.2f}/wk"

        fin_data["goals"].append({
            "name": g_name, "current": bal_val, "target": target_val, "pct": pct,
            "badge": badge, "badge_class": badge_class, "color": color, "details": details
        })

    for r in [22, 23]:
        try:
            d_name = str(df.iloc[r, 2]).strip()
            if d_name and d_name.lower() != 'nan':
                owing = clean_num(df.iloc[r, 3])
                repay = clean_num(df.iloc[r, 4])
                occur = str(df.iloc[r, 5]).strip()
                close = str(df.iloc[r, 6]).strip()
                fin_data["debts"].append({"name": d_name, "owing": owing, "repay": repay, "occur": occur, "close": close})
        except: pass

    for r in range(3, 9):
        try:
            a_name = str(df.iloc[r, 10]).strip()
            if a_name and a_name.lower() != 'nan':
                cost = clean_num(df.iloc[r, 12])
                val = clean_num(df.iloc[r, 14])
                fin_data["assets"].append({"item": a_name, "price": f"${cost:,.2f}", "val": f"${val:,.2f}"})
        except: pass

    return fin_data

# -----------------------------------------------------------------------------
# 4. Streamlit Layout & Tabs
# -----------------------------------------------------------------------------
focus_date_str = st.query_params.get("focus_date", "")

tab_cal, tab_focus, tab_fin = st.tabs([
    "📅  Calendar & Schedule", 
    f"🔍  Focus View: {focus_date_str}" if focus_date_str else "🔍  Focus View (Double-click date)", 
    "💰  Finances & Net Worth"
])

# =============================================================================
# TAB 1: CALENDAR
# =============================================================================
with tab_cal:
    live_data = fetch_calendar_data(CALENDAR_DATA_URL, RAW_DATA_URL)
    json_data = json.dumps(live_data)

    today_date = datetime.date.today()
    today_formatted = today_date.strftime("%A, %B %d, %Y")
    today_m_idx = today_date.month - 1
    today_d_num = today_date.day

    calendar_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
        body {{ background-color: #0e1117; color: #f1f5f9; width: 100%; height: 100vh; overflow: hidden; display: flex; flex-direction: column; justify-content: flex-start; align-items: center; padding: 0; }}
        .top-bar {{ display: inline-flex; align-items: center; align-self: flex-start; background: #161a22; border: 1px solid #222734; border-radius: 8px; padding: 6px 12px; margin-bottom: 6px; }}
        .today-badge {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 2px 6px; border-radius: 12px; font-size: 10px; font-weight: 700; text-transform: uppercase; }}
        .today-date-text {{ font-size: 14px; font-weight: 700; color: #f8fafc; margin-left: 8px; }}
        .calendar-container {{ background: #161a22; border: 1px solid #222734; border-radius: 10px; padding: 8px 12px; width: 100%; margin: 0 auto; }}
        table.cal-grid {{ width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: 2px; }}
        th.col-header {{ color: #94a3b8; font-size: 10px; font-weight: 700; text-align: center; padding: 2px 0; width: 2.4%; }}
        th.col-header-first {{ width: 8%; text-align: left; padding-left: 4px; color: #cbd5e1; font-size: 12px; }}
        td.month-label {{ color: #94a3b8; font-size: 11px; font-weight: 600; padding: 2px 4px; white-space: nowrap; text-align: left; width: 8%; overflow: hidden; text-overflow: ellipsis; }}
        .day-cell {{ height: 26px; width: 2.4%; border-radius: 4px; text-align: center; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.1s ease; user-select: none; vertical-align: middle; border: 1px solid transparent; position: relative; }}
        .day-cell:hover {{ transform: scale(1.12); border-color: #ffffff99 !important; z-index: 10; }}
        .day-cell.is-today {{ box-shadow: 0 0 0 2px #38bdf8, 0 0 8px rgba(56, 189, 248, 0.6) !important; border-color: #38bdf8 !important; }}
        .day-cell.selected {{ outline: 2px solid #ffffff; outline-offset: 1px; }}
        .status-empty {{ background-color: transparent; border: none; cursor: default; }}
        
        .day-cell.is-past.status-working {{ background-color: #0b2213 !important; color: #23633d !important; border-color: #0e331b !important; }}
        .day-cell.is-past.status-public-holiday {{ background-color: #112244 !important; color: #2d558c !important; border-color: #142a52 !important; }}
        .day-cell.is-past.status-holiday {{ background-color: #2b030f !important; color: #823043 !important; border-color: #4a061a !important; }}
        .day-cell.is-past.status-get-away {{ background-color: #261303 !important; color: #876219 !important; border-color: #452105 !important; }}
        .day-cell.is-past.status-work-trip {{ background-color: #23043d !important; color: #6d4791 !important; border-color: #3d076b !important; }}

        .status-working {{ background-color: #133a20; color: #4ade80; border-color: #16522c; }}
        .status-public-holiday {{ background-color: #1e3a8a; color: #60a5fa; border-color: #1d4ed8; }}
        .status-holiday {{ background-color: #4c0519; color: #fb7185; border-color: #9f1239; }}
        .status-get-away {{ background-color: #422006; color: #facc15; border-color: #713f12; }}
        .status-work-trip {{ background-color: #3b0764; color: #c084fc; border-color: #6b21a8; }}

        .legend-bar {{ display: flex; gap: 10px; margin-top: 6px; flex-wrap: wrap; }}
        .legend-item {{ display: flex; align-items: center; gap: 5px; font-size: 10px; color: #94a3b8; background: #1a1e27; padding: 2px 6px; border-radius: 4px; border: 1px solid #28303f; }}
        .legend-dot {{ width: 7px; height: 7px; border-radius: 2px; }}
        .detail-panel {{ margin-top: 8px; background: #161a22; border: 1px solid #222734; border-radius: 10px; padding: 10px 14px; width: 100%; }}
        .panel-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
        .panel-title {{ font-size: 14px; font-weight: 700; color: #f8fafc; }}
        .status-badge {{ font-size: 10px; padding: 2px 6px; border-radius: 8px; font-weight: 600; }}
        .tab-bar {{ display: flex; gap: 8px; border-bottom: 1px solid #222734; margin-bottom: 8px; }}
        .tab-btn {{ background: none; border: none; color: #64748b; font-size: 11px; font-weight: 600; padding: 3px 8px; cursor: pointer; border-bottom: 2px solid transparent; }}
        .tab-btn.active {{ color: #38bdf8; border-bottom-color: #38bdf8; }}
        .tab-content {{ display: none; color: #94a3b8; font-size: 12px; }}
        .tab-content.active {{ display: block; }}
        .data-card {{ background: #1c212c; border-left: 3px solid #38bdf8; padding: 6px 10px; border-radius: 6px; margin-bottom: 4px; }}
        .bill-card {{ border-left-color: #facc15; }}
        .card-meta {{ display: flex; align-items: center; gap: 12px; margin-top: 2px; font-size: 11px; }}
        .meta-item {{ display: flex; align-items: center; gap: 4px; }}
        .click-hint {{ font-size: 10px; color: #38bdf8; margin-top: 6px; text-align: right; }}
    </style>
    </head>
    <body>

    <div class="top-bar">
        <span class="today-badge">Today</span>
        <span class="today-date-text">{today_formatted}</span>
    </div>

    <div class="calendar-container">
        <table class="cal-grid" id="calendarGrid"></table>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="legend-bar">
                <div class="legend-item"><div class="legend-dot" style="background:#4ade80"></div>Working</div>
                <div class="legend-item"><div class="legend-dot" style="background:#60a5fa"></div>Public Holiday</div>
                <div class="legend-item"><div class="legend-dot" style="background:#fb7185"></div>Holiday</div>
                <div class="legend-item"><div class="legend-dot" style="background:#facc15"></div>Get-away</div>
                <div class="legend-item"><div class="legend-dot" style="background:#c084fc"></div>Work Trip</div>
                <div class="legend-item"><div class="legend-dot" style="background:#38bdf8"></div>Today</div>
            </div>
            <div class="click-hint">💡 Single-click to preview bottom • Double-click to jump straight to Focus Tab</div>
        </div>
    </div>

    <div class="detail-panel">
        <div class="panel-header">
            <div class="panel-title" id="selectedDateTitle">Select a date</div>
            <div class="status-badge status-working" id="selectedStatusBadge">Working</div>
        </div>

        <div class="tab-bar">
            <button class="tab-btn active" onclick="switchTab('eventsTab', this)">Events & Schedule</button>
            <button class="tab-btn" onclick="switchTab('billsTab', this)">Bills</button>
        </div>

        <div id="eventsTab" class="tab-content active"></div>
        <div id="billsTab" class="tab-content"></div>
    </div>

    <script>
        const YEAR = 2026;
        const TODAY = {{ month: {today_m_idx}, day: {today_d_num} }};
        const sheetData = {json_data};

        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        const daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        const dayLetters = ["T", "W", "T", "F", "S", "S", "M"]; 
        const TOTAL_GRID_COLS = 37;

        function getCssClassForCategory(category) {{
            switch(category) {{
                case 'Holiday': return 'status-holiday';
                case 'Work Trip': return 'status-work-trip';
                case 'Get-away': return 'status-get-away';
                case 'Public Holiday': return 'status-public-holiday';
                default: return 'status-working';
            }}
        }}

        function isPastDate(mIdx, d) {{
            if (mIdx < TODAY.month) return true;
            if (mIdx === TODAY.month && d < TODAY.day) return true;
            return false;
        }}

        function renderGrid() {{
            const grid = document.getElementById('calendarGrid');
            let html = '<thead><tr><th class="col-header-first">2026</th>';
            for (let col = 0; col < TOTAL_GRID_COLS; col++) {{
                html += `<th class="col-header">${{dayLetters[col % 7]}}</th>`;
            }}
            html += '</tr></thead><tbody>';

            months.forEach((mName, mIdx) => {{
                html += `<tr><td class="month-label">${{mName}}</td>`;
                const totalDays = daysInMonths[mIdx];
                const offset = (new Date(YEAR, mIdx, 1).getDay() - 2 + 7) % 7; 
                let currentDay = 1;

                for (let col = 0; col < TOTAL_GRID_COLS; col++) {{
                    if (col >= offset && currentDay <= totalDays) {{
                        const d = currentDay;
                        const dateKey = `${{YEAR}}-${{String(mIdx + 1).padStart(2, '0')}}-${{String(d).padStart(2, '0')}}`;
                        const entry = sheetData[dateKey];
                        const categoryName = entry ? entry.status : 'Working';
                        const statusClass = getCssClassForCategory(categoryName);
                        const isToday = (mIdx === TODAY.month && d === TODAY.day);
                        const pastClass = isPastDate(mIdx, d) ? 'is-past' : '';
                        
                        html += `<td class="day-cell ${{statusClass}} ${{isToday ? 'is-today' : ''}} ${{pastClass}}" 
                                     id="cell-${{mIdx}}-${{d}}"
                                     onclick="selectDate(${{mIdx}}, ${{d}}, '${{mName}}', '${{categoryName}}', '${{statusClass}}', this)"
                                     ondblclick="doubleClickDate('${{dateKey}}')">
                                     ${{d}}
                               </td>`;
                        currentDay++;
                    }} else {{
                        html += '<td class="status-empty"></td>';
                    }}
                }}
                html += '</tr>';
            }});
            html += '</tbody>';
            grid.innerHTML = html;
        }}

        function selectDate(mIdx, day, monthName, statusName, statusClass, element) {{
            document.querySelectorAll('.day-cell').forEach(c => c.classList.remove('selected'));
            if (element) element.classList.add('selected');

            document.getElementById('selectedDateTitle').innerText = `${{monthName}} ${{day}}, ${{YEAR}}`;
            const badge = document.getElementById('selectedStatusBadge');
            badge.innerText = statusName;
            badge.className = `status-badge ${{statusClass}}`;

            const dateKey = `${{YEAR}}-${{String(mIdx + 1).padStart(2, '0')}}-${{String(day).padStart(2, '0')}}`;
            const dayData = sheetData[dateKey] || {{ events: [], bills: [] }};
            
            const eventsTab = document.getElementById('eventsTab');
            const eventsList = dayData.events || [];
            eventsTab.innerHTML = eventsList.length > 0 
                ? eventsList.map(e => `
                    <div class="data-card">
                        <div style="color:#fff; font-weight:600; font-size: 13px;">${{e.title}}</div>
                        ${{e.time || e.location ? `<div class="card-meta">
                            ${{e.time ? `<span class="meta-item" style="color:#38bdf8;">⏰ ${{e.time}}</span>` : ''}}
                            ${{e.location ? `<span class="meta-item" style="color:#94a3b8;">📍 ${{e.location}}</span>` : ''}}
                        </div>` : ''}}
                    </div>
                `).join('')
                : `<p style="color:#64748b;">No events recorded for this date.</p>`;

            const billsTab = document.getElementById('billsTab');
            const billsList = dayData.bills || [];
            billsTab.innerHTML = billsList.length > 0 
                ? billsList.map(b => `
                    <div class="data-card bill-card">
                        <div style="color:#fff; font-weight:600; font-size: 13px;">💸 ${{b.title}}</div>
                    </div>
                `).join('')
                : `<p style="color:#64748b;">No bills due on this date.</p>`;
        }}

        function doubleClickDate(dateKey) {{
            try {{
                window.parent.location.href = window.parent.location.pathname + '?focus_date=' + dateKey;
            }} catch (e) {{
                window.location.href = '?focus_date=' + dateKey;
            }}
        }}

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }}

        renderGrid();
        setTimeout(() => {{
            const todayCell = document.getElementById(`cell-${{TODAY.month}}-${{TODAY.day}}`);
            if (todayCell) selectDate(TODAY.month, TODAY.day, months[TODAY.month], 'Working', 'status-working', todayCell);
        }}, 50);
    </script>

    </body>
    </html>
    """
    components.html(calendar_html, height=695, scrolling=False)


# =============================================================================
# TAB 2: FOCUS VIEW
# =============================================================================
with tab_focus:
    live_data = fetch_calendar_data(CALENDAR_DATA_URL, RAW_DATA_URL)
    
    if not focus_date_str:
        st.markdown("""
        <div class="cashflow-card" style="text-align: center; padding: 40px;">
            <div style="font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 8px;">No Date Selected</div>
            <div style="font-size: 13px; color: #94a3b8;">Go to the <b>Calendar & Schedule</b> tab and <b>double-click</b> any date cell on the grid to jump straight here with full details loaded.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        try:
            sel_dt = datetime.datetime.strptime(focus_date_str, "%Y-%m-%d").date()
            sel_formatted = sel_dt.strftime("%A, %B %d, %Y")
        except:
            sel_dt = datetime.date.today()
            sel_formatted = sel_dt.strftime("%A, %B %d, %Y")

        st.markdown(f"<div class='section-header' style='margin-top:10px;'>🎯 Deep Dive: {sel_formatted}</div>", unsafe_allow_html=True)
        
        curr_data = live_data.get(focus_date_str, {"events": [], "bills": [], "status": "Working"})
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.markdown("<div style='font-size: 13px; font-weight: 700; color: #38bdf8; margin-bottom: 6px;'>📅 Today's Events</div>", unsafe_allow_html=True)
            if curr_data["events"]:
                for ev in curr_data["events"]:
                    st.markdown(f"""
                    <div class="data-card">
                        <div style="color:#fff; font-weight:600; font-size: 12px;">{ev['title']}</div>
                        {f"<div style='font-size:11px; color:#38bdf8;'>⏰ {ev['time']} | 📍 {ev['location']}</div>" if (ev['time'] or ev['location']) else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='cashflow-card' style='color:#64748b; font-size:12px;'>No events scheduled for today.</div>", unsafe_allow_html=True)

        with col_d2:
            st.markdown("<div style='font-size: 13px; font-weight: 700; color: #facc15; margin-bottom: 6px;'>💸 Today's Bills</div>", unsafe_allow_html=True)
            if curr_data["bills"]:
                for b in curr_data["bills"]:
                    st.markdown(f"""
                    <div class="data-card bill-card">
                        <div style="color:#fff; font-weight:600; font-size: 12px;">{b['title']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='cashflow-card' style='color:#64748b; font-size:12px;'>No bills due today.</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header' style='margin-top:24px;'>⚡ Upcoming Week (Next 7 Days)</div>", unsafe_allow_html=True)
        week_cols = st.columns(7)
        
        for i in range(1, 8):
            future_dt = sel_dt + datetime.timedelta(days=i)
            f_key = future_dt.strftime("%Y-%m-%d")
            f_data = live_data.get(f_key, {"events": [], "bills": []})
            f_label = future_dt.strftime("%a<br>%b %d")
            
            with week_cols[i-1]:
                ev_count = len(f_data["events"])
                bill_count = len(f_data["bills"])
                st.markdown(f"""
                <div class="metric-card" style="padding: 8px; min-height: 90px; text-align: left;">
                    <div style="font-size: 10px; font-weight: 700; color: #38bdf8; border-bottom: 1px solid #222734; padding-bottom: 3px; margin-bottom: 4px;">{f_label}</div>
                    <div style="font-size: 11px; color: {'#4ade80' if ev_count > 0 else '#64748b'};">🗓️ {ev_count} event{"" if ev_count == 1 else "s"}</div>
                    <div style="font-size: 11px; color: {'#facc15' if bill_count > 0 else '#64748b'};">💸 {bill_count} bill{"" if bill_count == 1 else "s"}</div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("🔍 View Detailed Schedule for Next 7 Days"):
            for i in range(1, 8):
                future_dt = sel_dt + datetime.timedelta(days=i)
                f_key = future_dt.strftime("%Y-%m-%d")
                f_data = live_data.get(f_key, {"events": [], "bills": []})
                if f_data["events"] or f_data["bills"]:
                    st.markdown(f"<b style='color:#f8fafc; font-size:12px;'>{future_dt.strftime('%A, %b %d')}:</b>", unsafe_allow_html=True)
                    for ev in f_data["events"]:
                        st.markdown(f"<span style='color:#38bdf8; font-size:11px; margin-left:10px;'>• Event: {ev['title']}</span>", unsafe_allow_html=True)
                    for b in f_data["bills"]:
                        st.markdown(f"<span style='color:#facc15; font-size:11px; margin-left:10px;'>• Bill: {b['title']}</span>", unsafe_allow_html=True)

        st.markdown("<div class='section-header' style='margin-top:24px;'>📅 Next Month Overview (Days 8 to 37)</div>", unsafe_allow_html=True)
        
        month_events_summary = []
        for i in range(8, 38):
            m_dt = sel_dt + datetime.timedelta(days=i)
            m_key = m_dt.strftime("%Y-%m-%d")
            m_data = live_data.get(m_key)
            if m_data and (m_data["events"] or m_data["bills"]):
                titles = [e['title'] for e in m_data["events"]] + [b['title'] for b in m_data["bills"]]
                month_events_summary.append({
                    "date": m_dt.strftime("%b %d (%a)"),
                    "items": ", ".join(titles)
                })

        if month_events_summary:
            summary_rows = "".join([
                f'''<div class="cf-row">
                    <span style="color:#38bdf8; font-weight:600; width: 110px; flex-shrink: 0;">{item["date"]}</span>
                    <span style="color:#cbd5e1; font-size:11px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{item["items"]}</span>
                </div>'''
                for item in month_events_summary
            ])
            st.markdown(f'<div class="cashflow-card" style="max-height: 180px; overflow-y: auto;">{summary_rows}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cashflow-card" style="color:#64748b; font-size:12px;">No recorded events or bills in the subsequent 30-day window.</div>', unsafe_allow_html=True)


# =============================================================================
# TAB 3: FINANCIAL DASHBOARD
# =============================================================================
with tab_fin:
    fin = fetch_finances_data(FINANCES_URL)

    if fin:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Savings Balance</div>
                <div class="metric-value metric-positive">${fin['kpis']['savings']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Credit / Debt</div>
                <div class="metric-value metric-negative">-${abs(fin['kpis']['credit']):,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Asset Value</div>
                <div class="metric-value metric-neutral">${fin['kpis']['assets']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Net Financial Position</div>
                <div class="metric-value metric-negative">-${abs(fin['kpis']['net']):,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        col_goals, col_cash = st.columns([1.2, 1])

        with col_goals:
            st.markdown("<div class='section-header' style='margin-top:28px;'>🎯 Savings & Goal Tracker</div>", unsafe_allow_html=True)

            for g in fin["goals"]:
                st.markdown(f"""
                <div class="goal-card">
                    <div class="goal-header">
                        <span class="goal-title">{g['name']}</span>
                        <span class="goal-badge {g['badge_class']}">{g['badge']}</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: {g['pct']}%; background: {g['color']};"></div>
                    </div>
                    <div class="goal-footer">
                        <span>${g['current']:,.2f} of ${g['target']:,.2f} ({g['pct']}%)</span>
                        <span>{g['details']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col_cash:
            st.markdown("<div class='section-header' style='margin-top:28px;'>📊 Cash Flow Summary</div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="cashflow-card">
                <div class="cf-row" style="font-weight:700; color:#4ade80;">
                    <span>Total Weekly Income</span>
                    <span>+${fin['income']['total_wk']:,.2f} / wk</span>
                </div>
                <div class="cf-row">
                    <span>↳ Salary</span>
                    <span>${fin['income']['salary_wk']:,.2f} / wk</span>
                </div>
                <div class="cf-row">
                    <span>↳ Transfers</span>
                    <span>${fin['income']['transfers_wk']:,.2f} / wk</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="cashflow-card">
                <div class="cf-row" style="font-weight:700; color:#fb7185;">
                    <span>Total Weekly Expenses</span>
                    <span>-${fin['expenses']['total_wk']:,.2f} / wk</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"↳ Fixed Bills Breakdown — ${fin['expenses']['fixed_wk']:,.2f} / wk"):
                for b in fin["fixed_bills"]:
                    st.markdown(f"""
                    <div class="cf-row" style="padding: 3px 0;">
                        <span style="color:#cbd5e1; font-weight:600;">{b['item']}</span>
                        <span style="color:#94a3b8; font-size:11px;">
                            Impact: <b style="color:#fb7185;">{b['weekly']}/wk</b> &nbsp;|&nbsp; 
                            Bill: <b style="color:#f8fafc;">{b['native']}</b> ({b['freq']})
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

            with st.expander(f"↳ Variable Budgets Breakdown — ${fin['expenses']['variable_wk']:,.2f} / wk"):
                for v in fin["var_budgets"]:
                    st.markdown(f"""
                    <div class="cf-row" style="padding: 3px 0;">
                        <span style="color:#cbd5e1; font-weight:600;">{v['item']}</span>
                        <span style="color:#94a3b8; font-size:11px;">
                            Impact: <b style="color:#fb7185;">{v['weekly']}/wk</b> &nbsp;|&nbsp; 
                            Budget: <b style="color:#f8fafc;">{v['weekly']}</b> (Weekly)
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

            with st.expander(f"↳ Holiday Allocation — ${fin['expenses']['holiday_wk']:,.2f} / wk"):
                st.markdown(f"""
                <div class="cf-row" style="padding: 3px 0;">
                    <span style="color:#cbd5e1; font-weight:600;">Holidays Allocation</span>
                    <span style="color:#94a3b8; font-size:11px;">
                        Impact: <b style="color:#fb7185;">${fin['expenses']['holiday_wk']:,.2f}/wk</b> &nbsp;|&nbsp; 
                        Budget: <b style="color:#f8fafc;">${fin['expenses']['holiday_wk']:,.2f}</b> (Weekly)
                    </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="cashflow-card" style="border-left: 3px solid #38bdf8;">
                <div class="cf-row" style="font-weight:700; color:#38bdf8; font-size:13px;">
                    <span>Net Savings Flow</span>
                    <span>+${fin['net_flow']['wk']:,.2f} / wk</span>
                </div>
                <div style="font-size:11px; color:#94a3b8; margin-top:2px;">
                    Equates to <b>+${fin['net_flow']['mo']:,.2f} / mo</b> and <b>+${fin['net_flow']['yr']:,.2f} / yr</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)

        b_col1, b_col2 = st.columns([1, 1])

        with b_col1:
            st.markdown("<div class='section-header' style='margin-top:28px;'>💳 Credit & Loan Repayments</div>", unsafe_allow_html=True)
            debt_rows = "".join([
                f'''<div class="cf-row">
                        <div>
                            <span style="font-weight:600; color:#fff;">{d["name"]}</span><br>
                            <span style="font-size:10px; color:#94a3b8;">Payoff target: {d["close"]}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:#fb7185; font-weight:700;">${d["owing"]:,.2f}</span><br>
                            <span style="font-size:10px; color:#94a3b8;">${d["repay"]:,.2f} / {d["occur"]}</span>
                        </div>
                    </div>'''
                for d in fin["debts"]
            ])
            st.markdown(f'<div class="cashflow-card">{debt_rows}</div>', unsafe_allow_html=True)

        with b_col2:
            st.markdown(f"<div class='section-header' style='margin-top:28px;'>🛋️ Physical Assets (${fin['kpis']['assets']:,.2f} Total)</div>", unsafe_allow_html=True)
            asset_rows = "".join([
                f'''<div class="cf-row">
                        <span style="color:#fff; font-weight:600;">{a["item"]}</span>
                        <span style="color:#94a3b8; font-size:11px;">Cost: {a["price"]} &nbsp;|&nbsp; <b style="color:#38bdf8;">Val: {a["val"]}</b></span>
                    </div>'''
                for a in fin["assets"]
            ])
            st.markdown(f'<div class="cashflow-card" style="max-height: 120px; overflow-y: auto;">{asset_rows}</div>', unsafe_allow_html=True)
    else:
        st.warning("Unable to fetch financial data from Google Sheets.")
