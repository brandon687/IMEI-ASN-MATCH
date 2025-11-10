# IMEI/ASN Match

A modern, production-ready system for matching IMEI/Serial numbers to ASN orders with intelligent tracking. Built with Streamlit and designed for Railway deployment.

## Features

### 🎨 Modern UI
- Clean, professional interface with custom theming
- Gradient headers and smooth animations
- Card-based layout for better visual organization
- Responsive design that works on all devices

### 📊 Dashboard
- Real-time statistics overview
- Total orders, units, ASN uploads, and IMEI/Serial tracking
- Recent orders view with status badges
- Quick access to order details

### 📋 Order Processing
- Single or batch order selection
- Three different report views:
  - MODEL + GB Breakdown
  - MODEL Only Breakdown
  - GRADE MIX Report
- Download reports as CSV
- Copy to clipboard functionality
- Clean display showing order count and total quantity

### 🔍 Order Details & File Management
- Upload and store ASN files (any format)
- Upload and store IMEI/SERIAL files
- Automatic IMEI/Serial entry counting
- Download original uploaded files
- Order notes functionality
- Clear file management with delete options

### 🔒 Data Management
- PostgreSQL database for persistent storage
- Google Sheets integration for order data
- Secure service account authentication
- Automatic database migrations

## Prerequisites

1. **Google Cloud Service Account**
   - Create a service account at [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Sheets API and Google Drive API
   - Download the JSON credentials file

2. **Railway Account**
   - Sign up at [Railway.app](https://railway.app/)
   - Install Railway CLI (optional): `npm install -g @railway/cli`

## Deployment to Railway

### Step 1: Prepare Your Google Sheets

1. Open your Google Sheet with order data
2. Ensure your sheet has these columns: `INVOICE`, `MODEL`, `CAPACITY`, `GRADE`, `QTY`
3. Note your Sheet ID (from the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`)
4. Share your sheet with the service account email (found in your credentials JSON)

### Step 2: Deploy to Railway

#### Option A: Deploy from GitHub (Recommended)

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create new project on Railway:**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the configuration

3. **Add PostgreSQL database:**
   - In your project, click "New"
   - Select "Database" → "Add PostgreSQL"
   - Railway will automatically set the `DATABASE_URL` environment variable

4. **Set environment variables:**
   - Click on your web service
   - Go to "Variables" tab
   - Add the following variables:

   ```
   GOOGLE_SHEETS_CREDENTIALS=<paste your entire service account JSON here>
   PORT=8501
   ```

   Note: For `GOOGLE_SHEETS_CREDENTIALS`, paste the entire contents of your service account JSON file as a single line.

#### Option B: Deploy with Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   railway init
   ```

4. **Add PostgreSQL:**
   ```bash
   railway add postgresql
   ```

5. **Set environment variables:**
   ```bash
   railway variables set GOOGLE_SHEETS_CREDENTIALS="$(cat path/to/your-service-account.json)"
   ```

6. **Deploy:**
   ```bash
   railway up
   ```

### Step 3: Update Sheet ID (if different)

If your Google Sheet ID is different from the default, update `app.py`:

```python
# Line ~280 in app.py
SHEET_ID = "YOUR_SHEET_ID_HERE"
WORKSHEET_GID = "YOUR_WORKSHEET_GID_HERE"
```

### Step 4: Verify Deployment

1. Open your Railway deployment URL
2. You should see the dashboard with your orders
3. Test the refresh button - it should display order count and total quantity

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_SHEETS_CREDENTIALS` | Service account JSON credentials | Yes |
| `DATABASE_URL` | PostgreSQL connection string (auto-set by Railway) | Yes |
| `PORT` | Port for the application (default: 8501) | No |

## Local Development

1. **Clone the repository:**
   ```bash
   git clone YOUR_REPO_URL
   cd imei-asn-match
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Create a `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   GOOGLE_SHEETS_CREDENTIALS='{"type": "service_account", ...}'
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser:**
   ```
   http://localhost:8501
   ```

## Usage Guide

### Processing Orders

1. **Dashboard Tab:**
   - View real-time statistics
   - See recent orders with status
   - Click "Refresh Data" to sync with Google Sheets
   - The refresh will show: "Loaded X orders with Y total units"

2. **Orders Tab:**
   - Select single or multiple orders
   - View aggregated reports (MODEL+GB, MODEL, GRADE MIX)
   - Download as CSV or copy to clipboard

3. **Order Details Tab:**
   - Select an order to view details
   - Upload ASN file (any format accepted)
   - Upload IMEI/SERIAL file (counts entries automatically)
   - Add notes for internal tracking
   - Download previously uploaded files

### File Management

- **ASN Files:** Upload packing lists, invoices, or shipping notices
- **IMEI/Serial Files:** Upload text files or CSVs with device identifiers
- The system counts IMEI entries automatically when uploaded
- All files stored as binary blobs in PostgreSQL
- Download original files anytime from Order Details tab

## Project Structure

```
imei-asn-match/
├── app.py                      # Main Streamlit application
├── database.py                 # Database models and operations
├── google_sheets_auth.py       # Google Sheets authentication
├── requirements.txt            # Python dependencies
├── railway.toml               # Railway deployment config
├── Procfile                   # Process configuration
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Database Schema

### OrderReconciliation Table
- Invoice tracking
- ASN upload status and file storage
- IMEI/Serial upload status and file storage
- Notes and error logs
- Timestamps for audit trail

## Troubleshooting

### Google Sheets Connection Fails
- Verify service account has access to the sheet
- Check `GOOGLE_SHEETS_CREDENTIALS` environment variable is set correctly
- Ensure Google Sheets API and Drive API are enabled in Google Cloud

### Database Connection Issues
- Verify PostgreSQL service is running on Railway
- Check `DATABASE_URL` is automatically set
- Review Railway logs for connection errors

### Application Won't Start
- Check Railway logs: `railway logs`
- Verify all environment variables are set
- Ensure `requirements.txt` dependencies installed correctly

### Refresh Button Not Showing Stats
- Clear Streamlit cache and refresh
- Verify Google Sheets data structure matches expected format
- Check Railway logs for any data loading errors

## Support

For issues or questions:
1. Check Railway deployment logs
2. Review Google Sheets permissions
3. Verify environment variables are set correctly

## License

Proprietary - WRMA Internal Use Only

## Version

**v2.0.0** - Complete rebuild with modern UI, IMEI/Serial tracking, and Railway deployment
