# Calculator Microservices Platform with Istio Service Mesh

A production-grade microservices platform demonstrating enterprise DevOps practices including GitOps deployment with ArgoCD, Istio service mesh for traffic management and security, and comprehensive Infrastructure as Code using Terraform/Terragrunt on AWS EKS.

Demo - https://www.loom.com/share/eef9a0b4bfe14ba59b755ac9f70afe79

## 🎯 Project Overview

This project showcases a fully functional calculator application built as a microservices architecture, deployed on AWS EKS with advanced traffic management, observability, and security features. The platform demonstrates real-world production patterns suitable for reliant environments.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet Traffic                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  AWS Network LB    │
                    │  (Istio Gateway)   │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Istio Ingress      │
                    │  Gateway            │
                    │  (mTLS enabled)     │
                    └──────────┬──────────┘
                               │
                               │ Traffic Split: 80/20
                               ▼
                  ┌────────────────────────────┐
                  │   Calculator API           │
                  │   v1 (80%) | v2 (20%)     │
                  └─────────┬──────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐     ┌──────────┐
    │   Add    │      │ Subtract │     │ Multiply │
    │ Service  │      │ Service  │     │ Service  │
    │ v1 | v2  │      │ v1 | v2  │     │ v1 | v2  │
    │ 70% 30%  │      │ 60% 40%  │     │ 50% 50%  │
    └──────────┘      └──────────┘     └──────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ AWS Secrets     │
                   │ Manager         │
                   │ (IRSA)          │
                   └─────────────────┘
```

## ✨ Key Features

### 🔐 Security & Zero Trust
- **mTLS Encryption**: All service-to-service communication encrypted via Istio
- **Authorization Policies**: Fine-grained access control between services
- **IRSA Integration**: AWS IAM roles for service accounts (no hardcoded credentials)
- **AWS Secrets Manager**: Secure credential management with CSI driver

### 🌐 Traffic Management
- **Canary Deployments**: Progressive rollout with configurable traffic splits
  - Calculator API: 80% v1, 20% v2
  - Add Service: 70% v1, 30% v2
  - Subtract Service: 60% v1, 40% v2
  - Multiply Service: 50% v1, 50% v2
- **Circuit Breakers**: Automatic failure detection and ejection
- **Request Timeouts**: Configurable per-service timeout policies
- **Retry Logic**: Smart retry with exponential backoff
- **Rate Limiting**: Connection pooling and request throttling

### 📊 Observability
- **Kiali**: Service mesh visualization and traffic analysis
- **Jaeger**: Distributed tracing for end-to-end request tracking
- **Grafana**: Real-time metrics and custom dashboards
- **Prometheus**: Metrics collection and alerting

### 🚀 DevOps & Automation
- **GitOps**: ArgoCD for declarative continuous deployment
- **Infrastructure as Code**: Terraform + Terragrunt for AWS resources
- **Helm Charts**: Templated Kubernetes manifests
- **Multi-Environment**: Separate configurations for QA/Prod
- **Automated Sync**: Auto-heal and prune with ArgoCD

### 🏗️ Infrastructure
- **AWS EKS**: Managed Kubernetes service (v1.31)
- **Multi-AZ Deployment**: High availability across availability zones
- **Auto-scaling**: Node groups with dynamic scaling
- **Network Load Balancer**: AWS-managed load balancing
- **VPC Networking**: Custom VPC with public/private subnets

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Container Orchestration** | AWS EKS (Kubernetes 1.31) | Cluster management |
| **Service Mesh** | Istio 1.23.2 | Traffic management, security, observability |
| **GitOps** | ArgoCD | Continuous deployment |
| **Infrastructure** | Terraform + Terragrunt | Infrastructure as Code |
| **Package Manager** | Helm 3 | Application templating |
| **Microservices** | Python FastAPI | REST API services |
| **Observability** | Kiali, Jaeger, Grafana, Prometheus | Monitoring and tracing |
| **Secret Management** | AWS Secrets Manager + CSI Driver | Credential management |
| **Container Registry** | Amazon ECR | Docker image storage |
| **Load Balancing** | AWS Network Load Balancer | External traffic routing |

## 📁 Project Structure

```
calculator-k8s-platform/
├── Infra/
│   ├── terraform-resources/        # Terraform modules
│   │   ├── eks/                    # EKS cluster configuration
│   │   ├── iam/                    # IAM roles and policies
│   │   └── vpc-networking/         # VPC, subnets, routing
│   └── terragrunt-resources/       # Environment-specific configs
│       └── ap-south-1/qa/          # QA environment in Mumbai region
│
├── microservices/
│   ├── calculator-api/             # Main API gateway service
│   ├── add-service/                # Addition microservice
│   ├── subtract-service/           # Subtraction microservice
│   └── multiply-service/           # Multiplication microservice
│
├── helm-charts/
│   ├── calculator-platform/        # Application Helm chart
│   │   ├── templates/              # Kubernetes manifests
│   │   │   ├── deployment.yaml     # Multi-version deployments
│   │   │   ├── service.yaml        # ClusterIP services
│   │   │   ├── configmap.yaml      # Configuration
│   │   │   ├── serviceaccount.yaml # IRSA configuration
│   │   │   └── spc.yaml            # Secrets Provider Class
│   │   └── values-qa.yaml          # QA environment values
│   │
│   └── istio-config/               # Istio service mesh config
│       ├── templates/
│       │   ├── gateway.yaml        # Ingress gateway
│       │   ├── virtualservice-*.yaml  # Traffic routing
│       │   ├── destinationrules.yaml  # Load balancing, mTLS
│       │   └── authorizationpolicy.yaml  # Security policies
│       └── values.yaml             # Traffic split configuration
│
├── argocd/
│   ├── apps/
│   │   ├── calculator-app.yaml     # Main application
│   │   └── istio-config-app.yaml   # Istio configuration
│   └── projects/
│       └── calculator-project.yaml # ArgoCD project definition
│
├── Resource-Finder/                # AWS resource monitoring tool
└── traffic-gen.sh                  # Load testing script
```

## 🚀 Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- kubectl installed
- Helm 3.x installed
- Terraform and Terragrunt installed
- Docker for building images

### 1. Deploy Infrastructure

```bash
cd Infra/terragrunt-resources/ap-south-1/qa

