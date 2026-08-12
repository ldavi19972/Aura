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

# Load Data Live from Google Sheets (Refreshes automatically)
@st.cache_data(ttl=60)
def load_live_data():
    # REPLACE THESE URLs with your actual Google Sheet CSV export links
    finances_url = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/edit?gid=1688426207#gid=1688426207"
    calendar_url = "https://docs.google.com/spreadsheets/d/1ilr62jlHutXMTJScGlJ92dpX2O6CFtPkKRlQRDZbrhI/edit?gid=0#gid=0"
    
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

# --- TAB 1: DASHBOARD ---
if tab == "📊 Dashboard":
    st.title("Dashboard Overview")
    st.markdown("Your financial health and schedule synced live from Google Sheets.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Weekly Income", "$1,814.00", "Salary + Transfers")
    with col2:
        st.metric("Weekly Expenses", "$1,096.72", "Bills & Rent")
    with col3:
        st.metric("Net Surplus", "+$717.29", "Weekly buffer")
    with col4:
        st.metric("Total Liabilities", "-$21,118.00", "Loans & Debt")

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🎯 Active Savings Goals")
        st.write("• **🇮🇹 Italy Trip ($7,000):** $1,037.50 saved")
        st.progress(0.148)
        st.write("• **✈️ New Zealand:** $2,087.98 (Saved)")
        st.progress(1.0)
        st.write("• **🌆 Adelaide ($2,600):** $650.00 saved")
        st.progress(0.25)
        st.write("• **🛡️ Emergency Fund ($9,000):** $692.31 saved")
        st.progress(0.077)
        
    with col_b:
        st.subheader("📅 Upcoming Schedule")
        if calendar_df is not None:
            for idx, row in calendar_df.head(5).iterrows():
                st.info(f"**{row.get('Title', 'Event')}**\n🕒 {row.get('Date', '')} at {row.get('Time', '')}")
        else:
            st.warning("Could not load live calendar data. Check your Google Sheet URL.")

# --- TAB 2: FINANCES & BUDGETS ---
elif tab == "💳 Finances & Budgets":
    st.title("Finances, Budgets & Liabilities")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💰 Income & Fixed Bills")
        st.markdown("""
        * **Salary (Weekly):** $1,424.00
        * **Transfers (Weekly):** $390.00
        * **Rent:** $721.25 / wk
        * **Electricity:** $18.62 / wk
        * **Gym Membership:** $35.20 / wk
        * **RT Health Insurance:** $35.34 / wk
        * **Internet:** $11.31 / wk
        """)
    with col2:
        st.subheader("🏷️ Discretionary Budgets & Debt")
        st.markdown("""
        * **Groceries:** $100.00 / wk
        * **Eating Out:** $100.00 / wk
        * **Fun & Entertainment:** $50.00 / wk
        * **Credit Card Repayment:** $1.00 / wk
        * **Student Loan Repayment:** $192.00 / wk
        """)

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
