FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

RUN useradd -m -u 1000 calculator
COPY --from=builder --chown=calculator:calculator /root/.local /home/calculator/.local
COPY --chown=calculator:calculator app.py .

ENV PATH=/home/calculator/.local/bin:$PATH

USER calculator

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
