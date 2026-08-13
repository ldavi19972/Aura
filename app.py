import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------------------------------------------------------
# 1. Google Sheet Endpoints & API Setup
# -----------------------------------------------------------------------------
CALENDAR_DATA_URL = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=1456635855"
RAW_DATA_URL = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=528057576"
FINANCES_URL = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=1688426207"
SHEET_ID = "1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI"

def authenticate_gspread():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    return client

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
        padding-top: 0.4rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }

    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    div[data-testid="stVerticalBlock"] > div.stTabs {
        display: none !important;
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
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 6px 10px !important;
        border-radius: 10px !important;
    }

    .stExpander [data-testid="stExpanderDetails"] {
        background-color: #161a22 !important;
        padding: 8px 10px 16px 10px !important;
        border-top: 1px solid #222734 !important;
        min-height: 55px;
        max-height: 1000px;
        overflow-y: auto;
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
        "kpis": {"savings": 3290.32, "credit": -26058.52, "assets": 3128.64, "net": -22929.88},
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
        fin_data["kpis"]["savings"] = clean_num(df.iloc[3, 17])
        fin_data["kpis"]["credit"] = clean_num(df.iloc[4, 17])
        fin_data["kpis"]["assets"] = clean_num(df.iloc[5, 17])
    except Exception:
        pass

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

    transfer_balance_mapping = {}
    for r in range(25, 35):
        if r < len(df):
            name_val = str(df.iloc[r, 2]).strip()
            if name_val and name_val.lower() != 'nan':
                transfer_balance_mapping[name_val] = {"row": r, "balance": clean_num(df.iloc[r, 1])}

    for r in range(14, 25):
        try:
            g_name = str(df.iloc[r, 10]).strip() # Column K (Goal Name)
            if not g_name or g_name.lower() == 'nan': continue
            if "savings by" in g_name.lower(): continue # Skip header/calculation rows
            
            target_val = clean_num(df.iloc[r, 11]) # Column L (Target Amount)
            end_date = str(df.iloc[r, 13]).strip() if pd.notna(df.iloc[r, 13]) else "" # Column N (End Date)
            if end_date.lower() == 'nan': end_date = ""
            start_date = str(df.iloc[r, 14]).strip() if pd.notna(df.iloc[r, 14]) else "" # Column O (Start Date)
            if start_date.lower() == 'nan': start_date = ""
            
            p_val_raw = str(df.iloc[r, 15]).strip() if pd.notna(df.iloc[r, 15]) else "" # Column P
            
            rate_val = 0.0
            status_text = "IN PROGRESS"
            
            if p_val_raw.upper() in ["WAITING", "SAVED", "IN PROGRESS"]:
                status_text = p_val_raw.upper()
            else:
                rate_val = clean_num(p_val_raw)
                if rate_val > 0: status_text = "IN PROGRESS"

            bal_val = 0.0
            t_info = transfer_balance_mapping.get(g_name)
            if t_info:
                bal_val = t_info["balance"]

            pct = int((bal_val / target_val * 100)) if target_val > 0 else 0
            if pct > 100: pct = 100

            if status_text == "SAVED" or pct >= 100:
                badge = "SAVED"
                badge_class = "badge-saved"
                color = "#4ade80"
                details = "Target Achieved • $0/wk needed"
            elif status_text == "WAITING":
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
                "index": r,
                "name": g_name, "current": bal_val, "target": target_val, 
                "start_date": start_date, "end_date": end_date, "rate": rate_val, "pct": pct,
                "badge": badge, "badge_class": badge_class, "color": color, "details": details
            })
        except Exception:
            pass

    for r in range(21, 25):
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
# 4. State Management
# -----------------------------------------------------------------------------
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Calendar"

query_params = st.query_params
if "tab" in query_params:
    st.session_state["active_tab"] = query_params["tab"]

current_tab = st.session_state["active_tab"]

# -----------------------------------------------------------------------------
# 5. Render Custom Navigation Bar
# -----------------------------------------------------------------------------
col_nav1, col_nav2, col_nav3, col_spacer = st.columns([1.0, 1.1, 1.2, 5])

with col_nav1:
    is_cal_active = (current_tab == "Calendar")
    btn_type = "primary" if is_cal_active else "secondary"
    if st.button("📅 Calendar", use_container_width=True, type=btn_type):
        st.session_state["active_tab"] = "Calendar"
        st.rerun()

