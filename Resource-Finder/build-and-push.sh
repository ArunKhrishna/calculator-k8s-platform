#!/bin/bash
set -e

echo "======================================"
echo "AWS Resource Monitor - Build & Push to ECR"
echo "======================================"

# Configuration
AWS_ACCOUNT_ID=""
AWS_REGION="ap-south-1"
ECR_REPO="aws-unused-resource-finder"
IMAGE_TAG="latest"
IMAGE_TAG_DATED="$(date +%Y%m%d-%H%M%S)"

# Full ECR repository URL
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPO_URL="${ECR_REGISTRY}/${ECR_REPO}"

echo "Configuration:"
echo "  AWS Account: ${AWS_ACCOUNT_ID}"
echo "  AWS Region: ${AWS_REGION}"
echo "  ECR Repo: ${ECR_REPO_URL}"
echo ""

echo "Step 1: Building Docker image..."
docker build -t ${ECR_REPO}:${IMAGE_TAG} .

echo ""
echo "Step 2: Tagging Docker image..."
docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REPO_URL}:${IMAGE_TAG}
docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REPO_URL}:${IMAGE_TAG_DATED}

echo ""
echo "Step 3: Logging into Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

echo ""
echo "Step 4: Pushing Docker image to ECR..."
docker push ${ECR_REPO_URL}:${IMAGE_TAG}
docker push ${ECR_REPO_URL}:${IMAGE_TAG_DATED}

echo ""
echo "======================================"
echo "✅ Build and push completed successfully!"
echo "======================================"
echo "Images pushed:"
echo "  • ${ECR_REPO_URL}:${IMAGE_TAG}"
echo "  • ${ECR_REPO_URL}:${IMAGE_TAG_DATED}"
echo ""
echo "Next step: Deploy to Kubernetes"
echo "  ./deploy.sh k8s"