import streamlit as st
import pandas as pd
import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Aura Dashboard",
    page_icon="⚡",
    layout="wide",
)

# --- Facebook-Style Modern Dark UI CSS ---
st.markdown("""
    <style>
        /* Base App Background (Facebook Dark Theme Style) */
        .stApp {
            background-color: #18191a;
            color: #e4e6eb;
            font-family: SFProDisplay-Regular, Helvetica, Arial, sans-serif;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #242526;
            border-right: 1px solid #393a3b;
        }
        
        /* Metric Card Containers */
        [data-testid="stMetric"] {
            background-color: #242526;
            border: 1px solid #393a3b;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        [data-testid="stMetricLabel"] {
            color: #b0b3b8 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        [data-testid="stMetricValue"] {
            color: #e4e6eb !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
        }

        /* Headings */
        h1, h2, h3 {
            color: #e4e6eb;
            font-weight: 700;
        }
        
        /* Facebook Card Containers */
        .fb-card {
            background-color: #242526;
            border: 1px solid #393a3b;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 16px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        .fb-badge {
            background-color: #3a3b3c;
            color: #2e89ff;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.markdown("## ⚡ Aura Dashboard")
st.sidebar.markdown("---")
tab = st.sidebar.radio("Navigation", ["📊 News Feed / Dashboard", "💳 Finances & Budgets", "💎 Assets & Depreciation", "📅 Schedule & Calendar"])

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

# --- Extract Metrics Safely ---
weekly_income_val = 0.0
weekly_expenses_val = 0.0
total_liabilities_val = 47236.0  # Credit Card (26118) + Student Loan (21118)

if finances_df is not None:
    try:
        weekly_income_val = float(str(finances_df.iloc[0]['Weekly']).replace('$', '').replace(',', ''))
        weekly_expenses_val = float(str(finances_df.iloc[3]['Weekly']).replace('$', '').replace(',', ''))
    except Exception:
        pass

net_surplus_val = weekly_income_val - weekly_expenses_val

# ==========================================
# TAB 1: NEWS FEED / DASHBOARD
# ==========================================
if tab == "📊 News Feed / Dashboard":
    st.title("Dashboard Overview")
    st.caption("Your financial health and schedule feed synced live from Google Sheets.")
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Top Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Weekly Income", f"${weekly_income_val:,.2f}", "Salary + Transfers")
    with col2:
        st.metric("Weekly Expenses", f"${weekly_expenses_val:,.2f}", "Bills & Rent")
    with col3:
        st.metric("Net Surplus", f"${net_surplus_val:+,.2f}", "Weekly buffer")
    with col4:
        st.metric("Total Liabilities", f"${total_liabilities_val:,.2f}", "Loans & Debt")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Two Column Facebook Layout Feed
    col_feed, col_widget = st.columns([1.1, 0.9])
    
    with col_feed:
        st.subheader("🎯 Active Savings Goals Feed")
        
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

                    # Facebook Post-style Card for each goal
                    st.markdown(f"""
                        <div class="fb-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-weight: 700; font-size: 1.05rem; color: #e4e6eb;">{name}</span>
                                <span class="fb-badge">Target: ${target:,.0f}</span>
                            </div>
                            <div style="color: #b0b3b8; font-size: 0.85rem; margin-bottom: 6px;">
                                Saved: <strong style="color: #45bd62;">${saved:,.2f}</strong> • Due: {due_date}
                            </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(progress)
                    st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning("Could not parse savings goals format.")
        else:
            st.warning("Loading savings goals feed...")
        
    with col_widget:
        st.subheader("📅 Upcoming Schedule Feed")
        
        if calendar_df is not None and not calendar_df.empty:
            try:
                cal_clean = calendar_df.copy()
                cal_clean.columns = ['Date', 'Title', 'Time', 'Location', 'Category'] + list(range(5, len(cal_clean.columns)))
                cal_clean['Date'] = pd.to_datetime(cal_clean['Date'], errors='coerce')
                
                # Baseline current date: Aug 12, 2026
                today = pd.Timestamp(datetime.date(2026, 8, 12))
                upcoming_df = cal_clean[cal_clean['Date'] >= today].sort_values(by='Date', ascending=True)
                
                if not upcoming_df.empty:
                    for idx, row in upcoming_df.head(4).iterrows():
                        ev_date = row['Date'].strftime('%d %b %Y') if pd.notnull(row['Date']) else "TBD"
                        ev_title = str(row.get('Title', 'Event'))
                        ev_time = str(row.get('Time', ''))
                        ev_location = str(row.get('Location', ''))
                        if ev_location == 'nan' or not ev_location:
                            ev_location = "Online / Unspecified"
                        
                        st.markdown(f"""
                            <div class="fb-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <span style="color: #2e89ff; font-weight: 600; font-size: 0.85rem;">🗓️ {ev_date} at {ev_time}</span>
                                    <span style="color: #b0b3b8; font-size: 0.75rem;">Event</span>
                                </div>
                                <div style="font-weight: 600; font-size: 1rem; color: #e4e6eb; margin-bottom: 4px;">{ev_title}</div>
                                <div style="color: #b0b3b8; font-size: 0.82rem;">📍 {ev_location}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No upcoming events found from today onwards.")
            except Exception as e:
                st.warning("Error processing calendar timeline.")
        else:
            st.warning("Could not load live calendar data.")

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
    st.caption("Full synchronized schedule and calendar events feed.")
    if calendar_df is not None:
        st.dataframe(calendar_df, use_container_width=True)
    else:
        st.write("Loading schedule data from Google Sheets...")
