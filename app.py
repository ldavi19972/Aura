import streamlit as st
import pandas as pd
import datetime

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
        weekly_income_val = float(str(finances_df.iloc[0]['Weekly']).replace('$', '').replace(',', ''))
        weekly_expenses_val = float(str(finances_df.iloc[3]['Weekly']).replace('$', '').replace(',', ''))
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
        st.subheader("🎯 Active Savings Goals")
        if finances_df is not None:
            try:
                # Extract and parse goals cleanly from sheet layout
                goals_subset = finances_df.iloc[12:16, [9, 10, 12, 14, 15]].copy()
                goals_subset.columns = ["Goal", "Target", "Target_Date", "Weekly_Saving", "Saved"]
                
                for idx, row in goals_subset.iterrows():
                    name = str(row.get('Goal', 'Goal'))
                    
                    # Clean target amount
                    try:
                        target = float(str(row.get('Target', '0')).replace('$', '').replace(',', ''))
                    except:
                        target = 1.0
                        
                    # Clean saved amount
                    saved_raw = str(row.get('Saved', '0')).replace('$', '').replace(',', '')
                    try:
                        saved = float(saved_raw)
                    except:
                        saved = 0.0 if saved_raw.upper() in ['WAITING', 'SAVED', ''] else 0.0
                        if saved_raw.upper() == 'SAVED':
                            saved = target

                    progress = min(saved / target, 1.0) if target > 0 else 0.0
                    due_date = str(row.get('Target_Date', 'N/A'))
                    
                    st.markdown(f"**{name}** (Target: ${target:,.2f})")
                    st.progress(progress)
                    st.caption(f"Saved: ${saved:,.2f} | Due: {due_date}")
            except Exception as e:
                st.warning("Could not parse savings goals format.")
        else:
            st.warning("Loading savings goals...")
        
    with col_b:
        st.subheader("📅 Upcoming Schedule")
        if calendar_df is not None and not calendar_df.empty:
            try:
                # Standardize columns and parse dates
                cal_clean = calendar_df.copy()
                cal_clean.columns = ['Date', 'Title', 'Time', 'Location', 'Category'] + list(range(5, len(cal_clean.columns)))
                cal_clean['Date'] = pd.to_datetime(cal_clean['Date'], errors='coerce')
                
                # Filter for today onwards (Today = Aug 12, 2026)
                today = pd.Timestamp(datetime.date(2026, 8, 12))
                upcoming_df = cal_clean[cal_clean['Date'] >= today].sort_values(by='Date', ascending=True)
                
                if not upcoming_df.empty:
                    for idx, row in upcoming_df.head(5).iterrows():
                        ev_date = row['Date'].strftime('%d %b %Y') if pd.notnull(row['Date']) else "TBD"
                        ev_title = str(row.get('Title', 'Event'))
                        ev_time = str(row.get('Time', ''))
                        st.info(f"🕒 **{ev_date} at {ev_time}**\n\n{ev_title}")
                else:
                    st.info("No upcoming events found from today onwards.")
            except Exception as e:
                st.warning("Error processing calendar timeline.")
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
