#!/bin/bash
# Complete Automated Deployment Script for AWS Resource Finder CronJob

set -e

echo "=========================================="
echo "AWS Resource Finder - Complete Setup"
echo "=========================================="
echo ""

# Configuration
AWS_ACCOUNT_ID=""
AWS_REGION="ap-south-1"
ECR_REPO="aws-unused-resource-finder"
CLUSTER_NAME="qa-eks"
NAMESPACE="devops-tools"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check prerequisites
echo "Step 0: Checking Prerequisites..."
echo "--------------------------------"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed"
    exit 1
fi
print_success "AWS CLI found"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi
print_success "kubectl found"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_success "Docker found"

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi
print_success "Docker is running"

# Check kubectl context
CURRENT_CONTEXT=$(kubectl config current-context)
if [[ ! "$CURRENT_CONTEXT" =~ "qa-eks" ]]; then
    print_warning "Current kubectl context is: $CURRENT_CONTEXT"
    read -p "Is this the correct cluster? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Please configure kubectl for qa-eks cluster"
        exit 1
    fi
fi
print_success "kubectl configured for EKS cluster"

echo ""

# Get AWS credentials
echo "Step 1: AWS Credentials"
echo "-----------------------"
print_info "Please enter your AWS credentials (for the script to access AWS resources)"
echo ""

read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
read -sp "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
echo ""

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    print_error "AWS credentials are required"
    exit 1
fi

print_success "AWS credentials captured"
echo ""

# Update main.py with correct secret name
echo "Step 2: Updating Python Script"
echo "-------------------------------"

if [ -f "main.py" ]; then
    # Update secret name from devsecops-google-service-account to google-service-account
    sed -i 's/secret_name = "devsecops-google-service-account"/secret_name = "google-service-account"/g' main.py 2>/dev/null || \
    sed -i '' 's/secret_name = "devsecops-google-service-account"/secret_name = "google-service-account"/g' main.py
    
    # Update region from us-east-1 to ap-south-1
    sed -i 's/region_name = "us-east-1"/region_name = "ap-south-1"/g' main.py 2>/dev/null || \
    sed -i '' 's/region_name = "us-east-1"/region_name = "ap-south-1"/g' main.py
    
    print_success "Updated main.py with correct secret name and region"
else
    print_warning "main.py not found in current directory"
fi

echo ""

# Build and push Docker image
echo "Step 3: Building Docker Image"
echo "------------------------------"

print_info "Building Docker image..."
docker build -t ${ECR_REPO}:latest .

print_success "Docker image built"
echo ""

echo "Step 4: Pushing to ECR"
echo "----------------------"

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPO_URL="${ECR_REGISTRY}/${ECR_REPO}"

print_info "Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

print_info "Tagging image..."
docker tag ${ECR_REPO}:latest ${ECR_REPO_URL}:latest
docker tag ${ECR_REPO}:latest ${ECR_REPO_URL}:$(date +%Y%m%d-%H%M%S)

print_info "Pushing to ECR..."
docker push ${ECR_REPO_URL}:latest

print_success "Image pushed to ECR: ${ECR_REPO_URL}:latest"
echo ""

# Create/Update k8s-manifest.yaml with credentials
echo "Step 5: Creating Kubernetes Manifest"
echo "-------------------------------------"

cat > k8s-manifest-temp.yaml << EOF
---
apiVersion: v1
kind: Namespace
metadata:
  name: ${NAMESPACE}
  labels:
    name: ${NAMESPACE}
    
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-resource-monitor-config
  namespace: ${NAMESPACE}
data:
  SPREADSHEET_ID: ""
  
---
apiVersion: v1
kind: Secret
metadata:
  name: aws-credentials
  namespace: ${NAMESPACE}
type: Opaque
stringData:
  AWS_ACCOUNT_ID: "${AWS_ACCOUNT_ID}"
  AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
  AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
  SLACK_WEBHOOK_URL: ""
  
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: aws-resource-monitor-sa
  namespace: ${NAMESPACE}
  
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: aws-resource-monitor-${AWS_REGION}
  namespace: ${NAMESPACE}
  labels:
    app: aws-resource-monitor
    region: ${AWS_REGION}
spec:
  schedule: "30 3 * * *"  # Daily at 3:30 AM UTC (9:00 AM IST)
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        metadata:
          labels:
            app: aws-resource-monitor
            region: ${AWS_REGION}
        spec:
          serviceAccountName: aws-resource-monitor-sa
          restartPolicy: OnFailure
          containers:
          - name: aws-resource-monitor
            image: ${ECR_REPO_URL}:latest
            imagePullPolicy: Always
            env:
            - name: AWS_REGION
              value: "${AWS_REGION}"
            - name: AWS_ACCOUNT_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: AWS_ACCOUNT_ID
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: AWS_ACCESS_KEY_ID
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: AWS_SECRET_ACCESS_KEY
            - name: SLACK_WEBHOOK_URL
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: SLACK_WEBHOOK_URL
            - name: SPREADSHEET_ID
              valueFrom:
                configMapKeyRef:
                  name: aws-resource-monitor-config
                  key: SPREADSHEET_ID
            resources:
              requests:
                memory: "256Mi"
                cpu: "100m"
              limits:
                memory: "512Mi"
                cpu: "500m"
EOF

print_success "Kubernetes manifest created"
echo ""

# Create IAM policy (if doesn't exist)
echo "Step 6: Setting up IAM Permissions"
echo "-----------------------------------"

POLICY_NAME="EKS-ResourceMonitor-Policy"
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${POLICY_NAME}"

# Check if policy exists
if aws iam get-policy --policy-arn ${POLICY_ARN} &> /dev/null; then
    print_success "IAM policy already exists: ${POLICY_NAME}"
