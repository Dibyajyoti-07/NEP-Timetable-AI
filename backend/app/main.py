from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection
import logging
from starlette.middleware.base import BaseHTTPMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="AI-Based Timetable Generation System",
    description="NEP 2020 compliant timetable generation for educational institutions with AI optimization",
    version="1.0.0",
    lifespan=lifespan
)

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation error for {request.method} {request.url}")
    print(f"Validation errors: {exc.errors()}")
    
    # Handle body serialization safely
    body_content = None
    try:
        if exc.body is not None:
            body_content = str(exc.body)
    except Exception:
        body_content = "<unable to serialize body>"
    
    response = JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": body_content,
            "message": "Validation failed - check the required fields and data types"
        }
    )
    
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Global exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Global exception handler for all other exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception for {request.method} {request.url}: {exc}")
    import traceback
    traceback.print_exc()
    
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
    
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Allow both frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Based Timetable Generation System",
        "description": "NEP 2020 compliant timetable generation for educational institutions",
        "version": "1.0.0",
        "features": [
            "Constraint-based timetable generation",
            "AI-powered optimization using Google Gemini",
            "Multi-format export (Excel, PDF, JSON)",
            "Faculty workload balancing",
            "Room assignment optimization",
            "NEP 2020 compliance"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Timetable Generator"}

@app.get("/test-cors")
async def test_cors():
    """Test CORS endpoint"""
    return {"message": "CORS is working", "timestamp": "2025-08-30"}

@app.post("/test-cors")
async def test_cors_post():
    """Test CORS POST endpoint"""
    return {"message": "CORS POST is working", "timestamp": "2025-08-30"}

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
