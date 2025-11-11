# Railway Environment Variables Setup

## Required Environment Variables

Add these in Railway Dashboard → Your Service → Variables:

### 1. OpenAI API Key (Required for AI features)
```
OPENAI_API_KEY=your-openai-api-key-here
```

**Note**: The app will now start even without this key, but AI features will be disabled and fall back to fuzzy matching.

### 2. Database Connection (PostgreSQL)

**Railway automatically provides `DATABASE_URL`** when you add a Postgres service to your project:

1. In Railway Dashboard → Your Project → Click **"+ New"** → Select **"Database"** → Choose **"PostgreSQL"**
2. Railway will automatically create the database and add `DATABASE_URL` to your environment variables
3. Your app will automatically use this connection string - no manual configuration needed!

**For local development**, you can still use individual variables:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=orderhub
```

**Note**: The code now supports both `DATABASE_URL` (Railway's format) and individual DB_* variables (for local dev).

### 3. Twilio Variables (If using WhatsApp alerts)
```
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
MANAGER_WHATSAPP_NUMBER=whatsapp:+your-manager-number
```

## What Was Fixed

✅ **OpenAI Client Initialization**: Now handles missing API keys gracefully
- App will start even without `OPENAI_API_KEY`
- AI features fall back to fuzzy matching when unavailable
- No more startup crashes due to missing API key

✅ **Error Handling**: Added try-catch blocks for AI parsing
- Falls back to regular parsing if AI is unavailable
- App continues to function without AI features

## Next Steps

1. **Add Environment Variables in Railway**:
   - Go to Railway Dashboard → Your Service → Variables
   - Add `OPENAI_API_KEY` with your key from `.env`
   - Add other variables as needed

2. **Redeploy**:
   - Railway will automatically redeploy when you add variables
   - Or trigger a manual redeploy

3. **Verify**:
   - Check Railway logs - should see "⚠️ Warning" if API key is missing (but app still starts)
   - Test your endpoints to ensure everything works

