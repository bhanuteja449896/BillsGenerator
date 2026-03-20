import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
import requests

def format_indian_date(date_str):
    """Convert date to Indian format: DD Mon YYYY without time"""
    try:
        # Try parsing different date formats
        for fmt in ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S']:
            try:
                date_obj = datetime.strptime(str(date_str).strip(), fmt)
                return date_obj.strftime('%d-%m-%Y')  # Return as DD-MM-YYYY (no time)
            except:
                pass
        # If no format matched, return as is
        return str(date_str).split()[0]  # Remove time if present
    except:
        return str(date_str).split()[0]

def amount_to_words(amount):
    """Convert amount to English words (Indian numbering system)"""
    try:
        amount = int(round(float(amount)))
        if amount == 0:
            return "Zero Rupees only"
        
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        def convert_below_hundred(num):
            if num == 0:
                return ''
            elif num < 10:
                return ones[num]
            elif num < 20:
                return teens[num - 10]
            else:
                return tens[num // 10] + (' ' + ones[num % 10] if num % 10 else '')
        
        def convert_below_thousand(num):
            if num == 0:
                return ''
            elif num < 100:
                return convert_below_hundred(num)
            else:
                result = ones[num // 100] + ' Hundred'
                if num % 100:
                    result += ' ' + convert_below_hundred(num % 100)
                return result
        
        crores = amount // 10000000
        remainder = amount % 10000000
        lakhs = remainder // 100000
        remainder = remainder % 100000
        thousands = remainder // 1000
        remainder = remainder % 1000
        
        words = []
        if crores > 0:
            words.append(convert_below_hundred(crores) + ' Crore')
        if lakhs > 0:
            words.append(convert_below_hundred(lakhs) + ' Lakh')
        if thousands > 0:
            words.append(convert_below_hundred(thousands) + ' Thousand')
        if remainder > 0:
            words.append(convert_below_thousand(remainder))
        
        return ' '.join(words).strip() + ' Rupees only'
    except:
        return f"{amount} Rupees only"

# ============================================
# HARDCODED COMPANY DETAILS (2 COMPANIES)
# ============================================
COMPANIES = {
    "SREEDEVI TYRES": {
        'name': 'SREEDEVI TYRES',
        'address': 'SHOP NO 6 ,7 and 8 D NO 10-29-A RAJEEV NAGAR COLONY OPP BHASKAR GODOWNS , GOOTY ROAD , VADIYAMPETA POST ANANTAPUR',
        'phone': '9177336057',
        'email': 'satya.mba86@gmail.com',
        'gstin': '37ADYFS6878D1Z3',
        'state': '37-Andhra Pradesh'
    },
    "BHANU KIRAN TYRES": {
        'name': 'BHANU KIRAN TYRES',
        'address': '4-88 NEAR CHANDANA RAILWAY GATE, MAIN ROAD RAYALACHERUVU, YADIKI MANDAL',
        'phone': '8466884486',
        'email': 'satya.mba86@gmail.com',
        'gstin': '37AASFB0805G1ZJ',
        'state': '37-Andhra Pradesh'
    }
}

def get_gst_details(gstin):
    """Fetch GST details using multiple API attempts"""
    try:
        gstin = str(gstin).strip()
        
        # Try Method 1: Masters India API
        try:
            url = f"https://commonapi.mastersindia.com/CommonApi/rest/gst?gstnum={gstin}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('flag') == True or data.get('Status') == True:
                    ent = data.get('data', {}).get('EntireData', {})
                    if ent:
                        address = ent.get('AdditionalFields', {}).get('Address')
                        state = ent.get('AdditionalFields', {}).get('State')
                        if address and state:
                            return {'address': address, 'state': state}
                    # Try alternate keys
                    if 'AdditionalFields' in ent:
                        for key in ent.get('AdditionalFields', {}):
                            if 'address' in key.lower():
                                addr = ent['AdditionalFields'].get(key)
                                if addr:
                                    return {'address': addr, 'state': 'Andhra Pradesh'} # Default state
        except:
            pass
        
        # Try Method 2: Alternative GSTIN endpoint
        try:
            url = f"https://api.gstvalidator.com/v2/gst/validate?gstin={gstin}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('valid') or data.get('flag'):
                    business_details = data.get('data', {})
                    address = business_details.get('address') or business_details.get('tradeName')
                    state = business_details.get('state') or business_details.get('stateCode')
                    if address:
                        return {'address': address, 'state': state if state else 'Andhra Pradesh'}
        except:
            pass
        
        # Try Method 3: Simple fallback with state extraction from GSTIN
        try:
            # GSTIN format: 2-digit state code at position 0-1
            state_codes = {
                '37': 'Andhra Pradesh', '36': 'Telangana', '18': 'Chhattisgarh',
                '10': 'Bihar', '04': 'Assam', '12': 'Goa', '27': 'Delhi',
                '06': 'Delhi', '30': 'Gujarat', '40': 'Haryana', '32': 'Himachal Pradesh',
                '01': 'Jharkhand', '02': 'Odisha', '05': 'Punjab', '08': 'Rajasthan',
                '09': 'Tamil Nadu', '33': 'Karnataka', '19': 'Karnataka'
            }
            state_code = gstin[:2]
            state = state_codes.get(state_code, 'Andhra Pradesh')
            
            # Return with N/A for address but correct state
            return {'address': 'N/A', 'state': state}
        except:
            pass
            
    except:
        pass
    
    return None

def generate_pdf(company_details, invoice_data):
    """Generate professional PDF matching SREEDEVI TYRES exact format"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Register Unicode-supporting font
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Use rupee function
    def rupee(amount):
        """Format amount with rupee symbol"""
        return f"Rs. {amount:,.2f}"
    
    y_pos = height - 0.4*inch
    
    # ==================== COMPANY HEADER ====================
    c.setFont("Helvetica-Bold", 14)
    c.drawString(0.5*inch, y_pos, company_details['name'])
    
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 8)
    
    # Wrap address to multiple lines (max 80 chars per line)
    address = company_details['address']
    max_len = 80
    address_lines = []
    while len(address) > max_len:
        address_lines.append(address[:max_len])
        address = address[max_len:]
    if address:
        address_lines.append(address)
    
    for line in address_lines:
        c.drawString(0.5*inch, y_pos, line)
        y_pos -= 0.15*inch
    
    y_pos -= 0.05*inch
    c.drawString(0.5*inch, y_pos, f"Email: {company_details['email']}")
    
    y_pos -= 0.15*inch
    c.drawString(0.5*inch, y_pos, f"GSTIN: {company_details['gstin']}")
    
    y_pos -= 0.15*inch
    c.drawString(0.5*inch, y_pos, f"State: {company_details['state']}")
    
    # Horizontal line
    y_pos -= 0.15*inch
    c.setLineWidth(0.5)
    c.line(0.5*inch, y_pos, 7.5*inch, y_pos)
    
    # ==================== TAX INVOICE TITLE ====================
    y_pos -= 0.25*inch
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor('#8B7AB8'))
    c.drawCentredString(4.25*inch, y_pos, "Tax Invoice")
    c.setFillColor(colors.black)
    
    # ==================== BILL TO & INVOICE DETAILS ====================
    y_pos -= 0.35*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5*inch, y_pos, "Bill To")
    c.drawRightString(7.5*inch, y_pos, "Invoice Details")
    
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 9)
    c.drawString(0.5*inch, y_pos, invoice_data['party_name'])
    c.drawRightString(7.5*inch, y_pos, f"Invoice No.: {invoice_data['invoice_number']}")
    
    y_pos -= 0.15*inch
    # Wrap customer address
    cust_address = invoice_data.get('party_address', 'N/A')
    cust_addr_lines = []
    max_addr_len = 55
    while len(cust_address) > max_addr_len:
        cust_addr_lines.append(cust_address[:max_addr_len])
        cust_address = cust_address[max_addr_len:]
    if cust_address:
        cust_addr_lines.append(cust_address)
    
    for i, line in enumerate(cust_addr_lines[:2]):  # Max 2 lines
        c.drawString(0.5*inch, y_pos, line)
        if i == 0:
            c.drawRightString(7.5*inch, y_pos, f"Date: {invoice_data['date']}")
        y_pos -= 0.15*inch
    
    c.drawString(0.5*inch, y_pos, f"GSTIN Number: {invoice_data['customer_gstin']}")
    y_pos -= 0.15*inch
    c.drawString(0.5*inch, y_pos, f"State: {invoice_data.get('customer_state', 'N/A')}")
    c.drawRightString(7.5*inch, y_pos, f"Place of Supply: {company_details['state']}")
    
    # ==================== ITEMS TABLE ====================
    y_pos -= 0.3*inch
    
    # Table header with purple background
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor('#8B7AB8'))
    c.rect(0.5*inch, y_pos - 0.2*inch, 7*inch, 0.2*inch, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    headers = ['#', 'Item name', 'HSN/ SAC', 'Quantity', 'Price/ unit', 'GST', 'Amount']
    col_x = [0.6*inch, 1.1*inch, 2.2*inch, 3.2*inch, 4.3*inch, 5.5*inch, 6.5*inch]
    
    for i, header in enumerate(headers):
        if i == 1:  # Item name - left aligned
            c.drawString(col_x[i], y_pos - 0.13*inch, header)
        else:
            c.drawRightString(col_x[i] + 0.3*inch, y_pos - 0.13*inch, header)
    
    y_pos -= 0.25*inch
    
    # Item row
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8)
    
    qty = int(invoice_data['quantity'])
    gst_percent = int(invoice_data['percent'])
    total_amount_inclusive = float(invoice_data['amount'])
    
    # Calculate base amount and GST from inclusive amount
    # Formula: Base = Total / (1 + GST%/100)
    divisor = 1 + (gst_percent / 100)
    base_amount = total_amount_inclusive / divisor
    total_gst_amount = total_amount_inclusive - base_amount
    rate = base_amount / qty if qty > 0 else 0
    
    c.drawCentredString(col_x[0], y_pos - 0.1*inch, "1")
    c.drawString(col_x[1], y_pos - 0.1*inch, invoice_data['item_name'][:25])
    c.drawCentredString(col_x[2], y_pos - 0.1*inch, "")
    c.drawCentredString(col_x[3], y_pos - 0.1*inch, str(qty))
    c.drawRightString(col_x[4] + 0.3*inch, y_pos - 0.1*inch, rupee(rate))
    # GST with better spacing - separate lines
    c.drawRightString(col_x[5] + 0.25*inch, y_pos - 0.06*inch, rupee(total_gst_amount))
    c.setFont("Helvetica", 7)
    c.drawRightString(col_x[5] + 0.25*inch, y_pos - 0.13*inch, f"({gst_percent}%)")
    c.setFont("Helvetica", 8)
    c.drawRightString(col_x[6] + 0.45*inch, y_pos - 0.1*inch, rupee(total_amount_inclusive))
    
    y_pos -= 0.22*inch
    
    # Total row
    c.setFont("Helvetica-Bold", 8)
    c.drawString(col_x[1], y_pos - 0.1*inch, "Total")
    c.drawCentredString(col_x[3], y_pos - 0.1*inch, str(qty))
    c.drawRightString(col_x[5] + 0.3*inch, y_pos - 0.1*inch, rupee(total_gst_amount))
    c.drawRightString(col_x[6] + 0.3*inch, y_pos - 0.1*inch, rupee(total_amount_inclusive))
    
    # ==================== SUMMARY SECTION ====================
    y_pos -= 0.4*inch
    
    # Left side - Amount in words
    c.setFont("Helvetica", 8)
    c.drawString(0.5*inch, y_pos, "Invoice Amount In Words")
    y_pos -= 0.15*inch
    
    c.setFont("Helvetica-Bold", 9)
    amount_words = amount_to_words(total_amount_inclusive)
    c.drawString(0.5*inch, y_pos, amount_words)
    
    y_pos -= 0.2*inch
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.5*inch, y_pos, "Terms And Conditions")
    y_pos -= 0.13*inch
    c.setFont("Helvetica", 8)
    c.drawString(0.5*inch, y_pos, "Thank you for doing business with us.")
    
    # Right side - Amounts (with better spacing)
    summary_y = y_pos + 0.4*inch
    c.setFont("Helvetica", 9)
    
    c.drawString(4.5*inch, summary_y, "Sub Total")
    c.drawRightString(7.3*inch, summary_y, rupee(base_amount))
    
    summary_y -= 0.2*inch
    c.drawString(4.5*inch, summary_y, "SGST@9.0%")
    sgst = total_gst_amount / 2
    c.drawRightString(7.3*inch, summary_y, rupee(sgst))
    
    summary_y -= 0.18*inch
    c.drawString(4.5*inch, summary_y, "CGST@9.0%")
    cgst = total_gst_amount / 2
    c.drawRightString(7.3*inch, summary_y, rupee(cgst))
    
    summary_y -= 0.2*inch
    # Total box
    c.setFillColor(colors.HexColor('#8B7AB8'))
    c.rect(4.4*inch, summary_y - 0.18*inch, 2.9*inch, 0.2*inch, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(4.5*inch, summary_y - 0.11*inch, "Total")
    c.drawRightString(7.2*inch, summary_y - 0.11*inch, rupee(total_amount_inclusive))
    
    summary_y -= 0.4*inch
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawString(4.5*inch, summary_y, "Received")
    c.drawRightString(7.3*inch, summary_y, rupee(total_amount_inclusive))
    
    summary_y -= 0.18*inch
    c.drawString(4.5*inch, summary_y, "Balance")
    c.drawRightString(7.3*inch, summary_y, "Rs. 0.00")
    
    # ==================== FOOTER - COMPANY NAME AT BOTTOM ====================
    footer_y = 0.5*inch
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(7.5*inch, footer_y, f"For: {company_details['name']}")
    
    footer_y -= 0.35*inch
    c.setFont("Helvetica", 8)
    c.drawCentredString(4.25*inch, footer_y, "Authorized Signatory")
    
    c.save()
    buffer.seek(0)
    return buffer

# ============================================
# STREAMLIT APP
# ============================================
st.set_page_config(page_title="Bill PDF Generator", layout="wide")
st.title("📄 Professional Bill PDF Generator")

# Initialize session state
if 'generated_pdfs' not in st.session_state:
    st.session_state.generated_pdfs = None

# Company selection dropdown
st.markdown("### 🏢 Select Your Company")
selected_company = st.selectbox("Choose Company:", list(COMPANIES.keys()))
company = COMPANIES[selected_company]

st.info(f"✅ Selected: **{company['name']}** | GSTIN: {company['gstin']}")

# File upload
st.markdown("### 📊 Upload Excel File")
st.write("**Excel Format (in this exact order, skip first row):**")
st.code("Date | Party name | Item Name | Quantity | Invoice number | GST number | Amount | Percent")

uploaded_file = st.file_uploader("Choose Excel file (.xlsx or .csv)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # Read Excel - skip first row (headers)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=1, header=None)
        else:
            df = pd.read_excel(uploaded_file, skiprows=1, header=None)
        
        # Expected columns in order: Date, Party name, Item Name, Quantity, Invoice number, GST number, Amount, Percent, Address, State
        df.columns = ['date', 'party_name', 'item_name', 'quantity', 'invoice_number', 'customer_gstin', 'amount', 'percent', 'address', 'state']
        
        st.markdown("### 📋 Preview of Data")
        st.dataframe(df, use_container_width=True)
        
        st.markdown(f"**Total Records:** {len(df)}")
        
        if st.button("🚀 Generate All PDFs"):
            # Initialize session state for PDFs
            st.session_state.generated_pdfs = None
            progress_bar = st.progress(0)
            status_text = st.empty()
            error_list = []
            pdfs = []
            
            for idx, row in df.iterrows():
                try:
                    status_text.text(f"⏳ Processing {idx + 1}/{len(df)}...")
                    
                    # Use address and state from Excel columns
                    invoice_data = {
                        'date': format_indian_date(str(row['date'])),
                        'party_name': str(row['party_name']),
                        'item_name': str(row['item_name']),
                        'quantity': int(row['quantity']),
                        'invoice_number': str(row['invoice_number']),
                        'customer_gstin': str(row['customer_gstin']),
                        'amount': float(row['amount']),
                        'percent': int(row['percent']),
                        'party_address': str(row['address']).strip() if pd.notna(row['address']) else 'N/A',
                        'customer_state': str(row['state']).strip() if pd.notna(row['state']) else 'N/A'
                    }
                    
                    pdf_buffer = generate_pdf(company, invoice_data)
                    # Use party name, invoice number, and date for filename
                    party_name = str(row['party_name']).replace('/', '-').replace('\\', '-').strip()
                    invoice_no = str(row['invoice_number']).strip()
                    filename = f"{party_name}_{invoice_no}_{invoice_data['date']}.pdf"
                    pdfs.append((filename, pdf_buffer))
                    
                except Exception as e:
                    error_list.append(f"Row {idx + 1}: {str(e)}")
                
                progress_bar.progress((idx + 1) / len(df))
            
            # Store PDFs in session state to prevent reload
            st.session_state.generated_pdfs = pdfs
            
            # Show status
            if error_list:
                st.warning(f"⚠️ Completed with {len(error_list)} errors:")
                for error in error_list:
                    st.caption(f"❌ {error}")
            else:
                st.success(f"✅ Successfully generated {len(pdfs)} PDFs!")
        
        # Display downloaded PDFs from session state (no need to regenerate)
        if hasattr(st.session_state, 'generated_pdfs') and st.session_state.generated_pdfs:
            pdfs = st.session_state.generated_pdfs
            st.markdown("---")
            st.markdown("### 📥 Download Your PDFs")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Total PDFs:** {len(pdfs)}")
            
            # Display all download buttons
            cols = st.columns(2)
            for col_idx, (filename, pdf_buffer) in enumerate(pdfs):
                with cols[col_idx % 2]:
                    st.download_button(
                        label=f"📄 {filename}",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        key=f"download_{col_idx}_{filename}"
                    )
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("**Please ensure your Excel has columns in this exact order:**")
        st.code("Date | Party name | Item Name | Quantity | Invoice number | GST number | Amount | Percent | Address | State")

# Footer info
st.markdown("---")
st.markdown("""
### ℹ️ How to Use:
1. **Select your company** from the dropdown
2. **Prepare Excel file** with columns in exact order (skip first row - headers)
3. **Upload the file** and preview data
4. **Click "Generate All PDFs"** to create bills
5. **Download generated PDFs** individually

### 📝 Excel Format Requirements:
- **Column Order:** Date | Party name | Item Name | Quantity | Invoice number | GST number | Amount | Percent
- **Skip first row** (it's automatically skipped)
- **Date Format:** YYYY-MM-DD or DD-MM-YYYY
- **Amount:** Numeric value (rupees)
- **Percent:** GST percentage (e.g., 9, 12, 18)

### 🔍 GST Auto-Lookup:
- GST numbers are looked up automatically to fetch customer address and state
- If lookup fails, "N/A" is used
""")
