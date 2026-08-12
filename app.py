import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Calendar 26' Interactive Grid",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Render complete modern web component in Streamlit
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
        background-color: #0d0f12;
        color: #f1f5f9;
        padding: 24px;
    }

    /* App Header */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid #1e293b;
    }
    .title-group h1 {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #f8fafc;
    }
    .title-group p {
        font-size: 13px;
        color: #64748b;
        margin-top: 4px;
    }

    /* Grid Layout Container */
    .calendar-container {
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 12px;
        padding: 20px;
        overflow-x: auto;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    table.cal-grid {
        width: 100%;
        border-collapse: separate;
        border-spacing: 3px;
    }

    th.col-header {
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
        text-align: center;
        padding: 6px 0;
        min-width: 32px;
        text-transform: uppercase;
    }

    td.month-label {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        padding: 6px 12px;
        white-space: nowrap;
        text-align: left;
        min-width: 100px;
    }

    /* Calendar Day Cells */
    .day-cell {
        height: 34px;
        min-width: 32px;
        border-radius: 6px;
        text-align: center;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;
        user-select: none;
        display: table-cell;
        vertical-align: middle;
        border: 1px solid transparent;
    }

    .day-cell:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border-color: #ffffff33 !important;
        z-index: 10;
    }

    /* Status Themes (Subtle, modern pastel tones) */
    .status-empty { background-color: #1c212c; color: #334155; }
    .status-work { background-color: #143823; color: #4ade80; border-color: #16522c; }
    .status-pub-holiday { background-color: #1e3a8a; color: #60a5fa; border-color: #1d4ed8; }
    .status-holiday { background-color: #4c0519; color: #fb7185; border-color: #9f1239; }
    .status-getaway { background-color: #422006; color: #facc15; border-color: #713f12; }
    .status-work-trip { background-color: #3b0764; color: #c084fc; border-color: #6b21a8; }

    /* Selected Cell State */
    .day-cell.selected {
        outline: 2px solid #38bdf8;
        outline-offset: 1px;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
    }

    /* Legend Bar */
    .legend-bar {
        display: flex;
        gap: 12px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #94a3b8;
        background: #1e2430;
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid #2a3241;
    }
    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 3px;
    }

    /* Interactive Detail Panel & Tabs */
    .detail-panel {
        margin-top: 24px;
        background: #161a22;
        border: 1px solid #222734;
        border-radius: 12px;
        padding: 24px;
    }
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .panel-title {
        font-size: 18px;
        font-weight: 600;
        color: #f8fafc;
    }
    .status-badge {
        font-size: 12px;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }

    /* Tabs Styling */
    .tab-bar {
        display: flex;
        gap: 8px;
        border-bottom: 1px solid #222734;
        margin-bottom: 16px;
    }
    .tab-btn {
        background: none;
        border: none;
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        padding: 8px 16px;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
    }
    .tab-btn.active {
        color: #38bdf8;
        border-bottom-color: #38bdf8;
    }
    .tab-content {
        display: none;
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.6;
    }
    .tab-content.active {
        display: block;
    }

    .event-card {
        background: #1e2430;
        border-left: 3px solid #38bdf8;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
</style>
</head>
<body>

<div class="header">
    <div class="title-group">
        <h1>Calendar 2026</h1>
        <p>Click any date on the grid to inspect details and switch tabs.</p>
    </div>
</div>

<div class="calendar-container">
    <table class="cal-grid" id="calendarGrid"></table>

    <div class="legend-bar">
        <div class="legend-item"><div class="legend-dot" style="background:#4ade80"></div>Working</div>
        <div class="legend-item"><div class="legend-dot" style="background:#60a5fa"></div>Public Holiday</div>
        <div class="legend-item"><div class="legend-dot" style="background:#fb7185"></div>Holiday</div>
        <div class="legend-item"><div class="legend-dot" style="background:#facc15"></div>Get-away</div>
        <div class="legend-item"><div class="legend-dot" style="background:#c084fc"></div>Work Trip</div>
    </div>
</div>

<!-- Dynamic Detail View -->
<div class="detail-panel" id="detailPanel">
    <div class="panel-header">
        <div class="panel-title" id="selectedDateTitle">Select a date from the calendar</div>
        <div class="status-badge" id="selectedStatusBadge" style="display:none;"></div>
    </div>

    <div class="tab-bar">
        <button class="tab-btn active" onclick="switchTab('eventsTab', this)">Events & Schedule</button>
        <button class="tab-btn" onclick="switchTab('billsTab', this)">Bills Due</button>
        <button class="tab-btn" onclick="switchTab('notesTab', this)">Day Notes</button>
    </div>

    <div id="eventsTab" class="tab-content active">
        <div class="event-card">
            <strong style="color:#f8fafc;">Team Sync & Planning</strong><br>
            <small style="color:#64748b;">09:00 AM - 10:00 AM</small>
        </div>
        <p style="color:#64748b; font-size: 13px;">No other major events scheduled for this day.</p>
    </div>

    <div id="billsTab" class="tab-content">
        <p style="color:#64748b; font-size: 13px;">No recurring bills or payments due on this date.</p>
    </div>

    <div id="notesTab" class="tab-content">
        <p style="color:#64748b; font-size: 13px;">Click to edit notes for this date...</p>
    </div>
</div>

<script>
    const YEAR = 2026;
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    // Status map sample logic matching sheet
    function getStatus(monthIdx, day) {
        if (monthIdx === 7 && day >= 23 && day <= 29) return { class: 'status-holiday', name: 'Holiday' };
        if (monthIdx === 10 && day >= 16 && day <= 20) return { class: 'status-work-trip', name: 'Work Trip' };
        if (monthIdx === 10 && (day === 1 || day >= 30)) return { class: 'status-getaway', name: 'Get-away' };
        if (monthIdx === 0 && day === 1) return { class: 'status-pub-holiday', name: 'Public Holiday' };
        
        // General working pattern
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
                    
                    html += `<td class="day-cell ${status.class}" 
                                 onclick="selectDate('${mName}', ${d}, '${status.name}', '${status.class}', this)">
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

    function selectDate(month, day, statusName, statusClass, element) {
        // Clear old selections
        document.querySelectorAll('.day-cell').forEach(c => c.classList.remove('selected'));
        element.classList.add('selected');

        // Update details panel
        document.getElementById('selectedDateTitle').innerText = `${month} ${day}, 2026`;
        
        const badge = document.getElementById('selectedStatusBadge');
        badge.innerText = statusName;
        badge.style.display = 'inline-block';
        badge.className = `status-badge ${statusClass}`;
    }

    function switchTab(tabId, btn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(tabId).classList.add('active');
    }

    // Initialize Grid
    renderGrid();
</script>

</body>
</html>
"""

# Render full screen height component
components.html(calendar_html, height=850, scrolling=True)
