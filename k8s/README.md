# Kubernetes Deployment for Legal AI Platform

This directory contains the necessary configurations to deploy the Legal AI Platform on Kubernetes using Helm.

## Prerequisites

- A Kubernetes cluster (Minikube, Kind, or a cloud-managed service like EKS/GKE/AKS).
- `kubectl` configured to your cluster.
- `helm` installed.

## Helm Chart Structure

The deployment is managed via a Helm chart located in `helm/legal-ai`.

- `Chart.yaml`: Chart metadata.
- `values.yaml`: Default configuration values.
- `templates/`: Kubernetes resource templates.

## Quick Start

### 1. Create the Namespace

```bash
kubectl create namespace legal-ai
```

### 2. Configure Secrets

Copy the `values.yaml` to a new file, e.g., `my-values.yaml`, and update the secrets:

```yaml
backend:
  secrets:
    geminiApiKey: "your-actual-api-key"
    jwtSecret: "your-actual-jwt-secret"
```

### 3. Install the Chart

```bash
helm install legal-ai ./helm/legal-ai -f my-values.yaml -n legal-ai
```

## Architecture

- **Backend Deployment**: Scalable FastAPI application with resource limits and health probes.
- **Redis Deployment**: Single-node Redis with persistent storage.
- **Persistent Storage**: Claims for document uploads, FAISS indexes, and metadata.
- **Ingress**: NGINX-based ingress for routing external traffic.
- **Autoscaling**: HPA based on CPU utilization.
- **Security**: Network Policies to restrict traffic between pods.

## Health Probes

- **Startup**: `/health/ready` (waits for dependencies).
- **Liveness**: `/health/live`.
- **Readiness**: `/health/ready`.

## Resource Management

Default resource limits are set for production stability:
- Backend: 1 CPU, 2Gi RAM (Limit); 0.5 CPU, 1Gi RAM (Request).
- Redis: 0.5 CPU, 512Mi RAM (Limit); 0.2 CPU, 256Mi RAM (Request).

## Network Policies

The implementation enforces the principle of least privilege:
- **Backend** can only egress to **Redis** (port 6379) and the internet (for Gemini API).
- **Redis** only accepts ingress from the **Backend**.
- **Ingress** is only allowed through the NGINX Ingress Controller.
