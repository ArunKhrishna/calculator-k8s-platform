#!/bin/bash

set -e

echo "======================================"
echo "AWS Resource Monitor Deployment"
echo "======================================"

if [ "$1" = "local" ]; then
    echo "Running locally..."
    export AWS_ACCOUNT_ID=""
    export AWS_REGION="${2:-us-east-1}"  # Default to us-east-1, can pass region as 2nd arg
    export SLACK_WEBHOOK_URL=""
    export SPREADSHEET_ID=""
    
    python main.py
    
elif [ "$1" = "build-push" ]; then
    echo "Building and pushing Docker image to ECR..."
    ./build-and-push.sh
    
elif [ "$1" = "k8s" ]; then
    echo "Deploying to Kubernetes..."
    
    NAMESPACE="devops-tools"
    
    # Create namespace if it doesn't exist
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply the Kubernetes manifest
    echo "Applying k8s-manifest.yaml..."
    kubectl apply -f k8s-manifest.yaml
    
    echo ""
    echo "Deployment complete!"
    echo ""
    echo "CronJob schedules:"
    echo "  - us-east-1: Daily at 3:00 AM UTC (8:30 AM IST)"
    echo "  - ap-south-1: Daily at 3:30 AM UTC (9:00 AM IST)"
    echo ""
    echo "To test us-east-1 immediately:"
    echo "kubectl create job --from=cronjob/aws-resource-monitor-us-east-1 test-us-east-1-\$(date +%s) -n ${NAMESPACE}"
    echo ""
    echo "To test ap-south-1 immediately:"
    echo "kubectl create job --from=cronjob/aws-resource-monitor-ap-south-1 test-ap-south-1-\$(date +%s) -n ${NAMESPACE}"
    echo ""
    echo "To check logs:"
    echo "kubectl logs -n ${NAMESPACE} -l app=aws-resource-monitor --tail=100 -f"
    echo ""
    echo "To view CronJobs:"
    echo "kubectl get cronjobs -n ${NAMESPACE}"
    
elif [ "$1" = "full-deploy" ]; then
    echo "Running full deployment: Build, Push, and Deploy to K8s..."
    ./build-and-push.sh
    sleep 5
    $0 k8s
    
else
    echo "Usage: ./deploy.sh [local|build-push|k8s|full-deploy] [region]"
    echo ""
    echo "  local [region]  - Run the Python script locally (default region: us-east-1)"
    echo "  build-push      - Build and push Docker image to ECR"
    echo "  k8s             - Deploy to Kubernetes cluster"
    echo "  full-deploy     - Build, push, and deploy to K8s in one command"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh local us-east-1"
    echo "  ./deploy.sh local ap-south-1"
    echo "  ./deploy.sh full-deploy"
fi