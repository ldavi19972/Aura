import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import datetime

# -----------------------------------------------------------------------------
# 1. Hardcoded Google Sheet Configuration (CalendarData Tab: gid=1456635855)
# -----------------------------------------------------------------------------
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=1456635855"

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
# 3. Google Sheets Data Fetching (CalendarData Tab)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=30)
def load_calendar_data_sheet(csv_url):
    data_map = {}

    category_priority = {
        "Public Holiday": 5,
        "Holiday": 4,
        "Work Trip": 3,
        "Get-away": 2,
        "Working": 1
    }

    try:
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()

        for _, row in df.iterrows():
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
                data_map[date_key] = {
                    "status": category_val,
                    "events": []
                }
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
        st.error(f"Error fetching data from Google Sheets: {e}")

    return data_map

live_data = load_calendar_data_sheet(DEFAULT_SHEET_URL)
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
        padding: 8px 0;
    }}

    .top-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 12px;
    }}

    .today-badge {{
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
    }}

    .today-date-text {{
        font-size: 16px;
        font-weight: 700;
        color: #f8fafc;
        margin-left: 8px;
    }}

    .calendar-container {{
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 12px;
        width: 100%;
        margin: 0 auto;
    }}

    table.cal-grid {{
        width: 100%;
        table-layout: fixed;
        border-collapse: separate;
        border-spacing: 2px;
    }}

    th.col-header {{
        color: #94a3b8;
        font-size: 10px;
        font-weight: 700;
        text-align: center;
        padding: 4px 0;
        width: 2.4%;
    }}

    th.col-header-first {{
        width: 8%;
        text-align: left;
        padding-left: 6px;
        color: #cbd5e1;
        font-size: 12px;
    }}

    td.month-label {{
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 6px;
        white-space: nowrap;
        text-align: left;
        width: 8%;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .day-cell {{
        height: 26px;
        width: 2.4%;
        border-radius: 4px;
        text-align: center;
        font-size: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.1s ease;
        user-select: none;
        vertical-align: middle;
        border: 1px solid transparent;
        position: relative;
    }}

    .day-cell:hover {{
        transform: scale(1.12);
        border-color: #ffffff99 !important;
        z-index: 10;
    }}

    .day-cell.is-today {{
        box-shadow: 0 0 0 2px #38bdf8, 0 0 8px rgba(56, 189, 248, 0.6) !important;
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
        gap: 10px;
        margin-top: 10px;
        flex-wrap: wrap;
    }}

    .legend-item {{
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 10px;
        color: #94a3b8;
        background: #1a1e27;
        padding: 3px 8px;
        border-radius: 4px;
        border: 1px solid #28303f;
    }}

    .legend-dot {{
        width: 7px;
        height: 7px;
        border-radius: 2px;
    }}

    .detail-panel {{
        margin-top: 12px;
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 16px;
    }}

    .panel-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}

    .panel-title {{
        font-size: 15px;
        font-weight: 700;
        color: #f8fafc;
    }}

    .status-badge {{
        font-size: 10px;
        padding: 3px 8px;
        border-radius: 10px;
        font-weight: 600;
    }}

    .tab-bar {{
        display: flex;
        gap: 4px;
        border-bottom: 1px solid #222734;
        margin-bottom: 12px;
    }}

    .tab-btn {{
        background: none;
        border: none;
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 12px;
        cursor: pointer;
        border-bottom: 2px solid transparent;
    }}

    .tab-btn.active {{
        color: #38bdf8;
        border-bottom-color: #38bdf8;
    }}

    .tab-content {{
        display: none;
        color: #94a3b8;
        font-size: 12px;
    }}

    .tab-content.active {{
        display: block;
    }}

    .data-card {{
        background: #1c212c;
        border-left: 3px solid #38bdf8;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }}

    .card-meta {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-top: 6px;
        font-size: 11px;
    }}

    .meta-item {{
        display: flex;
        align-items: center;
        gap: 4px;
    }}
</style>
</head>
<body>

<div class="top-bar">
    <div>
        <span class="today-badge">Today</span>
        <span class="today-date-text">{today_formatted}</span>
    </div>
    <div style="font-size: 12px; color: #64748b;">CalendarData Sync • 2026</div>
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
    </div>

    <div id="eventsTab" class="tab-content active"></div>
</div>

<script>
    const YEAR = 2026;
    const TODAY = {{ month: {today_m_idx}, day: {today_d_num} }};
    const sheetData = {json_data};

    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    
    // Day letter map starting on Jan 1, 2026 (Thursday)
    const dayLetters = ["T", "F", "S", "S", "M", "T", "W"]; 
    const TOTAL_GRID_COLS = 37; // Max columns needed across all months

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
        
        // Render 37 column headers with repeating Day Letters (T, F, S, S, M, T, W...)
        for (let col = 0; col < TOTAL_GRID_COLS; col++) {{
            const letter = dayLetters[col % 7];
            html += `<th class="col-header">${{letter}}</th>`;
        }}
        html += '</tr></thead><tbody>';

        months.forEach((mName, mIdx) => {{
            html += `<tr><td class="month-label">${{mName}}</td>`;
            const totalDays = daysInMonths[mIdx];
            
            // Calculate weekday offset for the 1st of each month relative to Jan 1 (Thursday)
            const firstOfMonthDate = new Date(YEAR, mIdx, 1);
            // JavaScript getDay(): 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
            // Jan 1, 2026 is Thursday (4). Calculate column offset relative to Thursday:
            const jsDay = firstOfMonthDate.getDay(); 
            const offset = (jsDay - 4 + 7) % 7; 

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

        const dayData = sheetData[dateKey] || {{ events: [] }};
        
        const eventsTab = document.getElementById('eventsTab');
        eventsTab.innerHTML = dayData.events.length > 0 
            ? dayData.events.map(e => {{
                let metaHtml = '';
                if (e.time) {{
                    metaHtml += `<span class="meta-item" style="color:#38bdf8;">⏰ ${{e.time}}</span>`;
                }}
                if (e.location) {{
                    metaHtml += `<span class="meta-item" style="color:#94a3b8;">📍 ${{e.location}}</span>`;
                }}
                
                return `
                    <div class="data-card">
                        <div style="color:#fff; font-weight:600;">${{e.title}}</div>
                        ${{metaHtml ? `<div class="card-meta">${{metaHtml}}</div>` : ''}}
                    </div>
                `;
            }}).join('')
            : `<p style="color:#64748b;">No events recorded for this date.</p>`;
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

components.html(calendar_html, height=680, scrolling=False)
