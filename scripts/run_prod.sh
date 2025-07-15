#!/bin/bash

# This script builds the PRODUCTION version of our Docker image,
# runs it, and checks if it started successfully.

# Exit immediately if a command exits with a non-zero status.
set -e

# Use the production image name we defined earlier.
IMAGE_NAME="todo-flask-app-prod"

# --- Build Stage ---
echo "--- Building production Docker image: $IMAGE_NAME ---"
# We build the full Dockerfile here, without the --target flag,
# to create the final, lightweight production image.
docker build -t "$IMAGE_NAME" .
echo ""

echo "--- Starting container in the background ---"
# The production stage of the Dockerfile exposes port 8080.
# We map our local port 8080 to the container's port 8080.
CONTAINER_ID=$(docker run -d -p 8080:8080 "$IMAGE_NAME")

# This 'trap' command ensures the container is always stopped and removed
# when the script exits, no matter what happens.
trap 'echo ""; echo "--- Cleaning up container $CONTAINER_ID ---"; docker stop $CONTAINER_ID > /dev/null && docker rm $CONTAINER_ID > /dev/null' EXIT

echo "--- Waiting 5 seconds to check container health ---"
sleep 5

# Check if the container is still running.
if [ -z "$(docker ps -q -f "id=$CONTAINER_ID")" ]; then
    # If the command returns an empty string, the container is not running.
    echo "❌ ERROR: Container failed to start. Displaying logs:"
    echo "----------------------------------------------------"
    docker logs $CONTAINER_ID
    echo "----------------------------------------------------"
    exit 1
else
    # The container is running successfully.
    echo "✅ SUCCESS: Container is running."
    echo "--- Your app is available at http://localhost:8080 ---"
    echo "--- Attaching to container logs. Press Ctrl+C to stop. ---"
    docker attach $CONTAINER_ID
fi
```

Save this code as a new file named `run_prod.sh` in your project's root directory. Make sure to give it execute permissions with the command `chmod +x run_prod.sh`.

Now you can simply run `./run_prod.sh` to build and test your final production container local
