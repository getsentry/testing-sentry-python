#!/bin/bash

# Exit on error
set -e

# Configuration
FUNCTION_NAME="anton-test-potel-lambda"
RUNTIME="python3.13"
HANDLER="lambda_function.lambda_handler"
ROLE_NAME="anton-potel-role"
ROLE="arn:aws:iam::943013980633:role/$ROLE_NAME"
REGION=${AWS_DEFAULT_REGION:-"us-east-1"}


echo "Starting Lambda deployment..."

# Create IAM role if it doesn't exist
echo "Checking IAM role..."
ROLE_EXISTS=$(aws iam get-role --role-name $ROLE_NAME 2>/dev/null || echo "ROLE_NOT_FOUND")

if [[ $ROLE_EXISTS == *"ROLE_NOT_FOUND"* ]]; then
    echo "Creating IAM role: $ROLE_NAME"

    # Create the role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }]
        }'

    # Attach the basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    # Wait for role to be available
    echo "Waiting for role to be available..."
    sleep 10
fi

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
echo "Creating temporary directory: $TEMP_DIR"

# Copy function code to temp directory
echo "Copying function code..."
cp -r lambda_function/* $TEMP_DIR/

# Install dependencies
echo "Setting up Python environment..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
uv pip install --system --no-cache -r $TEMP_DIR/pyproject.toml --target $TEMP_DIR/

# Create deployment package
echo "Creating deployment package..."
cd $TEMP_DIR
zip -r function.zip . -x "*.pyc" -x "*.pyo" -x "__pycache__/*" -x ".venv/*"
cd -

# Move the zip file to the current directory
mv $TEMP_DIR/function.zip .

# Check if function exists
FUNCTION_EXISTS=$(aws lambda list-functions --query "Functions[?FunctionName=='$FUNCTION_NAME'].FunctionName" --output text)

if [ -z "$FUNCTION_EXISTS" ]; then
    echo "Creating new Lambda function: $FUNCTION_NAME"
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --role $ROLE \
        --zip-file fileb://function.zip \
        --region $REGION
else
    echo "Updating existing Lambda function: $FUNCTION_NAME"
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip \
        --region $REGION
fi

# Cleanup
echo "Cleaning up..."
rm -rf $TEMP_DIR
rm function.zip

# Test the function
echo "Testing the function..."
aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload '{}' \
    response.json

echo -e "Deployment completed successfully!"
echo "Function response:"
cat response.json
rm response.json
