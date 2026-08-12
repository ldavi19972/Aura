import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import datetime

# -----------------------------------------------------------------------------
# 1. Page Configuration & Layout
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
# 2. Google Sheets Data Fetching (Targeting 'Raw Data' Tab)
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Google Sheets Sync")
sheet_id = st.sidebar.text_input(
    "Google Sheet ID or Full CSV URL",
    placeholder="528057576#gid=528057576",
    help="Enter either your Google Sheet ID or full CSV URL for the 'Raw Data' tab."
)

@st.cache_data(ttl=30)
def load_raw_data_sheet(sheet_input):
    """
    Fetches and parses the 'Raw Data' tab from Google Sheets.
    Handles columns: Date, Bill 1..N, Event 1..N, Status
    """
    data_map = {}
    if not sheet_input:
        return data_map

    # Construct direct CSV export URL for 'Raw Data' tab
    if "docs.google.com" in sheet_input:
        if "export?format=csv" in sheet_input:
            csv_url = sheet_input
        else:
            # Extract Sheet ID from full URL
            parts = sheet_input.split('/d/')
            if len(parts) > 1:
                s_id = parts[1].split('/')[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{s_id}/gviz/tq?tqx=out:csv&sheet=Raw%20Data"
            else:
                csv_url = sheet_input
    else:
        # Standard Sheet ID input
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_input}/gviz/tq?tqx=out:csv&sheet=Raw%20Data"

    try:
        df = pd.read_csv(csv_url)
        
        # Strip whitespaces from column headers
        df.columns = df.columns.str.strip()

        for _, row in df.iterrows():
            raw_date = str(row.get("Date", "")).strip()
            if not raw_date or raw_date.lower() == "nan":
                continue

            # Parse Australian date format (DD/MM/YYYY) into YYYY-MM-DD
            try:
                date_obj = pd.to_datetime(raw_date, dayfirst=True)
                date_key = date_obj.strftime("%Y-%m-%d")
            except Exception:
                continue

            if date_key not in data_map:
                data_map[date_key] = {
                    "status": str(row.get("Status", "Working")).strip(),
                    "events": [],
                    "bills": [],
                    "notes": str(row.get("Notes", "")).replace("nan", "")
                }

            # Parse all Bill columns (Bill 1, Bill 2, Bill 3, etc.)
            bill_cols = [c for c in df.columns if c.startswith("Bill")]
            for col in bill_cols:
                val = str(row.get(col, "")).replace("nan", "").strip()
                if val:
                    data_map[date_key]["bills"].append({
                        "title": val,
                        "amount": "",
                        "due": "Due Today"
                    })

            # Parse all Event columns (Event 1, Event 2, Event 3, etc.)
            event_cols = [c for c in df.columns if c.startswith("Event")]
            for col in event_cols:
                val = str(row.get(col, "")).replace("nan", "").strip()
                if val:
                    data_map[date_key]["events"].append({
                        "title": val,
                        "time": "Scheduled"
                    })

    except Exception as e:
        st.sidebar.error(f"Error reading 'Raw Data' tab: {e}")

    return data_map

live_data = load_raw_data_sheet(sheet_id)
json_data = json.dumps(live_data)

# Current Date Setup
today_date = datetime.date.today()
today_formatted = today_date.strftime("%A, %B %d, %Y")
today_m_idx = today_date.month - 1
today_d_num = today_date.day

