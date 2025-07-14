#!/bin/bash

# This script builds the DEVELOPMENT version of our Docker image,
# runs it, and checks if it started successfully.

# Exit immediately if a command exits with a non-zero status.
set -e

IMAGE_NAME="todo-flask-app-dev"

# --- Build Stage ---
echo "--- Building development Docker image: $IMAGE_NAME ---"
# The --target flag tells Docker to stop at the "builder" stage.
docker build --target builder -t "$IMAGE_NAME" .
echo ""

echo "--- Starting container in the background ---"
# Start the container in detached (-d) mode and capture its ID
CONTAINER_ID=$(docker run -d -p 5000:5000 "$IMAGE_NAME")

# This 'trap' command ensures the container is always stopped and removed
# when the script exits, no matter what happens.
trap 'echo ""; echo "--- Cleaning up container $CONTAINER_ID ---"; docker stop $CONTAINER_ID > /dev/null && docker rm $CONTAINER_ID > /dev/null' EXIT

echo "--- Waiting 5 seconds to check container health ---"
sleep 5

# Check if the container is still running.
# `docker ps -q` lists running container IDs. We filter for our specific ID.
if [ -z "$(docker ps -q -f "id=$CONTAINER_ID")" ]; then
    # If the command returns an empty string, the container is not running.
    echo "❌ ERROR: Container failed to start. Displaying logs:"
    echo "----------------------------------------------------"
    # The container crashed, so print its logs to show the error.
    docker logs $CONTAINER_ID
    echo "----------------------------------------------------"
    # Exit with an error code to signal failure.
    exit 1
else
    # The container is running successfully.
    echo "✅ SUCCESS: Container is running."
    echo "--- Attaching to container logs. Press Ctrl+C to stop. ---"
    # Attach to the running container's logs so you can see live output.
    docker attach $CONTAINER_ID
fi
