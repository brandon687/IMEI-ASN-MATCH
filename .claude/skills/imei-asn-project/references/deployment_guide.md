# Deployment Guide

Complete guide for deploying the IMEI-ASN-Match application to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Google Cloud Service Account**:
   - Create at [console.cloud.google.com](https://console.cloud.google.com)
   - Enable Google Sheets API and Google Drive API
   - Download JSON credentials file
3. **GitHub Repository**: Code pushed to GitHub (recommended) or local Railway CLI

## Railway Deployment Steps

### Method 1: GitHub Deployment (Recommended)

**Step 1: Push Code to GitHub**
```bash
git init
git add .
git commit -m "Initial deployment"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

**Step 2: Create Railway Project**
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway auto-detects Python and uses railway.toml configuration

**Step 3: Add PostgreSQL Database**
1. In project, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway automatically sets `DATABASE_URL` environment variable
4. Database provisions in ~30 seconds

**Step 4: Configure Environment Variables**
1. Click on web service
2. Go to "Variables" tab
3. Add variables:

```
GOOGLE_SHEETS_CREDENTIALS=<paste entire service account JSON>
PORT=8501
```

**Important**: For `GOOGLE_SHEETS_CREDENTIALS`, paste the entire JSON file content as a single line string.

**Step 5: Deploy**
- Railway automatically deploys on push to main branch
- Monitor logs in Railway dashboard
- Get deployment URL from Railway

### Method 2: Railway CLI

**Step 1: Install CLI**
```bash
npm install -g @railway/cli
```

**Step 2: Login**
```bash
railway login
```

**Step 3: Initialize Project**
```bash
railway init
```

**Step 4: Add PostgreSQL**
```bash
railway add postgresql
```

**Step 5: Set Environment Variables**
```bash
railway variables set GOOGLE_SHEETS_CREDENTIALS="$(cat path/to/service-account.json)"
railway variables set PORT="8501"
```

**Step 6: Deploy**
```bash
railway up
```

## Configuration Files

### railway.toml
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### Procfile
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### requirements.txt
Key dependencies:
```
streamlit>=1.28.0
pandas>=2.0.0
gspread>=5.11.0
google-auth>=2.23.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
```

## Post-Deployment Verification

### 1. Check Logs
```bash
# Via CLI
railway logs

# Via Dashboard
Project → Service → Logs tab
```

Look for:
- "Database initialized successfully"
- "Streamlit running on port 8501"
- No Google Sheets authentication errors

### 2. Test Application
1. Open Railway deployment URL
2. Verify dashboard loads with statistics
3. Click "Refresh Data" - should show "Loaded X orders with Y total units"
4. Test file upload functionality
5. Test on multiple devices (mobile, desktop)

### 3. Verify Database Connection
- Check "Order Details" tab for database connection status
- Should show "✅ Connected" for database engine
- Test uploading a file to confirm data persistence

## Updating Deployment

### Automatic Deployment (GitHub)
```bash
git add .
git commit -m "Your changes"
git push origin main
# Railway automatically redeploys
```

### Manual Deployment (CLI)
```bash
railway up
```

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection (auto-set) | `postgresql://user:pass@host:5432/db` |
| `GOOGLE_SHEETS_CREDENTIALS` | Yes | Service account JSON | `{"type":"service_account",...}` |
| `PORT` | No | Application port (default: 8501) | `8501` |

## Troubleshooting

### Issue: Application won't start

**Check:**
1. Railway logs for Python errors
2. `requirements.txt` has all dependencies
3. Environment variables are set correctly

**Common causes:**
- Missing `GOOGLE_SHEETS_CREDENTIALS`
- Syntax error in recent code changes
- Dependency version conflicts

**Solution:**
```bash
railway logs --tail=100  # View recent logs
railway variables  # List all variables
```

### Issue: Database connection fails

**Check:**
1. PostgreSQL service is running (green status in Railway)
2. `DATABASE_URL` is automatically set
3. Database hasn't exceeded storage limits

**Solution:**
- Restart PostgreSQL service in Railway
- Check database metrics in Railway dashboard
- Review connection errors in logs

### Issue: Google Sheets authentication fails

**Check:**
1. Service account has access to Google Sheet
2. `GOOGLE_SHEETS_CREDENTIALS` is complete JSON (not truncated)
3. Google Sheets API is enabled in Google Cloud

**Solution:**
1. Re-copy service account JSON from Google Cloud
2. Verify JSON is valid (paste into JSON validator)
3. Share Google Sheet with service account email

### Issue: File uploads not persisting

**Check:**
1. Database connection is active
2. Binary data columns exist in schema
3. No storage quota exceeded

**Solution:**
- Check Railway logs during upload
- Verify database migration ran successfully
- Test with small file first

## Monitoring and Maintenance

### Metrics to Monitor
- Application uptime (Railway dashboard)
- Database storage usage
- Response times
- Error rates in logs

### Regular Maintenance
1. Review Railway logs weekly for errors
2. Monitor database size (PostgreSQL has limits)
3. Test file upload/download functionality
4. Verify Google Sheets sync is working

### Backup Strategy
- Railway PostgreSQL includes automatic backups
- Export critical data periodically via archive feature
- Keep service account JSON credentials secure

## Scaling Considerations

### Current Setup
- Single Railway service (web)
- Single PostgreSQL database
- No caching layer

### Future Scaling Options
1. **Redis Cache**: Add Redis for session/data caching
2. **Worker Services**: Separate background job processing
3. **CDN**: Add CDN for static assets (logo, CSS)
4. **Load Balancer**: Multiple Railway services with load balancing

## Security Best Practices

1. **Never commit** service account JSON to git
2. **Use environment variables** for all credentials
3. **Rotate credentials** periodically
4. **Monitor access logs** in Railway
5. **Keep dependencies updated** via `pip install --upgrade`

## Rollback Procedure

### Via GitHub
```bash
git revert HEAD  # Undo last commit
git push origin main  # Railway auto-deploys
```

### Via Railway
1. Go to project → Deployments
2. Find last working deployment
3. Click "Redeploy"

## Cost Management

### Railway Free Tier
- $5 free credit/month
- Usage-based pricing after free tier

### Typical Monthly Costs
- Web service: ~$2-5/month (based on usage)
- PostgreSQL: ~$1-3/month (based on storage)
- Total: ~$3-8/month for small-medium usage

### Cost Optimization
1. Use Railway sleep mode during off-hours
2. Archive old orders to reduce database size
3. Monitor usage in Railway dashboard
