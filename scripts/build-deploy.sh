#!/bin/bash

# This script automates the build and deployment process for the Flask To-Do List application.
# It ensures that if any step fails, the script will exit immediately.
set -e

# --- Configuration ---
# You can change these variables if you ever reuse this script for another project.
PROJECT_ID="todolist-465520"
SERVICE_NAME="todo-flask-app"
REGION="us-central1"

# The full tag for the container image in Google Container Registry.
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"


# --- Deployment Steps ---

echo "--- Starting deployment for ${SERVICE_NAME} ---"

# Step 1: Rebuild the Docker image.
# The --no-cache flag is used here to ensure that any changes to your
# Dockerfile or .dockerignore are always applied.
echo "--> STEP 1/3: Rebuilding the Docker image..."
docker build --no-cache -t "${SERVICE_NAME}" .

# Step 2: Push the new image to Google Container Registry (via Cloud Build).
echo "--> STEP 2/3: Pushing the image to Google Container Registry..."
gcloud builds submit --tag "${IMAGE_TAG}"

# Step 3: Redeploy the service on Cloud Run with the new image.
echo "--> STEP 3/3: Deploying the new image to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_TAG}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated

echo "--- ✅ Deployment to ${SERVICE_NAME} successful! ---"

