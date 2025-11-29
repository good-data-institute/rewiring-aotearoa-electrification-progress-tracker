# Deployment Checklist for Render

## Changes Made for Multipage Dashboard

### Files Updated
✅ **Dockerfile**
- Changed backend port from 8000 → 8001
- Updated Streamlit entry point: `streamlit_app.py` → `Introduction.py`
- Expose port 8001 instead of 8000

✅ **.env.example**
- Updated default `BACKEND_PORT=8001`

✅ **Documentation Files**
- README.md
- ARCHITECTURE.md
- MULTIPAGE_IMPLEMENTATION.md
- Workspace-1.md

### New Files Created
✅ **Frontend Structure**
- `frontend/Introduction.py` (renamed from streamlit_app.py)
- `frontend/pages/0_🏠_Overview.py`
- `frontend/pages/1_🚗_Transport_Electrification.py`
- `frontend/pages/2_⚡_Energy_Grid.py`
- `frontend/pages/3_🏠_Buildings_&_Heating.py`
- `frontend/pages/4_☀️_Solar_&_Batteries.py`
- `frontend/pages/5_🗺️_Regional_Deep_Dive.py`
- `frontend/pages/6_📊_Cross_Sector_Analysis.py`
- `frontend/pages/7_💾_Data_Explorer.py`

✅ **Backend Updates**
- `backend/repository.py` - Added 7 new dataset mappings

✅ **Utilities**
- `frontend/dashboard_utils.py` - Enhanced with district mapping, pagination

✅ **Configuration**
- `.streamlit/config.toml` - Streamlit configuration

## Deployment Process

### When Merged to Main Branch

Render will automatically:

1. **Detect Changes** - Watches `main` branch (configured in `render.yaml`)
2. **Build Docker Image** - Uses `Dockerfile` with updated paths
3. **Start Services**:
   - Backend FastAPI on port 8001
   - Streamlit on port assigned by Render (usually 8501 or `$PORT`)
4. **Health Check** - Render checks if service responds on assigned port

### Environment Variables on Render

Ensure these are set in Render Dashboard → Environment:

```bash
# Required (already in .env.example, Render will use these)
DATA_DIR=./data
BACKEND_HOST=localhost
BACKEND_PORT=8001

# Optional (Render provides automatically)
PORT=<assigned-by-render>
```

### Expected Behavior

✅ **Home Page**: Shows "Introduction" in sidebar (not "streamlit app")
✅ **Navigation**: 8 pages accessible via sidebar (Introduction + 7 pages)
✅ **Backend API**: Running on internal port 8001
✅ **Health Check**: `Introduction.py` checks backend at `http://localhost:8001/health`

## Testing Before Deployment

### Local Testing (matches production)

```bash
# Terminal 1: Start backend
python -m backend.main

# Terminal 2: Start Streamlit
streamlit run frontend/Introduction.py

# Verify:
# - http://localhost:8501 shows "Introduction" page
# - All 8 pages load in sidebar
# - Backend health check passes (green checkmark)
# - District/region toggle works in Transport page
# - Pagination works in Data Explorer
```

### Docker Testing (exact production environment)

```bash
# Build and run locally
docker build -t electrification-tracker .
docker run -p 8501:8501 -p 8001:8001 electrification-tracker

# Verify:
# - http://localhost:8501 accessible
# - All pages work correctly
# - No 404 errors in browser console
```

## Post-Deployment Verification

After merge to `main` and Render deployment:

1. **Check Render Logs**:
   - Look for "Starting backend server..." message
   - Look for "Starting Streamlit dashboard..." message
   - Check for any Python import errors

2. **Access Live URL**:
   - Navigate to your Render URL (e.g., `https://electrification-dashboard.onrender.com`)
   - Verify sidebar shows "Introduction" page
   - Click through all 8 pages
   - Test filters and interactive elements

3. **Backend Health**:
   - Landing page should show "✓ Backend API is connected and healthy"
   - If red error, check Render logs for backend startup issues

## Troubleshooting

### Common Issues

**Issue**: "Backend API is not available"
- **Cause**: Backend not starting or port mismatch
- **Fix**: Check Render logs, ensure BACKEND_PORT=8001 in environment

**Issue**: Pages not showing in sidebar
- **Cause**: `frontend/pages/` directory not copied to Docker
- **Fix**: Verify Dockerfile has `COPY frontend/ frontend/`

**Issue**: "streamlit app" still showing instead of "Introduction"
- **Cause**: Old cached build or wrong file
- **Fix**: Force rebuild on Render or verify `Introduction.py` exists

**Issue**: Import errors for dashboard_utils
- **Cause**: Missing parent directory in sys.path
- **Fix**: All page files have `sys.path.append()` at top

## Rollback Plan

If deployment fails:

1. **Quick Rollback**:
   - Revert merge commit on `main` branch
   - Render auto-deploys previous working version

2. **Manual Fix**:
   - Update `render.yaml` to point to specific commit/tag
   - Redeploy from Render dashboard

## Files That Should NOT Be Modified

- `render.yaml` - Render configuration (already correct)
- `pyproject.toml` - Dependencies (no changes needed)
- `.gitignore` - Git ignores (already includes .env)
- Backend code (no changes needed except repository.py)

## Verification Checklist

Before merging to main:

- [ ] All 8 page files created in `frontend/pages/`
- [ ] `Introduction.py` exists (renamed from streamlit_app.py)
- [ ] `dashboard_utils.py` enhanced with new functions
- [ ] `backend/repository.py` has 7 new dataset mappings
- [ ] `Dockerfile` references `Introduction.py`
- [ ] `.env.example` has `BACKEND_PORT=8001`
- [ ] All documentation updated (README, ARCHITECTURE, etc.)
- [ ] Local testing passes
- [ ] Docker build succeeds locally

## Success Metrics

Deployment is successful when:

✅ Render build completes without errors
✅ Service is "Live" in Render dashboard
✅ Landing page loads with "Introduction" in sidebar
✅ All 8 pages accessible and functional
✅ Backend health check shows green checkmark
✅ No JavaScript errors in browser console
✅ Transport page district/region toggle works
✅ Data Explorer pagination works with large datasets
