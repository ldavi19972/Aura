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

# -----------------------------------------------------------------------------
# 2. Page Configuration & Layout
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Aura Calendar 2026",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Force full width and disable horizontal page scrolling */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0e1117 !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
        overflow-x: hidden !important;
    }

    .main .block-container {
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }

    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    iframe {
        border: none !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Fetch & Merge Data from Both Tabs
# -----------------------------------------------------------------------------
@st.cache_data(ttl=30)
def fetch_combined_data(calendar_url, raw_url):
    data_map = {}

    category_priority = {
        "Public Holiday": 5,
        "Holiday": 4,
        "Work Trip": 3,
        "Get-away": 2,
        "Working": 1
    }

    # 1. Load Events from CalendarData tab
    try:
        df_cal = pd.read_csv(calendar_url)
        df_cal.columns = df_cal.columns.str.strip()

        for _, row in df_cal.iterrows():
            raw_date = str(row.get("Date", "")).strip()
            if not raw_date or raw_date.lower() == "nan":
                continue

            try:
                date_obj = pd.to_datetime(raw_date)
                date_key = date_obj.strftime("%Y-%m-%d")
            except Exception:
                continue

            title = str(row.get("Title", "")).replace("nan", "").strip()
            time_val = str(row.get("Time", "")).replace("nan", "").strip()
            location_val = str(row.get("Location", "")).replace("nan", "").strip()
            category_val = str(row.get("Category", "Working")).replace("nan", "").strip()

            if not category_val:
                category_val = "Working"

            if date_key not in data_map:
                data_map[date_key] = {"status": category_val, "events": [], "bills": []}
            else:
                current_prio = category_priority.get(data_map[date_key]["status"], 0)
                new_prio = category_priority.get(category_val, 0)
                if new_prio > current_prio:
                    data_map[date_key]["status"] = category_val

            if title:
                data_map[date_key]["events"].append({
                    "title": title,
                    "time": time_val,
                    "location": location_val,
                    "category": category_val
                })
    except Exception as e:
        st.error(f"Error fetching CalendarData tab: {e}")

    # 2. Load Bills from Raw Data tab
    try:
        df_raw = pd.read_csv(raw_url)
        df_raw.columns = df_raw.columns.str.strip()

        for _, row in df_raw.iterrows():
            raw_date = str(row.get("Date", "")).strip()
            if not raw_date or raw_date.lower() == "nan":
                continue

            try:
                date_obj = pd.to_datetime(raw_date, dayfirst=True)
                date_key = date_obj.strftime("%Y-%m-%d")
            except Exception:
                continue

            if date_key not in data_map:
                data_map[date_key] = {"status": "Working", "events": [], "bills": []}

            # Check Bill 1 through Bill 5 columns
            for col in df_raw.columns:
                if col.lower().startswith("bill"):
                    val = str(row.get(col, "")).replace("nan", "").strip()
                    if val:
                        data_map[date_key]["bills"].append({"title": val})

    except Exception as e:
        st.error(f"Error fetching Raw Data tab: {e}")

    return data_map

live_data = fetch_combined_data(CALENDAR_DATA_URL, RAW_DATA_URL)
json_data = json.dumps(live_data)

# Current Date Setup
today_date = datetime.date.today()
today_formatted = today_date.strftime("%A, %B %d, %Y")
today_m_idx = today_date.month - 1
today_d_num = today_date.day

# -----------------------------------------------------------------------------
# 4. HTML / JS Calendar Interface
# -----------------------------------------------------------------------------
calendar_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    body {{
        background-color: #0e1117;
        color: #f1f5f9;
        width: 100%;
        overflow-x: hidden;
        padding: 10px 0;
    }}

    /* Compact header bar ending right after the date */
    .top-bar {{
        display: inline-flex;
        align-items: center;
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 10px 18px;
        margin-bottom: 14px;
    }}

    .today-badge {{
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }}

    .today-date-text {{
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc;
        margin-left: 10px;
    }}

    .calendar-container {{
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 16px;
        width: 100%;
        margin: 0 auto;
    }}

    table.cal-grid {{
        width: 100%;
        table-layout: fixed;
        border-collapse: separate;
        border-spacing: 3px;
    }}

    th.col-header {{
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
        text-align: center;
        padding: 6px 0;
        width: 2.4%;
    }}

    th.col-header-first {{
        width: 8%;
        text-align: left;
        padding-left: 6px;
        color: #cbd5e1;
        font-size: 14px;
    }}

    td.month-label {{
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        padding: 4px 6px;
        white-space: nowrap;
        text-align: left;
        width: 8%;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* Scaled up grid cells for larger presentation */
    .day-cell {{
        height: 34px;
        width: 2.4%;
        border-radius: 5px;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.1s ease;
        user-select: none;
        vertical-align: middle;
        border: 1px solid transparent;
        position: relative;
    }}

    .day-cell:hover {{
        transform: scale(1.15);
        border-color: #ffffff99 !important;
        z-index: 10;
    }}

    .day-cell.is-today {{
        box-shadow: 0 0 0 2px #38bdf8, 0 0 10px rgba(56, 189, 248, 0.6) !important;
        border-color: #38bdf8 !important;
    }}

    .day-cell.selected {{
        outline: 2px solid #ffffff;
        outline-offset: 1px;
    }}

    /* Color Themes matched to Category */
    .status-empty {{ background-color: transparent; border: none; cursor: default; }}
    .status-working {{ background-color: #133a20; color: #4ade80; border-color: #16522c; }}
    .status-public-holiday {{ background-color: #1e3a8a; color: #60a5fa; border-color: #1d4ed8; }}
    .status-holiday {{ background-color: #4c0519; color: #fb7185; border-color: #9f1239; }}
    .status-get-away {{ background-color: #422006; color: #facc15; border-color: #713f12; }}
    .status-work-trip {{ background-color: #3b0764; color: #c084fc; border-color: #6b21a8; }}

    .legend-bar {{
        display: flex;
        gap: 12px;
        margin-top: 14px;
        flex-wrap: wrap;
    }}

    .legend-item {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        color: #94a3b8;
        background: #1a1e27;
        padding: 5px 10px;
        border-radius: 5px;
        border: 1px solid #28303f;
    }}

    .legend-dot {{
        width: 8px;
        height: 8px;
        border-radius: 2px;
    }}

    .detail-panel {{
        margin-top: 16px;
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 20px;
    }}

    .panel-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
    }}

    .panel-title {{
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc;
    }}

    .status-badge {{
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
    }}

    .tab-bar {{
        display: flex;
        gap: 12px;
        border-bottom: 1px solid #222734;
        margin-bottom: 14px;
    }}

    .tab-btn {{
        background: none;
        border: none;
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        padding: 8px 14px;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        transition: color 0.15s ease;
    }}

    .tab-btn.active {{
        color: #38bdf8;
        border-bottom-color: #38bdf8;
    }}

    .tab-content {{
        display: none;
        color: #94a3b8;
        font-size: 13px;
    }}

    .tab-content.active {{
        display: block;
    }}

    .data-card {{
        background: #1c212c;
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}

    .bill-card {{
        border-left-color: #facc15;
    }}

    .card-meta {{
        display: flex;
        align-items: center;
        gap: 16px;
        margin-top: 8px;
        font-size: 12px;
    }}

    .meta-item {{
        display: flex;
        align-items: center;
        gap: 5px;
    }}
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
    
    // Day letter sequence starting on Tuesday
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
            const letter = dayLetters[col % 7];
            html += `<th class="col-header">${{letter}}</th>`;
        }}
        html += '</tr></thead><tbody>';

        months.forEach((mName, mIdx) => {{
            html += `<tr><td class="month-label">${{mName}}</td>`;
            const totalDays = daysInMonths[mIdx];
            
            const firstOfMonthDate = new Date(YEAR, mIdx, 1);
            const jsDay = firstOfMonthDate.getDay(); 
            const offset = (jsDay - 2 + 7) % 7; 

            let currentDay = 1;

            for (let col = 0; col < TOTAL_GRID_COLS; col++) {{
                if (col >= offset && currentDay <= totalDays) {{
                    const d = currentDay;
                    const mStr = String(mIdx + 1).padStart(2, '0');
                    const dStr = String(d).padStart(2, '0');
                    const dateKey = `${{YEAR}}-${{mStr}}-${{dStr}}`;
                    
                    const entry = sheetData[dateKey];
                    const categoryName = entry ? entry.status : 'Working';
                    const statusClass = getCssClassForCategory(categoryName);
                    
                    const isToday = (mIdx === TODAY.month && d === TODAY.day);
                    const todayClass = isToday ? 'is-today' : '';
                    
                    html += `<td class="day-cell ${{statusClass}} ${{todayClass}}" 
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

        const mStr = String(mIdx + 1).padStart(2, '0');
        const dStr = String(day).padStart(2, '0');
        const dateKey = `${{YEAR}}-${{mStr}}-${{dStr}}`;

        const dayData = sheetData[dateKey] || {{ events: [], bills: [] }};
        
        // Render Events
        const eventsTab = document.getElementById('eventsTab');
        const eventsList = dayData.events || [];
        eventsTab.innerHTML = eventsList.length > 0 
            ? eventsList.map(e => {{
                let metaHtml = '';
                if (e.time) metaHtml += `<span class="meta-item" style="color:#38bdf8;">⏰ ${{e.time}}</span>`;
                if (e.location) metaHtml += `<span class="meta-item" style="color:#94a3b8;">📍 ${{e.location}}</span>`;
                
                return `
                    <div class="data-card">
                        <div style="color:#fff; font-weight:600; font-size: 15px;">${{e.title}}</div>
                        ${{metaHtml ? `<div class="card-meta">${{metaHtml}}</div>` : ''}}
                    </div>
                `;
            }}).join('')
            : `<p style="color:#64748b;">No events recorded for this date.</p>`;

        // Render Bills
        const billsTab = document.getElementById('billsTab');
        const billsList = dayData.bills || [];
        billsTab.innerHTML = billsList.length > 0 
            ? billsList.map(b => `
                <div class="data-card bill-card">
                    <div style="color:#fff; font-weight:600; font-size: 15px;">💸 ${{b.title}}</div>
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
        if (todayCell) {{
            selectDate(TODAY.month, TODAY.day, months[TODAY.month], 'Working', 'status-working', todayCell);
        }}
    }}, 50);
</script>

</body>
</html>
"""

components.html(calendar_html, height=800, scrolling=False)
