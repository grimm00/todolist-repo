#!/bin/bash

# Get the first running container ID
container_id=$(docker ps -q | head -n 1)

if [ -z "$container_id" ]; then
  echo "No running containers found."
  exit 1
fi

# Exec into the container
exec docker exec -it $container_id /bin/bash
