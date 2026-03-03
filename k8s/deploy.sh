#!/bin/bash
# Kubernetes deployment script

set -e

echo "========================================="
echo "  Friday Agent - Kubernetes Deployment"
echo "========================================="

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot access Kubernetes cluster"
    exit 1
fi

echo "✓ Kubernetes cluster accessible"

# Create namespace
echo "Creating namespace..."
kubectl create namespace friday-agent --dry-run=client -o yaml | kubectl apply -f -

# Apply configurations
echo "Applying ConfigMap..."
kubectl apply -f k8s/configmap.yaml -n friday-agent

echo "Applying Secrets..."
echo "⚠️  Make sure to update secrets.yaml with your API keys!"
kubectl apply -f k8s/secrets.yaml -n friday-agent

echo "Deploying backend..."
kubectl apply -f k8s/backend-deployment.yaml -n friday-agent

echo "Deploying frontend..."
kubectl apply -f k8s/frontend-deployment.yaml -n friday-agent

echo "Applying Ingress..."
kubectl apply -f k8s/ingress.yaml -n friday-agent

echo ""
echo "✓ Deployment complete!"
echo ""
echo "Check status with:"
echo "  kubectl get pods -n friday-agent"
echo "  kubectl get services -n friday-agent"
echo ""
echo "View logs with:"
echo "  kubectl logs -f deployment/friday-backend -n friday-agent"
echo "  kubectl logs -f deployment/friday-frontend -n friday-agent"
