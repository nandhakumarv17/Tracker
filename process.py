import os
import pandas as pd
import requests

print('🚀 Starting data processing script...')

# File paths (make sure your CSV files are in the same folder)
lead_path = 'overall_lead_report_80_1792913172185.csv'
payment_path = 'PaymentModeReport-Abstract (10).csv'
sales_path = 'SalesReport-Detail-25_10_2026.csv'

# Check if files exist
for path in [lead_path, payment_path, sales_path]:
  if not os.path.exists(path):
    print(f'❌ Error: Could not find file -> {path}')
    exit()

print('📁 Loading datasets...')
leads_df = pd.read_csv(lead_path)
payments_df = pd.read_csv(payment_path, skiprows=5, encoding='latin1')
sales_df = pd.read_csv(sales_path, skiprows=5, encoding='latin1')

print('\n📊 --- DATA SUMMARY ---')
print(f'Total Leads Recorded: {len(leads_df)}')
print(f'Total Payment Records: {len(payments_df)}')
print(f'Total Sales Records: {len(sales_df)}')

# Example of analyzing/connecting parameters internally
if 'StoreName' in sales_df.columns:
  print('\n🛍️ Sales Breakdown by Store:')
  print(sales_df['StoreName'].value_counts())

if 'Business Unit' in leads_df.columns:
  print('\n📋 Leads Breakdown by Business Unit:')
  print(leads_df['Business Unit'].value_counts())

print('\n✅ Processing complete!')