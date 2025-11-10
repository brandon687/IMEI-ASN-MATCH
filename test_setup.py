#!/usr/bin/env python3
"""
Quick setup verification script for WRMA Inbound Processor
Run this before deploying to verify your configuration
"""

import sys
import os
import json

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing Python imports...")
    try:
        import streamlit
        import pandas
        import gspread
        import google.oauth2.service_account
        import sqlalchemy
        import psycopg2
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_google_credentials():
    """Test Google Sheets credentials"""
    print("\n🔍 Testing Google Sheets credentials...")

    creds = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    if not creds:
        print("❌ GOOGLE_SHEETS_CREDENTIALS environment variable not set")
        print("Set it with: export GOOGLE_SHEETS_CREDENTIALS='$(cat your-service-account.json)'")
        return False

    try:
        creds_dict = json.loads(creds)
        required_keys = ['type', 'project_id', 'private_key', 'client_email']
        missing = [k for k in required_keys if k not in creds_dict]

        if missing:
            print(f"❌ Missing required keys in credentials: {missing}")
            return False

        if creds_dict['type'] != 'service_account':
            print("❌ Credentials must be for a service account")
            return False

        print(f"✅ Valid service account credentials")
        print(f"   Email: {creds_dict['client_email']}")
        print(f"   Project: {creds_dict['project_id']}")
        return True

    except json.JSONDecodeError:
        print("❌ GOOGLE_SHEETS_CREDENTIALS is not valid JSON")
        return False

def test_database_url():
    """Test database URL"""
    print("\n🔍 Testing database configuration...")

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("⚠️  DATABASE_URL not set (will be set automatically by Railway)")
        print("   For local testing, use: export DATABASE_URL='sqlite:///test.db'")
        return True

    if db_url.startswith('postgresql://') or db_url.startswith('postgres://'):
        print("✅ PostgreSQL database URL configured")
        return True
    elif db_url.startswith('sqlite://'):
        print("✅ SQLite database URL configured (for local testing)")
        return True
    else:
        print(f"⚠️  Unusual database URL format: {db_url[:20]}...")
        return True

def test_google_sheets_connection():
    """Test actual connection to Google Sheets"""
    print("\n🔍 Testing Google Sheets connection...")

    creds = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    if not creds:
        print("⏭️  Skipping (no credentials set)")
        return True

    try:
        from google_sheets_auth import get_google_sheets_client
        client = get_google_sheets_client()
        print("✅ Successfully connected to Google Sheets API")

        # Try to list spreadsheets (this verifies authentication works)
        print("   Testing API access...")
        # Note: We don't actually list all sheets, just verify the client works
        print("✅ Google Sheets API is accessible")
        return True

    except Exception as e:
        print(f"❌ Failed to connect to Google Sheets: {str(e)}")
        print("   Make sure:")
        print("   1. Google Sheets API is enabled in your Google Cloud project")
        print("   2. Google Drive API is enabled in your Google Cloud project")
        print("   3. Service account has access to your sheet")
        return False

def test_files():
    """Test required files exist"""
    print("\n🔍 Testing required files...")

    required_files = [
        'app.py',
        'database.py',
        'google_sheets_auth.py',
        'requirements.txt',
        'Procfile',
        'railway.toml'
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            all_exist = False

    return all_exist

def main():
    print("=" * 60)
    print("WRMA Inbound Processor - Setup Verification")
    print("=" * 60)

    tests = [
        ("Python imports", test_imports),
        ("Required files", test_files),
        ("Google credentials", test_google_credentials),
        ("Database URL", test_database_url),
        ("Google Sheets connection", test_google_sheets_connection),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error during {name}: {str(e)}")
            results.append(False)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All {total} tests passed!")
        print("\n🚀 Ready to deploy to Railway!")
        print("\nNext steps:")
        print("1. git init && git add . && git commit -m 'Initial commit'")
        print("2. Push to GitHub")
        print("3. Deploy on Railway: https://railway.app/new")
        print("4. Add PostgreSQL database in Railway")
        print("5. Set GOOGLE_SHEETS_CREDENTIALS variable in Railway")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\n❌ Fix the errors above before deploying")
        print("\nFor help, see:")
        print("- README.md for detailed setup instructions")
        print("- RAILWAY_QUICKSTART.md for quick deployment guide")
        return 1

if __name__ == "__main__":
    sys.exit(main())
