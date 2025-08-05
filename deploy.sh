#!/bin/bash

# Kiddy AI Backend AWS Lambda Deployment Script

set -e

echo "Deploying Kiddy AI Backend to AWS Lambda..."

# Check if required environment variables are set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY environment variable is not set"
    echo "   Please set your Google API key:"
    echo "   export GOOGLE_API_KEY=your_api_key_here"
    exit 1
fi

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "Error: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"
    echo "   Please set your Google service account credentials path:"
    echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json"
    exit 1
fi

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo "Installing Serverless Framework..."
    npm install -g serverless
fi

# Check if serverless-python-requirements plugin is installed
if ! serverless plugin list | grep -q "serverless-python-requirements"; then
    echo "Installing serverless-python-requirements plugin..."
    npm install --save-dev serverless-python-requirements
fi

# Deploy to AWS
echo "Deploying to AWS Lambda..."
serverless deploy --verbose

echo ""
echo "Deployment complete!"
echo ""
echo "Your API endpoints:"
echo "   - Main API: https://your-api-id.execute-api.us-east-1.amazonaws.com"
echo "   - Health Check: https://your-api-id.execute-api.us-east-1.amazonaws.com/health"
echo "   - API Docs: https://your-api-id.execute-api.us-east-1.amazonaws.com/docs"
echo ""
echo "Useful commands:"
echo "   - View logs: serverless logs -f api"
echo "   - Remove deployment: serverless remove"
echo "   - Deploy to production: serverless deploy --stage prod" 