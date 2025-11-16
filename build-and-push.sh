#!/bin/bash

# Configuration
AWS_REGION="ap-south-1"
AWS_ACCOUNT_ID="089580247689"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG="v1.0.0"

# Services to build
SERVICES=("calculator-api" "add-service" "subtract-service" "multiply-service")

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Create ECR repositories if they don't exist
for SERVICE in "${SERVICES[@]}"; do
    echo "📦 Checking/Creating ECR repository for ${SERVICE}..."
    aws ecr describe-repositories --repository-names ${SERVICE} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${SERVICE} --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
done

# Build and push images
for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "=========================================="
    echo "🏗️  Building ${SERVICE}..."
    echo "=========================================="
    
    cd microservices/${SERVICE}
    
    # Build the image
    docker build -t ${SERVICE}:${IMAGE_TAG} . --no-cache
    
    # Tag for ECR
    docker tag ${SERVICE}:${IMAGE_TAG} ${ECR_REGISTRY}/${SERVICE}:${IMAGE_TAG}
    docker tag ${SERVICE}:${IMAGE_TAG} ${ECR_REGISTRY}/${SERVICE}:latest
    
    echo "⬆️  Pushing ${SERVICE} to ECR..."
    docker push ${ECR_REGISTRY}/${SERVICE}:${IMAGE_TAG}
    docker push ${ECR_REGISTRY}/${SERVICE}:latest
    
    echo "✅ ${SERVICE} pushed successfully!"
    
    cd ../..
done

echo ""
echo "=========================================="
echo "✅ All images built and pushed successfully!"
echo "=========================================="
echo ""
echo "Images pushed:"
for SERVICE in "${SERVICES[@]}"; do
    echo "  ✓ ${ECR_REGISTRY}/${SERVICE}:${IMAGE_TAG}"
done
echo ""
echo "Next steps:"
echo "  1. Update k8s-configs/secret.yaml with RDS password"
echo "  2. kubectl apply -f k8s-configs/namespace.yaml"
echo "  3. kubectl apply -f k8s-configs/configmap.yaml"
echo "  4. kubectl apply -f k8s-configs/secret.yaml"
echo "  5. kubectl apply -f k8s-configs/deployments/"