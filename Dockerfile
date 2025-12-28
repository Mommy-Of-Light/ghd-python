# Use Python slim image
FROM python:3.11-slim

# Install nano & dos2unix
RUN apt-get update && apt-get install -y --no-install-recommends \
    nano \
    dos2unix \
 && rm -rf /var/lib/apt/lists/*

# Create workspace
RUN mkdir -p /home/user
WORKDIR /home/user

# Copy extracted data into container
COPY container_root/home/user/ /home/user/

# Create protected folder for main app files
RUN mkdir -p /usr/local/fm

# Copy main script and class folder
COPY src/main.py /usr/local/fm/main.py
COPY src/classes /usr/local/fm/classes

# Convert line endings to LF (fix Windows CRLF issue)
RUN dos2unix /usr/local/fm/main.py

# (Optional) convert line endings in class folder too
COPY src/classes /usr/local/fm/classes
RUN find /usr/local/fm/classes -type f -exec dos2unix {} \;

# Make main script executable
RUN chmod +x /usr/local/fm/main.py

# Create symlink in PATH for convenience
RUN ln -s /usr/local/fm/main.py /usr/local/bin/fm

ENV PYTHONPATH=/usr/local/fm

# Default entrypoint
ENTRYPOINT ["fm"]
