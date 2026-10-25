import os
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Retail Sales & Lead Analytics Hub", page_icon="📊", layout="wide"
)

st.title("📊 Retail Sales, Leads & Payment Analytics Dashboard")
st.markdown(
    "Analyze your retail performance data, review lead metrics, and publish"
    " processed records via API."
)


@st.cache_data
def load_data():
  # Load datasets using appropriate headers and skipping metadata rows
  leads = pd.read_csv("overall_lead_report_80_1792913172185.csv")
  payments = pd.read_csv(
      "PaymentModeReport-Abstract (10).csv", skiprows=5, encoding="latin1"
  )
  sales = pd.read_csv(
      "SalesReport-Detail-25_10_2026.csv", skiprows=5, encoding="latin1"
  )
  return leads, payments, sales


try:
  leads_df, payments_df, sales_df = load_data()
  st.sidebar.success("All raw data files loaded successfully!")
except Exception as e:
  st.error(f"Error loading data files: {e}")
  st.stop()

# Sidebar Navigation
analysis_tab = st.sidebar.selectbox(
    "Select Module", ["Overview & Metrics", "Sales Detail", "Lead Reports"]
)

# API Configuration Sidebar
st.sidebar.markdown("---")
st.sidebar.header("API Publication Settings")
api_url = st.sidebar.text_input(
    "API Endpoint URL", placeholder="https://api.example.com/v1/data"
)
api_token = st.sidebar.text_input(
    "API Authorization Token (Optional)", type="password"
)

if analysis_tab == "Overview & Metrics":
  st.subheader("📈 Executive Summary")

  col1, col2, col3 = st.columns(3)
  col1.metric("Total Leads Recorded", len(leads_df))
  col2.metric("Total Sales Transactions", len(sales_df))
  col3.metric("Total Payment Records", len(payments_df))

  st.markdown("---")
  st.subheader("💡 Quick Preview of Sales Dataset")
  st.dataframe(
      sales_df[
          [
              "BillDate",
              "BillNumber",
              "CustomerName",
              "ProductName",
              "MRP",
              "StoreName",
          ]
      ].head(10),
      use_container_width=True,
  )

elif analysis_tab == "Sales Detail":
  st.subheader("🛍️ Sales Detail Analytics")

  if "StoreName" in sales_df.columns:
    stores = ["All"] + list(sales_df["StoreName"].dropna().unique())
    selected_store = st.selectbox("Filter by Store", stores)
    filtered_sales = (
        sales_df
        if selected_store == "All"
        else sales_df[sales_df["StoreName"] == selected_store]
    )
  else:
    filtered_sales = sales_df

  st.metric("Filtered Records Count", len(filtered_sales))
  st.dataframe(filtered_sales.head(50), use_container_width=True)

elif analysis_tab == "Lead Reports":
  st.markdown("### 📋 Lead Generation & Status Report")
  if "Business Unit" in leads_df.columns:
    bu = ["All"] + list(leads_df["Business Unit"].dropna().unique())
    selected_bu = st.selectbox("Filter by Business Unit", bu)
    filtered_leads = (
        leads_df
        if selected_bu == "All"
        else leads_df[leads_df["Business Unit"] == selected_bu]
    )
  else:
    filtered_leads = leads_df

  st.dataframe(filtered_leads.head(50), use_container_width=True)

# Data Publishing Section
st.markdown("---")
st.subheader("🚀 Publish Dataset via API")
dataset_choice = st.selectbox(
    "Select Dataset to Publish", ["Sales Data", "Lead Data", "Payment Data"]
)

if st.button("Publish Selected Data"):
  if not api_url:
    st.error("Please provide a valid API Endpoint URL in the sidebar.")
  else:
    target_df = (
        sales_df
        if dataset_choice == "Sales Data"
        else (leads_df if dataset_choice == "Lead Data" else payments_df)
    )
    payload_sample = target_df.head(100).to_dict(
        orient="records"
    )  # Send sample payload

    headers = {"Content-Type": "application/json"}
    if api_token:
      headers["Authorization"] = f"Bearer {api_token}"

    try:
      response = requests.post(api_url, json=payload_sample, headers=headers)
      if response.status_code in [200, 201, 202]:
        st.success(
            f"Data successfully published! Status Code: {response.status_code}"
        )
      else:
        st.error(
            f"Failed to publish data. Server responded with status:"
            f" {response.status_code}"
        )
        st.text(response.text)
    except Exception as e:
      st.error(f"Connection error: {e}")
