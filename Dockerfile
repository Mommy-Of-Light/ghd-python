# Use Python slim image
FROM python:3.11-slim

# Install nano & dos2unix
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nano \
        dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /home/user

# Copy extracted data into container
COPY container_root/home/user/ /home/user/

# Create protected folder and install application
RUN mkdir -p /usr/local/fm

COPY src/main.py /usr/local/fm/main.py
COPY src/classes /usr/local/fm/classes

# Convert Windows CRLF line endings to Unix LF,
# make the application executable, and create its PATH symlink
RUN dos2unix /usr/local/fm/main.py \
    && find /usr/local/fm/classes -type f -exec dos2unix {} \; \
    && chmod +x /usr/local/fm/main.py \
    && ln -s /usr/local/fm/main.py /usr/local/bin/fm

ENV PYTHONPATH=/usr/local/fm

# Default entrypoint
ENTRYPOINT ["fm"]