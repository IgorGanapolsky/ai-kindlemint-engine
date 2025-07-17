#!/bin/bash
# Deploy Lambda revenue function

# Package the function
zip lambda_revenue.zip lambda_revenue_function.py

# Create/Update Lambda function
aws lambda create-function \
    --function-name PuzzleRevenueGenerator \
    --runtime python3.9 \
    --role arn:aws:iam::352505431931:role/lambda-execution-role \
    --handler lambda_revenue_function.lambda_handler \
    --zip-file fileb://lambda_revenue.zip \
    --timeout 60 \
    --memory-size 256 \
    2>/dev/null || \
aws lambda update-function-code \
    --function-name PuzzleRevenueGenerator \
    --zip-file fileb://lambda_revenue.zip

# Set up daily trigger
aws events put-rule \
    --name DailyRevenueGeneration \
    --schedule-expression "rate(1 day)"

aws lambda add-permission \
    --function-name PuzzleRevenueGenerator \
    --statement-id DailyRevenuePermission \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:352505431931:rule/DailyRevenueGeneration

aws events put-targets \
    --rule DailyRevenueGeneration \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:352505431931:function:PuzzleRevenueGenerator"

echo "✅ Lambda revenue generator deployed!"
echo "Will run automatically every day"
