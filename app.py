import pandas as pd
import streamlit as st


# Safe metric helper with NaN fallback
def safe_sum(df, column_name):
  if df is not None and column_name in df.columns:
    return pd.to_numeric(df[column_name], errors="coerce").sum()
  return 0.0


# Example metric layout
col1, col2, col3, col4 = st.columns(4)

with col1:
  income_val = safe_sum(income_df, "Amount")
  st.metric(
      label="Weekly Income",
      value=f"${income_val:,.2f}",
      delta="Salary + Transfers",
  )

with col2:
  expense_val = safe_sum(expenses_df, "Amount")
  st.metric(
      label="Weekly Expenses",
      value=f"${expense_val:,.2f}",
      delta="Bills & Rent",
  )

with col3:
  net_surplus = income_val - expense_val
  st.metric(
      label="Net Surplus",
      value=f"${net_surplus:,.2f}",
      delta="Weekly buffer",
  )

with col4:
  liabilities_val = safe_sum(liabilities_df, "Balance")
  st.metric(
      label="Total Liabilities",
      value=f"${liabilities_val:,.2f}",
      delta="Loans & Debt",
  )
