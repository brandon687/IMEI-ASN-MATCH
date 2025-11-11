import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from google_sheets_auth import get_google_sheets_client
from database import (
    init_database,
    create_or_update_reconciliation,
    get_all_reconciliations,
    clear_asn_data,
    clear_all_asn_data,
    clear_imei_serial_data,
    get_order_statistics,
    get_database_engine,
    archive_order,
    get_all_archived_orders,
    get_archived_order,
    delete_archived_order
)
from datetime import datetime
from imei_extractor import extract_imeis_from_file, format_imeis_for_display

# Page configuration
st.set_page_config(
    page_title="IMEI/ASN Match",
    page_icon="🔢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Custom CSS
st.markdown("""
<style>
    /* Main theme colors and responsive base */
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --success-color: #06D6A0;
        --warning-color: #F18F01;
        --danger-color: #C73E1D;
        --bg-color: #F8F9FA;
        --card-bg: #FFFFFF;
        --text-primary: #212529;
        --text-secondary: #6C757D;
        --border-color: #DEE2E6;
    }

    /* Responsive typography */
    h1 { font-size: clamp(1.5rem, 2.5vw, 2.5rem); }
    h2 { font-size: clamp(1.25rem, 2vw, 2rem); }
    h3 { font-size: clamp(1.1rem, 1.5vw, 1.5rem); }
    h4 { font-size: clamp(0.95rem, 1.2vw, 1.25rem); }
    p { font-size: clamp(0.875rem, 1vw, 1rem); }

    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Stats cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .stat-card h3 {
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        margin: 0 0 0.5rem 0;
        letter-spacing: 0.5px;
    }

    .stat-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    /* Order cards */
    .order-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
        transition: all 0.2s;
    }

    .order-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        border-color: var(--primary-color);
    }

    .order-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--bg-color);
    }

    .order-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0;
    }

    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-complete {
        background: #D1FAE5;
        color: #065F46;
    }

    .status-partial {
        background: #FEF3C7;
        color: #92400E;
    }

    .status-pending {
        background: #DBEAFE;
        color: #1E40AF;
    }

    /* Compact Buttons */
    .stButton > button {
        border-radius: 3px;
        font-weight: 600;
        border: none;
        padding: 0.15rem 0.4rem;
        transition: all 0.2s;
        font-size: 9px;
        line-height: 1.2;
        height: auto;
        min-height: 20px;
        text-transform: uppercase;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }

    /* Download buttons specifically */
    .stDownloadButton > button {
        border-radius: 3px;
        font-weight: 600;
        border: none;
        padding: 0.15rem 0.4rem;
        font-size: 9px;
        line-height: 1.2;
        height: auto;
        min-height: 20px;
        text-transform: uppercase;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stButton > button,
        .stDownloadButton > button {
            font-size: 11px;
            padding: 0.25rem 0.6rem;
            min-height: 28px;
        }
    }

    /* Large screen adjustments */
    @media (min-width: 2560px) {
        .stButton > button,
        .stDownloadButton > button {
            font-size: 10px;
            padding: 0.2rem 0.5rem;
            min-height: 24px;
        }
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 1rem 2rem;
        font-weight: 600;
        border: 2px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--bg-color);
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
    }

    /* Responsive DataFrames */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Compact table styling - reduce cell padding and spacing */
    .stDataFrame table {
        font-size: clamp(0.75rem, 0.9vw, 0.95rem);
    }

    .stDataFrame th, .stDataFrame td {
        padding: clamp(0.2rem, 0.4vw, 0.5rem) clamp(0.3rem, 0.5vw, 0.75rem) !important;
        white-space: nowrap;
    }

    .stDataFrame thead th {
        padding: clamp(0.3rem, 0.5vw, 0.6rem) clamp(0.3rem, 0.5vw, 0.75rem) !important;
        font-weight: 600;
    }

    /* Mobile table adjustments */
    @media (max-width: 768px) {
        .stDataFrame table {
            font-size: 0.75rem;
        }
        .stDataFrame th, .stDataFrame td {
            padding: 0.25rem 0.4rem !important;
        }
    }

    /* Large screen table adjustments */
    @media (min-width: 2560px) {
        .stDataFrame table {
            font-size: 1rem;
        }
        .stDataFrame th, .stDataFrame td {
            padding: 0.5rem 0.75rem !important;
        }
    }

    /* File uploader */
    .stFileUploader {
        background: white;
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 2rem;
    }

    /* Expander/Accordion styling for breakdowns */
    [data-testid="stExpander"] {
        border: none;
        margin-bottom: 1rem;
    }

    [data-testid="stExpander"] summary {
        background: white;
        border: 2px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s;
        cursor: pointer;
    }

    [data-testid="stExpander"] summary:hover {
        border-color: var(--primary-color);
        background: var(--bg-color);
    }

    [data-testid="stExpander"][open] summary {
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
        border-color: var(--primary-color);
        background: var(--bg-color);
    }

    [data-testid="stExpander"] > div:last-child {
        border: 2px solid var(--primary-color);
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        background: white;
    }

    /* Mobile expander adjustments */
    @media (max-width: 768px) {
        [data-testid="stExpander"] summary {
            font-size: 0.9rem;
            padding: 0.75rem 1rem;
        }
    }

    /* Large screen expander adjustments */
    @media (min-width: 2560px) {
        [data-testid="stExpander"] summary {
            font-size: 1.1rem;
            padding: 1.25rem 2rem;
        }
    }

    /* Alerts */
    .stAlert {
        border-radius: 8px;
        border: none;
        padding: 1rem 1.5rem;
    }

    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .info-box h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }

    /* Metric improvements */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }

    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid var(--border-color);
    }
</style>
""", unsafe_allow_html=True)

# Constants
SHEET_ID = "1Jz7HV0Jjad6NVvlomUdydjysaCTJcA-CUu7cVacMwFg"
WORKSHEET_GID = "1072853082"

@st.cache_data(ttl=300)
def load_data_from_sheets():
    """Load data from Google Sheets"""
    try:
        client = get_google_sheets_client()
        spreadsheet = client.open_by_key(SHEET_ID)

        worksheet = spreadsheet.get_worksheet_by_id(int(WORKSHEET_GID))
        all_values = worksheet.get_all_values()

        if len(all_values) < 3:
            return None, "Not enough rows in the spreadsheet"

        headers_row1 = all_values[0]
        headers_row2 = all_values[1]

        if 'INVOICE' in headers_row2:
            headers = headers_row2
            data_start_index = 2
        elif 'INVOICE' in headers_row1:
            headers = headers_row1
            data_start_index = 1
        else:
            return None, "Could not find INVOICE column"

        cleaned_headers = []
        for i, header in enumerate(headers):
            header = str(header).strip()
            if header == '':
                header = f'Unnamed_{i}'
            base_header = header
            counter = 1
            while header in cleaned_headers:
                header = f'{base_header}_{counter}'
                counter += 1
            cleaned_headers.append(header)

        headers = cleaned_headers

        required_columns = ['INVOICE', 'MODEL', 'CAPACITY', 'GRADE', 'QTY']
        missing_columns = [col for col in required_columns if col not in headers]

        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"

        data = all_values[data_start_index:]
        df = pd.DataFrame(data, columns=headers)
        df = df[df['INVOICE'].str.strip() != '']
        df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce').fillna(0).astype(int)

        return df, None
    except Exception as e:
        return None, str(e)

def clean_model_name(model):
    """Clean model name by removing 'IPHONE' prefix"""
    if pd.isna(model):
        return ""
    model = str(model).strip()
    if model.upper().startswith('IPHONE '):
        model = model[7:].strip()
    return model

def process_selected_orders(df, selected_invoices):
    """Process selected invoices and generate output tables"""
    filtered_df = df[df['INVOICE'].isin(selected_invoices)].copy()

    if filtered_df.empty:
        return None, None, None

    filtered_df['CLEAN_MODEL'] = filtered_df['MODEL'].apply(clean_model_name)

    model_gb_df = filtered_df.groupby(['CLEAN_MODEL', 'CAPACITY'], as_index=False)['QTY'].sum()
    model_gb_df['MODEL_GB'] = model_gb_df['CLEAN_MODEL'] + ' ' + model_gb_df['CAPACITY']
    model_gb_output = model_gb_df[['MODEL_GB', 'QTY']].sort_values('MODEL_GB', ascending=True)

    model_only_df = filtered_df.groupby('CLEAN_MODEL', as_index=False)['QTY'].sum()
    model_only_df.columns = ['MODEL', 'QTY']
    model_only_output = model_only_df.sort_values('MODEL', ascending=True)

    grade_mix_df = filtered_df.groupby(['MODEL', 'CAPACITY', 'GRADE'], as_index=False)['QTY'].sum()
    grade_mix_output = grade_mix_df[['MODEL', 'CAPACITY', 'GRADE', 'QTY']].sort_values(['MODEL', 'CAPACITY', 'GRADE'], ascending=True)

    return model_gb_output, model_only_output, grade_mix_output

def create_copy_button(df, button_id):
    """Create a client-side copy to clipboard button"""
    tsv = df.to_csv(sep='\t', index=False)
    escaped_data = tsv.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

    html = f"""
    <button id="{button_id}" style="
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 0.15rem 0.4rem;
        border-radius: 3px;
        cursor: pointer;
        font-size: 9px;
        font-weight: 600;
        transition: all 0.2s;
        width: 100%;
        height: auto;
        min-height: 20px;
        line-height: 1.2;
    " onmouseover="this.style.backgroundColor='#246A87'" onmouseout="this.style.backgroundColor='#2E86AB'">
    COPY
    </button>
    <span id="{button_id}_status" style="margin-left: 6px; color: #06D6A0; font-weight: 600; font-size: 9px;"></span>
    <script>
        document.getElementById('{button_id}').addEventListener('click', function() {{
            const data = `{escaped_data}`;
            navigator.clipboard.writeText(data).then(function() {{
                document.getElementById('{button_id}_status').textContent = '✓';
                setTimeout(function() {{
                    document.getElementById('{button_id}_status').textContent = '';
                }}, 2000);
            }}).catch(function(err) {{
                document.getElementById('{button_id}_status').textContent = '✗';
                console.error('Could not copy text: ', err);
            }});
        }});
    </script>
    """
    return html

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔢 IMEI/ASN Match</h1>
        <p>Match IMEI/Serial numbers to ASN orders with intelligent tracking</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize database
    init_database()

    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "🔍 Order Details", "📦 Archived"])

    # TAB 1: Dashboard
    with tab1:
        st.markdown("## 📊 Overview")

        # Load data in background
        df, error = load_data_from_sheets()

        if error:
            st.error(f"❌ Failed to load data: {error}")
        else:
            # Get statistics
            stats = get_order_statistics()
            reconciliations = get_all_reconciliations()

            # Create reconciliation lookup
            recon_dict = {r.invoice: r for r in reconciliations}

            # Calculate real-time stats from Google Sheets
            if df is not None and not df.empty:
                unique_invoices = df['INVOICE'].unique()
                total_qty = df['QTY'].sum()

                # Count orders with ASN and IMEI
                orders_with_asn = sum(1 for inv in unique_invoices if recon_dict.get(inv) and recon_dict[inv].asn_uploaded)
                orders_with_imei = sum(1 for inv in unique_invoices if recon_dict.get(inv) and recon_dict[inv].imei_serial_uploaded)
                pending_orders = len(unique_invoices) - orders_with_asn

                # Stats row
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>Total Orders</h3>
                        <p class="value">{len(unique_invoices)}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>Total Units</h3>
                        <p class="value">{total_qty:,}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>With ASN</h3>
                        <p class="value">{orders_with_asn}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>With IMEI/Serial</h3>
                        <p class="value">{orders_with_imei}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                # Recent Orders Section
                st.markdown("### 📦 Recent Orders")

                # Show recent 10 orders
                recent_invoices = sorted(unique_invoices, reverse=True)[:10]

                for invoice in recent_invoices:
                    recon = recon_dict.get(invoice)
                    order_df = df[df['INVOICE'] == invoice]
                    order_qty = order_df['QTY'].sum()

                    # Determine status
                    has_asn = recon and recon.asn_uploaded
                    has_imei = recon and recon.imei_serial_uploaded

                    if has_asn and has_imei:
                        status_class = "status-complete"
                        status_text = "✅ Complete"
                    elif has_asn:
                        status_class = "status-partial"
                        status_text = "⚠️ ASN Only"
                    else:
                        status_class = "status-pending"
                        status_text = "📋 Pending"

                    col1, col2, col3, col4, col5 = st.columns([2.5, 1.5, 1.8, 0.9, 1.1])

                    with col1:
                        st.markdown(f"**{invoice}**")
                    with col2:
                        st.markdown(f"**{order_qty:,} units**")
                    with col3:
                        st.markdown(f'<span class="status-badge {status_class}">{status_text}</span>', unsafe_allow_html=True)
                    with col4:
                        if st.button("📤", key=f"upload_{invoice}", use_container_width=True, help="Upload files"):
                            st.session_state['upload_order'] = invoice
                            st.rerun()
                    with col5:
                        if st.button("View", key=f"view_{invoice}", use_container_width=True):
                            st.session_state['selected_order_detail'] = invoice
                            st.rerun()

                # Upload File Modal
                if 'upload_order' in st.session_state and st.session_state['upload_order']:
                    st.markdown("---")
                    st.markdown(f"### 📤 Upload Files for Order: {st.session_state['upload_order']}")

                    upload_invoice = st.session_state['upload_order']
                    upload_recon = recon_dict.get(upload_invoice)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### 📄 ASN File")
                        has_asn = upload_recon and upload_recon.asn_uploaded

                        if has_asn:
                            st.success(f"✅ Uploaded: {upload_recon.asn_filename}")
                            if st.button("🗑️ Remove ASN", key=f"remove_asn_{upload_invoice}"):
                                if clear_asn_data(upload_invoice):
                                    st.success("ASN removed!")
                                    st.rerun()
                        else:
                            asn_file = st.file_uploader("Choose ASN file", key=f"quick_asn_{upload_invoice}", type=['xlsx', 'xls', 'csv', 'txt'])
                            if asn_file:
                                if st.button("✅ Confirm Upload", key=f"confirm_asn_{upload_invoice}", type="primary"):
                                    asn_file.seek(0)
                                    asn_data = asn_file.read()
                                    create_or_update_reconciliation(
                                        invoice=upload_invoice,
                                        asn_uploaded=True,
                                        asn_filename=asn_file.name,
                                        asn_file_data=asn_data,
                                        asn_upload_date=datetime.utcnow()
                                    )
                                    st.success("✅ ASN uploaded successfully!")
                                    st.session_state.pop('upload_order', None)
                                    st.rerun()

                    with col2:
                        st.markdown("#### 🔢 Extracted IMEIs")

                        # Extract IMEIs from ASN file if available
                        if has_asn and upload_recon.asn_file_data:
                            imeis, count, error = extract_imeis_from_file(upload_recon.asn_file_data, upload_recon.asn_filename)

                            if error:
                                st.error(f"⚠️ {error}")
                            elif imeis:
                                st.success(f"✅ Found {count} IMEIs")
                                imei_text = format_imeis_for_display(imeis)
                                st.text_area(
                                    "Copy IMEIs:",
                                    value=imei_text,
                                    height=200,
                                    key=f"quick_imei_display_{upload_invoice}"
                                )
                            else:
                                st.warning("⚠️ No IMEIs found")
                        else:
                            st.info("📄 Upload ASN file first")

                    # Close button
                    st.markdown("---")
                    if st.button("❌ Close Upload", use_container_width=False):
                        st.session_state.pop('upload_order', None)
                        st.rerun()

                # Refresh button with stats
                st.markdown("---")
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
                        st.cache_data.clear()
                        st.rerun()

                # Show refresh stats after button
                st.info(f"📊 Loaded **{len(unique_invoices)} orders** with **{total_qty:,} total units** from Google Sheets")

            else:
                st.warning("No data available")

    # TAB 2: Order Details - Grid Card View
    with tab2:
        st.markdown("## 🔍 Order Details")

        df, error = load_data_from_sheets()

        if error or df is None or df.empty:
            st.error("Failed to load orders")
            return

        all_invoices = sorted(df['INVOICE'].unique().tolist(), reverse=True)
        reconciliations = get_all_reconciliations()
        recon_dict = {r.invoice: r for r in reconciliations}

        # Check database connection
        engine = get_database_engine()
        if engine is None:
            st.error("⚠️ **DATABASE NOT CONNECTED!**")
            st.warning("Files cannot be saved without database. Check DATABASE_URL in Railway settings.")
            st.info("Go to Railway → Your Project → PostgreSQL → Connect → Copy DATABASE_URL → Add to your web service variables")

        # Debug toggle
        if st.checkbox("🐛 Show Debug Info", key="debug_toggle"):
            import os
            db_url = os.environ.get('DATABASE_URL', 'NOT SET')
            st.write(f"**Database URL:** {db_url[:50]}... (truncated)" if db_url != 'NOT SET' else "**Database URL:** NOT SET")
            st.write(f"**Database Engine:** {'✅ Connected' if engine else '❌ Not Connected'}")
            st.write(f"**Total Records:** {len(reconciliations)}")
            if reconciliations:
                st.write("**Sample Records:**")
                for r in reconciliations[:3]:
                    st.write(f"- {r.invoice}: ASN={r.asn_uploaded}, File Size={len(r.asn_file_data) if r.asn_file_data else 0} bytes")

        # Initialize selected order
        if 'selected_order_card' not in st.session_state:
            st.session_state['selected_order_card'] = None

        # Detail view for selected order
        if st.session_state['selected_order_card']:
            selected_invoice = st.session_state['selected_order_card']

            if st.button("← Back to All Orders", key="back_to_grid"):
                st.session_state['selected_order_card'] = None
                st.rerun()

            st.markdown("---")

            recon = recon_dict.get(selected_invoice)
            order_df = df[df['INVOICE'] == selected_invoice]
            order_qty = order_df['QTY'].sum()
            unique_models = order_df['MODEL'].nunique()
            has_asn = recon and recon.asn_uploaded
            has_imei = recon and recon.imei_serial_uploaded

            # REDESIGNED HEADER - Compact with actions grouped
            st.markdown(f"### 📦 {selected_invoice}")

            # Status and Archive button in compact inline layout
            action_col1, action_col2 = st.columns([1, 1])
            with action_col1:
                if has_asn:
                    st.markdown('<span class="status-badge status-complete" style="display: inline-block; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 600; background: #D1FAE5; color: #065F46;">✅ ASN Uploaded</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-badge status-pending" style="display: inline-block; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 600; background: #DBEAFE; color: #1E40AF;">⚠️ No ASN</span>', unsafe_allow_html=True)
            with action_col2:
                if st.button("📦 Archive", key=f"archive_{selected_invoice}", use_container_width=True):
                    # Prepare order data for archiving
                    order_data_list = order_df.to_dict('records')
                    result = archive_order(
                        invoice=selected_invoice,
                        order_data=order_data_list,
                        total_qty=order_qty,
                        unique_models=unique_models,
                        notes=recon.notes if recon else None
                    )
                    if result:
                        st.success("✅ Order archived!")
                        st.session_state['selected_order_card'] = None
                        st.rerun()
                    else:
                        st.error("❌ Failed to archive")

            st.markdown("---")

            # Metrics and Order Details Side by Side
            col1, col2 = st.columns([1.5, 3.5])

            with col1:
                # Compact square metrics
                st.markdown("### 📊 Summary")

                # IMEI Comparison: ON ASN vs EXPECTED
                if has_asn and recon.asn_file_data:
                    imeis, imei_count, _ = extract_imeis_from_file(recon.asn_file_data, recon.asn_filename)
                    on_asn_count = imei_count
                else:
                    on_asn_count = 0

                expected_count = order_qty

                # Determine color based on match
                if on_asn_count == expected_count:
                    border_color = "#06D6A0"  # Green - match
                    status_icon = "✅"
                elif on_asn_count > 0:
                    border_color = "#F18F01"  # Orange - partial
                    status_icon = "⚠️"
                else:
                    border_color = "#C73E1D"  # Red - missing
                    status_icon = "❌"

                # Bigger square cards
                st.markdown(f"""
                <div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #2E86AB; min-height: 70px;">
                    <p style="color: #6C757D; margin: 0; font-size: 0.75rem;">Total Units</p>
                    <p style="font-size: 1.8rem; font-weight: 700; margin: 0;">{order_qty:,}</p>
                </div>

                <div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #A23B72; min-height: 70px;">
                    <p style="color: #6C757D; margin: 0; font-size: 0.75rem;">Models</p>
                    <p style="font-size: 1.8rem; font-weight: 700; margin: 0;">{unique_models}</p>
                </div>

                <div style="background: white; padding: 0.8rem; border-radius: 8px; border-left: 4px solid {border_color}; min-height: 90px;">
                    <p style="color: #6C757D; margin: 0 0 0.4rem 0; font-size: 0.75rem;">{status_icon} Compare</p>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span style="font-size: 0.75rem; color: #6C757D;">ASN:</span>
                        <span style="font-size: 1.3rem; font-weight: 700;">{on_asn_count}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 0.75rem; color: #6C757D;">EXP:</span>
                        <span style="font-size: 1.3rem; font-weight: 700;">{expected_count}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Compact Order Details Card with proper column widths
                st.markdown("### 📋 Expected Order Details")

                # Define columns to display in order
                display_columns = ['INVOICE', 'MODEL', 'CAPACITY', 'COLOR', 'LOCKED', 'GRADE', 'UNIT', 'TOTAL', 'QTY', 'STATUS', 'SUPPLIER', 'FALLOUT RATE']

                # Filter to only columns that exist in the dataframe
                available_columns = [col for col in display_columns if col in order_df.columns]

                # Configure column widths with specific pixel values for tighter spacing
                column_config = {
                    "INVOICE": st.column_config.TextColumn("INVOICE", width=100),
                    "MODEL": st.column_config.TextColumn("MODEL", width=150),
                    "CAPACITY": st.column_config.TextColumn("CAPACITY", width=80),
                    "COLOR": st.column_config.TextColumn("COLOR", width=80),
                    "LOCKED": st.column_config.TextColumn("LOCKED", width=70),
                    "GRADE": st.column_config.TextColumn("GRADE", width=70),
                    "UNIT": st.column_config.TextColumn("UNIT", width=60),
                    "TOTAL": st.column_config.NumberColumn("TOTAL", width=70),
                    "QTY": st.column_config.NumberColumn("QTY", width=60),
                    "STATUS": st.column_config.TextColumn("STATUS", width=80),
                    "SUPPLIER": st.column_config.TextColumn("SUPPLIER", width=100),
                    "FALLOUT RATE": st.column_config.TextColumn("FALLOUT RATE", width=90)
                }

                st.dataframe(
                    order_df[available_columns] if available_columns else order_df,
                    hide_index=True,
                    use_container_width=True,
                    height=250,
                    column_config=column_config
                )

            st.markdown("---")

            # Process breakdowns for this order
            model_gb_output, model_only_output, grade_mix_output = process_selected_orders(df, [selected_invoice])

            # REDESIGNED BREAKDOWNS - Vertical Accordion Layout
            st.markdown("### 📊 Breakdowns")
            st.caption("Expand each section to view detailed breakdown tables")

            # Model + GB Breakdown - Expanded by default
            with st.expander(f"📊 MODEL + GB BREAKDOWN ({len(model_gb_output)} items)", expanded=True):
                if model_gb_output is not None and not model_gb_output.empty:
                    config_model_gb = {
                        "MODEL_GB": st.column_config.TextColumn("MODEL + GB", width=None),
                        "QTY": st.column_config.NumberColumn("QTY", width=120)
                    }
                    st.dataframe(
                        model_gb_output,
                        hide_index=True,
                        use_container_width=True,
                        height=min(300, len(model_gb_output) * 35 + 50),
                        column_config=config_model_gb
                    )
                else:
                    st.info("No data available")

            # Model + Qty Breakdown
            with st.expander(f"📱 MODEL + QTY BREAKDOWN ({len(model_only_output)} items)", expanded=False):
                if model_only_output is not None and not model_only_output.empty:
                    config_model = {
                        "MODEL": st.column_config.TextColumn("MODEL", width=None),
                        "QTY": st.column_config.NumberColumn("QTY", width=120)
                    }
                    st.dataframe(
                        model_only_output,
                        hide_index=True,
                        use_container_width=True,
                        height=min(300, len(model_only_output) * 35 + 50),
                        column_config=config_model
                    )
                else:
                    st.info("No data available")

            # Grade Breakdown
            with st.expander(f"🏷️ GRADE BREAKDOWN ({len(grade_mix_output)} items)", expanded=False):
                if grade_mix_output is not None and not grade_mix_output.empty:
                    config_grade = {
                        "MODEL": st.column_config.TextColumn("MODEL", width=None),
                        "CAPACITY": st.column_config.TextColumn("CAPACITY", width=120),
                        "GRADE": st.column_config.TextColumn("GRADE", width=100),
                        "QTY": st.column_config.NumberColumn("QTY", width=100)
                    }
                    st.dataframe(
                        grade_mix_output,
                        hide_index=True,
                        use_container_width=True,
                        height=min(300, len(grade_mix_output) * 35 + 50),
                        column_config=config_grade
                    )
                else:
                    st.info("No data available")

            st.markdown("---")

            # Files
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📤 ASN File")
                if has_asn:
                    st.success(f"✅ {recon.asn_filename}")
                    if recon.asn_file_data:
                        st.caption(f"{len(recon.asn_file_data)} bytes")
                        st.download_button("⬇️ Download", recon.asn_file_data, recon.asn_filename, key=f"dl_asn_{selected_invoice}", use_container_width=True)
                    else:
                        st.error("⚠️ File data missing!")
                    if st.button("🗑️ Clear", key=f"clear_asn_{selected_invoice}", use_container_width=True):
                        clear_asn_data(selected_invoice)
                        st.rerun()
                else:
                    asn_file = st.file_uploader("Upload", key=f"asn_{selected_invoice}", type=['xlsx', 'xls', 'csv', 'txt', 'pdf'])
                    if asn_file:
                        st.info(f"{asn_file.name} ({asn_file.size} bytes)")
                        if st.button("💾 Save", key=f"save_asn_{selected_invoice}", type="primary", use_container_width=True):
                            asn_file.seek(0)
                            result = create_or_update_reconciliation(invoice=selected_invoice, asn_uploaded=True, asn_filename=asn_file.name, asn_file_data=asn_file.read(), asn_upload_date=datetime.utcnow())
                            if result:
                                st.success(f"✅ Saved! ID:{result.id}")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save")

            with col2:
                st.markdown("#### 🔢 Extracted IMEIs")

                # Extract IMEIs from ASN file if available
                if has_asn and recon.asn_file_data:
                    imeis, count, error = extract_imeis_from_file(recon.asn_file_data, recon.asn_filename)

                    if error:
                        st.error(f"⚠️ {error}")
                    elif imeis:
                        st.success(f"✅ Found {count} IMEIs")

                        # Display IMEIs in copyable text area
                        imei_text = format_imeis_for_display(imeis)
                        st.text_area(
                            "Copy IMEIs:",
                            value=imei_text,
                            height=300,
                            key=f"imei_display_{selected_invoice}",
                            help="Click inside and press Ctrl+A (Cmd+A on Mac) to select all, then Ctrl+C (Cmd+C) to copy"
                        )

                        # Download as text file
                        st.download_button(
                            "⬇️ Download IMEIs",
                            data=imei_text,
                            file_name=f"{selected_invoice}_IMEIs.txt",
                            mime="text/plain",
                            key=f"dl_imeis_{selected_invoice}",
                            use_container_width=True
                        )
                    else:
                        st.info("📄 No IMEIs found. Upload ASN file with IMEI/Serial columns.")
                else:
                    st.info("📄 Upload ASN file to extract IMEIs")
                    st.caption("Supports: Excel (.xlsx, .xls), CSV, TXT | Looks for columns: SERIAL, IMEI, Serial No, etc.")

            # Notes
            st.markdown("---")
            st.markdown("#### 📝 Notes")
            notes = st.text_area("", value=recon.notes if recon and recon.notes else "", height=100, key=f"notes_{selected_invoice}")
            if st.button("💾 Save Notes", key=f"save_notes_{selected_invoice}"):
                create_or_update_reconciliation(invoice=selected_invoice, notes=notes)
                st.success("✅ Saved!")
                st.rerun()

        else:
            # Grid view - show all orders as compact cards
            st.markdown("### 📦 All Orders - Click to View")
            st.markdown("---")

            # Create 3-column grid
            cards_per_row = 3
            for i in range(0, len(all_invoices), cards_per_row):
                cols = st.columns(cards_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx >= len(all_invoices):
                        break

                    invoice = all_invoices[idx]
                    recon = recon_dict.get(invoice)
                    order_df = df[df['INVOICE'] == invoice]
                    order_qty = order_df['QTY'].sum()

                    has_asn = recon and recon.asn_uploaded
                    has_imei = recon and recon.imei_serial_uploaded

                    if has_asn and has_imei:
                        status_icon = "✅"
                        status_color = "#D1FAE5"
                    elif has_asn:
                        status_icon = "⚠️"
                        status_color = "#FEF3C7"
                    else:
                        status_icon = "📋"
                        status_color = "#DBEAFE"

                    with col:
                        # Compact card
                        st.markdown(f"""
                        <div style="background: white; padding: 1.2rem; border-radius: 10px; border: 2px solid #DEE2E6;
                             box-shadow: 0 2px 4px rgba(0,0,0,0.08); height: 180px; cursor: pointer;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                                <h4 style="margin: 0; color: #2E86AB; font-size: 1.1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{invoice}</h4>
                                <span style="font-size: 1.5rem;">{status_icon}</span>
                            </div>
                            <div style="margin-bottom: 0.5rem;">
                                <p style="color: #6C757D; margin: 0; font-size: 0.75rem;">Total Units</p>
                                <p style="font-size: 1.3rem; font-weight: 700; margin: 0;">{order_qty:,}</p>
                            </div>
                            <div style="background: {status_color}; padding: 0.3rem 0.8rem; border-radius: 15px; text-align: center; font-size: 0.75rem; font-weight: 600;">
                                {"Complete" if has_asn and has_imei else "ASN Only" if has_asn else "Pending"}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if st.button("View Details", key=f"card_{invoice}", use_container_width=True):
                            st.session_state['selected_order_card'] = invoice
                            st.rerun()

    # TAB 3: Archived Orders
    with tab3:
        st.markdown("## 📦 Archived Orders")
        st.info("📋 Archived orders are preserved here even after they are removed from the Google Sheet source.")

        archived_orders = get_all_archived_orders()

        if not archived_orders:
            st.warning("No archived orders yet")
        else:
            # Initialize selected archived order
            if 'selected_archived_order' not in st.session_state:
                st.session_state['selected_archived_order'] = None

            # Detail view for selected archived order
            if st.session_state['selected_archived_order']:
                selected_archived = st.session_state['selected_archived_order']
                archived = get_archived_order(selected_archived)

                if not archived:
                    st.error("Archived order not found")
                    st.session_state['selected_archived_order'] = None
                    st.rerun()

                if st.button("← Back to Archived Orders", key="back_to_archived"):
                    st.session_state['selected_archived_order'] = None
                    st.rerun()

                st.markdown("---")

                # Header
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### 📦 {archived.invoice}")
                    st.caption(f"Archived on: {archived.archived_date.strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    if st.button("🗑️ Delete Archive", key=f"delete_archived_{archived.invoice}", type="secondary", use_container_width=True):
                        if delete_archived_order(archived.invoice):
                            st.success("✅ Archive deleted!")
                            st.session_state['selected_archived_order'] = None
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete")

                st.markdown("---")

                # Summary and Order Details
                col1, col2 = st.columns([1.5, 3.5])

                with col1:
                    st.markdown("### 📊 Summary")
                    st.markdown(f"""
                    <div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #2E86AB; min-height: 70px;">
                        <p style="color: #6C757D; margin: 0; font-size: 0.75rem;">Total Units</p>
                        <p style="font-size: 1.8rem; font-weight: 700; margin: 0;">{archived.total_qty:,}</p>
                    </div>

                    <div style="background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #A23B72; min-height: 70px;">
                        <p style="color: #6C757D; margin: 0; font-size: 0.75rem;">Models</p>
                        <p style="font-size: 1.8rem; font-weight: 700; margin: 0;">{archived.unique_models}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("### 📋 Order Details")
                    if archived.order_data:
                        import json
                        order_data = json.loads(archived.order_data)
                        order_df = pd.DataFrame(order_data)

                        # Define columns to display in order
                        display_columns = ['INVOICE', 'MODEL', 'CAPACITY', 'COLOR', 'LOCKED', 'GRADE', 'UNIT', 'TOTAL', 'QTY', 'STATUS', 'SUPPLIER', 'FALLOUT RATE']

                        # Filter to only columns that exist in the dataframe
                        available_columns = [col for col in display_columns if col in order_df.columns]

                        column_config = {
                            "INVOICE": st.column_config.TextColumn("INVOICE", width=100),
                            "MODEL": st.column_config.TextColumn("MODEL", width=150),
                            "CAPACITY": st.column_config.TextColumn("CAPACITY", width=80),
                            "COLOR": st.column_config.TextColumn("COLOR", width=80),
                            "LOCKED": st.column_config.TextColumn("LOCKED", width=70),
                            "GRADE": st.column_config.TextColumn("GRADE", width=70),
                            "UNIT": st.column_config.TextColumn("UNIT", width=60),
                            "TOTAL": st.column_config.NumberColumn("TOTAL", width=70),
                            "QTY": st.column_config.NumberColumn("QTY", width=60),
                            "STATUS": st.column_config.TextColumn("STATUS", width=80),
                            "SUPPLIER": st.column_config.TextColumn("SUPPLIER", width=100),
                            "FALLOUT RATE": st.column_config.TextColumn("FALLOUT RATE", width=90)
                        }

                        st.dataframe(
                            order_df[available_columns] if available_columns else order_df,
                            hide_index=True,
                            use_container_width=True,
                            height=250,
                            column_config=column_config
                        )
                    else:
                        st.warning("No order details available")

                st.markdown("---")

                # Files
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📤 ASN File")
                    if archived.asn_filename and archived.asn_file_data:
                        st.success(f"✅ {archived.asn_filename}")
                        st.download_button(
                            "⬇️ Download ASN",
                            data=archived.asn_file_data,
                            file_name=archived.asn_filename,
                            key=f"dl_archived_asn_{archived.invoice}",
                            use_container_width=True
                        )

                        # Extract and show IMEIs from archived ASN
                        imeis, count, error = extract_imeis_from_file(archived.asn_file_data, archived.asn_filename)
                        if imeis:
                            st.success(f"✅ Found {count} IMEIs")
                    else:
                        st.info("No ASN file archived")

                with col2:
                    st.markdown("#### 🔢 Extracted IMEIs")
                    if archived.asn_file_data:
                        imeis, count, error = extract_imeis_from_file(archived.asn_file_data, archived.asn_filename)

                        if error:
                            st.error(f"⚠️ {error}")
                        elif imeis:
                            imei_text = format_imeis_for_display(imeis)
                            st.text_area(
                                "Copy IMEIs:",
                                value=imei_text,
                                height=300,
                                key=f"archived_imei_display_{archived.invoice}"
                            )
                            st.download_button(
                                "⬇️ Download IMEIs",
                                data=imei_text,
                                file_name=f"{archived.invoice}_IMEIs.txt",
                                mime="text/plain",
                                key=f"dl_archived_imeis_{archived.invoice}",
                                use_container_width=True
                            )
                        else:
                            st.info("No IMEIs found")
                    else:
                        st.info("No ASN file to extract from")

                # Notes
                if archived.notes:
                    st.markdown("---")
                    st.markdown("#### 📝 Notes")
                    st.text_area("", value=archived.notes, height=100, key=f"archived_notes_{archived.invoice}", disabled=True)

            else:
                # Grid view - show all archived orders
                st.markdown(f"### 📦 All Archived Orders ({len(archived_orders)})")
                st.markdown("---")

                # Create 3-column grid
                cards_per_row = 3
                for i in range(0, len(archived_orders), cards_per_row):
                    cols = st.columns(cards_per_row)
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx >= len(archived_orders):
                            break

                        archived = archived_orders[idx]

                        with col:
                            # Compact card
                            st.markdown(f"""
                            <div style="background: white; padding: 1.2rem; border-radius: 10px; border: 2px solid #DEE2E6;
                                 box-shadow: 0 2px 4px rgba(0,0,0,0.08); height: 180px; cursor: pointer;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                                    <h4 style="margin: 0; color: #2E86AB; font-size: 1.1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{archived.invoice}</h4>
                                    <span style="font-size: 1.5rem;">📦</span>
                                </div>
                                <div style="margin-bottom: 0.5rem;">
                                    <p style="color: #6C757D; margin: 0; font-size: 0.75rem;">Total Units</p>
                                    <p style="font-size: 1.3rem; font-weight: 700; margin: 0;">{archived.total_qty:,}</p>
                                </div>
                                <div style="background: #E3F2FD; padding: 0.3rem 0.8rem; border-radius: 15px; text-align: center; font-size: 0.75rem; font-weight: 600;">
                                    Archived {archived.archived_date.strftime('%Y-%m-%d')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            if st.button("View Details", key=f"archived_card_{archived.invoice}", use_container_width=True):
                                st.session_state['selected_archived_order'] = archived.invoice
                                st.rerun()

if __name__ == "__main__":
    main()