with col_nav2:
    is_focus_active = (current_tab == "Focus")
    btn_type = "primary" if is_focus_active else "secondary"
    if st.button("🔍 Focus View", use_container_width=True, type=btn_type):
        st.session_state["active_tab"] = "Focus"
        st.rerun()

with col_nav3:
    is_fin_active = (current_tab == "Finances")
    btn_type = "primary" if is_fin_active else "secondary"
    if st.button("💰 Finances & Net Worth", use_container_width=True, type=btn_type):
        st.session_state["active_tab"] = "Finances"
        st.rerun()

st.markdown("""
<style>
    button[kind="secondary"] {
        background-color: #161a22 !important;
        border: 1px solid #28303f !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #1e2532 !important;
        border-color: #3b82f6 !important;
        color: #ffffff !important;
    }
    button[kind="primary"] {
        background-color: #3b82f6 !important;
        border: 1px solid #60a5fa !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

# =============================================================================
# TAB 1: CALENDAR
# =============================================================================
if current_tab == "Calendar":
    live_data = fetch_calendar_data(CALENDAR_DATA_URL, RAW_DATA_URL)
    json_data = json.dumps(live_data)

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
        <span class="today-date-text" id="todayText">Loading...</span>
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
            <div class="click-hint">💡 Click any date in your calendar to preview details below</div>
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
        const now = new Date();
        const TODAY = {{ month: now.getMonth(), day: now.getDate() }};
        const options = {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }};
        document.getElementById('todayText').innerText = now.toLocaleDateString('en-US', options);

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
                                     onclick="selectDate(${{mIdx}}, ${{d}}, '${{mName}}', '${{categoryName}}', '${{statusClass}}', this)">
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

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }}

        renderGrid();
        setTimeout(() => {{
            const targetCell = document.getElementById(`cell-${{TODAY.month}}-${{TODAY.day}}`);
            if (targetCell) {{
                targetCell.classList.add('selected');
                selectDate(TODAY.month, TODAY.day, months[TODAY.month], 'Working', 'status-working', targetCell);
            }}
        }}, 50);
    </script>

    </body>
    </html>
    """
    components.html(calendar_html, height=695, scrolling=False)


# =============================================================================
# TAB 2: FOCUS VIEW
# =============================================================================
elif current_tab == "Focus":
    live_data = fetch_calendar_data(CALENDAR_DATA_URL, RAW_DATA_URL)
    
    focus_date_val = (datetime.datetime.utcnow() + datetime.timedelta(hours=10)).date()
    focus_date_str = focus_date_val.strftime("%Y-%m-%d")
    sel_formatted = focus_date_val.strftime("%A, %B %d, %Y")

    st.markdown(f"<div class='section-header' style='margin-top:2px;'>🎯 Deep Dive: {sel_formatted}</div>", unsafe_allow_html=True)
    
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
                <div class="goal-card" style="border-left-color: #facc15;">
                    <div style="color:#fff; font-weight:600; font-size: 12px;">{b['title']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='cashflow-card' style='color:#64748b; font-size:12px;'>No bills due today.</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header' style='margin-top:20px;'>Upcoming Week</div>", unsafe_allow_html=True)
    
    week_cols = st.columns(7)
    for i in range(1, 8):
        future_dt = focus_date_val + datetime.timedelta(days=i)
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
            
            day_title = future_dt.strftime('%a, %b %d')
            with st.expander(f"View {day_title}"):
                if f_data["events"] or f_data["bills"]:
                    for ev in f_data["events"]:
                        time_suffix = f" (@ {ev['time']})" if ev["time"] else ""
                        st.markdown(f"<div style='color:#38bdf8; font-size:11px; margin-bottom:6px; line-height:1.3; word-break:break-word;'>• <b>Event:</b> {ev['title']}{time_suffix}</div>", unsafe_allow_html=True)
                    for b in f_data["bills"]:
                        st.markdown(f"<div style='color:#facc15; font-size:11px; margin-bottom:6px; line-height:1.3; word-break:break-word;'>• <b>Bill:</b> {b['title']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#64748b; font-size:11px; min-height: 25px;'>No events or bills.</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header' style='margin-top:28px;'>Next Month Overview</div>", unsafe_allow_html=True)
    
    month_events_list = []
    for i in range(8, 38):
        m_dt = focus_date_val + datetime.timedelta(days=i)
        m_key = m_dt.strftime("%Y-%m-%d")
        m_data = live_data.get(m_key, {"events": [], "bills": []})
        month_events_list.append({
            "date_str": m_dt.strftime("%b %d (%a)"),
            "events": [e['title'] for e in m_data["events"]],
            "bills": [b['title'] for b in m_data["bills"]]
        })

    full_weeks = [month_events_list[idx:idx + 7] for idx in range(0, 28, 7)]
    remaining_days = month_events_list[28:]

    for row in full_weeks:
        cols = st.columns(7)
        for idx, item in enumerate(row):
            with cols[idx]:
                content_inner = f"<div style='font-weight:700; color:#e2e8f0; font-size:11px; border-bottom:1px solid #222734; padding-bottom:2px; margin-bottom:3px;'>{item['date_str']}</div>"
                for ev in item["events"]:
                    content_inner += f"<div style='color:#38bdf8; font-size:10px; margin-top:2px; line-height:1.2;'>📅 {ev}</div>"
                for bi in item["bills"]:
                    content_inner += f"<div style='color:#facc15; font-size:10px; margin-top:2px; line-height:1.2;'>💸 {bi}</div>"
                
                st.markdown(f"""
                <div style="background:#161a22; border:1px solid #222734; border-radius:8px; padding:8px; height:105px; overflow-y:auto; margin-bottom:6px;">
                    {content_inner}
                </div>
                """, unsafe_allow_html=True)

    if remaining_days:
        rem_cols = st.columns(7)
        target_indices = [2, 3]
        for i, item in enumerate(remaining_days):
            col_idx = target_indices[i]
            with rem_cols[col_idx]:
                content_inner = f"<div style='font-weight:700; color:#e2e8f0; font-size:11px; border-bottom:1px solid #222734; padding-bottom:2px; margin-bottom:3px;'>{item['date_str']}</div>"
                for ev in item["events"]:
                    content_inner += f"<div style='color:#38bdf8; font-size:10px; margin-top:2px; line-height:1.2;'>📅 {ev}</div>"
                for bi in item["bills"]:
                    content_inner += f"<div style='color:#facc15; font-size:10px; margin-top:2px; line-height:1.2;'>💸 {bi}</div>"
                
                st.markdown(f"""
                <div style="background:#161a22; border:1px solid #222734; border-radius:8px; padding:8px; height:105px; overflow-y:auto; margin-bottom:6px;">
                    {content_inner}
                </div>
                """, unsafe_allow_html=True)


# =============================================================================
# TAB 3: FINANCIAL DASHBOARD
# =============================================================================
elif current_tab == "Finances":
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

        st.markdown("<br>", unsafe_allow_html=True)
        
        # -------------------------------------------------------------------------
        # REVIEW & UPDATE GOALS SECTION
        # -------------------------------------------------------------------------
        with st.expander("📝 Review & Update Goals"):
            st.markdown("<div style='color: #cbd5e1; font-size: 13px; margin-bottom: 12px;'>Edit your savings goals below. The projected weekly cashflow will update automatically. Click Save to push changes to your Google Sheet.</div>", unsafe_allow_html=True)
            
            if "edit_goals" not in st.session_state:
                st.session_state.edit_goals = fin["goals"]
            
            def calculate_live_cashflow(target, current, start_str, end_str):
                try:
                    start_dt = datetime.datetime.strptime(start_str.strip(), "%d-%b-%Y") if start_str.strip() else datetime.datetime.now()
                    end_dt = datetime.datetime.strptime(end_str.strip(), "%d-%b-%Y")
                    weeks = (end_dt - start_dt).days / 7.0
                    if weeks > 0 and target > current:
                        return (target - current) / weeks
                    return 0.0
                except:
                    return 0.0

            updated_goals = []
            total_live_cashflow = 0.0

            for i, goal in enumerate(st.session_state.edit_goals):
                st.markdown(f"<strong style='color:#38bdf8;'>Goal: {goal['name']}</strong>", unsafe_allow_html=True)
                col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1])
                
                with col1:
                    new_name = st.text_input("Name", value=goal["name"], key=f"name_{i}")
                with col2:
                    new_bal = st.number_input("Current Balance", value=float(goal["current"]), key=f"bal_{i}")
                with col3:
                    new_target = st.number_input("Target ($)", value=float(goal["target"]), key=f"target_{i}")
                with col4:
                    new_start = st.text_input("Start Date (DD-Mon-YYYY)", value=goal["start_date"], key=f"start_{i}")
                with col5:
                    new_end = st.text_input("End Date (DD-Mon-YYYY)", value=goal["end_date"], key=f"end_{i}")

                live_rate = calculate_live_cashflow(new_target, new_bal, new_start, new_end)
                total_live_cashflow += live_rate

                st.markdown(f"<div style='text-align: right; font-size: 12px; color: #4ade80;'>Live Projected Contrib: <b>${live_rate:,.2f} / wk</b></div>", unsafe_allow_html=True)
                st.markdown("<hr style='border-color: #222734; margin: 8px 0;'>", unsafe_allow_html=True)
                
                updated_goals.append({
                    "index": goal.get("index", 15 + i),
                    "name": new_name, "current": new_bal, "target": new_target,
                    "start_date": new_start, "end_date": new_end, "rate": live_rate,
                    "is_new": goal.get("is_new", False)
                })
            
            st.markdown(f"""
            <div style='background: #1c212c; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;'>
                <span style='color: #94a3b8; font-size: 12px;'>Total Projected Weekly Goal Contributions:</span><br>
                <span style='color: #facc15; font-size: 18px; font-weight: 700;'>${total_live_cashflow:,.2f} / wk</span>
            </div>
            """, unsafe_allow_html=True)

            col_add, col_save = st.columns([1, 1])
            with col_add:
                if st.button("➕ Add New Goal", use_container_width=True):
                    st.session_state.edit_goals.append({
                        "name": "New Goal", "current": 0.0, "target": 1000.0, 
                        "start_date": datetime.datetime.now().strftime("%d-%b-%Y"), 
                        "end_date": (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%d-%b-%Y"), 
                        "rate": 0.0,
                        "is_new": True
                    })
                    st.rerun()

            with col_save:
                if st.button("💾 Save Changes to Google Sheets", type="primary", use_container_width=True):
                    with st.spinner("Writing to Google Sheets..."):
                        try:
                            client = authenticate_gspread()
                            sheet = client.open_by_key(SHEET_ID).worksheet("Finances")
                            
                            # Determine the row index of the last existing goal dynamically
                            existing_indices = [g["index"] for g in fin["goals"] if not g.get("is_new", False)]
                            last_rate_row = max(existing_indices) if existing_indices else 19
                            last_transfer_row = 31 # Account Transfers last row in current setup

                            new_offset_rate = 0
                            new_offset_transfer = 0

                            for idx, ug in enumerate(updated_goals):
                                if ug.get("is_new", False):
                                    # Dynamically insert right after the last goal row (Row 20 for first new goal)
                                    target_rate_row = last_rate_row + 1 + new_offset_rate
                                    sheet.insert_row(["", ug["name"], "", ug["target"], "", ug["end_date"], ug["start_date"], "", ""], index=target_rate_row)
                                    new_offset_rate += 1

                                    # Insert into Account Transfers table right below last transfer row (Row 32 for first new goal)
                                    target_transfer_row = last_transfer_row + 1 + new_offset_transfer
                                    sheet.insert_row([ug["current"], ug["name"], "", "Balance after", 0, "weeks", ""], index=target_transfer_row)
                                    new_offset_transfer += 1
                                else:
                                    row_idx = ug["index"] + 1
                                    sheet.update(f'K{row_idx}:L{row_idx}', [[ug["name"], ug["target"]]], value_input_option='USER_ENTERED')
                                    sheet.update(f'N{row_idx}:O{row_idx}', [[ug["end_date"], ug["start_date"]]], value_input_option='USER_ENTERED')
                                    
                                    transfer_row = 28 + idx 
                                    sheet.update(f'B{transfer_row}:C{transfer_row}', [[ug["current"], ug["name"]]], value_input_option='USER_ENTERED')
                            
                            st.success("Successfully updated Google Sheets!")
                            st.cache_data.clear() 
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Failed to update sheet. Error: {e}")
    else:
        st.warning("Unable to fetch financial data from Google Sheets.")
