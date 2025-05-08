# Use an official Python base
FROM python:3.11-slim

# Allow build-time override of host UID/GID
ARG HOST_UID=1000
ARG HOST_GID=1000

# Create group and user with matching IDs
RUN groupadd --gid ${HOST_GID} appgroup \
    && useradd --uid ${HOST_UID} --gid appgroup --shell /bin/bash --create-home appuser

# Install dependencies as root
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of your code and chown it
COPY . .
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Default command
CMD ["python", "src/main.py"]
