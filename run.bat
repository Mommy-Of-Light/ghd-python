@echo off
docker build -t console-file-manager:latest .
cls
docker-compose run --rm fm
cls