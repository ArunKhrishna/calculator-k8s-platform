FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Create user FIRST
RUN useradd -m -u 1000 calculator

# Copy dependencies to calculator's home directory
COPY --from=builder --chown=calculator:calculator /root/.local /home/calculator/.local

# Copy application
COPY --chown=calculator:calculator app.py .

# Set PATH to include user's local bin
ENV PATH=/home/calculator/.local/bin:$PATH

# Switch to non-root user
USER calculator

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
