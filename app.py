import os
import shutil

# --- Self-healing fix for Render/Git .streamlit file conflicts ---
if os.path.exists(".streamlit"):
  if not os.path.isdir(".streamlit"):
    os.remove(".streamlit")
  else:
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path) and not os.path.isfile(secrets_path):
      shutil.rmtree(secrets_path, ignore_errors=True)

os.makedirs(".streamlit", exist_ok=True)
config_path = ".streamlit/config.toml"
with open(config_path, "w") as f:
  f.write(
      "[server]\n"
      "headless = true\n"
      "enableCORS = false\n"
      "enableXsrfProtection = false\n"
      "port = 10000\n"
      'address = "0.0.0.0"\n'
  )
# ---------------------------------------------------------------

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Retail & Lead Multi-Report Analytics Hub",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Retail Sales, Leads & Payment Multi-Report Analytics Hub")
st.markdown(
    "Upload your three report files below to connect parameters, run"
    " analytics, and publish data via API."
)

# Sidebar for API configuration
st.sidebar.header("API Publication Settings")
api_url = st.sidebar.text_input(
    "API Endpoint URL", placeholder="https://api.example.com/v1/data"
)
api_token = st.sidebar.text_input(
    "API Authorization Token (Optional)", type="password"
)

# Three Separate Upload Windows
st.markdown("---")
st.subheader("📁 Step 1: Upload Your Three Report Files")

col1, col2, col3 = st.columns(3)

with col1:
  st.markdown("### 1. Overall Lead Report")
  lead_file = st.file_uploader("Upload Lead CSV", type=["csv"], key="lead_up")

with col2:
  st.markdown("### 2. Payment Mode Report")
  payment_file = st.file_uploader(
      "Upload Payment CSV", type=["csv"], key="payment_up"
  )

with col3:
  st.markdown("### 3. Sales Detail Report")
  sales_file = st.file_uploader(
      "Upload Sales CSV", type=["csv"], key="sales_up"
  )

# Check if all files are uploaded
if lead_file and payment_file and sales_file:
  try:

    @st.cache_data
    def load_uploaded_data(l_file, p_file, s_file):
      leads = pd.read_csv(l_file)
      payments = pd.read_csv(p_file, skiprows=5, encoding="latin1")
      sales = pd.read_csv(s_file, skiprows=5, encoding="latin1")
      return leads, payments, sales

    leads_df, payments_df, sales_df = load_uploaded_data(
        lead_file, payment_file, sales_file
    )
    st.success("All three reports uploaded and loaded successfully!")

    st.markdown("---")
    st.subheader(
        "🔍 Step 2: Interactive Analysis & Parameter Cross-Matching"
    )

    tab1, tab2, tab3 = st.tabs(
        ["Overview Metrics", "Sales Analysis", "Lead & Payment Insights"]
    )

    with tab1:
      col_m1, col_m2, col_m3 = st.columns(3)
      col_m1.metric("Total Leads Recorded", len(leads_df))
      col_m2.metric("Total Sales Transactions", len(sales_df))
      col_m3.metric("Total Payment Records", len(payments_df))

      st.markdown("---")
      st.subheader("💡 Quick Preview of Sales Dataset")
      cols_to_show = [
          col
          for col in [
              "BillDate",
              "BillNumber",
              "CustomerName",
              "ProductName",
              "MRP",
              "StoreName",
          ]
          if col in sales_df.columns
      ]
      st.dataframe(sales_df[cols_to_show].head(10), use_container_width=True)

    with tab2:
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

    with tab3:
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
    st.subheader("🚀 Step 3: Publish Dataset via API")
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
        payload_sample = target_df.head(100).to_dict(orient="records")

        headers = {"Content-Type": "application/json"}
        if api_token:
          headers["Authorization"] = f"Bearer {api_token}"

        try:
          response = requests.post(api_url, json=payload_sample, headers=headers)
          if response.status_code in [200, 201, 202]:
            st.success(
                f"Data successfully published! Status Code:"
                f" {response.status_code}"
            )
          else:
            st.error(
                f"Failed to publish data. Server responded with status:"
                f" {response.status_code}"
            )
            st.text(response.text)
        except Exception as e:
          st.error(f"Connection error: {e}")

  except Exception as e:
    st.error(f"Error processing uploaded files: {e}")
else:
  st.info(
      "👆 Please upload all three required CSV files using the boxes above to"
      " begin the analysis and publishing workflow."
  )