# Deploy VPC and networking
cd vpc-networking/vpc && terragrunt apply
cd ../subnet && terragrunt apply
cd ../igw && terragrunt apply
cd ../elastic-ips && terragrunt apply
cd ../nat && terragrunt apply
cd ../route_table && terragrunt apply
cd ../sg && terragrunt apply

# Deploy IAM roles
cd ../../iam && terragrunt apply

# Deploy EKS cluster
cd ../eks && terragrunt apply
```

### 2. Configure kubectl

```bash
aws eks update-kubeconfig --region ap-south-1 --name qa-eks
kubectl get nodes
```

### 3. Install Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.23.2 sh -
cd istio-1.23.2

# Install Istio with observability add-ons
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y

# Enable automatic sidecar injection
kubectl label namespace calculator istio-injection=enabled

# Install observability tools
kubectl apply -f samples/addons/kiali.yaml
kubectl apply -f samples/addons/jaeger.yaml
kubectl apply -f samples/addons/grafana.yaml
kubectl apply -f samples/addons/prometheus.yaml
```

### 4. Install ArgoCD

```bash
cd argocd
./install-argocd.sh

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

### 5. Deploy Applications

```bash
# Create ArgoCD project
kubectl apply -f argocd/projects/calculator-project.yaml

# Deploy calculator platform
kubectl apply -f argocd/apps/calculator-app.yaml

# Deploy Istio configuration
kubectl apply -f argocd/apps/istio-config-app.yaml

# Verify deployment
kubectl get applications -n argocd
```

### 6. Access the Application

```bash
# Get the Gateway URL
export GATEWAY_URL=$(kubectl get svc istio-ingressgateway \
  -n istio-system \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

echo "Gateway URL: http://$GATEWAY_URL"
```

## 🧪 Testing

### Manual Testing

```bash
# Test Addition
curl -X POST "http://$GATEWAY_URL/calculate" \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "a": 15, "b": 25}'

# Test Subtraction
curl -X POST "http://$GATEWAY_URL/calculate" \
  -H "Content-Type: application/json" \
  -d '{"operation": "subtract", "a": 50, "b": 20}'

# Test Multiplication
curl -X POST "http://$GATEWAY_URL/calculate" \
  -H "Content-Type: application/json" \
  -d '{"operation": "multiply", "a": 7, "b": 6}'

# Health Check
curl "http://$GATEWAY_URL/health"
```

### Automated Load Testing

```bash
# Run traffic generator
./traffic-gen.sh

# The script will continuously send requests:
# - Add operation every second
# - Subtract operation every second
# - Multiply operation every second
```

### Expected Response

```json
{
  "operation": "add",
  "a": 15.0,
  "b": 25.0,
  "result": 40.0,
  "timestamp": "2025-12-07T10:10:36.941251",
  "processed_by": "http://add-service:8001"
}
```

## 📊 Observability & Monitoring

### Access Kiali (Service Mesh Dashboard)

```bash
kubectl port-forward svc/kiali -n istio-system 20001:20001
# Open http://localhost:20001 (admin/admin)
```

**Features:**
- Real-time service graph with traffic flow
- Traffic distribution percentages
- mTLS security badges
- Configuration validation

### Access Jaeger (Distributed Tracing)

```bash
kubectl port-forward svc/tracing -n istio-system 16686:80
# Open http://localhost:16686
```

**Features:**
- End-to-end request tracing
- Latency analysis per service
- Dependency graphs
- Performance bottleneck identification

### Access Grafana (Metrics Dashboard)

```bash
kubectl port-forward svc/grafana -n istio-system 3000:3000
# Open http://localhost:3000 (admin/admin)
```

**Features:**
- Istio service dashboards
- Request rate, latency, error metrics
- Resource utilization graphs
- Custom alerting rules

### Access ArgoCD

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open https://localhost:8080
```

