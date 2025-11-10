# Deploy IMEI/ASN Match - Run These Commands Now 🚀

## ✅ Project Status

- **Project Name:** IMEI/ASN Match
- **Repository Name:** `imei-asn-match`
- **Location:** `/Users/brandonin/IMEI-ASN-Match`
- **App Title:** Updated to "🔢 IMEI/ASN Match"
- **Tagline:** "Match IMEI/Serial numbers to ASN orders with intelligent tracking"

---

## Step 1: Update Documentation (Run This First)

Open Terminal and run:

```bash
cd "/Users/brandonin/IMEI-ASN-Match"

# Update all occurrences of old name
find . -type f \( -name "*.md" -o -name "*.txt" \) -exec sed -i '' 's/imei-asn-match/imei-asn-match/g' {} +
find . -type f \( -name "*.md" -o -name "*.txt" \) -exec sed -i '' 's/IMEI/ASN Match/IMEI\/ASN Match/g' {} +

echo "✅ Documentation updated!"
```

---

## Step 2: Commit All Changes

```bash
cd "/Users/brandonin/IMEI-ASN-Match"

# Add all changes
git add -A

# Commit with descriptive message
git commit -m "Rename project to IMEI/ASN Match

- Updated app title and branding
- Changed repository name to imei-asn-match
- Updated all documentation
- Focus on IMEI/Serial matching workflow"

echo "✅ Changes committed!"
```

---

## Step 3: Create GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `imei-asn-match`
   - **Description:** "Match IMEI/Serial numbers to ASN orders with intelligent tracking"
   - **Privacy:** Private (recommended)
   - **DO NOT** check any initialization options
3. Click "Create repository"

---

## Step 4: Push to GitHub

```bash
cd "/Users/brandonin/IMEI-ASN-Match"

# Add GitHub remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/imei-asn-match.git

# Push code
git push -u origin main
```

**When prompted for credentials:**
- Username: Your GitHub username
- Password: Use a Personal Access Token
  - Create at: https://github.com/settings/tokens
  - Select "repo" scope
  - Copy and use as password

---

## Step 5: Deploy to Railway

### 5a. Go to Railway

Visit: https://railway.app/new

### 5b. Deploy from GitHub

1. Click "Deploy from GitHub repo"
2. Select `imei-asn-match`
3. Click "Deploy"

### 5c. Add PostgreSQL

1. In your Railway project, click "+ New"
2. Select "Database"
3. Choose "PostgreSQL"
4. Wait ~30 seconds for provisioning

### 5d. Set Environment Variables

1. Click on your **web service** (not the database)
2. Go to "Variables" tab
3. Click "+ New Variable"
4. Add:
   ```
   Name: GOOGLE_SHEETS_CREDENTIALS
   Value: <paste your entire service account JSON here>
   ```

**Getting your service account JSON:**
- Go to Google Cloud Console
- Create service account
- Download JSON key file
- Copy the entire content
- Paste as the value (should start with `{"type":"service_account"...}`)

### 5e. Generate Domain

1. Click "Settings" tab
2. Scroll to "Environment"
3. Click "Generate Domain"
4. Your app URL: `https://YOUR-APP.up.railway.app`

### 5f. Wait for Deployment

- Check "Deployments" tab
- Should complete in 2-3 minutes
- Watch for "Success" status

---

## Step 6: Test Your App

1. Visit your Railway URL
2. Check Dashboard loads
3. Click "Refresh Data" button
4. Should show: "📊 Loaded X orders with Y total units from Google Sheets"
5. Test uploading ASN file
6. Test uploading IMEI/Serial file
7. Verify downloads work

---

## Quick Reference Commands

### Check Git Status
```bash
cd "/Users/brandonin/IMEI-ASN-Match"
git status
```

### View Commit History
```bash
git log --oneline
```

### Check Remote
```bash
git remote -v
```

---

## Troubleshooting

### "Repository not found" when pushing
- Make sure you created the repo on GitHub first
- Check the URL matches your username
- Verify you have access to create private repos

### "Authentication failed"
- Don't use your GitHub password
- Create a Personal Access Token: https://github.com/settings/tokens
- Use the token as your password

### Railway deployment fails
- Check logs in Railway dashboard
- Verify `GOOGLE_SHEETS_CREDENTIALS` is set correctly
- Ensure PostgreSQL database is added
- Try redeploying: Click "⋯" → "Redeploy"

### App loads but no data
- Check Google Sheets permissions
- Service account email must have Editor access to your sheet
- Verify sheet ID in app.py (lines ~280-281)

---

## What's Different From Old Version?

### Old Name
- IMEI/ASN Match
- imei-asn-match

### New Name
- IMEI/ASN Match
- imei-asn-match

### Focus Shift
- **Before:** General inbound order processing
- **After:** IMEI/Serial matching to ASN orders

### Key Features Kept
- ✅ Modern UI with gradient theme
- ✅ Dashboard with statistics
- ✅ ASN file upload and storage
- ✅ IMEI/Serial file upload with auto-counting
- ✅ Order tracking and notes
- ✅ Google Sheets integration
- ✅ PostgreSQL database

---

## Ready to Deploy!

**Run the commands in order:**
1. Step 1: Update documentation
2. Step 2: Commit changes
3. Step 3: Create GitHub repo
4. Step 4: Push to GitHub
5. Step 5: Deploy to Railway
6. Step 6: Test!

**Total Time:** ~15 minutes

---

**Need help?** The commands are all ready to copy/paste above! 🎉
