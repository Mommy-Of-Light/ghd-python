#!/bin/bash
# Exit on error
set -e

# Build the Docker image
docker build -t console-file-manager:latest .

# Clear the terminal
clear

# Run the container using docker-compose
docker-compose run --rm fm

# Clear the screen at the end to leave the shell empty
clear