# ANIPE GitHub Deployment Guide

## 🚀 Quick Start

Your ANIPE deployment package is ready! Here's how to get it running on GitHub + Google Cloud Run.

## 📦 Package Contents

### Core Application Files
- `anip-opportunity-identifier.py` - AI service for finding niche opportunities
- `anip-product-generator.py` - AI service for generating digital products
- `requirements-opportunity.txt` - Dependencies for opportunity service
- `requirements-product.txt` - Dependencies for product service

### Container Configuration
- `Dockerfile.opportunity` - Container for opportunity identifier
- `Dockerfile.product` - Container for product generator
- `cloudbuild-opportunity.yaml` - Cloud Build config for opportunity service
- `cloudbuild-product.yaml` - Cloud Build config for product service

### Orchestration
- `anipe-workflow.yaml` - Cloud Workflow for service orchestration
- `deploy-anipe.ps1` - PowerShell deployment script (local)
- `deploy-workflow-scheduler.ps1` - PowerShell workflow deployment (local)

### GitHub Integration
- `.github/workflows/deploy-anipe.yml` - GitHub Actions for automated deployment
- `.gitignore` - Git ignore rules
- `README.md` - Comprehensive documentation
- `DEPLOYMENT_GUIDE.md` - This file

## 🔧 GitHub Setup Instructions

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (e.g., `anipe-deployment`)
3. Initialize with README (optional, we have our own)

### Step 2: Upload Files to GitHub
```bash
# Navigate to your project folder
cd "C:\Projects\The Machine\Content Empire"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit files
git commit -m "Initial ANIPE deployment package"

# Add GitHub remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/anipe-deployment.git

# Push to GitHub
git push -u origin main
```

### Step 3: Configure GitHub Secrets
In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add:

1. **`GCP_PROJECT_ID`** - Your Google Cloud Project ID (e.g., `windsurf-ai-project`)
2. **`GCS_BUCKET_NAME`** - Your GCS bucket name (e.g., `windsurf-anipe-data`)
3. **`GCP_SA_KEY`** - Your service account JSON key (see below)

### Step 4: Create Service Account Key
```bash
# Create service account
gcloud iam service-accounts create anipe-github-deploy

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:anipe-github-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:anipe-github-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:anipe-github-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/workflows.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:anipe-github-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudscheduler.admin"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=anipe-github-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Copy the entire contents of key.json and paste as GCP_SA_KEY secret
```

## 🎯 Deployment Options

### Option A: Automated GitHub Deployment (Recommended)
1. Push code to GitHub `main` branch
2. GitHub Actions will automatically deploy to Google Cloud Run
3. Services will be live within 5-10 minutes

### Option B: Manual Deployment
Follow the detailed instructions in `README.md` for manual deployment via Google Cloud Console or Cloud Shell.

## 🔗 After Deployment

Once deployed, your ANIPE system will:
- **Opportunity Identifier**: Available at `https://anip-opportunity-identifier-[hash]-uc.a.run.app`
- **Product Generator**: Available at `https://anip-product-generator-[hash]-uc.a.run.app`
- **Automated Workflow**: Runs daily at 2:00 AM
- **Results**: Stored in your GCS bucket

## 🧪 Testing Your Deployment

```bash
# Test opportunity identifier
curl -X POST "https://YOUR_OPPORTUNITY_SERVICE_URL/identify" \
  -H "Content-Type: application/json" \
  -d '{"trend_keywords": ["AI automation", "remote work"]}'

# Test product generator
curl -X POST "https://YOUR_PRODUCT_SERVICE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"opportunity": "AI-powered remote work tools", "market_size": "large"}'
```

## 💰 Expected Costs
- **Development/Testing**: $0-$1/month
- **Production**: $5-$25/month (depending on usage)
- **First 300 requests**: Free tier

## 🎉 Success Indicators
- ✅ Both Cloud Run services show "Healthy" status
- ✅ Cloud Workflow executes without errors
- ✅ Cloud Scheduler job is created and active
- ✅ Files appear in your GCS bucket after workflow execution

Your ANIPE system is now ready to autonomously generate income through AI-powered niche identification and digital product creation!
