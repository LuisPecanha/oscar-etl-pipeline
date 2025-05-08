FROM python:3.11-slim

ARG USER_ID
ARG GROUP_ID

# Install gosu for privilege drop
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

# Create group if missing, then user with host UID:GID
RUN getent group ${GROUP_ID} || groupadd -g ${GROUP_ID} appgroup \
    && useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application code
COPY . .

# Entrypoint script to fix permissions and drop privileges
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "src/main.py"]