import os
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Excel Data Analyzer & Publisher", page_icon="📊", layout="wide"
)

st.title("📊 Excel Data Analyzer & API Publisher")
st.markdown(
    "Upload your Excel file for automated analysis, view key metrics, and"
    " publish the processed data to your external API endpoint."
)

# Sidebar configuration for API publishing
st.sidebar.header("API Configuration")
api_url = st.sidebar.text_input(
    "API Endpoint URL", placeholder="https://api.example.com/v1/data"
)
api_token = st.sidebar.text_input(
    "API Authorization Token (Optional)", type="password"
)

# File uploader widget
uploaded_file = st.file_uploader(
    "Choose an Excel file", type=["xlsx", "xls"]
)

if uploaded_file is not None:
  try:
    # Read Excel file
    excel_data = pd.ExcelFile(uploaded_file)
    sheet_names = excel_data.sheet_names

    selected_sheet = st.selectbox("Select Worksheet", sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    st.success(
        f"Successfully loaded '{selected_sheet}' with {df.shape[0]} rows and"
        f" {df.shape[1]} columns."
    )

    # Data Preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # Quick Analysis Metrics
    st.subheader("📈 Quick Analysis")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Missing Values", int(df.isna().sum().sum()))

    # Numeric Summary
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
      st.subheader("📊 Statistical Summary")
      st.dataframe(df[numeric_cols].describe(), use_container_width=True)

    # Data Publishing Section
    st.markdown("---")
    st.subheader("🚀 Publish Data via API")

    if st.button("Publish Data"):
      if not api_url:
        st.error("Please enter a valid API Endpoint URL in the sidebar.")
      else:
        with st.spinner("Publishing data to endpoint..."):
          # Convert DataFrame rows to JSON records payload
          payload = df.to_dict(orient="records")
          headers = {"Content-Type": "application/json"}
          if api_token:
            headers["Authorization"] = f"Bearer {api_token}"

          try:
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code in [200, 201, 202]:
              st.success(
                  f"Data published successfully! Status Code:"
                  f" {response.status_code}"
              )
              try:
                st.json(response.json())
              except Exception:
                st.write(response.text)
            else:
              st.error(
                  f"Failed to publish data. Status Code: {response.status_code}"
              )
              st.text(response.text)
          except Exception as e:
            st.error(f"Connection error: {e}")

  except Exception as e:
    st.error(f"Error reading the Excel file: {e}")
else:
  st.info("Please upload an Excel file (.xlsx or .xls) to begin.")
