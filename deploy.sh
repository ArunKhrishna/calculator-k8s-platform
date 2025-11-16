#!/bin/bash

echo "🚀 Deploying Calculator Platform to Kubernetes..."

# Update kubeconfig
echo "📡 Updating kubeconfig for qa-eks..."
aws eks update-kubeconfig --region ap-south-1 --name qa-eks

# Apply manifests in order
echo "📦 Creating namespace..."
kubectl apply -f k8s-configs/namespace.yaml

echo "⚙️  Applying ConfigMap..."
kubectl apply -f k8s-configs/configmap.yaml

echo "🔐 Applying Secrets..."
kubectl apply -f k8s-configs/secret.yaml

echo "🚢 Deploying services..."
kubectl apply -f k8s-configs/deployments/

echo ""
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=add-service -n calculator --timeout=120s
kubectl wait --for=condition=ready pod -l app=subtract-service -n calculator --timeout=120s
kubectl wait --for=condition=ready pod -l app=multiply-service -n calculator --timeout=120s
kubectl wait --for=condition=ready pod -l app=calculator-api -n calculator --timeout=120s

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Pod Status:"
kubectl get pods -n calculator

echo ""
echo "🌐 Services:"
kubectl get svc -n calculator

echo ""
echo "🔍 Get LoadBalancer URL:"
echo "kubectl get svc calculator-api -n calculator -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'"