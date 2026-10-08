# Cloud Deployment & Maintenance Guide
**Project:** AI-Powered Code Review and Error Detection Platform Using Explainable AI  
**Author:** Final Year B.Tech Project Team  
**Architecture:** React/Vite (Vercel) + FastAPI/Uvicorn (Render) + MySQL 8.0 (Managed Cloud) + Gemini AI  

---

## Architecture Overview

```mermaid
flowchart LR
    User["Any Device\n(PC, Laptop, Mobile)"]
    
    subgraph Frontend_Vercel ["Frontend: Vercel"]
        ReactApp["React 18 + Vite SPA\nhttps://<your-project>.vercel.app"]
    end
    
    subgraph Backend_Render ["Backend: Render"]
        FastAPIApp["FastAPI REST API\nhttps://<your-service>.onrender.com"]
        Engine["XAI Engine + Static Analyzers"]
    end
    
    subgraph Database_Cloud ["Database: Managed Cloud"]
        MySQLDB[("MySQL 8.0\n(Railway / Aiven)")]
    end
    
    subgraph AI_Cloud ["AI Engine: Google AI"]
        Gemini["Gemini 1.5 Flash API"]
    end
    
    User -->|HTTPS| ReactApp
    ReactApp -->|REST API Requests| FastAPIApp
    FastAPIApp -->|SSL Connection| MySQLDB
    FastAPIApp -->|HTTPS Prompts| Gemini
```

---

## Step 1: Push Code to GitHub

Open PowerShell in `c:\Major Project\ai-code-review-platform`:

```powershell
# 1. Create a new repository on https://github.com/new named: ai-code-review-platform
# 2. Push your code directly (remote is already configured):
git push -u origin main
```

*(Note: Secrets, passwords, and `.env` are automatically ignored by `.gitignore` and will never be exposed).*

---

## Step 2: Deploy Managed MySQL Database (Railway or Aiven)

You need a public MySQL 8.0 database accessible by Render.