# -----------------------------------------------------------------------------
# 3. HTML / JS Calendar Interface
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
        color: #64748b;
        font-size: 10px;
        font-weight: 600;
        text-align: center;
        padding: 3px 0;
        width: 2.9%;
    }}

    th.col-header-first {{
        width: 9%;
        text-align: left;
        padding-left: 6px;
    }}

    td.month-label {{
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 6px;
        white-space: nowrap;
        text-align: left;
        width: 9%;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .day-cell {{
        height: 28px;
        width: 2.9%;
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
        transform: scale(1.1);
        border-color: #ffffff77 !important;
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

    /* Color Themes */
    .status-empty {{ background-color: #1a1e27; color: #475569; }}
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
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 6px;
    }}

    .data-card.bill {{
        border-left-color: #f59e0b;
    }}
</style>
</head>
<body>

<div class="top-bar">
    <div>
        <span class="today-badge">Today</span>
        <span class="today-date-text">{today_formatted}</span>
    </div>
    <div style="font-size: 12px; color: #64748b;">Raw Data Tab Sync • 2026</div>
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
        <button class="tab-btn" onclick="switchTab('billsTab', this)">Bills Due</button>
        <button class="tab-btn" onclick="switchTab('notesTab', this)">Day Notes</button>
    </div>

    <div id="eventsTab" class="tab-content active"></div>
    <div id="billsTab" class="tab-content"></div>
    <div id="notesTab" class="tab-content"></div>
</div>

<script>
    const YEAR = 2026;
    const TODAY = {{ month: {today_m_idx}, day: {today_d_num} }};
    const sheetData = {json_data};

    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    function getStaticStatus(monthIdx, day) {{
        if (monthIdx === 7 && day >= 23 && day <= 29) return {{ class: 'status-holiday', name: 'Holiday' }};
        if (monthIdx === 10 && day >= 16 && day <= 20) return {{ class: 'status-work-trip', name: 'Work Trip' }};
        if (monthIdx === 10 && (day === 1 || day === 30)) return {{ class: 'status-get-away', name: 'Get-away' }};
        if (monthIdx === 9 && (day === 30 || day === 31)) return {{ class: 'status-get-away', name: 'Get-away' }};
        if (monthIdx === 0 && day === 1) return {{ class: 'status-public-holiday', name: 'Public Holiday' }};
        
        const dateObj = new Date(YEAR, monthIdx, day);
        if (dateObj.getDay() === 0 || dateObj.getDay() === 6) return {{ class: 'status-empty', name: 'Weekend' }};
        
        return {{ class: 'status-working', name: 'Working' }};
    }}

    function renderGrid() {{
        const grid = document.getElementById('calendarGrid');
        let html = '<thead><tr><th class="col-header-first">2026</th>';
        
        for (let d = 1; d <= 31; d++) {{
            html += `<th class="col-header">${{d}}</th>`;
        }}
        html += '</tr></thead><tbody>';

        months.forEach((mName, mIdx) => {{
            html += `<tr><td class="month-label">${{mName}}</td>`;
            const totalDays = daysInMonths[mIdx];

            for (let d = 1; d <= 31; d++) {{
                if (d <= totalDays) {{
                    const dateObj = new Date(YEAR, mIdx, d);
                    const dayLetter = dateObj.toLocaleDateString('en-US', {{ weekday: 'narrow' }});
                    
                    const mStr = String(mIdx + 1).padStart(2, '0');
                    const dStr = String(d).padStart(2, '0');
                    const dateKey = `${{YEAR}}-${{mStr}}-${{dStr}}`;
                    
                    const entry = sheetData[dateKey];
                    const defaultStatus = getStaticStatus(mIdx, d);
                    const statusName = (entry && entry.status && entry.status !== 'Working') ? entry.status : defaultStatus.name;
                    const statusClass = defaultStatus.class;
                    
                    const isToday = (mIdx === TODAY.month && d === TODAY.day);
                    const todayClass = isToday ? 'is-today' : '';
                    
                    html += `<td class="day-cell ${{statusClass}} ${{todayClass}}" 
                                 id="cell-${{mIdx}}-${{d}}"
                                 onclick="selectDate(${{mIdx}}, ${{d}}, '${{mName}}', '${{statusName}}', '${{statusClass}}', this)">
                                 ${{dayLetter}}
                             </td>`;
                }} else {{
                    html += '<td style="background:transparent;"></td>';
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

        const dayData = sheetData[dateKey] || {{ events: [], bills: [], notes: '' }};
        
        const eventsTab = document.getElementById('eventsTab');
        eventsTab.innerHTML = dayData.events.length > 0 
            ? dayData.events.map(e => `<div class="data-card"><div style="color:#fff;font-weight:600;">${{e.title}}</div></div>`).join('')
            : `<p style="color:#64748b;">No events recorded in Raw Data tab for this date.</p>`;

        const billsTab = document.getElementById('billsTab');
        billsTab.innerHTML = dayData.bills.length > 0 
            ? dayData.bills.map(b => `<div class="data-card bill"><div style="color:#fff;font-weight:600;">${{b.title}}</div></div>`).join('')
            : `<p style="color:#64748b;">No bills recorded in Raw Data tab for this date.</p>`;

        const notesTab = document.getElementById('notesTab');
        notesTab.innerHTML = `<p style="color:#94a3b8;">${{dayData.notes || 'No notes found for this date.'}}</p>`;
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
