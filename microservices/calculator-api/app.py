from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel
import httpx
import os
import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Calculator API", version="1.0.0")

# Service URLs (Kubernetes DNS)
ADD_SERVICE_URL = os.getenv('ADD_SERVICE_URL', 'http://add-service:8001')
SUBTRACT_SERVICE_URL = os.getenv('SUBTRACT_SERVICE_URL', 'http://subtract-service:8002')
MULTIPLY_SERVICE_URL = os.getenv('MULTIPLY_SERVICE_URL', 'http://multiply-service:8003')

# Prometheus metrics
REQUEST_COUNT = Counter('calculator_api_requests_total', 'Total API requests', ['operation'])
REQUEST_DURATION = Histogram('calculator_api_response_time_seconds', 'API response time', ['operation'])
ERROR_COUNT = Counter('calculator_api_errors_total', 'Total API errors', ['operation'])

class CalculationRequest(BaseModel):
    operation: str  # add, subtract, multiply
    a: float
    b: float

class CalculationResponse(BaseModel):
    operation: str
    a: float
    b: float
    result: float
    timestamp: str
    processed_by: str

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "calculator-api"}

@app.get("/ready")
async def ready():
    """Check if all downstream services are ready"""
    services = {
        "add": f"{ADD_SERVICE_URL}/health",
        "subtract": f"{SUBTRACT_SERVICE_URL}/health",
        "multiply": f"{MULTIPLY_SERVICE_URL}/health"
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        results = {}
        for name, url in services.items():
            try:
                response = await client.get(url)
                results[name] = response.status_code == 200
            except:
                results[name] = False
        
        all_ready = all(results.values())
        status_code = 200 if all_ready else 503
        
        return {
            "status": "ready" if all_ready else "not ready",
            "services": results
        }

@app.post("/calculate", response_model=CalculationResponse)
async def calculate(calc: CalculationRequest):
    """Route calculation to appropriate microservice"""
    REQUEST_COUNT.labels(operation=calc.operation).inc()
    
    # Determine target service
    service_map = {
        "add": (ADD_SERVICE_URL, "/add"),
        "subtract": (SUBTRACT_SERVICE_URL, "/subtract"),
        "multiply": (MULTIPLY_SERVICE_URL, "/multiply")
    }
    
    if calc.operation not in service_map:
        ERROR_COUNT.labels(operation=calc.operation).inc()
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid operation. Supported: {list(service_map.keys())}"
        )
    
    service_url, endpoint = service_map[calc.operation]
    full_url = f"{service_url}{endpoint}"
    
    try:
        with REQUEST_DURATION.labels(operation=calc.operation).time():
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    full_url,
                    json={"a": calc.a, "b": calc.b}
                )
                response.raise_for_status()
                
                result_data = response.json()
                logger.info(f"Calculation successful: {calc.operation} - {calc.a}, {calc.b}")
                
                return CalculationResponse(
                    operation=result_data['operation'],
                    a=result_data['a'],
                    b=result_data['b'],
                    result=result_data['result'],
                    timestamp=result_data['timestamp'],
                    processed_by=service_url
                )
    except httpx.HTTPError as e:
        ERROR_COUNT.labels(operation=calc.operation).inc()
        logger.error(f"Service call failed: {e}")
        raise HTTPException(status_code=503, detail=f"Downstream service error: {str(e)}")

@app.get("/history")
async def get_history():
    """Get calculation history from database"""
    # This would query RDS directly or call a dedicated history service
    return {"message": "History endpoint - to be implemented"}

@app.get("/metrics")
async def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)