else
    print_info "Creating IAM policy..."
    
    cat > policy-temp.json << 'POLICY_EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": "arn:aws:secretsmanager:ap-south-1:accountid:secret:google-service-account-*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "elasticloadbalancing:Describe*",
                "rds:Describe*",
                "s3:ListAllMyBuckets",
                "s3:GetBucketTagging",
                "s3:GetBucketLocation",
                "s3:GetBucketMetricsConfiguration",
                "lambda:List*",
                "lambda:GetFunction",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics",
                "cloudtrail:LookupEvents",
                "autoscaling:Describe*",
                "backup:ListRecoveryPointsByResource",
                "ecs:Describe*",
                "ecs:List*",
                "eks:Describe*",
                "eks:List*",
                "ecr:Describe*",
                "iam:ListAttachedRolePolicies",
                "sns:List*",
                "sqs:List*",
                "dynamodb:Describe*",
                "dynamodb:List*",
                "elasticache:Describe*",
                "redshift:Describe*",
                "route53:List*",
                "cloudfront:List*",
                "apigateway:GET"
            ],
            "Resource": "*"
        }
    ]
}
POLICY_EOF
    
    aws iam create-policy \
        --policy-name ${POLICY_NAME} \
        --policy-document file://policy-temp.json \
        --region ${AWS_REGION}
    
    rm policy-temp.json
    
    print_success "IAM policy created: ${POLICY_NAME}"
fi

echo ""

# Create IRSA (IAM Role for Service Account)
echo "Step 7: Setting up IAM Role for Service Account (IRSA)"
echo "-------------------------------------------------------"

print_info "Checking OIDC provider..."
if eksctl utils associate-iam-oidc-provider --cluster=${CLUSTER_NAME} --region=${AWS_REGION} --approve 2>&1 | grep -q "already associated"; then
    print_success "OIDC provider already configured"
else
    print_success "OIDC provider configured"
fi

print_info "Creating/Updating IAM service account..."
eksctl create iamserviceaccount \
    --cluster=${CLUSTER_NAME} \
    --region=${AWS_REGION} \
    --namespace=${NAMESPACE} \
    --name=aws-resource-monitor-sa \
    --attach-policy-arn=${POLICY_ARN} \
    --approve \
    --override-existing-serviceaccounts

print_success "IAM service account configured"
echo ""

# Deploy to Kubernetes
echo "Step 8: Deploying to Kubernetes"
echo "--------------------------------"

print_info "Applying Kubernetes manifest..."
kubectl apply -f k8s-manifest-temp.yaml

print_success "CronJob deployed to Kubernetes"
echo ""

# Clean up temp file
rm k8s-manifest-temp.yaml

# Verify deployment
echo "Step 9: Verifying Deployment"
echo "-----------------------------"

sleep 5

print_info "Checking CronJob..."
if kubectl get cronjob aws-resource-monitor-${AWS_REGION} -n ${NAMESPACE} &> /dev/null; then
    print_success "CronJob is running"
    kubectl get cronjob -n ${NAMESPACE}
else
    print_error "CronJob not found"
fi

echo ""

# Test the CronJob
echo "Step 10: Testing the CronJob"
echo "-----------------------------"

read -p "Do you want to test the CronJob now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Creating test job..."
    
    TEST_JOB_NAME="test-run-$(date +%s)"
    kubectl create job --from=cronjob/aws-resource-monitor-${AWS_REGION} ${TEST_JOB_NAME} -n ${NAMESPACE}
    
    print_success "Test job created: ${TEST_JOB_NAME}"
    print_info "Waiting for job to start..."
    
    sleep 10
    
    # Get pod name
    POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l job-name=${TEST_JOB_NAME} -o jsonpath='{.items[0].metadata.name}')
    
    if [ ! -z "$POD_NAME" ]; then
        print_success "Pod started: ${POD_NAME}"
        print_info "Following logs (Ctrl+C to stop)..."
        echo ""
        
        kubectl logs -f ${POD_NAME} -n ${NAMESPACE}
    else
        print_warning "Pod not found yet. Check manually with:"
        echo "  kubectl get pods -n ${NAMESPACE}"
        echo "  kubectl logs -n ${NAMESPACE} <pod-name>"
    fi
fi

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "  • ECR Image: ${ECR_REPO_URL}:latest"
echo "  • Namespace: ${NAMESPACE}"
echo "  • CronJob: aws-resource-monitor-${AWS_REGION}"
echo "  • Schedule: Daily at 3:30 AM UTC (9:00 AM IST)"
echo ""
echo "🔍 Useful Commands:"
echo "  • View CronJobs:"
echo "    kubectl get cronjobs -n ${NAMESPACE}"
echo ""
echo "  • View Jobs:"
echo "    kubectl get jobs -n ${NAMESPACE}"
echo ""
echo "  • View Pods:"
echo "    kubectl get pods -n ${NAMESPACE}"
echo ""
echo "  • View Logs:"
echo "    kubectl logs -n ${NAMESPACE} -l app=aws-resource-monitor --tail=100"
echo ""
echo "  • Manually trigger a run:"
echo "    kubectl create job --from=cronjob/aws-resource-monitor-${AWS_REGION} manual-run-\$(date +%s) -n ${NAMESPACE}"
echo ""
echo "  • Delete CronJob:"
echo "    kubectl delete cronjob aws-resource-monitor-${AWS_REGION} -n ${NAMESPACE}"
echo ""
echo "📊 Check Results:"
echo "  • Google Sheets: https://docs.google.com/spreadsheets/d/1NxxfT83Q0NcX_GoeivBxUGR7we97vai1vyalq4WwcWU"
echo "  • Slack: Check your configured Slack channel"
echo ""
print_success "All done! Your AWS Resource Finder CronJob is now automated! 🎉"