# Bill PDF Generator - Professional Invoice Creator

A web-based application to automatically generate professional PDF invoices/bills with automatic GST calculations.

## ✨ Features

✅ **2 Companies Pre-configured** - SREEDEVI TYRES & BHANU KIRAN TYRES  
✅ **Simple Company Selection** - Just choose which company to use  
✅ **Automatic GST Calculation** - Split GST (SGST 9% + CGST 9%) calculated automatically  
✅ **Excel Bulk Import** - Generate PDFs from Excel data  
✅ **GST Auto-Lookup** - Customer address & state auto-fetched from GST number  
✅ **Professional PDFs** - Exact layout matching your invoice format  
✅ **No Logos** - Clean design  
✅ **Rupee Symbols (₹)** - All amounts properly formatted  

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start the App
```bash
streamlit run app.py
```

Or simply click: `run.bat`

## 📖 How to Use

### Step 1: Select Company  
Choose between SREEDEVI TYRES or BHANU KIRAN TYRES - details auto-fill!

### Step 2: Prepare Excel File

Create Excel with these columns (IN THIS EXACT ORDER):

| Date | Party name | Item Name | Quantity | Invoice number | Gst number | amount | percent |
|------|---------|---------|---------|---------|---------|---------|---------|
| 22-01-2026 | SS logistics | 295-90-R20 S3P4 | 4 | 41 | 37CDGPT4792P1ZF | 85593.22 | 18 |

**IMPORTANT:**
- ✅ **First row is headers - automatically skipped**
- ✅ Column order MUST be exactly as shown
- ✅ GST% in `percent` column (9, 12, 18, etc.)
- ✅ `amount` is total BEFORE GST

### Step 3: Generate PDFs
1. Upload Excel  
2. Click "🚀 Generate All PDFs"
3. Download PDFs

## 💼 Pre-configured Companies

### SREEDEVI TYRES
- Phone: 9177336057
- GSTIN: 37ADYFS6878D1Z3

### BHANU KIRAN TYRES  
- Phone: 8466884486
- GSTIN: 37AASFB0805G1ZJ

## 📝 Excel Column Details

1. **Date** - DD-MM-YYYY or YYYY-MM-DD
2. **Party name** - Customer name
3. **Item Name** - Product description
4. **Quantity** - Number  
5. **Invoice number** - Invoice ID
6. **Gst number** - Customer GSTIN
7. **amount** - Total before GST (₹)
8. **percent** - GST% (9, 12, 18)

## 📄 PDF Output

Each PDF includes:
- Company header
- Tax Invoice title  
- Bill To (customer details)
- Items table
- Tax calculation (SGST + CGST)
- Payment status
- Signature line

## 🔍 GST Auto-Lookup

Automatically fetches from GST number:
- Customer name
- Customer address
- Customer state

## 💻 Requirements

- Python 3.8+
- Dependencies: streamlit, pandas, reportlab, openpyxl

## 📊 Calculations

```
Sub Total = amount (from Excel)
SGST = amount × 9%
CGST = amount × 9%
Total = amount + SGST + CGST
```

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "Error processing file" | Check column order matches exactly |
| No data shows | First row should be headers (auto-skipped) |
| PDFs not generating | Check amounts are numeric values |

## 📁 Files

```
BillsGenerator/
├── app.py                # Main app
├── requirements.txt      # Dependencies  
├── create_sample.py      # Sample generator
├── run.bat              # Quick start
├── sample_data.xlsx     # Template
└── README.md            # This file
```

## 🎉 Ready to Go!

Your invoice generator is ready! Create your Excel file using the sample template and start generating professional PDFs instantly! 📄✨