## 🔧 Configuration

### Adjusting Traffic Splits

Edit `helm-charts/istio-config/values.yaml`:

```yaml
trafficSplit:
  calculatorApi:
    v1Weight: 80  # Change to desired percentage
    v2Weight: 20
  addService:
    v1Weight: 70
    v2Weight: 30
  # ... etc
```

Commit and push - ArgoCD will automatically sync the changes.

### Scaling Services

Edit `helm-charts/calculator-platform/values-qa.yaml`:

```yaml
services:
  - name: calculator-api
    versions:
      - name: v1
        replicas: 5  # Increase replica count
        imageTag: v1.0.0
```

### Circuit Breaker Configuration

Edit `helm-charts/istio-config/values.yaml`:

```yaml
circuitBreaker:
  consecutive5xxErrors: 5  # Errors before ejection
  interval: 30s            # Detection interval
  baseEjectionTime: 30s    # Ejection duration
  maxEjectionPercent: 50   # Max % of pods ejected
```

## 🏗️ GitOps Methodology

The project uses **GitOps** principles with ArgoCD:

1. **Developer** commits code changes to GitHub
2. **GitHub** triggers image build (via `build-and-push.sh`)
3. **Images** pushed to Amazon ECR
4. **Developer** updates Helm values with new image tags
5. **ArgoCD** detects Git changes automatically
6. **ArgoCD** syncs cluster state with Git
7. **Kubernetes** performs rolling update
8. **Istio** manages traffic during deployment

### Deployment Flow

```
GitHub Repository (Single Source of Truth)
    ↓
ArgoCD (Watches for Changes)
    ↓
Helm Renders Templates with Values
    ↓
Kubernetes Applies Resources
    ↓
Istio Manages Traffic & Security
    ↓
Observability Tools Track Everything
```

## 🔐 Security Features

### mTLS (Mutual TLS)

All service-to-service communication is encrypted:

```bash
# Verify mTLS
kubectl exec -n calculator deployment/calculator-api-v1 -c istio-proxy -- \
  curl -s localhost:15000/config_dump | grep -A 5 "tls_context"
```

### Authorization Policies

```yaml
# Only calculator-api can call backend services
# Only istio-system can access calculator-api externally
```

### IRSA (IAM Roles for Service Accounts)

Services authenticate to AWS using IAM roles instead of access keys:

```bash
# Service account automatically gets AWS credentials
kubectl get serviceaccount calculator-sa -n calculator -o yaml
```

## 📈 Performance Metrics

Based on load testing:

- **Throughput**: ~1.5 requests/second sustained
- **Success Rate**: 99.9%
- **Average Latency**: 35-40ms per request
- **P95 Latency**: <100ms
- **Resource Usage**: 
  - CPU: <10% per pod
  - Memory: ~150Mi per pod

## 🐛 Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n calculator
kubectl describe pod <pod-name> -n calculator
kubectl logs <pod-name> -n calculator -c <container-name>
```

### Check Istio Sidecar Injection

```bash
# Should show 2/2 containers (app + istio-proxy)
kubectl get pods -n calculator
```

### Check ArgoCD Sync Status

```bash
kubectl get applications -n argocd
kubectl describe application calculator-platform-qa -n argocd
```

### View Istio Configuration

```bash
kubectl get gateway,virtualservice,destinationrule -n calculator
kubectl describe virtualservice calculator-api-main -n calculator
```

### Check Service Connectivity

```bash
kubectl exec -n calculator deployment/calculator-api-v1 -- \
  curl -s http://add-service:8001/health
```

## 🎓 Learning Resources

This project demonstrates the following concepts:

- **Microservices Architecture**: Service decomposition and communication
- **Service Mesh**: Traffic management, security, observability
- **GitOps**: Declarative infrastructure and application deployment
- **Infrastructure as Code**: Terraform and Terragrunt patterns
- **Kubernetes Patterns**: Deployments, services, config maps, secrets
- **Cloud Native Security**: mTLS, RBAC, IRSA, secrets management
- **Observability**: Metrics, logging, tracing (Prometheus, Jaeger, Grafana)
- **Progressive Delivery**: Canary deployments, traffic splitting
- **High Availability**: Multi-AZ deployment, auto-scaling
- **DevOps Best Practices**: Version control, automation, monitoring

## 🤝 Contributing

This is a demonstration project for learning and interview purposes. Feel free to fork and experiment!

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

**Arun Krishna**
- GitHub: [@ArunKhrishna](https://github.com/ArunKhrishna)
- LinkedIn: [Connect with me](https://linkedin.com/in/arunkhrishna)

## 🙏 Acknowledgments

- Istio documentation and community
- ArgoCD project
- AWS EKS best practices
- Kubernetes patterns and anti-patterns guides

---

**Built with ❤️ for demonstrating production-grade DevOps practices**
