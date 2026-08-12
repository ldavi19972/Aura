import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Aura — Personal Finance & Life Dashboard",
    page_icon="⚡",
    layout="wide",
)

# Custom Dark Mode Styling
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("## ⚡ Aura Dashboard")
st.sidebar.markdown("---")
tab = st.sidebar.radio("Navigation", ["📊 Dashboard", "💳 Finances & Budgets", "💎 Assets & Depreciation", "📅 Schedule & Calendar"])

# Load Data Live from Google Sheets
@st.cache_data(ttl=60)
def load_live_data():
    finances_url = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=1688426207"
    calendar_url = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/export?format=csv&gid=0"
    
    try:
        finances = pd.read_csv(finances_url)
    except Exception:
        finances = None
        
    try:
        calendar = pd.read_csv(calendar_url)
    except Exception:
        calendar = None
        
    return finances, calendar

finances_df, calendar_df = load_live_data()

# --- Extract Live Metrics from Google Sheet Data ---
weekly_income_val = 0.0
weekly_expenses_val = 0.0
total_liabilities_val = 0.0

if finances_df is not None:
    try:
        # Pulls Weekly Income from Row 0, 'Weekly' column
        weekly_income_val = float(str(finances_df.iloc[0]['Weekly']).replace('$', '').replace(',', ''))
        # Pulls Weekly Expenses from Row 3, 'Weekly' column
        weekly_expenses_val = float(str(finances_df.iloc[3]['Weekly']).replace('$', '').replace(',', ''))
        # Pulls Total Liabilities from Row 11, 'Unnamed: 8' column
        total_liabilities_val = float(str(finances_df.iloc[11]['Unnamed: 8']).replace('$', '').replace(',', ''))
    except Exception:
        pass

net_surplus_val = weekly_income_val - weekly_expenses_val

# --- TAB 1: DASHBOARD ---
if tab == "📊 Dashboard":
    st.title("Dashboard Overview")
    st.markdown("Your financial health and schedule synced live from Google Sheets.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Weekly Income", f"${weekly_income_val:,.2f}", "Salary + Transfers")
    with col2:
        st.metric("Weekly Expenses", f"${weekly_expenses_val:,.2f}", "Bills & Rent")
    with col3:
        st.metric("Net Surplus", f"${net_surplus_val:+,.2f}", "Weekly buffer")
    with col4:
        st.metric("Total Liabilities", f"${total_liabilities_val:,.2f}", "Loans & Debt")

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🎯 Active Savings Goals (Live from Sheet)")
        if finances_df is not None:
            try:
                goals_subset = finances_df.iloc[12:16, [9, 10, 12, 15]].dropna(how='all')
                goals_subset.columns = ["Goal", "Target", "Target Date", "Saved"]
                for idx, row in goals_subset.iterrows():
                    st.write(f"• **{row.get('Goal', 'Goal')} (Target: ${row.get('Target', '0')}):** ${row.get('Saved', '0')} saved (Due: {row.get('Target Date', 'N/A')})")
            except Exception:
                st.write("Unable to parse savings goals table.")
        else:
            st.warning("Loading savings goals...")
        
    with col_b:
        st.subheader("📅 Upcoming Schedule (Live Calendar)")
        if calendar_df is not None and not calendar_df.empty:
            for idx, row in calendar_df.head(5).iterrows():
                event_title = row.iloc[1] if len(row) > 1 else "Event"
                event_date = row.iloc[0] if len(row) > 0 else ""
                event_time = row.iloc[2] if len(row) > 2 else ""
                st.info(f"**{event_title}**\n🕒 {event_date} at {event_time}")
        else:
            st.warning("Could not load live calendar data.")

# --- TAB 2: FINANCES & BUDGETS ---
elif tab == "💳 Finances & Budgets":
    st.title("Finances, Budgets & Liabilities")
    if finances_df is not None:
        st.dataframe(finances_df, use_container_width=True)
    else:
        st.write("Loading finances data...")

# --- TAB 3: ASSETS & DEPRECIATION ---
elif tab == "💎 Assets & Depreciation":
    st.title("Physical Asset Portfolio")
    if finances_df is not None:
        st.dataframe(finances_df, use_container_width=True)
    else:
        st.write("Loading asset data from Google Sheets...")

# --- TAB 4: SCHEDULE & CALENDAR ---
elif tab == "📅 Schedule & Calendar":
    st.title("Full Event Timeline")
    if calendar_df is not None:
        st.dataframe(calendar_df, use_container_width=True)
    else:
        st.write("Loading schedule data from Google Sheets...")
