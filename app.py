import streamlit as st
import pandas as pd
import datetime
import calendar

# 1. Page Configuration & Dark Theme styling matching Aura Dashboard
st.set_page_config(
    page_title="Aura Dashboard & Calendar 26'",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Aura Dark Aesthetic + Custom Horizontal Calendar Grid Styling
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp {
        background-color: #16181a;
        color: #e0e0e0;
    }
    
    /* Metrics / Summary Cards */
    .metric-card {
        background-color: #212529;
        border: 1px solid #343a40;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 13px;
        color: #98a6ad;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-badge {
        font-size: 11px;
        background-color: #1e3a29;
        color: #2ecc71;
        padding: 2px 8px;
        border-radius: 10px;
        display: inline-block;
        margin-top: 5px;
    }

    /* Custom Calendar Grid Styling */
    .cal-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 2px;
        font-size: 12px;
        color: #000;
        margin-bottom: 25px;
    }
    .cal-header {
        background-color: #212529;
        color: #fff;
        text-align: center;
        padding: 4px;
        font-weight: bold;
    }
    .cal-month-title {
        background-color: #2b3035;
        color: #ffffff;
        font-weight: bold;
        padding: 6px;
        border-radius: 4px;
        text-align: left;
    }
    .cal-cell {
        text-align: center;
        padding: 4px;
        border-radius: 2px;
        min-width: 28px;
    }
    .bg-empty { background-color: transparent; }
    .bg-work { background-color: #a2db96; font-weight: bold; } /* Green */
    .bg-pub-holiday { background-color: #0088ff; color: white; font-weight: bold; } /* Blue */
    .bg-holiday { background-color: #ff0000; color: white; font-weight: bold; } /* Red */
    .bg-getaway { background-color: #ffff00; font-weight: bold; } /* Yellow */
    .bg-work-trip { background-color: #a020f0; color: white; font-weight: bold; } /* Purple */
    
    /* Key / Legend Styling */
    .legend-box {
        padding: 8px 12px;
        border-radius: 4px;
        text-align: center;
        font-weight: bold;
        font-size: 12px;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
st.sidebar.title("⚡ Aura Dashboard")
st.sidebar.caption("Navigation")

navigation = st.sidebar.radio(
    "",
    ["📰 News Feed / Dashboard", "📅 Schedule & Calendar", "💳 Finances & Budgets", "💎 Assets & Depreciation"],
    index=0
)

# Year Selector
YEAR = 2026

# Sample Data Store for Legend/Events
STATUS_COLORS = {
    "Working": "#a2db96",
    "Public Holiday": "#0088ff",
    "Holiday": "#ff0000",
    "Get-away": "#ffff00",
    "Work Trip": "#a020f0",
}

# ---------------------------------------------------------
# TAB 1: News Feed / Dashboard Overview
# ---------------------------------------------------------
if navigation == "📰 News Feed / Dashboard":
    st.title("Dashboard Overview")
    st.caption("Your financial health and schedule feed synced live from Google Sheets.")

    # 4 Top Summary Cards (Matching your exact screenshot layout)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Weekly Income</div>
            <div class="metric-value">$0.00</div>
            <div class="metric-badge">↑ Salary + Transfers</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Weekly Expenses</div>
            <div class="metric-value">$0.00</div>
            <div class="metric-badge">↑ Bills & Rent</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Net Surplus</div>
            <div class="metric-value">+$0.00</div>
            <div class="metric-badge">↑ Weekly buffer</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Liabilities</div>
            <div class="metric-value">$47,236.00</div>
            <div class="metric-badge" style="background:#3d1a1a; color:#ff6b6b;">↑ Loans & Debt</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("🎯 Active Savings Goals Feed")
        
        with st.container():
            st.markdown("""
            <div class="metric-card">
                <div style="display:flex; justify-content:space-between;">
                    <strong>Position</strong>
                    <span style="background:#2b3035; padding:2px 8px; border-radius:4px; font-size:12px;">Target: $1</span>
                </div>
                <p style="color:#98a6ad; margin-top:10px; font-size:13px;">Saved: <span style="color:#2ecc71;">$0.00</span> • Due: Ongoing</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="metric-card">
                <div style="display:flex; justify-content:space-between;">
                    <strong>-$21,179.97</strong>
                    <span style="background:#2b3035; padding:2px 8px; border-radius:4px; font-size:12px;">Target: $1</span>
                </div>
                <p style="color:#98a6ad; margin-top:10px; font-size:13px;">Saved: <span style="color:#2ecc71;">$0.00</span> • Due: Maintain</p>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.subheader("📅 Upcoming Schedule Feed")
        st.info("No upcoming events found from today onwards.")


# ---------------------------------------------------------
# TAB 2: Schedule & Calendar (Replicating Calendar 26' Grid)
# ---------------------------------------------------------
elif navigation == "📅 Schedule & Calendar":
    st.title(f"Calendar {str(YEAR)[2:]}' Review")

    # Interactive Date Selection Controls
    col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 2])
    with col_sel1:
        selected_month = st.selectbox("Select Month", list(calendar.month_name)[1:], index=7) # Default August
    with col_sel2:
        month_idx = list(calendar.month_name).index(selected_month)
        max_days = calendar.monthrange(YEAR, month_idx)[1]
        selected_day = st.number_input("Select Day", min_value=1, max_value=max_days, value=12)

    selected_date_str = f"{selected_month} {selected_day}, {YEAR}"
    st.success(f"📌 Selected Date: **{selected_date_str}**")

    st.markdown("---")

    # Helper function to generate calendar HTML matching your sheet layout
    def render_linear_calendar():
        months = list(calendar.month_name)[1:]
        
        # Sample custom status mappings to mirror sheet colors
        # (Day 1-31 status mapping)
        def get_day_status(month_num, day_num):
            # August sample matching sheet image
            if month_num == 8:
                if 23 <= day_num <= 29:
                    return "bg-holiday" # Red
            # November sample
            if month_num == 11:
                if 16 <= day_num <= 20:
                    return "bg-work-trip" # Purple
                if day_num == 1:
                    return "bg-getaway" # Yellow
            # October sample
            if month_num == 10 and day_num in [30, 31]:
                return "bg-getaway"
            return "bg-work" if (day_num + month_num) % 3 == 0 else ""

        html = '<div style="overflow-x:auto;"><table class="cal-table">'
        
        # Header Row: Days 1 to 31
        html += f'<tr><th class="cal-header" style="min-width:100px;">{YEAR}</th>'
        for d in range(1, 32):
            html += f'<th class="cal-header">{d}</th>'
        html += '</tr>'

        # Render Each Month Row
        for m_idx, m_name in enumerate(months, start=1):
            html += f'<tr><td class="cal-month-title">{m_name}</td>'
            
            num_days = calendar.monthrange(YEAR, m_idx)[1]
            
            for d in range(1, 32):
                if d <= num_days:
                    # Get Day of week letter (T, W, T, F, S, S, M)
                    day_obj = datetime.date(YEAR, m_idx, d)
                    day_letter = day_obj.strftime("%a")[0]
                    
                    status_class = get_day_status(m_idx, d)
                    
                    # Highlight selected date with a border outline
                    border_style = "border: 2px solid #0088ff;" if (m_name == selected_month and d == selected_day) else ""

                    html += f'<td class="cal-cell {status_class}" style="{border_style}">{day_letter}</td>'
                else:
                    html += '<td class="cal-cell bg-empty"></td>'
            
            html += '</tr>'

        html += '</table></div>'
        return html

    # Render Grid
    st.markdown(render_linear_calendar(), unsafe_allow_html=True)

    # Key / Legend (Matching bottom of image)
    st.subheader("Key")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown('<div class="legend-box" style="background:#a2db96; color:#000;">Working</div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="legend-box" style="background:#0088ff; color:#fff;">Public Holiday</div>', unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="legend-box" style="background:#ff0000; color:#fff;">Holiday</div>', unsafe_allow_html=True)
    with k4:
        st.markdown('<div class="legend-box" style="background:#ffff00; color:#000;">Get-away</div>', unsafe_allow_html=True)
    with k5:
        st.markdown('<div class="legend-box" style="background:#a020f0; color:#fff;">Work Trip</div>', unsafe_allow_html=True)
    with k6:
        st.markdown('<div class="legend-box" style="background:#2b3035; color:#fff;">Events | Bills<br><small>1 | 2</small></div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 3 & 4: Placeholder Pages
# ---------------------------------------------------------
elif navigation == "💳 Finances & Budgets":
    st.title("💳 Finances & Budgets")
    st.info("Finance detailed view and budget allocation tables.")

elif navigation == "💎 Assets & Depreciation":
    st.title("💎 Assets & Depreciation")
    st.info("Asset tracking and depreciation schedules.")
