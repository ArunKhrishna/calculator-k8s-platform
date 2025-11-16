#!/bin/bash
set -e

AWS_REGION="ap-south-1"
AWS_ACCOUNT_ID="089580247689"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG="v1.0.0"

SERVICES=("calculator-api" "add-service" "subtract-service" "multiply-service")

echo "Ì¥ê Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "=========================================="
    echo "Ì≥¶ Processing ${SERVICE}..."
    echo "=========================================="
    
    # Create ECR repository if it doesn't exist
    echo "Creating ECR repository for ${SERVICE}..."
    aws ecr describe-repositories --repository-names ${SERVICE} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${SERVICE} --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    
    # Build the image
    echo "ÌøóÔ∏è  Building ${SERVICE}..."
    cd microservices/${SERVICE}
    docker build -t ${SERVICE}:${IMAGE_TAG} . --no-cache
    
    # Tag for ECR
    docker tag ${SERVICE}:${IMAGE_TAG} ${ECR_REGISTRY}/${SERVICE}:${IMAGE_TAG}
    docker tag ${SERVICE}:${IMAGE_TAG} ${ECR_REGISTRY}/${SERVICE}:latest
    
    # Push to ECR
    echo "‚¨ÜÔ∏è  Pushing ${SERVICE} to ECR..."
    docker push ${ECR_REGISTRY}/${SERVICE}:${IMAGE_TAG}
    docker push ${ECR_REGISTRY}/${SERVICE}:latest
    
    echo "‚úÖ ${SERVICE} complete!"
    
    cd ../..
done

echo ""
echo "=========================================="
echo "‚úÖ ALL IMAGES BUILT AND PUSHED!"
echo "=========================================="
echo ""
echo "Images:"
for SERVICE in "${SERVICES[@]}"; do
    echo "  ‚úì ${ECR_REGISTRY}/${SERVICE}:${IMAGE_TAG}"
done
echo ""
echo "Next: Pods will auto-pull images and start!"
