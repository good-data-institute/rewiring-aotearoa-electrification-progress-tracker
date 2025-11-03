# Use Python 3.12 base image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize Reflex and build everything during Docker build (has more memory)
RUN reflex init

# Compile the app once during build (with plenty of memory)
RUN reflex export --loglevel debug

# Expose port
EXPOSE 8000

# Start only the backend server using the compiled assets
# This avoids recompilation at startup
CMD ["python", "-m", "reflex.reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0", "--backend-port", "8000", "--loglevel", "info"]
