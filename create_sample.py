import pandas as pd

# Create sample Excel file with CORRECT format (skip first row as headers)
data = {
    'Date': ['22-01-2026', '23-01-2026', '24-01-2026'],
    'Party name': ['SS logistics', 'ABC Trading', 'XYZ Enterprises'],
    'Item Name': ['295-90-R20 S3P4', 'Tube 100-90-R20', 'Tyre 80-100-R17'],
    'Quantity': [4, 2, 3],
    'Invoice number': [41, 42, 43],
    'Gst number': ['37CDGPT4792P1ZF', '37ABCDE1234F5Z1', '37XYZPQ5678R9Z2'],
    'amount': [85593.22, 50000.00, 60000.00],
    'percent': [18, 9, 12]
}

df = pd.DataFrame(data)
df.to_excel('sample_data.xlsx', index=False, sheet_name='Invoices')
print("✅ Sample Excel file created: sample_data.xlsx")
print("\nPreview (First row is headers - will be skipped):")
print(df)
