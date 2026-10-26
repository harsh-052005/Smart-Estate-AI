# 🚀 Render Deployment Guide — Smart Estate AI

This guide provides step-by-step instructions to deploy the **Smart Estate AI** full-stack machine learning platform onto [Render](https://render.com/) on the **100% Free Tier**.

---

## ⚡ Method 1: One-Click Blueprint Deployment (Recommended)

Render Blueprints allow you to deploy the entire stack using the included Infrastructure-as-Code file [`render.yaml`](file:///Users/harsh/Desktop/Smart%20Estate%20AI/render.yaml).

### Steps:
1. Ensure your latest changes are pushed to GitHub:
   ```bash
   git add .
   git commit -m "feat: configure render deployment blueprint, build script, and dockerfile"
   git push origin main
   ```
2. Navigate to your [Render Dashboard](https://dashboard.render.com/).
3. Click the **New +** button in the top navigation bar and select **Blueprint**.
4. Connect your GitHub repository: `harsh-052005/Smart-Estate-AI`.
5. Render will automatically detect [`render.yaml`](file:///Users/harsh/Desktop/Smart%20Estate%20AI/render.yaml) and pre-populate all parameters:
   - **Service Name**: `smart-estate-ai`
   - **Runtime**: `Docker` (Multi-stage build with Node 20 + Python 3.11 + XGBoost runtime)
   - **Dockerfile**: `./Dockerfile`
   - **Port**: `10000`
   - **Health Check Path**: `/api/health`
6. Click **Apply** (or **Manual sync** if already created).
7. Wait 2–3 minutes for the build and deployment to complete. Your application will be live at `https://smart-estate-ai.onrender.com`!

---

## 🛠️ Method 2: Manual Web Service Setup on Render

If you prefer configuring the Web Service manually via the Render UI:

1. Go to [Render Dashboard](https://dashboard.render.com/) -> **New +** -> **Web Service**.
2. Select your GitHub repository: `harsh-052005/Smart-Estate-AI`.
3. Fill in the configuration details:
   - **Name**: `smart-estate-ai`
   - **Region**: Oregon (US West) or Frankfurt (EU)
   - **Branch**: `main`
   - **Root Directory**: *(leave blank)*
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     ./build.sh
     ```
   - **Start Command**:
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`
4. Expand **Advanced** -> **Add Environment Variable**:
   | Key | Value | Purpose |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.9` | Enforces modern Python runtime |
   | `NODE_VERSION` | `20.18.0` | Enables Node.js/npm for frontend build |
5. In **Health Check Path**, enter: `/api/health`
6. Click **Create Web Service**.

---

## 🐳 Method 3: Docker Deployment on Render

A production-ready multi-stage [`Dockerfile`](file:///Users/harsh/Desktop/Smart%20Estate%20AI/Dockerfile) is also provided. This packages the Node.js frontend compiler and Python ML inference engine into an isolated image:

1. In Render Dashboard, click **New +** -> **Web Service**.
2. Select `Smart-Estate-AI` repository.
3. Choose **Docker** as the Runtime.
4. Keep the default Dockerfile path `./Dockerfile`.
5. Click **Create Web Service**.

---

## 🔍 Verification & Health Check

Once deployed, you can verify your service:
- **Frontend SPA**: `https://<your-render-subdomain>.onrender.com/`
- **Backend Health Check**: `https://<your-render-subdomain>.onrender.com/api/health`
- **Interactive Swagger Docs**: `https://<your-render-subdomain>.onrender.com/docs`
- **Valuation Inference API**: `https://<your-render-subdomain>.onrender.com/api/predict`

> **Note on Free Tier Sleep Mode**:
> Render's free tier services automatically spin down after 15 minutes of inactivity. When a new request arrives, Render spins up the container within 30–50 seconds. Subsequent requests respond in sub-50 milliseconds.
