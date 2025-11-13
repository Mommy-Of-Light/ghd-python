# Build the Docker image
docker build -t console-file-manager:latest .

# Clear the screen
Clear-Host

# Run the container using docker-compose
docker-compose run --rm fm

# Clear the screen at the end to leave the shell empty
Clear-Host