### Option A: Railway (Recommended - Fastest)
1. Go to [https://railway.app](https://railway.app) and sign in with GitHub.
2. Click **+ New Project** -> Select **Provision MySQL**.
3. Once created, click the **MySQL** card -> Navigate to the **Variables** or **Connect** tab.
4. Copy the **`DATABASE_URL`** (or assemble: `mysql+pymysql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>?ssl_mode=REQUIRED`).

### Option B: Aiven MySQL (Free Forever tier)
1. Go to [https://aiven.io](https://aiven.io) and register.
2. Create a free **MySQL** service.
3. In the Overview tab, copy the **Service URI**.
4. Prefix it with `mysql+pymysql://` (e.g. `mysql+pymysql://avnadmin:<PASSWORD>@<HOST>:<PORT>/defaultdb?ssl_mode=REQUIRED`).

---

## Step 3: Deploy Backend to Render

1. Go to [https://dashboard.render.com](https://dashboard.render.com) and log in.
2. Click **New +** -> Select **Web Service**.
3. Choose **Build and deploy from a Git repository** -> Connect your GitHub repository (`ai-code-review-platform`).
4. Configure the service:
   - **Name:** `ai-code-review-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`
5. Under **Environment Variables**, add:
   | Key | Value | Description |
   | :--- | :--- | :--- |
   | `DATABASE_URL` | `mysql+pymysql://user:pass@host:port/dbname` | Your cloud MySQL connection string |
   | `SECRET_KEY` | *(Click "Generate" or paste a 64-char random string)* | Production JWT signing secret |
   | `APP_ENV` | `production` | Production environment flag |
   | `LLM_PROVIDER` | `gemini` | Gemini AI provider |
   | `LLM_API_KEY` | *(Your Google Gemini API Key)* | Free key from Google AI Studio |
   | `FRONTEND_URL` | `https://<your-app>.vercel.app` | *(Will be updated after Step 4)* |
6. Click **Create Web Service**.
7. Render will build and deploy your backend.
8. Once live, note your **Backend URL** (e.g., `https://ai-code-review-backend.onrender.com`).
9. Verify health probe in your browser: `https://ai-code-review-backend.onrender.com/health`.
   It should return:
   ```json
   {
     "status": "healthy",
     "database": {
       "connected": true,
       "message": "MySQL database connected successfully."
     }
   }
   ```

---

## Step 4: Deploy Frontend to Vercel

1. Go to [https://vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository (`ai-code-review-platform`).
4. In the configuration screen:
   - **Root Directory:** Click **Edit** and select `frontend`.
   - **Framework Preset:** `Vite` (auto-detected).
   - **Build Command:** `npm run build` (default).
   - **Output Directory:** `dist` (default).
5. Expand **Environment Variables**:
   | Key | Value |
   | :--- | :--- |
   | `VITE_API_URL` | `https://ai-code-review-backend.onrender.com` *(Your Render Backend URL)* |
6. Click **Deploy**.
7. Vercel will build the frontend in ~20 seconds and assign a public URL (e.g., `https://ai-code-review-platform.vercel.app`).
8. Return to Render -> Web Service -> **Environment Variables** -> Update `FRONTEND_URL` with your exact Vercel URL:
   `FRONTEND_URL=https://ai-code-review-platform.vercel.app`. Render will automatically restart.

---

## Step 5: Initialize Production Database Schema

The backend automatically creates all tables on startup. If you want to run the verification migration manually against your cloud database, run from your local terminal:

```powershell
$env:DATABASE_URL="mysql+pymysql://<USER>:<PASS>@<HOST>:<PORT>/<DB>?ssl_mode=REQUIRED"
$env:PYTHONPATH="backend"
python backend/init_db.py
```

Output:
```
[SUCCESS] MySQL database connected successfully.
[SUCCESS] Verified existing tables in database: ['code_reviews', 'findings', 'suggestions', 'users']
[SUCCESS] All required tables are present and ready for production traffic.
```

---

## Step 6: Multi-Device Verification Checklist

Open your public Vercel URL on:
- [x] **Windows PC Browser** (Chrome / Edge / Firefox)
- [x] **Laptop Browser**
- [x] **Android Mobile Browser** (Chrome / Samsung Internet)

### Verification Actions:
1. **Registration:**
   - Click **Register** -> Create a new account with your name, email, and password.
   - Verify that your account is saved in MySQL and JWT token is issued.
2. **Login & Persistence:**
   - Log out -> Log back in.
   - Refresh the page -> Verify authentication state persists.
3. **Analyze Sample Code:**
   - Go to **Review Studio**.
   - Click **Load Python Buggy Sample** -> Click **Analyze Code**.
   - Verify that:
     - Division by zero or security risks are detected with line numbers.
     - 5 Explainability dimensions are displayed (What happened, Where, Why, Evidence, Impact, How to fix).
     - ScoreCard displays Overall Score, Security, Correctness, Maintainability, Style, and Complexity.
     - CodeDiff viewer displays side-by-side or inline corrected code.
4. **History & Dashboard:**
   - Navigate to **Review History** -> Verify the review record is displayed.
   - Click **View Report** -> Verify the complete audit breakdown loads from MySQL.
   - Navigate to **Dashboard** -> Verify KPI cards (Total Reviews, Average Score, Issues Detected) update dynamically.

---

## Deployment Maintenance & Updates

### Pushing Code Updates:
```powershell
git add .
git commit -m "update: improvements"
git push origin main
```
- Vercel automatically redeploys the frontend in under 30 seconds.
- Render automatically redeploys the backend in under 2 minutes.

### Monitoring & Logs:
- **Backend Logs:** Check Render Dashboard -> **Logs** tab.
- **Frontend Logs:** Check Vercel Dashboard -> **Deployments** tab.
- **Health Check:** `https://<your-render-url>/health`
- **Swagger Docs:** `https://<your-render-url>/docs`
