# Kubernetes Deployment Guide

## Overview

This directory contains Kubernetes manifests for deploying F.R.I.D.A.Y. Agent to a Kubernetes cluster.

## Files

- `backend-deployment.yaml` - Backend deployment, service, and PVC
- `frontend-deployment.yaml` - Frontend deployment and service
- `secrets.yaml` - Secrets for API keys (update before use)
- `configmap.yaml` - Configuration values
- `ingress.yaml` - Ingress with TLS configuration
- `deploy.sh` - Automated deployment script

## Prerequisites

1. **Kubernetes Cluster** (v1.24+)
   - Minikube for local testing
   - GKE, EKS, AKS for production

2. **kubectl** installed and configured
   ```bash
   kubectl version --client
   ```

3. **Ingress Controller** (nginx)
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
   ```

4. **Cert-Manager** for TLS (optional)
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```

## Quick Start

### 1. Update Secrets

Edit `secrets.yaml` and replace placeholders:
```yaml
stringData:
  gemini-api-key: "YOUR_ACTUAL_API_KEY_HERE"
```

### 2. Deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Verify

```bash
# Check pods
kubectl get pods -n friday-agent

# Check services
kubectl get svc -n friday-agent

# Check ingress
kubectl get ingress -n friday-agent
```

## Manual Deployment

```bash
# Create namespace
kubectl create namespace friday-agent

# Apply configurations
kubectl apply -f configmap.yaml -n friday-agent
kubectl apply -f secrets.yaml -n friday-agent
kubectl apply -f backend-deployment.yaml -n friday-agent
kubectl apply -f frontend-deployment.yaml -n friday-agent
kubectl apply -f ingress.yaml -n friday-agent
```

## Scaling

### Scale Backend
```bash
kubectl scale deployment friday-backend --replicas=5 -n friday-agent
```

### Scale Frontend
```bash
kubectl scale deployment friday-frontend --replicas=3 -n friday-agent
```

### Autoscaling
```bash
kubectl autoscale deployment friday-backend \
  --cpu-percent=80 \
  --min=3 \
  --max=10 \
  -n friday-agent
```

## Monitoring

### View Logs
```bash
# Backend logs
kubectl logs -f deployment/friday-backend -n friday-agent

# Frontend logs
kubectl logs -f deployment/friday-frontend -n friday-agent
```

### Describe Resources
```bash
kubectl describe deployment friday-backend -n friday-agent
kubectl describe pod <pod-name> -n friday-agent
```

### Execute Commands in Pod
```bash
kubectl exec -it <backend-pod-name> -n friday-agent -- /bin/bash
```

## Updating Deployment

### Update Image
```bash
kubectl set image deployment/friday-backend \
  backend=friday-backend:v2.1.0 \
  -n friday-agent
```

### Rollback
```bash
kubectl rollout undo deployment/friday-backend -n friday-agent
```

### Rollout Status
```bash
kubectl rollout status deployment/friday-backend -n friday-agent
```

## Resource Usage

### Current Configuration

**Backend:**
- Replicas: 3
- CPU Request: 500m
- CPU Limit: 2000m
- Memory Request: 512Mi
- Memory Limit: 2Gi

**Frontend:**
- Replicas: 2
- CPU Request: 250m
- CPU Limit: 1000m
- Memory Request: 256Mi
- Memory Limit: 1Gi

### Adjust Resources

Edit deployment files and apply:
```bash
kubectl apply -f backend-deployment.yaml -n friday-agent
```

## Ingress Configuration

### Update Domain

Edit `ingress.yaml`:
```yaml
spec:
  tls:
  - hosts:
    - your-domain.com
    - api.your-domain.com
```

### Verify Ingress
```bash
kubectl describe ingress friday-ingress -n friday-agent
```

## Persistent Storage

Backend uses PersistentVolumeClaim for data:
```bash
kubectl get pvc -n friday-agent
```

## Health Checks

### Liveness Probe
Checks if pod is running:
- Endpoint: `/health`
- Frequency: Every 10s
- Failure threshold: 3

### Readiness Probe
Checks if pod can serve traffic:
- Endpoint: `/ready`
- Frequency: Every 5s
- Failure threshold: 3

## Troubleshooting

### Pods Not Starting
```bash
kubectl describe pod <pod-name> -n friday-agent
kubectl logs <pod-name> -n friday-agent
```

### Service Not Accessible
```bash
kubectl get endpoints -n friday-agent
kubectl get svc -n friday-agent
```

### Ingress Not Working
```bash
kubectl describe ingress friday-ingress -n friday-agent
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

## Production Checklist

- [ ] Secrets updated with real API keys
- [ ] Domain names configured in ingress
- [ ] TLS certificates configured
- [ ] Resource limits appropriate for load
- [ ] Persistent storage configured
- [ ] Monitoring/alerts set up
- [ ] Backup strategy in place
- [ ] Rollback plan tested

## Cost Optimization

### Use Spot Instances
For non-critical workloads:
```yaml
spec:
  tolerations:
  - key: "spot"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

### Reduce Replicas
During low-traffic periods:
```bash
kubectl scale deployment friday-backend --replicas=1 -n friday-agent
```

## Additional Resources

- Kubernetes Docs: https://kubernetes.io/docs/
- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Production Best Practices: https://kubernetes.io/docs/concepts/configuration/overview/
