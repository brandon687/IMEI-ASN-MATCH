---
name: imei-asn-project
description: Provides comprehensive knowledge of the IMEI-ASN-Match system architecture, database schema, workflows, and deployment configuration. Use this skill when working on the IMEI/ASN matching application, modifying features, debugging issues, or understanding the codebase structure.
---

# IMEI-ASN-Match Project Knowledge

## Overview

This skill provides deep knowledge of the IMEI-ASN-Match system, a production Streamlit application deployed on Railway that matches IMEI/Serial numbers to ASN orders with intelligent tracking. The system integrates Google Sheets for order data, PostgreSQL for persistent storage, and provides a modern UI for managing order reconciliation workflows.

## Core Architecture

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **External Integration**: Google Sheets API
- **Deployment**: Railway platform
- **Authentication**: Google Cloud Service Account

### Project Structure

```
IMEI-ASN-Match/
├── app.py                      # Main Streamlit application (51KB, 1056 lines)
├── database.py                 # Database models and operations (18KB, 530 lines)
├── google_sheets_auth.py       # Google Sheets authentication (1.3KB)
├── imei_extractor.py          # IMEI/Serial number extraction (3.4KB)
├── requirements.txt            # Python dependencies
├── railway.toml               # Railway deployment configuration
├── Procfile                   # Process configuration
├── assets/
│   └── logo.png              # SCAL MOBILE logo with "ASN & IMEIS" text
└── .streamlit/
    └── config.toml           # Streamlit theme configuration
```

### Database Schema

Reference `references/database_schema.md` for complete schema documentation.

**Key Tables:**
- `OrderReconciliation` - Tracks invoice processing, file uploads, and status
- `ArchivedOrder` - Stores completed/archived orders
- `OrderLineItem` - Individual order line details
- `SupplierProfile` - Supplier configuration
- `ColumnMapping` - Field mapping configuration

## Key Workflows

### 1. Order Data Loading

**When to execute:** On application startup, data refresh, or when orders need to be synced from Google Sheets.

**Process:**
1. Authenticate with Google Sheets using service account credentials
2. Load order data from configured Sheet ID and Worksheet GID
3. Parse columns: INVOICE, MODEL, CAPACITY, COLOR, LOCKED, GRADE, UNIT, TOTAL, QTY, STATUS, SUPPLIER, FALLOUT RATE
4. Clean and normalize model names (remove special characters, standardize format)
5. Return pandas DataFrame for processing

**Implementation:** `app.py` → `load_data_from_sheets()` function (lines ~390-441)

### 2. Order Breakdown Generation

**When to execute:** When user selects orders and needs breakdown reports.

**Process:**
1. Filter DataFrame by selected invoice(s)
2. Generate three breakdown types:
   - **MODEL + GB**: Groups by MODEL and CAPACITY, sums QTY
   - **MODEL Only**: Groups by MODEL only, sums QTY
   - **GRADE MIX**: Shows MODEL, CAPACITY, GRADE with QTY
3. Sort results for consistent display
4. Return formatted DataFrames

**Implementation:** `app.py` → `process_selected_orders()` function (lines ~452-472)

### 3. File Upload and Storage

**When to execute:** When user uploads ASN or IMEI/Serial files.

**Process:**
1. User selects file via Streamlit file_uploader
2. File read as binary data
3. Create/update OrderReconciliation record with:
   - Original filename
   - Binary file data (stored as BLOB)
   - Upload timestamp
   - File type flag (ASN or IMEI)
4. For IMEI files: Extract and count IMEI/Serial entries
5. Commit to PostgreSQL database

**Implementation:**
- `database.py` → `create_or_update_reconciliation()` function
- `imei_extractor.py` → `extract_imeis_from_file()` function

### 4. Order Archiving

**When to execute:** When user archives a completed order.

**Process:**
1. Retrieve order data from OrderReconciliation table
2. Create ArchivedOrder record with:
   - Invoice number
   - Order data JSON
   - Total quantity and unique models
   - Optional notes
   - Archive timestamp
3. Delete original OrderReconciliation record
4. Maintain audit trail

**Implementation:** `database.py` → `archive_order()` function (lines ~448-488)

**Important Note:** Fixed numpy type conversion issue - total_qty and unique_models must be converted to Python int before database insert to avoid `ProgrammingError: can't adapt type 'numpy.int64'`.

### 5. UI Layout Structure

**Dashboard Tab (Tab 1):**
- Statistics cards: Total orders, units, ASN uploads, IMEI tracking
- Recent orders list with status badges
- Quick upload button (📤) for each order
- Upload modal for ASN and IMEI files

