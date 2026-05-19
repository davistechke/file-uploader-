# CrackedApp 🔓

Free premium app download site with admin upload panel.

## Deploy on Render (3 steps)

### Step 1 — Upload to GitHub
Push this folder to a GitHub repo.

### Step 2 — Create Render Web Service
1. Go to https://render.com → New → Web Service
2. Connect your GitHub repo
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120`

### Step 3 — Add Environment Variables
In Render → your service → Environment:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | (any long random string) |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_PASSWORD` | `root` |

### Step 4 — Add a Disk (IMPORTANT)
So uploaded files survive redeploys:
1. Render → your service → **Disks** tab
2. Add disk:
   - **Name**: `uploads`
   - **Mount Path**: `/opt/render/project/src/static/uploads`
   - **Size**: 1 GB (or more)

---

## Admin Login
- URL: `https://your-app.onrender.com/admin`
- Username: `test`
- Password: `root`

## Local Development
```bash
pip install -r requirements.txt
python app.py
```
Visit https://crackedapps.onrender.com
