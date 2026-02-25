FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y wget gnupg && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only to keep image size small) and required OS dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy our bot script
COPY gate_rank_bot.py .

# Create a non-root user and set permissions (Required by HuggingFace Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app

# Run the python script
CMD ["python", "-u", "gate_rank_bot.py"]