**Order Details Tab (Tab 2):**
- Order selection dropdown
- Summary statistics (ASN count, expected count)
- Order details table with compact column widths
- Breakdown sections (expanders):
  - MODEL + GB BREAKDOWN (expanded by default)
  - MODEL + QTY BREAKDOWN (collapsed)
  - GRADE BREAKDOWN (collapsed)
- Each breakdown has copy button (📋 COPY) that displays copyable tab-separated text
- File upload sections for ASN and IMEI files
- Archive button

**Archived Tab (Tab 3):**
- List of archived orders
- View and restore capabilities
- Delete permanently option

## Common Development Tasks

### Adding New Columns to Order Data

1. Update Google Sheets with new column
2. Modify `load_data_from_sheets()` to include new column in fetch
3. Update display_columns list in Order Details section
4. Add column_config entry with appropriate width
5. Test data loading and display

### Modifying Breakdown Logic

1. Locate `process_selected_orders()` in app.py
2. Add new breakdown DataFrame with appropriate groupby logic
3. Add expander section in Order Details tab
4. Configure column widths and styling
5. Add copy button with unique key

### Updating Database Schema

1. Add new column/table to models in `database.py`
2. Update `_run_migrations()` to handle schema changes
3. Test locally first with PostgreSQL
4. Deploy to Railway (automatic migration on startup)
5. Verify in Railway logs that migration succeeded

### Styling and UI Changes

**CSS Customization:**
- All custom CSS is in app.py lines ~30-388
- Uses CSS variables for theming
- Responsive design with media queries (@media rules)
- Key classes: `.main-header`, `.metric-card`, `.status-badge`, expander styling

**Button Styling:**
- Native Streamlit buttons (no HTML/JS needed after previous issues)
- Copy functionality uses `st.code()` for displayable text
- File uploaders use `label_visibility="collapsed"` for clean look

### Deployment Configuration

**Railway Setup:**
1. PostgreSQL database automatically provisions DATABASE_URL
2. Environment variables required:
   - `GOOGLE_SHEETS_CREDENTIALS` (service account JSON as string)
   - `PORT=8501`
3. railway.toml specifies build and start commands
4. Procfile defines web process

**Key Files:**
- `railway.toml`: Build configuration
- `Procfile`: Process definition
- `requirements.txt`: Python dependencies

## Troubleshooting Guide

### Issue: HTML buttons displaying as text

**Cause:** Streamlit escaping HTML when using nested f-strings or complex column layouts.

**Solution:** Use native Streamlit buttons instead of HTML/JavaScript. For copy functionality, display data in `st.code()` block for manual copy.

**Reference:** Fixed in commits 347608d, 09fb1ce, 6f548bd, 4dc073a

### Issue: JavaScript errors with button IDs containing spaces

**Cause:** Invoice numbers with spaces (e.g., "110725 ECO ATM") break `getElementById()`.

**Solution:** Sanitize button IDs using regex: `re.sub(r'[^a-zA-Z0-9_-]', '_', button_id)`

**Reference:** Fixed in commit 4dc073a

### Issue: numpy.int64 type error in database

**Cause:** Pandas returns numpy types that PostgreSQL adapter can't handle.

**Solution:** Convert to Python native types before insert: `int(total_qty)`, `int(unique_models)`

**Reference:** Fixed in database.py `archive_order()` function

### Issue: Breakdown tables too wide

**Cause:** `use_container_width=True` causes tables to stretch across screen.

**Solution:** Set `use_container_width=False` and define specific pixel widths for columns.

**Reference:** Fixed in commit ec07bf2

## References

- `references/database_schema.md` - Complete database schema documentation
- `references/api_patterns.md` - Common API integration patterns
- `references/deployment_guide.md` - Detailed Railway deployment steps

## Development Patterns

### State Management

- Use `st.session_state` for storing selected orders, upload state
- Clear state on actions that require refresh: `st.rerun()`
- Session state keys follow pattern: `{action}_{invoice}` (e.g., `copy_model_gb_110725`)

### Error Handling

- Database operations wrapped in try-except with SQLAlchemy error handling
- Google Sheets errors display user-friendly messages
- File upload errors caught and displayed with st.error()

### Code Organization

- **app.py**: UI and workflow orchestration (DO NOT add business logic here)
- **database.py**: All database operations and models
- **google_sheets_auth.py**: Authentication only
- **imei_extractor.py**: File parsing logic

### Testing Approach

- Test locally with PostgreSQL before Railway deployment
- Use st.write() for debugging (remove before commit)
- Check Railway logs after deployment
- Test on multiple screen sizes (iPhone, MacBook, 40" monitor)
