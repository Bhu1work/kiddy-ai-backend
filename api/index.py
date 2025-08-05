"""
Mangum wrapper for AWS Lambda deployment.

This file provides the Lambda handler for deploying the Kiddy AI Backend
to AWS Lambda using Mangum adapter.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

from mangum import Mangum
from app.main import app

# Create Mangum handler for AWS Lambda
handler = Mangum(app, lifespan="off")

# Optional: Add CORS headers for API Gateway
def lambda_handler(event, context):
    """AWS Lambda handler function."""
    
    # Add CORS headers for API Gateway
    response = handler(event, context)
    
    # Ensure CORS headers are present
    if "headers" not in response:
        response["headers"] = {}
    
    # Add CORS headers
    response["headers"].update({
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Credentials": "true"
    })
    
    return response 