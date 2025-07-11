#!/bin/bash

# This script automates the build, test, and deployment process.
# It first builds and tests the container locally. Only if the test passes
# will it proceed to deploy the application to Google Cloud Run.
set -e

# --- Configuration ---
PROJECT_ID="todolist-465520"
SERVICE_NAME="todo-flask-app"
REGION="us-central1"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# --- Build Stage ---
echo "--- STEP 1/4: Rebuilding the Docker image ---"
docker build --no-cache -t "${SERVICE_NAME}" .


# --- Local Test Stage ---
echo "--- STEP 2/4: Starting local container for testing ---"
# Run the container in detached mode and get its ID
CONTAINER_ID=$(docker run -d -p 8080:8080 "${SERVICE_NAME}")

# This 'trap' command ensures the container is stopped and removed when the script exits,
# whether it succeeds or fails. This is a critical cleanup step.
trap 'echo "--> Cleaning up local test container..."; docker stop ${CONTAINER_ID} > /dev/null && docker rm ${CONTAINER_ID} > /dev/null' EXIT

echo "--> Waiting for application to start..."
sleep 5 # Give the app a few seconds to initialize

echo "--> Testing the application's health..."
# Use curl to check if the root endpoint is responding with a success code.
# The --fail flag causes curl to exit with an error if the HTTP code is not 2xx.
curl --fail http://localhost:8080/

echo "--> ✅ Local test passed successfully!"


# --- Cloud Deploy Stage ---
echo "--- STEP 3/4: Pushing the image to Google Container Registry ---"
gcloud builds submit --tag "${IMAGE_TAG}"

echo "--- STEP 4/4: Deploying the new image to Cloud Run ---"
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_TAG}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated

echo "--- ✅ Deployment to ${SERVICE_NAME} complete! ---"
