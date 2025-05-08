# Dockerfile
# Use an official Python base
FROM python:3.11-slim

# Allow build-time override of host UID/GID
ARG HOST_UID=1000
ARG HOST_GID=1000

# Create group and user with matching IDs
RUN groupadd --gid ${HOST_GID} appgroup \
    && useradd --uid ${HOST_UID} --gid appgroup --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy and install dependencies as root
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Install gosu for permission management
RUN apt-get update && \
    apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/*

# Copy and configure entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Copy application code and set ownership
COPY . .
RUN chown -R appuser:appgroup /app

# Use the entrypoint to manage permissions and drop privileges
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default command (will be run as appuser via gosu in entrypoint)
CMD ["python", "src/main.py"]