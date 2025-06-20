# Deploy ANIPE services to Google Cloud Run
# This script deploys both ANIPE services to Cloud Run

# Set your project ID
$PROJECT_ID = "windsurf-ai-project"
$REGION = "us-central1"
$GCS_BUCKET_NAME = "windsurf-anipe-data"
$VERSION = "v1.0"

Write-Host "=== ANIPE Deployment Script ===" -ForegroundColor Green
Write-Host "This script will deploy the ANIPE services to Google Cloud Run" -ForegroundColor Green
Write-Host ""

# Enable required APIs
Write-Host "Ensuring required APIs are enabled..." -ForegroundColor Cyan
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com cloudscheduler.googleapis.com workflows.googleapis.com

# Function to deploy a service
function Deploy-Service {
    param (
        [string]$ServiceName,
        [string]$ServiceFileName,
        [string]$DockerfileName,
        [string]$BuildConfigFile
    )
    
    Write-Host "Deploying $ServiceName..." -ForegroundColor Cyan
    
    # Build and push the container image using Cloud Build
    Write-Host "Building and deploying with Cloud Build..."
    gcloud builds submit --config $BuildConfigFile --substitutions=_VERSION=$VERSION,_REGION=$REGION,_GCS_BUCKET_NAME=$GCS_BUCKET_NAME .
    
    Write-Host "$ServiceName deployment completed!" -ForegroundColor Green
    Write-Host ""
}

# Deploy Opportunity Identifier Service
Deploy-Service -ServiceName "ANIPE Opportunity Identifier" -ServiceFileName "anip-opportunity-identifier.py" -DockerfileName "Dockerfile-opportunity.txt" -BuildConfigFile "cloudbuild-opportunity.yaml"

# Deploy Product Generator Service
Deploy-Service -ServiceName "ANIPE Product Generator" -ServiceFileName "anip-product-generator.py" -DockerfileName "Dockerfile-product.txt" -BuildConfigFile "cloudbuild-product.yaml"

Write-Host "All ANIPE services have been deployed successfully!" -ForegroundColor Green
Write-Host "Your ANIPE services are now available at the following URLs:" -ForegroundColor Green
Write-Host " - Opportunity Identifier: https://anip-opportunity-identifier-[service-hash].run.app" -ForegroundColor Yellow
Write-Host " - Product Generator: https://anip-product-generator-[service-hash].run.app" -ForegroundColor Yellow
Write-Host ""
Write-Host "NOTE: Replace [service-hash] with the actual service URL from your GCP Console" -ForegroundColor Yellow
