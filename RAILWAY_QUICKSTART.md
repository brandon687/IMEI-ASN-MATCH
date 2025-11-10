# Railway Deployment Quick Start

Get your WRMA Inbound Processor running on Railway in 10 minutes.

## Prerequisites Checklist

- [ ] Google Cloud service account JSON file
- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled
- [ ] Sheet shared with service account email
- [ ] Railway account created
- [ ] Code pushed to GitHub (optional but recommended)

## Quick Deploy Steps

### 1. Create Service Account (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create Service Account:
   - IAM & Admin → Service Accounts → Create
   - Name it "wrma-inbound-processor"
   - Create and download JSON key
5. Copy the service account email (looks like: `name@project.iam.gserviceaccount.com`)

### 2. Share Your Google Sheet

1. Open your orders Google Sheet
2. Click "Share" button
3. Paste the service account email
4. Give "Editor" permissions
5. Done!

### 3. Deploy to Railway (5 minutes)

#### From GitHub (Recommended):

1. **Push to GitHub:**
   ```bash
   cd "/Users/brandonin/WRMA SUBMISSION"
   git init
   git add .
   git commit -m "Initial deployment"
   gh repo create wrma-inbound-processor --private --source=. --push
   # OR manually create repo and push:
   # git remote add origin YOUR_GITHUB_URL
   # git push -u origin main
   ```

2. **Deploy on Railway:**
   - Visit [railway.app/new](https://railway.app/new)
   - Select "Deploy from GitHub repo"
   - Choose `wrma-inbound-processor`
   - Click "Add variables" and skip for now
   - Click "Deploy"

3. **Add Database:**
   - In your project, click "+ New"
   - Select "Database"
   - Choose "PostgreSQL"
   - Done! (DATABASE_URL is auto-configured)

4. **Set Environment Variables:**
   - Click on your web service (not database)
   - Click "Variables" tab
   - Click "+ New Variable"
   - Add:
     ```
     Name: GOOGLE_SHEETS_CREDENTIALS
     Value: <paste entire JSON from service account file>
     ```
   - The JSON should be on one line, starting with `{"type":"service_account"...}`

5. **Wait for Deploy:**
   - Railway will automatically redeploy
   - Check "Deployments" tab for progress
   - Should complete in 2-3 minutes

6. **Get Your URL:**
   - Click "Settings" tab
   - Under "Environment", click "Generate Domain"
   - Your app will be at: `https://YOUR-APP.up.railway.app`

## Verification Checklist

After deployment, verify:

- [ ] App loads without errors
- [ ] Dashboard shows statistics
- [ ] Refresh button displays order count and total qty
- [ ] Can view order details
- [ ] Can upload ASN files
- [ ] Can upload IMEI/Serial files
- [ ] Files can be downloaded

## Common Issues & Quick Fixes

### "Could not find INVOICE column"
- **Fix:** Check your Google Sheet structure
- Verify headers: INVOICE, MODEL, CAPACITY, GRADE, QTY
- Make sure service account has access

### "GOOGLE_SHEETS_CREDENTIALS not found"
- **Fix:** Check environment variable is set in Railway
- Click on web service → Variables tab
- Should see `GOOGLE_SHEETS_CREDENTIALS` listed
- Value should start with `{"type":"service_account"`

### "Database connection error"
- **Fix:** Ensure PostgreSQL is added to project
- Railway should auto-set `DATABASE_URL`
- Try redeploying: Click "⋯" → "Redeploy"

### App won't start / 502 error
- **Check Railway logs:**
  - Click on your service
  - Click "View Logs"
  - Look for Python errors
- **Common causes:**
  - Missing environment variables
  - Invalid JSON in credentials
  - Database not connected

### Orders not loading
- **Fix:** Verify Google Sheet permissions
- Service account email should have Editor access
- Check sheet ID in app.py matches your sheet
- Sheet must have correct column names

## Update Sheet ID (if needed)

If you're using a different Google Sheet:

1. Get your Sheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
   ```

2. Get your Worksheet GID:
   - Right-click on sheet tab at bottom
   - Copy link
   - Look for `gid=NUMBERS` in URL

3. Update Railway environment variables:
   - Add `SHEET_ID` = your sheet ID
   - Add `WORKSHEET_GID` = your worksheet GID

OR edit `app.py` lines ~280-281:
```python
SHEET_ID = "YOUR_SHEET_ID"
WORKSHEET_GID = "YOUR_GID"
```

## Testing Locally First (Optional)

Want to test before deploying?

```bash
cd "/Users/brandonin/WRMA SUBMISSION"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file:
echo 'GOOGLE_SHEETS_CREDENTIALS='"'"'{"type":"service_account",...}'"'"'' > .env
echo 'DATABASE_URL=sqlite:///test.db' >> .env

# Run:
streamlit run app.py
```

Open http://localhost:8501

## Next Steps

Once deployed successfully:

1. **Test all features:**
   - Process an order
   - Upload ASN file
   - Upload IMEI/Serial file
   - Download files
   - Add notes

2. **Share with team:**
   - Send Railway URL to team members
   - No login required (add authentication later if needed)

3. **Monitor usage:**
   - Check Railway dashboard for usage
   - Review logs periodically

4. **Plan for exports:**
   - Once verified working, we'll add export functionality
   - Export IMEI/Serial data matched to orders
   - Bulk export capabilities

## Support

Issues during deployment?
1. Check Railway logs first
2. Verify all environment variables
3. Test Google Sheets access manually
4. Review README.md for detailed troubleshooting

## Cost

Railway free tier includes:
- $5 free credit per month
- Should cover light usage
- Upgrade to Developer plan ($5/mo) for production use

---

**Ready to deploy?** Start with Step 1 above! 🚀
