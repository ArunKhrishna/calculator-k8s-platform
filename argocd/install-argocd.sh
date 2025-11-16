#!/bin/bash

# ArgoCD Helm Installation Script
# This script will install ArgoCD in your EKS cluster

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ArgoCD Installation Script ===${NC}\n"

# Configuration
NAMESPACE="argocd"
RELEASE_NAME="argocd"
CHART_REPO="https://argoproj.github.io/argo-helm"
CHART_NAME="argo-cd"
VALUES_FILE="argocd-values.yaml"

# Step 1: Verify kubectl context
echo -e "${YELLOW}Step 1: Verifying kubectl context...${NC}"
CURRENT_CONTEXT=$(kubectl config current-context)
echo "Current context: $CURRENT_CONTEXT"
read -p "Is this the correct cluster? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Installation cancelled.${NC}"
    exit 1
fi

# Step 2: Verify namespace exists
echo -e "\n${YELLOW}Step 2: Checking namespace...${NC}"
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo -e "${GREEN}Namespace '$NAMESPACE' exists.${NC}"
else
    echo -e "${YELLOW}Namespace '$NAMESPACE' does not exist. Creating...${NC}"
    kubectl create namespace "$NAMESPACE"
    echo -e "${GREEN}Namespace created.${NC}"
fi

# Step 3: Add ArgoCD Helm repository
echo -e "\n${YELLOW}Step 3: Adding ArgoCD Helm repository...${NC}"
helm repo add argo "$CHART_REPO"
helm repo update
echo -e "${GREEN}Repository added and updated.${NC}"

# Step 4: Verify values file exists
echo -e "\n${YELLOW}Step 4: Verifying values file...${NC}"
if [ ! -f "$VALUES_FILE" ]; then
    echo -e "${RED}Error: $VALUES_FILE not found!${NC}"
    exit 1
fi
echo -e "${GREEN}Values file found: $VALUES_FILE${NC}"

# Step 5: Validate Helm chart
echo -e "\n${YELLOW}Step 5: Validating Helm chart...${NC}"
helm lint argo/$CHART_NAME -f "$VALUES_FILE" || {
    echo -e "${RED}Warning: Helm lint found issues. Continuing anyway...${NC}"
}

# Step 6: Dry-run installation
echo -e "\n${YELLOW}Step 6: Running dry-run...${NC}"
read -p "Do you want to see the dry-run output? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    helm install "$RELEASE_NAME" argo/$CHART_NAME \
        --namespace "$NAMESPACE" \
        --values "$VALUES_FILE" \
        --dry-run --debug
    
    read -p "Continue with actual installation? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Installation cancelled.${NC}"
        exit 1
    fi
fi

# Step 7: Install ArgoCD
echo -e "\n${YELLOW}Step 7: Installing ArgoCD...${NC}"
helm install "$RELEASE_NAME" argo/$CHART_NAME \
    --namespace "$NAMESPACE" \
    --values "$VALUES_FILE" \
    --create-namespace

echo -e "${GREEN}ArgoCD installation initiated!${NC}"

# Step 8: Wait for pods to be ready
echo -e "\n${YELLOW}Step 8: Waiting for ArgoCD pods to be ready...${NC}"
echo "This may take a few minutes..."

kubectl wait --for=condition=ready pod \
    --selector=app.kubernetes.io/name=argocd-server \
    --namespace="$NAMESPACE" \
    --timeout=300s

# Step 9: Check installation status
echo -e "\n${YELLOW}Step 9: Checking installation status...${NC}"
helm list -n "$NAMESPACE"

echo -e "\n${GREEN}=== Pod Status ===${NC}"
kubectl get pods -n "$NAMESPACE"

echo -e "\n${GREEN}=== Services ===${NC}"
kubectl get svc -n "$NAMESPACE"

# Step 10: Get admin password
echo -e "\n${YELLOW}Step 10: Retrieving admin password...${NC}"
ADMIN_PASSWORD=$(kubectl -n "$NAMESPACE" get secret argocd-initial-admin-secret \
    -o jsonpath="{.data.password}" 2>/dev/null | base64 -d)

if [ -n "$ADMIN_PASSWORD" ]; then
    echo -e "${GREEN}Admin password retrieved successfully!${NC}"
    echo -e "\n${GREEN}=== ArgoCD Login Credentials ===${NC}"
    echo "Username: admin"
    echo "Password: $ADMIN_PASSWORD"
    echo -e "\n${YELLOW}Note: Save this password securely and change it after first login!${NC}"
else
    echo -e "${YELLOW}Could not retrieve admin password. It may not be created yet.${NC}"
    echo "Run this command later:"
    echo "kubectl -n $NAMESPACE get secret argocd-initial-admin-secret -o jsonpath=\"{.data.password}\" | base64 -d"
fi

# Step 11: Port forward instructions
echo -e "\n${GREEN}=== Access ArgoCD UI ===${NC}"
echo "To access ArgoCD UI, run:"
echo -e "${YELLOW}kubectl port-forward svc/argocd-server -n $NAMESPACE 8080:443${NC}"
echo "Then open: https://localhost:8080"
echo ""
echo "Or use ArgoCD CLI:"
echo -e "${YELLOW}argocd login localhost:8080${NC}"

echo -e "\n${GREEN}=== Installation Complete! ===${NC}"