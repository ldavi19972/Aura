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
    /* Base theme override */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0e1117 !important;
        color: #f1f5f9 !important;
    }

    .main .block-container {
        padding: 0.5rem 1.5rem !important;
        max-width: 100% !important;
    }

    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Streamlit Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #161a22;
        padding: 6px;
        border-radius: 8px;
        border: 1px solid #222734;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 14px;
        border: none;
        padding: 0 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }

    /* Financial Dashboard Metrics & Cards */
    .metric-card {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    
    .metric-title {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .metric-value {
        font-size: 20px;
        font-weight: 700;
    }

    .metric-positive { color: #4ade80; }
    .metric-negative { color: #fb7185; }
    .metric-neutral  { color: #38bdf8; }
    .metric-warning  { color: #facc15; }

    /* Custom Goal Progress Cards */
    .goal-card {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .goal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }

    .goal-title {
        font-size: 15px;
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
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 8px 0;
    }

    .progress-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }

    .goal-footer {
        display: flex;
        justify-content: space-between;
        font-size: 11px;
        color: #94a3b8;
    }

    /* Cashflow Custom Display */
    .cashflow-card {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }

    .cf-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #1c212c;
        font-size: 13px;
    }

    .cf-row:last-child {
        border-bottom: none;
    }

    .cf-sub {
        color: #94a3b8;
        padding-left: 12px;
        font-size: 12px;
    }

    iframe {
        border: none !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Data Loaders
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 4. Streamlit Main Tabs Layout
# -----------------------------------------------------------------------------
tab_cal, tab_fin = st.tabs(["📅 Calendar & Schedule", "💰 Finances & Net Worth"])

# =============================================================================
# TAB 1: CALENDAR INTERFACE
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
        body {{ background-color: #0e1117; color: #f1f5f9; width: 100%; height: 100vh; overflow: hidden; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 0 10px; }}
        .top-bar {{ display: inline-flex; align-items: center; align-self: flex-start; background: #161a22; border: 1px solid #222734; border-radius: 8px; padding: 8px 14px; margin-bottom: 8px; }}
        .today-badge {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 3px 8px; border-radius: 16px; font-size: 10px; font-weight: 700; text-transform: uppercase; }}
        .today-date-text {{ font-size: 15px; font-weight: 700; color: #f8fafc; margin-left: 8px; }}
        .calendar-container {{ background: #161a22; border: 1px solid #222734; border-radius: 10px; padding: 10px 14px; width: 100%; margin: 0 auto; }}
        table.cal-grid {{ width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: 2px; }}
        th.col-header {{ color: #94a3b8; font-size: 10px; font-weight: 700; text-align: center; padding: 2px 0; width: 2.4%; }}
        th.col-header-first {{ width: 8%; text-align: left; padding-left: 4px; color: #cbd5e1; font-size: 12px; }}
        td.month-label {{ color: #94a3b8; font-size: 11px; font-weight: 600; padding: 2px 4px; white-space: nowrap; text-align: left; width: 8%; overflow: hidden; text-overflow: ellipsis; }}
        .day-cell {{ height: 28px; width: 2.4%; border-radius: 4px; text-align: center; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.1s ease; user-select: none; vertical-align: middle; border: 1px solid transparent; position: relative; }}
        .day-cell:hover {{ transform: scale(1.12); border-color: #ffffff99 !important; z-index: 10; }}
        .day-cell.is-today {{ box-shadow: 0 0 0 2px #38bdf8, 0 0 8px rgba(56, 189, 248, 0.6) !important; border-color: #38bdf8 !important; }}
        .day-cell.selected {{ outline: 2px solid #ffffff; outline-offset: 1px; }}
        .status-empty {{ background-color: transparent; border: none; cursor: default; }}
        .status-working {{ background-color: #133a20; color: #4ade80; border-color: #16522c; }}
        .status-public-holiday {{ background-color: #1e3a8a; color: #60a5fa; border-color: #1d4ed8; }}
        .status-holiday {{ background-color: #4c0519; color: #fb7185; border-color: #9f1239; }}
        .status-get-away {{ background-color: #422006; color: #facc15; border-color: #713f12; }}
        .status-work-trip {{ background-color: #3b0764; color: #c084fc; border-color: #6b21a8; }}
        .legend-bar {{ display: flex; gap: 10px; margin-top: 8px; flex-wrap: wrap; }}
        .legend-item {{ display: flex; align-items: center; gap: 5px; font-size: 10px; color: #94a3b8; background: #1a1e27; padding: 3px 8px; border-radius: 4px; border: 1px solid #28303f; }}
        .legend-dot {{ width: 7px; height: 7px; border-radius: 2px; }}
        .detail-panel {{ margin-top: 10px; background: #161a22; border: 1px solid #222734; border-radius: 10px; padding: 12px 16px; width: 100%; }}
        .panel-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
        .panel-title {{ font-size: 15px; font-weight: 700; color: #f8fafc; }}
        .status-badge {{ font-size: 10px; padding: 3px 8px; border-radius: 10px; font-weight: 600; }}
        .tab-bar {{ display: flex; gap: 8px; border-bottom: 1px solid #222734; margin-bottom: 10px; }}
        .tab-btn {{ background: none; border: none; color: #64748b; font-size: 12px; font-weight: 600; padding: 4px 10px; cursor: pointer; border-bottom: 2px solid transparent; transition: color 0.15s ease; }}
        .tab-btn.active {{ color: #38bdf8; border-bottom-color: #38bdf8; }}
        .tab-content {{ display: none; color: #94a3b8; font-size: 12px; }}
        .tab-content.active {{ display: block; }}
        .data-card {{ background: #1c212c; border-left: 3px solid #38bdf8; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; }}
        .bill-card {{ border-left-color: #facc15; }}
        .card-meta {{ display: flex; align-items: center; gap: 12px; margin-top: 4px; font-size: 11px; }}
        .meta-item {{ display: flex; align-items: center; gap: 4px; }}
    </style>
    </head>
    <body>

    <div class="top-bar">
        <span class="today-badge">Today</span>
        <span class="today-date-text">{today_formatted}</span>
    </div>

    <div class="calendar-container">
        <table class="cal-grid" id="calendarGrid"></table>
        <div class="legend-bar">
            <div class="legend-item"><div class="legend-dot" style="background:#4ade80"></div>Working</div>
            <div class="legend-item"><div class="legend-dot" style="background:#60a5fa"></div>Public Holiday</div>
            <div class="legend-item"><div class="legend-dot" style="background:#fb7185"></div>Holiday</div>
            <div class="legend-item"><div class="legend-dot" style="background:#facc15"></div>Get-away</div>
            <div class="legend-item"><div class="legend-dot" style="background:#c084fc"></div>Work Trip</div>
            <div class="legend-item"><div class="legend-dot" style="background:#38bdf8"></div>Today</div>
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
                        
                        html += `<td class="day-cell ${{statusClass}} ${{isToday ? 'is-today' : ''}}" 
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
                        <div style="color:#fff; font-weight:600; font-size: 14px;">${{e.title}}</div>
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
                        <div style="color:#fff; font-weight:600; font-size: 14px;">💸 ${{b.title}}</div>
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
            const todayCell = document.getElementById(`cell-${{TODAY.month}}-${{TODAY.day}}`);
            if (todayCell) selectDate(TODAY.month, TODAY.day, months[TODAY.month], 'Working', 'status-working', todayCell);
        }}, 50);
    </script>

    </body>
    </html>
    """
    components.html(calendar_html, height=720, scrolling=False)


# =============================================================================
# TAB 2: FINANCIAL DASHBOARD (REDESIGNED VISUAL UI)
# =============================================================================
with tab_fin:
    st.markdown("<h2 style='margin-bottom: 16px; font-weight:700;'>💰 Financial Dashboard</h2>", unsafe_allow_html=True)
    
    # 1. Executive Metric Header
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Savings Balance</div>
            <div class="metric-value metric-positive">$4,937.98</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Credit / Debt</div>
            <div class="metric-value metric-negative">-$26,117.95</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Asset Value</div>
            <div class="metric-value metric-neutral">$3,129.96</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Net Financial Position</div>
            <div class="metric-value metric-negative">-$18,050.01</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Main Visual Area: Priorities First (Goals [55%] + Cash Flow [45%])
    col_goals, col_cash = st.columns([1.2, 1])

    # --- GOALS visual cards with progress bars ---
    with col_goals:
        st.markdown("<h4 style='font-size:16px; color:#cbd5e1; font-weight:700; margin-bottom:12px;'>🎯 Savings & Goal Tracker</h4>", unsafe_allow_html=True)

        goals_list = [
            {
                "name": "New Zealand Trip",
                "current": 2087.98,
                "target": 2087.98,
                "pct": 100,
                "badge": "SAVED",
                "badge_class": "badge-saved",
                "color": "#4ade80",
                "details": "Target Achieved • $0/wk needed"
            },
            {
                "name": "Italy Trip",
                "current": 1037.50,
                "target": 7000.00,
                "pct": 15,
                "badge": "IN PROGRESS",
                "badge_class": "badge-progress",
                "color": "#38bdf8",
                "details": "Target: 9-Sep-2026 • Contrib: $1,037.50/wk"
            },
            {
                "name": "Emergency Fund",
                "current": 0.00,
                "target": 9000.00,
                "pct": 0,
                "badge": "WAITING",
                "badge_class": "badge-waiting",
                "color": "#facc15",
                "details": "Starts 7-Oct-2026 • Target: $692.31/wk"
            },
            {
                "name": "Adelaide Trip",
                "current": 0.00,
                "target": 2600.00,
                "pct": 0,
                "badge": "WAITING",
                "badge_class": "badge-waiting",
                "color": "#facc15",
                "details": "Starts 2-Sep-2026 • Target: $650.00/wk"
            }
        ]

        for g in goals_list:
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

    # --- CASH FLOW visual breakdown ---
    with col_cash:
        st.markdown("<h4 style='font-size:16px; color:#cbd5e1; font-weight:700; margin-bottom:12px;'>📊 Cash Flow Summary</h4>", unsafe_allow_html=True)

        st.markdown("""
        <div class="cashflow-card">
            <div class="cf-row" style="font-weight:700; color:#4ade80;">
                <span>Total Weekly Income</span>
                <span>+$1,814.00 / wk</span>
            </div>
            <div class="cf-row cf-sub">
                <span>↳ Salary</span>
                <span>$1,424.00 / wk</span>
            </div>
            <div class="cf-row cf-sub">
                <span>↳ Transfers</span>
                <span>$390.00 / wk</span>
            </div>
        </div>

        <div class="cashflow-card">
            <div class="cf-row" style="font-weight:700; color:#fb7185;">
                <span>Total Weekly Expenses</span>
                <span>-$1,096.72 / wk</span>
            </div>
            <div class="cf-row cf-sub">
                <span>↳ Fixed Bills (Rent, Gym, Card, etc.)</span>
                <span>$846.72 / wk</span>
            </div>
            <div class="cf-row cf-sub">
                <span>↳ Variable Budgets (Groceries, Fun, etc.)</span>
                <span>$250.00 / wk</span>
            </div>
            <div class="cf-row cf-sub">
                <span>↳ Holiday Allocation</span>
                <span>$254.62 / wk</span>
            </div>
        </div>

        <div class="cashflow-card" style="border-left: 4px solid #38bdf8;">
            <div class="cf-row" style="font-weight:700; color:#38bdf8; font-size:14px;">
                <span>Net Savings Flow</span>
                <span>+$717.28 / wk</span>
            </div>
            <div style="font-size:11px; color:#94a3b8; margin-top:4px;">
                Equates to <b>+$3,108.23 / mo</b> and <b>+$37,298.80 / yr</b> net retention.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:none; border-top:1px solid #222734; margin: 16px 0;'>", unsafe_allow_html=True)

    # 3. Bottom Layer: Liabilities & Physical Assets Expander
    b_col1, b_col2 = st.columns([1, 1])

    with b_col1:
        st.markdown("<h4 style='font-size:15px; color:#cbd5e1; font-weight:700;'>💳 Credit & Loan Repayments</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div class="cashflow-card">
            <div class="cf-row">
                <div>
                    <span style="font-weight:600; color:#fff;">Student Loan</span><br>
                    <span style="font-size:10px; color:#94a3b8;">Payoff target: 19-Sep-2028</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:#fb7185; font-weight:700;">$21,117.95</span><br>
                    <span style="font-size:11px; color:#94a3b8;">$192.00 / wk</span>
                </div>
            </div>
            <div class="cf-row">
                <div>
                    <span style="font-weight:600; color:#fff;">Credit Card</span><br>
                    <span style="font-size:10px; color:#94a3b8;">Payoff target: 10-Jun-2122</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:#fb7185; font-weight:700;">$5,000.00</span><br>
                    <span style="font-size:11px; color:#94a3b8;">$1.00 / wk</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with b_col2:
        st.markdown("<h4 style='font-size:15px; color:#cbd5e1; font-weight:700;'>🛋️ Physical Assets Valuation</h4>", unsafe_allow_html=True)
        with st.expander("View Asset Valuation Details ($3,129.96 total)", expanded=False):
            asset_items = [
                {"item": "Couch", "price": "$1,453.64", "val": "$946.23"},
                {"item": "Fridge", "price": "$687.00", "val": "$606.65"},
                {"item": "PS5", "price": "$749.00", "val": "$533.73"},
                {"item": "Washing Machine", "price": "$500.00", "val": "$434.38"},
                {"item": "Watch", "price": "$423.76", "val": "$257.44"},
                {"item": "Dining Set", "price": "$268.95", "val": "$237.50"},
                {"item": "Kindle", "price": "$269.00", "val": "$114.03"}
            ]
            
            for a in asset_items:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; font-size:12px; padding:4px 0; border-bottom:1px solid #1c212c;">
                    <span style="color:#fff;">{a['item']}</span>
                    <span style="color:#94a3b8;">Cost: {a['price']} &nbsp;|&nbsp; <b style="color:#38bdf8;">Value: {a['val']}</b></span>
                </div>
                """, unsafe_allow_html=True)
