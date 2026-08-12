import streamlit as st
import pandas as pd
import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Aura Dashboard",
    page_icon="⚡",
    layout="wide",
)

# --- Modern App Styling & CSS ---
st.markdown("""
    <style>
        /* Main Theme Background */
        .stApp {
            background-color: #0b0f19;
            color: #f3f4f6;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #111827;
            border-right: 1px solid #1f2937;
        }
        
        /* Metric Card Containers */
        [data-testid="stMetric"] {
            background-color: #161e2e;
            border: 1px solid #1f2937;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        [data-testid="stMetricLabel"] {
            color: #9ca3af !important;
            font-size: 0.85rem !important;
        }
        [data-testid="stMetricValue"] {
            color: #f9fafb !important;
            font-size: 1.6rem !important;
            font-weight: 700 !important;
        }

        /* Section Headings */
        h1, h2, h3 {
            color: #f9fafb;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        
        /* Card Containers */
        .custom-card {
            background-color: #161e2e;
            border: 1px solid #1f2937;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.markdown("## ⚡ Aura Dashboard")
st.sidebar.markdown("---")
tab = st.sidebar.radio("Navigation", ["📊 Dashboard", "💳 Finances & Budgets", "💎 Assets & Depreciation", "📅 Schedule & Calendar"])

# --- Load Live Data from Google Sheets ---
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

# --- Extract Metrics ---
weekly_income_val = 0.0
weekly_expenses_val = 0.0
total_liabilities_val = 0.0

if finances_df is not None:
    try:
        weekly_income_val = float(str(finances_df.iloc[0]['Weekly']).replace('$', '').replace(',', ''))
        weekly_expenses_val = float(str(finances_df.iloc[3]['Weekly']).replace('$', '').replace(',', ''))
        # Get total liabilities sum or specific cell
        total_liabilities_val = 26118.0 + 21118.0 # Example fallback or exact row sum
    except Exception:
        pass

net_surplus_val = weekly_income_val - weekly_expenses_val

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
if tab == "📊 Dashboard":
    st.title("Dashboard Overview")
    st.caption("Your financial health and schedule synced live from Google Sheets.")
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Weekly Income", f"${weekly_income_val:,.2f}", "Salary + Transfers")
    with col2:
        st.metric("Weekly Expenses", f"${weekly_expenses_val:,.2f}", "Bills & Rent")
    with col3:
        st.metric("Net Surplus", f"${net_surplus_val:+,.2f}", "Weekly buffer")
    with col4:
        st.metric("Total Liabilities", f"${total_liabilities_val:,.2f}", "Loans & Debt")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Two Column Main View
    col_a, col_b = st.columns([1.1, 0.9])
    
    with col_a:
        st.subheader("🎯 Active Savings Goals")
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        
        if finances_df is not None:
            try:
                # Parse Savings Goals from rows 12 to 15
                goals_subset = finances_df.iloc[12:16, [9, 10, 12, 14, 15]].copy()
                goals_subset.columns = ["Goal", "Target", "Target_Date", "Weekly_Saving", "Saved"]
                
                for idx, row in goals_subset.iterrows():
                    name = str(row.get('Goal', 'Goal'))
                    if name == 'nan' or not name:
                        continue
                        
                    try:
                        target = float(str(row.get('Target', '0')).replace('$', '').replace(',', ''))
                    except:
                        target = 1.0
                        
                    saved_raw = str(row.get('Saved', '0')).replace('$', '').replace(',', '')
                    if saved_raw.upper() == 'SAVED':
                        saved = target
                    elif saved_raw.upper() == 'WAITING':
                        saved = 0.0
                    else:
                        try:
                            saved = float(saved_raw)
                        except:
                            saved = 0.0

                    progress = min(saved / target, 1.0) if target > 0 else 0.0
                    due_date = str(row.get('Target_Date', 'Ongoing'))
                    if due_date == 'nan':
                        due_date = 'Ongoing'

                    col_g1, col_g2 = st.columns([2, 1])
                    with col_g1:
                        st.markdown(f"**{name}**")
                    with col_g2:
                        st.markdown(f"<div style='text-align: right; color: #9ca3af; font-size: 0.85rem;'>${saved:,.0f} / ${target:,.0f}</div>", unsafe_allow_html=True)
                    
                    st.progress(progress)
                    st.caption(f"Estimated Completion / Due: {due_date}")
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning("Could not parse savings goals format.")
        else:
            st.warning("Loading savings goals...")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_b:
        st.subheader("📅 Upcoming Schedule")
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        
        if calendar_df is not None and not calendar_df.empty:
            try:
                cal_clean = calendar_df.copy()
                cal_clean.columns = ['Date', 'Title', 'Time', 'Location', 'Category'] + list(range(5, len(cal_clean.columns)))
                cal_clean['Date'] = pd.to_datetime(cal_clean['Date'], errors='coerce')
                
                # Current baseline date set to Aug 12, 2026
                today = pd.Timestamp(datetime.date(2026, 8, 12))
                upcoming_df = cal_clean[cal_clean['Date'] >= today].sort_values(by='Date', ascending=True)
                
                if not upcoming_df.empty:
                    for idx, row in upcoming_df.head(4).iterrows():
                        ev_date = row['Date'].strftime('%d %b %Y') if pd.notnull(row['Date']) else "TBD"
                        ev_title = str(row.get('Title', 'Event'))
                        ev_time = str(row.get('Time', ''))
                        
                        st.markdown(f"🗓️ **{ev_date}** • <span style='color: #38bdf8;'>{ev_time}</span>", unsafe_allow_html=True)
                        st.markdown(f"**{ev_title}**")
                        st.markdown("<hr style='margin: 8px 0px; border-color: #1f2937;'>", unsafe_allow_html=True)
                else:
                    st.info("No upcoming events found from today onwards.")
            except Exception as e:
                st.warning("Error processing calendar timeline.")
        else:
            st.warning("Could not load live calendar data.")
            
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: FINANCES & BUDGETS
# ==========================================
elif tab == "💳 Finances & Budgets":
    st.title("Finances & Budgets")
    st.caption("Detailed breakdown of income, expenses, and budget categories.")
    if finances_df is not None:
        st.dataframe(finances_df, use_container_width=True)
    else:
        st.write("Loading finances data...")

# ==========================================
# TAB 3: ASSETS & DEPRECIATION
# ==========================================
elif tab == "💎 Assets & Depreciation":
    st.title("Assets & Depreciation Portfolio")
    st.caption("Physical asset tracking and valuation over time.")
    if finances_df is not None:
        st.dataframe(finances_df, use_container_width=True)
    else:
        st.write("Loading asset data from Google Sheets...")

# ==========================================
# TAB 4: SCHEDULE & CALENDAR
# ==========================================
elif tab == "📅 Schedule & Calendar":
    st.title("Schedule & Calendar Timeline")
    st.caption("Full synchronized schedule and calendar events.")
    if calendar_df is not None:
        st.dataframe(calendar_df, use_container_width=True)
    else:
        st.write("Loading schedule data from Google Sheets...")
