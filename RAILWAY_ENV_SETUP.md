# Railway Environment Variables Setup

## Required Environment Variables

Add these in Railway Dashboard → Your Service → Variables:

### 1. OpenAI API Key (Required for AI features)
```
OPENAI_API_KEY=your-openai-api-key-here
```

**Note**: The app will now start even without this key, but AI features will be disabled and fall back to fuzzy matching.

### 2. Database Variables (If using PostgreSQL)
```
DB_HOST=your-postgres-host
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=orderhub
```

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

