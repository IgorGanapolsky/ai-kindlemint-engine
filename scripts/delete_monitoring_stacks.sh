#!/bin/bash

# AWS Stack Deletion Script - SAVE $80-140/MONTH
# CTO Executive Decision: Delete redundant monitoring infrastructure

set -e

echo "🗑️  CTO MANDATE: Deleting redundant monitoring stacks"
echo "💸 Expected savings: $80-140/month"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check AWS CLI authentication
echo -e "${YELLOW}🔍 Checking AWS authentication...${NC}"
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not authenticated. Please run:${NC}"
    echo "   aws sso login"
    echo "   OR"
    echo "   aws configure"
    exit 1
fi

echo -e "${GREEN}✅ AWS authenticated${NC}"

# Delete failed stack
echo -e "${YELLOW}🗑️  Deleting failed stack: kindlemint-autonomous-orchestration${NC}"
aws cloudformation delete-stack \
    --stack-name kindlemint-autonomous-orchestration \
    --region us-east-1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Failed stack deletion initiated${NC}"
else
    echo -e "${YELLOW}⚠️  Failed stack may not exist (already deleted)${NC}"
fi

# Delete production monitoring stack  
echo -e "${YELLOW}🗑️  Deleting redundant monitoring: autonomous-orchestration-production${NC}"
aws cloudformation delete-stack \
    --stack-name autonomous-orchestration-production \
    --region us-east-1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Production monitoring deletion initiated${NC}"
else
    echo -e "${YELLOW}⚠️  Production stack may not exist${NC}"
fi

# Monitor deletion progress
echo -e "${YELLOW}📊 Monitoring deletion progress...${NC}"
echo "This will take 5-10 minutes. Checking status:"

for i in {1..20}; do
    echo -e "${YELLOW}Check $i/20...${NC}"
    
    # Check remaining stacks
    STACKS=$(aws cloudformation describe-stacks \
        --region us-east-1 \
        --query 'Stacks[?contains(StackName, `autonomous-orchestration`)].[StackName,StackStatus]' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$STACKS" ]; then
        echo -e "${GREEN}🎉 ALL MONITORING STACKS DELETED SUCCESSFULLY!${NC}"
        break
    else
        echo "Remaining stacks:"
        echo "$STACKS"
        echo "Waiting 30 seconds..."
        sleep 30
    fi
done

# Final verification
echo -e "${YELLOW}🔍 Final verification...${NC}"
REMAINING=$(aws cloudformation describe-stacks \
    --region us-east-1 \
    --query 'Stacks[?contains(StackName, `autonomous-orchestration`)].[StackName,StackStatus]' \
    --output table 2>/dev/null || echo "No stacks found")

if echo "$REMAINING" | grep -q "No stacks found"; then
    echo -e "${GREEN}✅ SUCCESS: All monitoring stacks deleted${NC}"
    echo -e "${GREEN}💰 Monthly savings: $80-140${NC}"
    echo -e "${GREEN}🚀 Ready to deploy revenue-generating infrastructure${NC}"
else
    echo -e "${YELLOW}⚠️  Some stacks still exist:${NC}"
    echo "$REMAINING"
    echo "They may still be deleting. Check CloudFormation console."
fi

echo ""
echo -e "${GREEN}🎯 CTO MISSION ACCOMPLISHED${NC}"
echo "Next: Deploy book production pipeline for REAL business value"