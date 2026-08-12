import streamlit as st
import streamlit.components.v1 as components

# Page configuration for full-width layout
st.set_page_config(
    page_title="Calendar 26' Interactive Dashboard",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to eliminate Streamlit's default margins/padding & double scrollbars
st.markdown("""
<style>
    /* Remove padding around main Streamlit block */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    /* Hide Streamlit header & footer elements for clean full-screen look */
    header, footer, #MainMenu {
        visibility: hidden;
        height: 0px;
    }
    iframe {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

calendar_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    body {
        background-color: #0e1117;
        color: #f1f5f9;
        padding: 12px;
        overflow-x: hidden;
    }

    /* Top Navigation / Today Bar */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 14px 20px;
        margin-bottom: 16px;
    }

    .today-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .today-badge {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .today-date-text {
        font-size: 18px;
        font-weight: 700;
        color: #f8fafc;
    }

    .year-title {
        font-size: 14px;
        color: #64748b;
        font-weight: 600;
    }

    /* Grid Layout Container */
    .calendar-container {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 16px;
        overflow-x: auto;
    }

    table.cal-grid {
        width: 100%;
        border-collapse: separate;
        border-spacing: 2px;
    }

    th.col-header {
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
        text-align: center;
        padding: 4px 0;
        min-width: 28px;
    }

    td.month-label {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 8px;
        white-space: nowrap;
        text-align: left;
        min-width: 90px;
    }

    /* Calendar Day Cells */
    .day-cell {
        height: 30px;
        min-width: 28px;
        border-radius: 5px;
        text-align: center;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.12s ease;
        user-select: none;
        display: table-cell;
        vertical-align: middle;
        border: 1px solid transparent;
        position: relative;
    }

    .day-cell:hover {
        transform: scale(1.08);
        border-color: #ffffff55 !important;
        z-index: 5;
    }

    /* Today Highlight Ring */
    .day-cell.is-today {
        box-shadow: 0 0 0 2px #38bdf8, 0 0 10px rgba(56, 189, 248, 0.6) !important;
        border-color: #38bdf8 !important;
        z-index: 4;
    }

    /* Status Color Themes */
    .status-empty { background-color: #1a1e27; color: #475569; }
    .status-work { background-color: #133a20; color: #4ade80; border-color: #16522c; }
    .status-pub-holiday { background-color: #1e3a8a; color: #60a5fa; border-color: #1d4ed8; }
    .status-holiday { background-color: #4c0519; color: #fb7185; border-color: #9f1239; }
    .status-getaway { background-color: #422006; color: #facc15; border-color: #713f12; }
    .status-work-trip { background-color: #3b0764; color: #c084fc; border-color: #6b21a8; }

    /* Active Selected State */
    .day-cell.selected {
        outline: 2px solid #ffffff;
        outline-offset: 1px;
    }

    /* Legend Bar */
    .legend-bar {
        display: flex;
        gap: 12px;
        margin-top: 14px;
        flex-wrap: wrap;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        color: #94a3b8;
        background: #1a1e27;
        padding: 4px 10px;
        border-radius: 5px;
        border: 1px solid #28303f;
    }

    .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 2px;
    }

    /* Detail Panel & Tabbed Interface */
    .detail-panel {
        margin-top: 16px;
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 10px;
        padding: 20px;
    }

    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }

    .panel-title {
        font-size: 16px;
        font-weight: 700;
        color: #f8fafc;
    }

    .status-badge {
        font-size: 11px;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
    }

    /* Tabs Styling */
    .tab-bar {
        display: flex;
        gap: 6px;
        border-bottom: 1px solid #222734;
        margin-bottom: 16px;
    }

    .tab-btn {
        background: none;
        border: none;
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        padding: 8px 14px;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        transition: all 0.15s;
    }

    .tab-btn.active {
        color: #38bdf8;
        border-bottom-color: #38bdf8;
    }

    .tab-content {
        display: none;
        color: #94a3b8;
        font-size: 13px;
        line-height: 1.5;
    }

    .tab-content.active {
        display: block;
    }

    /* Dynamic Data Cards */
    .data-card {
        background: #1c212c;
        border-left: 3px solid #38bdf8;
        padding: 10px 14px;
        border-radius: 5px;
        margin-bottom: 8px;
    }

    .data-card.bill {
        border-left-color: #f59e0b;
    }

    .data-title {
        color: #f8fafc;
        font-weight: 600;
        font-size: 13px;
    }

    .data-sub {
        color: #64748b;
        font-size: 11px;
        margin-top: 2px;
    }
</style>
</head>
<body>

<!-- Top Bar showing Today's Date -->
<div class="top-bar">
    <div class="today-info">
        <span class="today-badge">Today</span>
        <span class="today-date-text" id="todayTextDisplay">Wednesday, August 12, 2026</span>
    </div>
    <div class="year-title">Annual Schedule Sync • 2026</div>
</div>

<!-- Linear Calendar Grid -->
<div class="calendar-container">
    <table class="cal-grid" id="calendarGrid"></table>

    <div class="legend-bar">
        <div class="legend-item"><div class="legend-dot" style="background:#4ade80"></div>Working</div>
        <div class="legend-item"><div class="legend-dot" style="background:#60a5fa"></div>Public Holiday</div>
        <div class="legend-item"><div class="legend-dot" style="background:#fb7185"></div>Holiday</div>
        <div class="legend-item"><div class="legend-dot" style="background:#facc15"></div>Get-away</div>
        <div class="legend-item"><div class="legend-dot" style="background:#c084fc"></div>Work Trip</div>
        <div class="legend-item"><div class="legend-dot" style="background:#38bdf8; border:1px solid #fff"></div>Today's Date</div>
    </div>
</div>

<!-- Interactive Detail Panel -->
<div class="detail-panel" id="detailPanel">
    <div class="panel-header">
        <div class="panel-title" id="selectedDateTitle">August 12, 2026</div>
        <div class="status-badge status-work" id="selectedStatusBadge">Working</div>
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
    const TODAY = { month: 7, day: 12 }; // August 12, 2026 (0-indexed month: 7 = August)
    
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    // Mock Live Database synced by Date Key ("YYYY-MM-DD")
    const database = {
        "2026-08-12": {
            events: [
                { title: "Team Sync & Standup", time: "09:00 AM - 09:30 AM" },
                { title: "Aura Dashboard Sprint Review", time: "02:00 PM - 03:00 PM" }
            ],
            bills: [
                { title: "Google Workspace Subscription", amount: "$18.00 AUD", due: "Auto-debit today" }
            ],
            notes: "Focus on finalizing calendar interface sync today."
        },
        "2026-08-25": {
            events: [{ title: "Flight to Sydney (Get-away)", time: "08:15 AM" }],
            bills: [{ title: "Rent Payment", amount: "$520.00 AUD", due: "Due today" }],
            notes: "Pack bags night before."
        },
        "2026-11-16": {
            events: [{ title: "Q4 Strategy Conference (Work Trip)", time: "All Day" }],
            bills: [],
            notes: "Prepare presentation slides."
        }
    };

    function getStatus(monthIdx, day) {
        if (monthIdx === 7 && day >= 23 && day <= 29) return { class: 'status-holiday', name: 'Holiday' };
        if (monthIdx === 10 && day >= 16 && day <= 20) return { class: 'status-work-trip', name: 'Work Trip' };
        if (monthIdx === 10 && (day === 1 || day >= 30)) return { class: 'status-getaway', name: 'Get-away' };
        if (monthIdx === 0 && day === 1) return { class: 'status-pub-holiday', name: 'Public Holiday' };
        
        const dateObj = new Date(YEAR, monthIdx, day);
        const dayOfWeek = dateObj.getDay();
        if (dayOfWeek === 0 || dayOfWeek === 6) return { class: 'status-empty', name: 'Weekend' };
        
        return { class: 'status-work', name: 'Working' };
    }

    function renderGrid() {
        const grid = document.getElementById('calendarGrid');
        let html = '<thead><tr><th class="col-header">2026</th>';
        
        for (let d = 1; d <= 31; d++) {
            html += `<th class="col-header">${d}</th>`;
        }
        html += '</tr></thead><tbody>';

        months.forEach((mName, mIdx) => {
            html += `<tr><td class="month-label">${mName}</td>`;
            const totalDays = daysInMonths[mIdx];

            for (let d = 1; d <= 31; d++) {
                if (d <= totalDays) {
                    const dateObj = new Date(YEAR, mIdx, d);
                    const dayLetter = dateObj.toLocaleDateString('en-US', { weekday: 'narrow' });
                    const status = getStatus(mIdx, d);
                    
                    const isToday = (mIdx === TODAY.month && d === TODAY.day);
                    const todayClass = isToday ? 'is-today' : '';
                    
                    html += `<td class="day-cell ${status.class} ${todayClass}" 
                                 id="cell-${mIdx}-${d}"
                                 onclick="selectDate(${mIdx}, ${d}, '${mName}', '${status.name}', '${status.class}', this)">
                                 ${dayLetter}
                             </td>`;
                } else {
                    html += '<td style="background:transparent;"></td>';
                }
            }
            html += '</tr>';
        });

        html += '</tbody>';
        grid.innerHTML = html;
    }

    function selectDate(mIdx, day, monthName, statusName, statusClass, element) {
        document.querySelectorAll('.day-cell').forEach(c => c.classList.remove('selected'));
        element.classList.add('selected');

        document.getElementById('selectedDateTitle').innerText = `${monthName} ${day}, ${YEAR}`;
        
        const badge = document.getElementById('selectedStatusBadge');
        badge.innerText = statusName;
        badge.className = `status-badge ${statusClass}`;

        // Format Date Key (YYYY-MM-DD)
        const mStr = String(mIdx + 1).padStart(2, '0');
        const dStr = String(day).padStart(2, '0');
        const dateKey = `${YEAR}-${mStr}-${dStr}`;

        // Sync Data Content into Tabs
        const dayData = database[dateKey] || { events: [], bills: [], notes: '' };
        
        // Render Events
        const eventsContainer = document.getElementById('eventsTab');
        if (dayData.events.length > 0) {
            eventsContainer.innerHTML = dayData.events.map(e => `
                <div class="data-card">
                    <div class="data-title">${e.title}</div>
                    <div class="data-sub">🕒 ${e.time}</div>
                </div>
            `).join('');
        } else {
            eventsContainer.innerHTML = `<p style="color:#64748b; font-size:12px;">No scheduled events for this date.</p>`;
        }

        // Render Bills
        const billsContainer = document.getElementById('billsTab');
        if (dayData.bills.length > 0) {
            billsContainer.innerHTML = dayData.bills.map(b => `
                <div class="data-card bill">
                    <div class="data-title">${b.title} — <span style="color:#f59e0b;">${b.amount}</span></div>
                    <div class="data-sub">💳 ${b.due}</div>
                </div>
            `).join('');
        } else {
            billsContainer.innerHTML = `<p style="color:#64748b; font-size:12px;">No bills due on this date.</p>`;
        }

        // Render Notes
        const notesContainer = document.getElementById('notesTab');
        notesContainer.innerHTML = `<p style="color:#94a3b8; font-size:13px;">${dayData.notes || 'No notes added for this date.'}</p>`;
    }

    function switchTab(tabId, btn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(tabId).classList.add('active');
    }

    // Initialize Grid & Auto-select Today (August 12)
    renderGrid();
    setTimeout(() => {
        const todayCell = document.getElementById(`cell-${TODAY.month}-${TODAY.day}`);
        if (todayCell) {
            selectDate(TODAY.month, TODAY.day, months[TODAY.month], 'Working', 'status-work', todayCell);
        }
    }, 50);
</script>

</body>
</html>
"""

# Render dynamically with enough height to eliminate internal scrollbars
components.html(calendar_html, height=720, scrolling=False)
