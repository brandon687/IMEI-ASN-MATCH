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
    get_order_statistics
)
from datetime import datetime

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
    /* Main theme colors */
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

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
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

    /* DataFrames */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* File uploader */
    .stFileUploader {
        background: white;
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 2rem;
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

    grade_mix_df = filtered_df.groupby(['GRADE', 'MODEL', 'CAPACITY'], as_index=False)['QTY'].sum()
    grade_mix_output = grade_mix_df[['GRADE', 'MODEL', 'CAPACITY', 'QTY']].sort_values(['GRADE', 'MODEL', 'CAPACITY'], ascending=True)

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
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.2s;
    " onmouseover="this.style.backgroundColor='#246A87'" onmouseout="this.style.backgroundColor='#2E86AB'">
    📋 Copy to Clipboard
    </button>
    <span id="{button_id}_status" style="margin-left: 10px; color: #06D6A0; font-weight: 600;"></span>
    <script>
        document.getElementById('{button_id}').addEventListener('click', function() {{
            const data = `{escaped_data}`;
            navigator.clipboard.writeText(data).then(function() {{
                document.getElementById('{button_id}_status').textContent = '✅ Copied!';
                setTimeout(function() {{
                    document.getElementById('{button_id}_status').textContent = '';
                }}, 2000);
            }}).catch(function(err) {{
                document.getElementById('{button_id}_status').textContent = '❌ Failed';
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
    tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "📋 Orders", "🔍 Order Details"])

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

                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1.5, 1.5])

                    with col1:
                        st.markdown(f"**{invoice}**")
                    with col2:
                        st.markdown(f"**{order_qty:,} units**")
                    with col3:
                        st.markdown(f'<span class="status-badge {status_class}">{status_text}</span>', unsafe_allow_html=True)
                    with col4:
                        if st.button("📤 Upload", key=f"upload_{invoice}", use_container_width=True):
                            st.session_state['upload_order'] = invoice
                            st.rerun()
                    with col5:
                        if st.button("View Details", key=f"view_{invoice}", use_container_width=True):
                            st.session_state['selected_order'] = invoice
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
                        st.markdown("#### 🔢 IMEI/Serial File")
                        has_imei = upload_recon and upload_recon.imei_serial_uploaded

                        if has_imei:
                            st.success(f"✅ Uploaded: {upload_recon.imei_serial_filename}")
                            if st.button("🗑️ Remove IMEI/Serial", key=f"remove_imei_{upload_invoice}"):
                                if clear_imei_serial_data(upload_invoice):
                                    st.success("IMEI/Serial removed!")
                                    st.rerun()
                        else:
                            imei_file = st.file_uploader("Choose IMEI/Serial file", key=f"quick_imei_{upload_invoice}", type=['xlsx', 'xls', 'csv', 'txt'])
                            if imei_file:
                                # Try to count entries
                                imei_file.seek(0)
                                try:
                                    content = imei_file.read().decode('utf-8')
                                    count = len([line for line in content.split('\n') if line.strip()])
                                    st.info(f"📊 Detected {count} entries")
                                    imei_file.seek(0)
                                except:
                                    count = None

                                if st.button("✅ Confirm Upload", key=f"confirm_imei_{upload_invoice}", type="primary"):
                                    imei_file.seek(0)
                                    imei_data = imei_file.read()
                                    create_or_update_reconciliation(
                                        invoice=upload_invoice,
                                        imei_serial_uploaded=True,
                                        imei_serial_filename=imei_file.name,
                                        imei_serial_file_data=imei_data,
                                        imei_serial_upload_date=datetime.utcnow(),
                                        imei_serial_count=count
                                    )
                                    st.success("✅ IMEI/Serial uploaded successfully!")
                                    st.session_state.pop('upload_order', None)
                                    st.rerun()

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

    # TAB 2: Orders Processing
    with tab2:
        st.markdown("## 📋 Order Processing")

        df, error = load_data_from_sheets()

        if error:
            st.error(f"❌ {error}")
            return

        if df is None or df.empty:
            st.warning("No orders found")
            return

        invoices = sorted(df['INVOICE'].unique().tolist())

        # Selection mode
        col1, col2 = st.columns([1, 3])

        with col1:
            selection_mode = st.radio(
                "Selection Mode:",
                ["Single Order", "Multiple Orders"]
            )

        with col2:
            if selection_mode == "Single Order":
                selected_invoices = [st.selectbox("Select Invoice:", invoices)]
            else:
                selected_invoices = st.multiselect("Select Invoices:", invoices)

        if not selected_invoices:
            st.info("👆 Please select at least one invoice")
            return

        st.markdown("---")

        # Process orders
        model_gb_output, model_only_output, grade_mix_output = process_selected_orders(df, selected_invoices)

        if model_gb_output is None:
            st.error("No data found")
            return

        total_qty = model_gb_output['QTY'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Selected Orders", len(selected_invoices))
        with col2:
            st.metric("Total Units", f"{total_qty:,}")
        with col3:
            st.metric("Unique Models", len(model_only_output))

        st.markdown("---")

        # MODEL + GB
        st.markdown("### 📊 MODEL + GB Breakdown")
        st.dataframe(model_gb_output, hide_index=True, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            csv1 = model_gb_output.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv1,
                file_name=f"model_gb_{'_'.join(selected_invoices[:3])}.csv",
                mime="text/csv",
                key="download_model_gb"
            )
        with col2:
            components.html(create_copy_button(model_gb_output, "copy_btn_1"), height=50)

        st.markdown("---")

        # MODEL Only
        st.markdown("### 📱 MODEL Breakdown")
        st.dataframe(model_only_output, hide_index=True, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            csv2 = model_only_output.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv2,
                file_name=f"model_only_{'_'.join(selected_invoices[:3])}.csv",
                mime="text/csv",
                key="download_model_only"
            )
        with col2:
            components.html(create_copy_button(model_only_output, "copy_btn_2"), height=50)

        st.markdown("---")

        # Grade Mix
        st.markdown("### 🏷️ GRADE MIX")
        st.dataframe(grade_mix_output, hide_index=True, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            csv3 = grade_mix_output.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv3,
                file_name=f"grade_mix_{'_'.join(selected_invoices[:3])}.csv",
                mime="text/csv",
                key="download_grade_mix"
            )
        with col2:
            components.html(create_copy_button(grade_mix_output, "copy_btn_3"), height=50)

    # TAB 3: Order Details
    with tab3:
        st.markdown("## 🔍 Order Details & File Management")

        df, error = load_data_from_sheets()

        if error or df is None or df.empty:
            st.error("Failed to load orders")
            return

        all_invoices = sorted(df['INVOICE'].unique().tolist(), reverse=True)
        reconciliations = get_all_reconciliations()
        recon_dict = {r.invoice: r for r in reconciliations}

        # Order selector
        selected_order = st.selectbox("Select Order:", all_invoices, key="detail_order_select")

        if selected_order:
            st.markdown("---")

            recon = recon_dict.get(selected_order)
            order_data = df[df['INVOICE'] == selected_order].copy()
            total_qty = order_data['QTY'].sum()

            # Order header
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"### 📦 {selected_order}")

            with col2:
                has_asn = recon and recon.asn_uploaded
                if has_asn:
                    st.success("✅ ASN Uploaded")
                else:
                    st.warning("⚠️ No ASN")

            with col3:
                has_imei = recon and recon.imei_serial_uploaded
                if has_imei:
                    st.success("✅ IMEI/Serial")
                else:
                    st.warning("⚠️ No IMEI")

            st.markdown("---")

            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Units", f"{total_qty:,}")
            with col2:
                st.metric("Unique Models", order_data['MODEL'].nunique())
            with col3:
                if has_imei and recon.imei_serial_count:
                    st.metric("IMEI/Serial Count", f"{recon.imei_serial_count:,}")
                else:
                    st.metric("IMEI/Serial Count", "N/A")

            st.markdown("---")

            # Order details table
            st.markdown("#### 📋 Expected Order Details")
            st.dataframe(
                order_data[['MODEL', 'CAPACITY', 'GRADE', 'QTY']],
                hide_index=True,
                use_container_width=True
            )

            st.markdown("---")

            # ASN Upload Section
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📤 ASN File")

                if has_asn:
                    st.info(f"**File:** {recon.asn_filename}")
                    st.download_button(
                        label="⬇️ Download ASN",
                        data=recon.asn_file_data,
                        file_name=recon.asn_filename,
                        mime="application/octet-stream",
                        key=f"download_asn_{selected_order}",
                        use_container_width=True
                    )
                    if st.button("🗑️ Clear ASN", key=f"clear_asn_{selected_order}", use_container_width=True):
                        if clear_asn_data(selected_order):
                            st.success("Cleared!")
                            st.rerun()
                else:
                    asn_file = st.file_uploader("Upload ASN File", key=f"asn_upload_{selected_order}")
                    if asn_file:
                        if st.button("💾 Save ASN", type="primary", use_container_width=True):
                            asn_file.seek(0)
                            asn_data = asn_file.read()
                            create_or_update_reconciliation(
                                invoice=selected_order,
                                asn_uploaded=True,
                                asn_filename=asn_file.name,
                                asn_file_data=asn_data,
                                asn_upload_date=datetime.utcnow()
                            )
                            st.success("✅ ASN saved!")
                            st.rerun()

            with col2:
                st.markdown("#### 🔢 IMEI/SERIAL File")

                if has_imei:
                    st.info(f"**File:** {recon.imei_serial_filename}")
                    st.download_button(
                        label="⬇️ Download IMEI/Serial",
                        data=recon.imei_serial_file_data,
                        file_name=recon.imei_serial_filename,
                        mime="application/octet-stream",
                        key=f"download_imei_{selected_order}",
                        use_container_width=True
                    )
                    if st.button("🗑️ Clear IMEI/Serial", key=f"clear_imei_{selected_order}", use_container_width=True):
                        if clear_imei_serial_data(selected_order):
                            st.success("Cleared!")
                            st.rerun()
                else:
                    imei_file = st.file_uploader("Upload IMEI/SERIAL File", key=f"imei_upload_{selected_order}")
                    if imei_file:
                        # Try to count lines/rows
                        imei_file.seek(0)
                        try:
                            content = imei_file.read().decode('utf-8')
                            count = len([line for line in content.split('\n') if line.strip()])
                            st.info(f"📊 Detected {count} entries")
                            imei_file.seek(0)
                        except:
                            count = None

                        if st.button("💾 Save IMEI/Serial", type="primary", use_container_width=True):
                            imei_file.seek(0)
                            imei_data = imei_file.read()
                            create_or_update_reconciliation(
                                invoice=selected_order,
                                imei_serial_uploaded=True,
                                imei_serial_filename=imei_file.name,
                                imei_serial_file_data=imei_data,
                                imei_serial_upload_date=datetime.utcnow(),
                                imei_serial_count=count
                            )
                            st.success("✅ IMEI/Serial saved!")
                            st.rerun()

            # Notes section
            st.markdown("---")
            st.markdown("#### 📝 Notes")
            current_notes = recon.notes if recon and recon.notes else ""
            notes = st.text_area("Order Notes:", value=current_notes, height=100, key=f"notes_{selected_order}")

            if st.button("💾 Save Notes", key=f"save_notes_{selected_order}"):
                create_or_update_reconciliation(invoice=selected_order, notes=notes)
                st.success("✅ Notes saved!")
                st.rerun()

if __name__ == "__main__":
    main()
