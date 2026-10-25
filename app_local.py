import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Local Retail Analytics & Interactive API Hub", page_icon="📊", layout="wide")

st.title("📊 Local Interactive Analytics & API Testing Hub")
st.markdown("Upload your three key reports below to connect parameters, run local data analysis, and test API publishing interactively.")

st.sidebar.header("API Configuration & Testing")
api_url = st.sidebar.text_input("API Endpoint URL", value="https://httpbin.org/post", placeholder="https://api.example.com/v1/data")
api_token = st.sidebar.text_input("API Authorization Token (Optional)", type="password")

st.markdown("---")
st.subheader("📁 Step 1: Upload Your Three Report Files")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1. Overall Lead Report")
    lead_file = st.file_uploader("Upload Lead CSV", type=["csv"], key="lead_file_up")

with col2:
    st.markdown("### 2. Payment Mode Report")
    payment_file = st.file_uploader("Upload Payment CSV", type=["csv"], key="payment_file_up")

with col3:
    st.markdown("### 3. Sales Detail Report")
    sales_file = st.file_uploader("Upload Sales CSV", type=["csv"], key="sales_file_up")

if lead_file and payment_file and sales_file:
    try:
        @st.cache_data
        def load_data(l_f, p_f, s_f):
            leads = pd.read_csv(l_f)
            payments = pd.read_csv(p_f, skiprows=5, encoding="latin1")
            sales = pd.read_csv(s_f, skiprows=5, encoding="latin1")
            return leads, payments, sales

        leads_df, payments_df, sales_df = load_data(lead_file, payment_file, sales_file)
        st.success("✅ All three reports loaded successfully into memory!")

        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs(["Overview Metrics", "Sales Analysis", "Lead Insights", "API Publisher & Tester"])

        with tab1:
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Total Leads Recorded", len(leads_df))
            col_m2.metric("Total Sales Transactions", len(sales_df))
            col_m3.metric("Total Payment Records", len(payments_df))
            st.dataframe(sales_df.head(10), use_container_width=True)

        with tab2:
            st.markdown("### 🛍️ Sales Detail Filtering & Exploration")
            if "StoreName" in sales_df.columns:
                stores = ["All"] + list(sales_df["StoreName"].dropna().unique())
                selected_store = st.selectbox("Filter by Store Name", stores)
                filtered_sales = sales_df if selected_store == "All" else sales_df[sales_df["StoreName"] == selected_store]
            else:
                filtered_sales = sales_df
            st.dataframe(filtered_sales.head(50), use_container_width=True)

        with tab3:
            st.markdown("### 📋 Lead Generation & Business Unit Breakdown")
            if "Business Unit" in leads_df.columns:
                bus = ["All"] + list(leads_df["Business Unit"].dropna().unique())
                selected_bu = st.selectbox("Filter by Business Unit", bus)
                filtered_leads = leads_df if selected_bu == "All" else leads_df[leads_df["Business Unit"] == selected_bu]
            else:
                filtered_leads = leads_df
            st.dataframe(filtered_leads.head(50), use_container_width=True)

        with tab4:
            st.markdown("### 🚀 Interactive API Publishing & Payload Inspector")
            dataset_choice = st.selectbox("Select Dataset to Publish", ["Sales Dataset", "Lead Dataset", "Payment Dataset"])
            row_limit = st.slider("Select Number of Rows to Send in Payload", 1, 100, 10)
            target_df = sales_df if dataset_choice == "Sales Dataset" else (leads_df if dataset_choice == "Lead Dataset" else payments_df)
            payload_preview = target_df.head(row_limit).to_dict(orient="records")
            st.json(payload_preview[:2])

            if st.button("🚀 Send API Request Now"):
                if not api_url:
                    st.error("Please enter a valid API Endpoint URL.")
                else:
                    response = requests.post(api_url, json=payload_preview, headers={"Content-Type": "application/json"})
                    st.write(f"**Status Code:** `{response.status_code}`")
                    st.json(response.json())
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👆 Please upload all three required CSV files using the boxes above.")
