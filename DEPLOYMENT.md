# OrderHub Deployment Guide

This guide explains how to deploy OrderHub to Railway (backend) and Vercel (frontend).

## Architecture

- **Backend (Railway)**: FastAPI application that processes orders and stores them in CSV files
- **Frontend (Vercel)**: Static HTML/JavaScript application
- **Database**: CSV files (`orders.csv`, `corrections.csv`) stored on Railway's filesystem

## Prerequisites

1. GitHub account (for connecting repositories)
2. Railway account (https://railway.app)
3. Vercel account (https://vercel.com)
4. Your Railway backend URL (will be generated after deployment)

---

## Part 1: Deploy Backend to Railway

### Step 1: Prepare Your Repository

1. Make sure all your code is committed to a Git repository (GitHub, GitLab, etc.)
2. Ensure `requirements.txt`, `Procfile`, and `runtime.txt` are in the root directory

### Step 2: Deploy to Railway

1. Go to https://railway.app and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"** (or GitLab/Bitbucket)
4. Select your OrderHub repository
5. Railway will automatically detect it's a Python project

### Step 3: Configure Environment Variables

In Railway dashboard, go to your service → **Variables** tab and add:

```
DB_HOST=your-postgres-host (if using PostgreSQL)
DB_PORT=5432
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=orderhub
OPENAI_API_KEY=your-openai-api-key (if using AI features)
```

**Note**: If you're using Excel/CSV files only (no PostgreSQL), you can skip the DB_* variables. However, your `src/db.py` currently uses PostgreSQL. You may need to modify it if you want to use Excel files only.

### Step 4: Set Up Persistent Storage (for CSV files)

Railway's filesystem is ephemeral by default. To persist CSV files:

1. In Railway dashboard, go to your service
2. Click **"Add Volume"**
3. Mount it to `/app/data` (or your preferred path)
4. Update your code to save CSV files to this volume path

Alternatively, you can use Railway's persistent storage or an external service like AWS S3.

### Step 5: Get Your Railway URL

1. After deployment, Railway will provide a URL like: `https://your-app-name.up.railway.app`
2. Copy this URL - you'll need it for the frontend configuration

### Step 6: Update CORS (if needed)

The backend already includes CORS configuration that allows Vercel domains. If you need to add specific domains, edit `src/main.py`.

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Prepare Frontend

The frontend is already configured with `vercel.json`. Make sure it's in your repository root.

### Step 2: Deploy to Vercel

**Option A: Via Vercel Dashboard**

1. Go to https://vercel.com and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: Leave as root
   - **Build Command**: `node build.js` (this injects the API URL)
   - **Output Directory**: Leave empty (handled by vercel.json)

**Option B: Via Vercel CLI**

```bash
npm i -g vercel
vercel login
vercel
```

### Step 3: Configure Environment Variables

In Vercel dashboard → Your Project → Settings → Environment Variables, add:

```
API_BASE_URL=https://your-railway-app.up.railway.app
```

**Important**: Replace `your-railway-app.up.railway.app` with your actual Railway URL.

The `build.js` script will automatically inject this URL into your HTML during deployment.

### Step 4: Deploy

1. Click **"Deploy"** in Vercel
2. Wait for deployment to complete
3. Your frontend will be available at: `https://your-project.vercel.app`

---

## Part 3: Post-Deployment Configuration

### Update CORS in Backend

After deploying frontend, update `src/main.py` to include your Vercel domain:

```python
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-project.vercel.app",  # Add your Vercel URL
]
```

Or use the environment variable approach (already implemented).

### Test the Connection

1. Visit your Vercel frontend URL
2. Try submitting an order
3. Check Railway logs if there are any CORS errors
4. Verify orders are being saved to CSV files

---

## Important Notes

### CSV File Storage

Railway's filesystem is **ephemeral** - files are lost when the service restarts. To persist CSV files:

1. **Use Railway Volumes** (recommended)
   - Add a volume in Railway dashboard
   - Mount it to a path like `/app/data`
   - Update `src/saver.py` and `src/history.py` to use this path

2. **Use External Storage**
   - AWS S3, Google Cloud Storage, etc.
   - Update your code to upload CSV files to these services

3. **Use a Database**
   - Consider migrating from CSV to PostgreSQL (Railway offers managed PostgreSQL)
   - Update your code to use database instead of CSV files

### Environment Variables

Make sure all sensitive data (API keys, database credentials) are stored as environment variables, not hardcoded in your code.

### Monitoring

- **Railway**: Check logs in Railway dashboard
- **Vercel**: Check logs in Vercel dashboard
- Set up error tracking (Sentry, etc.) for production

---

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Check that your Vercel URL is in the `allowed_origins` list in `src/main.py`
2. Verify the Railway URL is correct in frontend
3. Check Railway logs for CORS-related errors

### CSV Files Not Persisting

1. Ensure you're using Railway Volumes or external storage
2. Check file paths are correct
3. Verify write permissions

### API Connection Issues

1. Verify Railway service is running
2. Check Railway URL is correct
3. Test Railway health endpoint: `https://your-railway-app.up.railway.app/`
4. Check Railway logs for errors

---

## Quick Reference

- **Railway Backend URL**: `https://your-app-name.up.railway.app`
- **Vercel Frontend URL**: `https://your-project.vercel.app`
- **Health Check**: `https://your-railway-app.up.railway.app/`
- **API Endpoints**:
  - `/whatsapp` - Submit order
  - `/history` - Get order history
  - `/feed` - Get today's orders

