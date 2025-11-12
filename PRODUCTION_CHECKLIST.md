# Production Deployment Checklist

## ✅ What Will Work the Same

1. **Database Connection**: Your code already uses `DATABASE_URL` from environment variables, which Railway provides automatically when you add a PostgreSQL service. The connection logic in `src/saver.py` handles Railway's format correctly.

2. **API Endpoints**: All your endpoints (`/history`, `/feed`, `/whatsapp`, etc.) will work identically.

3. **Dependencies**: Your `requirements.txt` is complete and will install the same packages.

4. **Server Configuration**: Your `Procfile` correctly uses `$PORT` which Railway provides automatically.

## ⚠️ What Needs to Be Configured

### 1. Environment Variables in Railway
Make sure these are set in your Railway project settings:
- ✅ `DATABASE_URL` - Railway provides this automatically when you add PostgreSQL
- ✅ `OPENAI_API_KEY` - Your OpenAI API key
- ✅ `TWILIO_ACCOUNT_SID` - Your Twilio account SID
- ✅ `TWILIO_AUTH_TOKEN` - Your Twilio auth token
- ✅ `TWILIO_WHATSAPP_NUMBER` - Your Twilio WhatsApp number
- ✅ `MANAGER_WHATSAPP_NUMBER` - Manager's WhatsApp number
- ⚠️ `VERCEL_URL` - Only needed if you're using Vercel for frontend (optional)

### 2. CORS Configuration
Currently, your CORS is set to allow all origins (`allow_origins=["*"]`). This works but isn't ideal for security.

**Current code in `src/main.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    ...
)
```

**For production, you should update it to:**
```python
# Get production frontend URL from environment variable
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://order-hub-nine.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        FRONTEND_URL,  # Your production frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Frontend API URL
Your frontend already has logic to switch between local and production:
- **Local**: `http://localhost:8000`
- **Production**: `https://web-production-07a0c.up.railway.app`

**Current code in `frontend/index.html`:**
```javascript
window.API_BASE_URL = (function() {
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  return 'https://web-production-07a0c.up.railway.app';
})();
```

**⚠️ Make sure this Railway URL matches your actual Railway deployment URL!**

### 4. Database Table
Make sure the `restaurant_orders` table exists in your Railway PostgreSQL database. You can verify this by:
- Connecting to your Railway database
- Running: `SELECT * FROM restaurant_orders LIMIT 1;`

If the table doesn't exist, create it with:
```sql
CREATE TABLE restaurant_orders (
  id SERIAL PRIMARY KEY,
  restaurant_id INT REFERENCES restaurants(id) ON DELETE CASCADE,
  restaurant_name VARCHAR(100),
  quantity NUMERIC(10,2),
  unit VARCHAR(20),
  product VARCHAR(100),
  corrections TEXT,
  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  original_text TEXT,
  need_attention BOOLEAN DEFAULT FALSE,
  message TEXT
);
```

## 🚀 Deployment Steps

1. **Push your code to GitHub** (if using Railway's GitHub integration)

2. **In Railway Dashboard:**
   - Create a new project (or use existing)
   - Add PostgreSQL service (if not already added)
   - Add Python service
   - Connect your GitHub repository
   - Set all environment variables listed above
   - Railway will automatically detect your `Procfile` and deploy

3. **Get your Railway URL:**
   - After deployment, Railway will give you a URL like: `https://your-app-name.up.railway.app`
   - Update `frontend/index.html` with this URL (line 18)

4. **Deploy your frontend:**
   - Deploy to Vercel (or your preferred hosting)
   - Make sure the API URL in `frontend/index.html` points to your Railway backend

5. **Test:**
   - Visit your frontend URL
   - Test submitting an order
   - Check that history loads
   - Verify live feed shows today's orders

## 🔍 Quick Verification

After deployment, test these endpoints:
- `https://your-railway-url.up.railway.app/` - Should return `{"status": "ok"}`
- `https://your-railway-url.up.railway.app/history` - Should return orders
- `https://your-railway-url.up.railway.app/feed` - Should return today's orders

## 📝 Notes

- Railway automatically provides `DATABASE_URL` when you add PostgreSQL
- Railway automatically provides `PORT` environment variable
- Your code already handles Railway's database URL format correctly
- The `restaurant_orders` table should already exist if you created it earlier

