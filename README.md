# ANIPE - Autonomous Niche Intelligence & Product Engine

🚀 **An AI-powered system that autonomously identifies niche market opportunities and generates digital products**

ANIPE is a self-sustaining system designed to generate income by discovering profitable niches and creating digital products automatically. It uses advanced AI to analyze market trends, identify opportunities, and generate comprehensive product packages.

## 🏗️ Architecture

ANIPE consists of two main microservices:

1. **Opportunity Identifier Service** (`anip-opportunity-identifier.py`)
   - Analyzes market trends and web search data
   - Uses Vertex AI Gemini to identify profitable niches
   - Stores opportunities in Google Cloud Storage

2. **Product Generator Service** (`anip-product-generator.py`)
   - Takes identified opportunities as input
   - Generates comprehensive digital product content
   - Creates detailed product packages with marketing materials

## 🚀 Deployment Options

### Option 1: GitHub + Google Cloud Console (Recommended)

1. **Fork or Clone this Repository**
   ```bash
   git clone <your-github-repo-url>
   cd anipe-deployment
   ```

2. **Deploy via Google Cloud Console**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to **Cloud Run** > **Create Service**
   - Select **"Continuously deploy from a repository"**
   - Connect your GitHub repository
   - Set up automated deployments

### Option 2: Google Cloud Shell Deployment

1. **Open Cloud Shell**: https://shell.cloud.google.com
2. **Clone your repository**:
   ```bash
   git clone <your-github-repo-url>
   cd anipe-deployment
   ```
3. **Set your project**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```
4. **Enable APIs**:
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
     artifactregistry.googleapis.com cloudscheduler.googleapis.com \
     workflows.googleapis.com aiplatform.googleapis.com storage.googleapis.com
   ```
5. **Deploy Opportunity Identifier**:
   ```bash
   gcloud run deploy anip-opportunity-identifier \
     --source . \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars GCS_BUCKET_NAME=YOUR_BUCKET_NAME,GCP_PROJECT_ID=YOUR_PROJECT_ID,GCP_REGION=us-central1
   ```
6. **Deploy Product Generator**:
   ```bash
   gcloud run deploy anip-product-generator \
     --source . \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars GCS_BUCKET_NAME=YOUR_BUCKET_NAME,GCP_PROJECT_ID=YOUR_PROJECT_ID,GCP_REGION=us-central1
   ```

### Option 3: Manual Cloud Console Deployment

1. **Go to Cloud Run** in Google Cloud Console
2. **Create Service** > **Deploy one revision from source**
3. **Source**: Upload files or connect Git repository
4. **Container**: Will be built automatically
5. **Set Environment Variables**:
   - `GCS_BUCKET_NAME`: Your bucket name
   - `GCP_PROJECT_ID`: Your project ID
   - `GCP_REGION`: us-central1
6. **Allow unauthenticated invocations**: 
7. **Deploy**

## 🔧 Prerequisites

### 1. Google Cloud Project Setup
- Create a GCP project: https://console.cloud.google.com
- Enable billing for your project
- Note your Project ID

### 2. Create GCS Bucket
```bash
gsutil mb gs://YOUR_BUCKET_NAME
```

### 3. Service Account (Optional but Recommended)
```bash
gcloud iam service-accounts create anipe-service-account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:anipe-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:anipe-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## 🤖 Automation Setup

### Deploy Cloud Workflow (Optional)
```bash
# Deploy the workflow that orchestrates both services
gcloud workflows deploy anipe-workflow \
  --source=anipe-workflow.yaml \
  --location=us-central1
```

### Schedule Daily Execution (Optional)
```bash
# Create a Cloud Scheduler job to run daily at 2 AM
gcloud scheduler jobs create http anipe-daily-job \
  --schedule="0 2 * * *" \
  --http-method=POST \
  --uri="https://workflowexecutions-us-central1.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/workflows/anipe-workflow/executions" \
  --headers="Authorization=Bearer $(gcloud auth print-access-token)" \
  --time-zone="America/New_York"
```

## 📁 File Structure
```
anipe-deployment/
├── anip-opportunity-identifier.py  # Main opportunity service
├── anip-product-generator.py       # Main product service
├── requirements-opportunity.txt    # Dependencies for opportunity service
├── requirements-product.txt        # Dependencies for product service
├── Dockerfile.opportunity          # Container config for opportunity service
├── Dockerfile.product             # Container config for product service
├── cloudbuild-opportunity.yaml    # Cloud Build config for opportunity service
├── cloudbuild-product.yaml        # Cloud Build config for product service
├── anipe-workflow.yaml            # Cloud Workflow orchestration
├── deploy-anipe.ps1               # PowerShell deployment script
├── deploy-workflow-scheduler.ps1  # PowerShell workflow/scheduler script
└── README.md                      # This file
```

## 🔗 API Endpoints

Once deployed, your services will have these endpoints:

### Opportunity Identifier
- **POST** `/identify` - Find new niche opportunities
- **GET** `/health` - Health check

### Product Generator  
- **POST** `/generate` - Generate product from opportunity
- **GET** `/health` - Health check

## 🧪 Testing

### Test Opportunity Identifier
```bash
curl -X POST "https://YOUR_OPPORTUNITY_SERVICE_URL/identify" \
  -H "Content-Type: application/json" \
  -d '{"trend_keywords": ["AI automation", "remote work"]}'
```

### Test Product Generator
```bash
curl -X POST "https://YOUR_PRODUCT_SERVICE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"opportunity": "AI-powered remote work tools", "market_size": "large"}'
```

## 🔍 Monitoring

- **Cloud Console**: Monitor services at https://console.cloud.google.com/run
- **Logs**: View logs in Cloud Logging
- **Metrics**: Monitor performance and costs in Cloud Monitoring

## 💰 Cost Optimization

- Services automatically scale to zero when not in use
- Pay only for actual usage (requests + compute time)
- Expected cost: $0.10-$5.00/month for typical usage

## 🛠️ Troubleshooting

### Common Issues

1. **"Permission Denied" errors**
   - Ensure your service account has required IAM roles
   - Verify APIs are enabled

2. **"Bucket not found" errors**
   - Create the GCS bucket: `gsutil mb gs://YOUR_BUCKET_NAME`
   - Verify bucket name in environment variables

3. **Vertex AI errors**
   - Ensure Vertex AI API is enabled
   - Verify your project has Vertex AI access

4. **Build failures**
   - Check requirements.txt files are present
   - Verify Python dependencies are compatible

### Support

For issues or questions:
1. Check Google Cloud Status: https://status.cloud.google.com
2. Review Cloud Build logs in Console
3. Check service logs in Cloud Logging

## 🎯 Usage

1. **Manual Trigger**: Call the `/identify` endpoint to find opportunities
2. **Automated**: Set up Cloud Scheduler for daily execution
3. **Results**: Check your GCS bucket for generated opportunities and products

The system is designed to run autonomously and generate income-producing digital products without manual intervention.
