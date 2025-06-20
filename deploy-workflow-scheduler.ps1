# Deploy ANIPE Cloud Workflow and Scheduler
# This script deploys the Cloud Workflow and sets up a Cloud Scheduler job

# Set your project ID
$PROJECT_ID = "windsurf-ai-project"
$REGION = "us-central1"
$WORKFLOW_NAME = "anipe-workflow"
$JOB_NAME = "anipe-daily-job"

Write-Host "=== ANIPE Workflow & Scheduler Deployment Script ===" -ForegroundColor Green
Write-Host "This script will deploy the Cloud Workflow and set up a Cloud Scheduler job" -ForegroundColor Green
Write-Host ""

# Step 1: Deploy the Cloud Workflow
Write-Host "Deploying Cloud Workflow..." -ForegroundColor Cyan

# Replace placeholders with actual Cloud Run service URLs
Write-Host "First, let's get the actual URLs for your deployed services..." -ForegroundColor Yellow
Write-Host "Fetching Opportunity Identifier URL..."
$OPPORTUNITY_URL = gcloud run services describe anip-opportunity-identifier --format="value(status.url)" --platform managed --region $REGION
Write-Host "Opportunity Identifier URL: $OPPORTUNITY_URL" -ForegroundColor Yellow

Write-Host "Fetching Product Generator URL..."
$PRODUCT_URL = gcloud run services describe anip-product-generator --format="value(status.url)" --platform managed --region $REGION
Write-Host "Product Generator URL: $PRODUCT_URL" -ForegroundColor Yellow

# Update the workflow file with actual URLs
Write-Host "Updating workflow YAML with actual service URLs..." -ForegroundColor Yellow
$workflow_content = Get-Content "anipe-workflow.yaml" -Raw
$workflow_content = $workflow_content.Replace("anip-opportunity-identifier-URL_PLACEHOLDER.run.app", $OPPORTUNITY_URL.Replace("https://", ""))
$workflow_content = $workflow_content.Replace("anip-product-generator-URL_PLACEHOLDER.run.app", $PRODUCT_URL.Replace("https://", ""))
$workflow_content | Set-Content "anipe-workflow-updated.yaml" -Force
Write-Host "Updated workflow YAML created." -ForegroundColor Green

# Deploy the workflow
Write-Host "Deploying workflow to Google Cloud..." -ForegroundColor Yellow
gcloud workflows deploy $WORKFLOW_NAME --source="anipe-workflow-updated.yaml" --location=$REGION
Write-Host "Workflow deployed!" -ForegroundColor Green

# Step 2: Create a Cloud Scheduler job to trigger the workflow
Write-Host "Creating Cloud Scheduler job..." -ForegroundColor Cyan

# Create service account for the Cloud Scheduler
$SCHEDULER_SA = "anipe-scheduler-sa"
$SCHEDULER_SA_EMAIL = "$SCHEDULER_SA@$PROJECT_ID.iam.gserviceaccount.com"

Write-Host "Creating service account for Cloud Scheduler..." -ForegroundColor Yellow
gcloud iam service-accounts create $SCHEDULER_SA --display-name "ANIPE Scheduler Service Account"
Write-Host "Granting Workflow Invoker role to service account..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SCHEDULER_SA_EMAIL" --role="roles/workflows.invoker"
Write-Host "Service account created and role assigned." -ForegroundColor Green

# Create the scheduler job (set to run daily at 2:00 AM)
Write-Host "Creating Cloud Scheduler job to run daily at 2:00 AM..." -ForegroundColor Yellow
gcloud scheduler jobs create http $JOB_NAME `
    --location=$REGION `
    --schedule="0 2 * * *" `
    --uri="https://workflowexecutions.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/workflows/$WORKFLOW_NAME/executions" `
    --http-method=POST `
    --oauth-service-account-email=$SCHEDULER_SA_EMAIL `
    --headers="Content-Type=application/json" `
    --message-body="{}"

Write-Host "Cloud Scheduler job created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "=== ANIPE Autonomous System Deployment Complete! ===" -ForegroundColor Green
Write-Host "Your ANIPE system is now fully deployed and will run automatically every day at 2:00 AM." -ForegroundColor Green
Write-Host ""
Write-Host "To manually execute the workflow, run:" -ForegroundColor Yellow
Write-Host "gcloud workflows run $WORKFLOW_NAME --location=$REGION" -ForegroundColor Yellow
Write-Host ""
Write-Host "To view execution history, visit the Google Cloud Console:" -ForegroundColor Yellow
Write-Host "https://console.cloud.google.com/workflows/workflow/$WORKFLOW_NAME?project=$PROJECT_ID" -ForegroundColor Yellow
