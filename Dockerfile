FROM google/cloud-sdk:slim
 
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    && rm -rf /var/lib/apt/lists/*

ARG NODE_VERSION=20
RUN apt-get update -y && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages --upgrade pip && \
    pip install --break-system-packages -r requirements.txt
    
# Expose port
EXPOSE 8080

# Run the application
CMD ["python3", "main.py"]