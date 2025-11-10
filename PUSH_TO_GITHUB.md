# Push to GitHub - Step by Step

Your code is ready to push! Follow these steps:

## Option 1: Using GitHub Website (Easiest)

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Fill in the details:
   - **Repository name:** `imei-asn-match`
   - **Description:** "Modern order processing system with ASN and IMEI/Serial tracking"
   - **Privacy:** Choose "Private" (recommended for business use)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

### Step 2: Push Your Code

GitHub will show you commands. Use these from your terminal:

```bash
cd "/Users/brandonin/WRMA SUBMISSION"

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/imei-asn-match.git

# Push your code
git branch -M main
git push -u origin main
```

**Example if your GitHub username is "brandonin":**
```bash
git remote add origin https://github.com/brandonin/imei-asn-match.git
git branch -M main
git push -u origin main
```

### Step 3: Enter Credentials

When prompted:
- **Username:** Your GitHub username
- **Password:** Use a Personal Access Token (not your password)

**To create a token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "WRMA Railway Deploy"
4. Select scopes: Check "repo" (full control of private repositories)
5. Click "Generate token"
6. Copy the token and use it as your password

---

## Option 2: Using SSH (If you have SSH keys set up)

```bash
cd "/Users/brandonin/WRMA SUBMISSION"

# Add remote with SSH
git remote add origin git@github.com:YOUR_USERNAME/imei-asn-match.git

# Push
git branch -M main
git push -u origin main
```

---

## Option 3: Install GitHub CLI (For future convenience)

```bash
# Install GitHub CLI
brew install gh

# Login to GitHub
gh auth login

# Create repo and push in one command
cd "/Users/brandonin/WRMA SUBMISSION"
gh repo create imei-asn-match --private --source=. --push
```

---

## After Successfully Pushing

You should see output like:
```
Enumerating objects: 28, done.
Counting objects: 100% (28/28), done.
Delta compression using up to 8 threads
Compressing objects: 100% (25/25), done.
Writing objects: 100% (28/28), 1.45 MiB | 2.89 MiB/s, done.
Total 28 (delta 2), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/imei-asn-match.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

✅ **Your code is now on GitHub!**

---

## Next Step: Deploy to Railway

Once pushed to GitHub, proceed to deploy on Railway:

### Quick Railway Deploy:

1. **Go to Railway:** https://railway.app/new
2. **Click "Deploy from GitHub repo"**
3. **Select:** `imei-asn-match`
4. **Click "Add variables"** → Skip for now
5. **Click "Deploy"**

6. **Add PostgreSQL Database:**
   - Click "+ New" in your project
   - Select "Database" → "PostgreSQL"
   - Wait for provisioning (~30 seconds)

7. **Set Environment Variables:**
   - Click on your web service (not database)
   - Go to "Variables" tab
   - Click "+ New Variable"
   - Add `GOOGLE_SHEETS_CREDENTIALS` with your service account JSON

8. **Generate Domain:**
   - Click "Settings" tab
   - Scroll to "Environment"
   - Click "Generate Domain"
   - Your app will be at: `https://YOUR-APP.up.railway.app`

9. **Wait for Deployment** (~2-3 minutes)

10. **Test Your App!**

---

## Troubleshooting

### "Permission denied" when pushing
- You need to authenticate with GitHub
- Create a Personal Access Token (see Step 3 above)
- Use the token as your password

### "Repository not found"
- Make sure you created the repository on GitHub first
- Check the URL in your git remote command matches your username

### "Updates were rejected"
- This shouldn't happen on first push
- If it does, you may have accidentally initialized with README
- Contact me for help

---

## Current Status

✅ Git repository initialized
✅ Files committed locally
⏳ **NEXT:** Push to GitHub using Option 1 above
⏳ **THEN:** Deploy to Railway

---

**Need help?** Just ask!
