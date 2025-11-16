from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel
import psycopg2
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Subtract Service", version="1.0.0")

# Prometheus metrics
REQUEST_COUNT = Counter('calculator_subtract_requests_total', 'Total subtract operation requests')
REQUEST_DURATION = Histogram('calculator_subtract_response_time_seconds', 'Subtract operation response time')
ERROR_COUNT = Counter('calculator_subtract_errors_total', 'Total subtract operation errors')

class CalculationRequest(BaseModel):
    a: float
    b: float

class CalculationResponse(BaseModel):
    operation: str
    a: float
    b: float
    result: float
    timestamp: str

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS calculation_history (
                id SERIAL PRIMARY KEY,
                operation VARCHAR(20),
                operand_a FLOAT,
                operand_b FLOAT,
                result FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                service_name VARCHAR(50)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "subtract-service"}

@app.get("/ready")
async def ready():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "ready", "database": "connected"}
    except:
        raise HTTPException(status_code=503, detail="Database not ready")

@app.post("/subtract", response_model=CalculationResponse)
@REQUEST_DURATION.time()
def subtract_numbers(calc: CalculationRequest):
    REQUEST_COUNT.inc()
    
    try:
        result = calc.a - calc.b
        timestamp = datetime.now().isoformat()
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO calculation_history 
               (operation, operand_a, operand_b, result, service_name) 
               VALUES (%s, %s, %s, %s, %s)""",
            ('subtract', calc.a, calc.b, result, 'subtract-service')
        )
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"Subtraction: {calc.a} - {calc.b} = {result}")
        
        return CalculationResponse(
            operation="subtract",
            a=calc.a,
            b=calc.b,
            result=result,
            timestamp=timestamp
        )
    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"Subtraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)