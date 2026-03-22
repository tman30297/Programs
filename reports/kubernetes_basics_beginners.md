# Kubernetes Basics for Beginners

## What is Kubernetes?
Kubernetes (K8s) is an open-source platform for managing containerized workloads and services. Originally developed by Google, it automates deployment, scaling, and operations of application containers.

**Name origin:** Greek for "helmsman/pilot" | K8s = K + 8 letters + s

## Why Use Kubernetes?

### Core Capabilities
- **Service Discovery & Load Balancing** - DNS-based or IP-based exposure
- **Storage Orchestration** - Auto-mount local/cloud storage
- **Automated Rollouts/Rollbacks** - Describe desired state, Kubernetes manages changes
- **Automatic Bin Packing** - Optimizes resource allocation (CPU/RAM)
- **Self-Healing** - Restarts failed containers, replaces unhealthy ones
- **Secret & Configuration Management** - Store sensitive data securely
- **Horizontal Scaling** - Scale with command, UI, or auto based on CPU
- **Batch Execution** - Manage CI/CD workloads
- **IPv4/IPv6 Dual-Stack** - Modern networking support

### What Kubernetes is NOT
- Not a traditional PaaS (works at container level, not hardware)
- Doesn't deploy source code or build applications
- Doesn't provide built-in middleware, databases, or caches
- Doesn't mandate logging/monitoring solutions
- Not orchestration (eliminates need for it via declarative control loops)

## Kubernetes Architecture

### Key Components

#### Control Plane (Master Node)
- **API Server** - REST API for cluster communication
- **etcd** - Distributed key-value store (cluster state)
- **Scheduler** - Assigns pods to nodes
- **Controller Manager** - Runs controller loops

#### Worker Nodes
- **Kubelet** - Agent running on each node
- **Kube Proxy** - Network proxy for pods
- **Container Runtime** - Docker, containerd, etc.

### Core Objects

#### Pod
- Smallest deployable unit
- One or more containers sharing storage/network
- Ephemeral, disposable

#### Service
- Stable network endpoint for pods
- Load balancing across pod replicas

#### Deployment
- Declarative updates for pods/replica sets
- Manages rollout/rollback

#### ReplicaSet
- Ensures N running pod replicas
- Used by Deployments

#### Namespace
- Virtual cluster isolation
- Resource quota enforcement

## Getting Started

### Local Development
- **Minikube** - Single-node local Kubernetes
- **Kind** - Kubernetes in Docker

### Cloud Kubernetes Services
- **GKE** - Google Kubernetes Engine
- **EKS** - Amazon Elastic Kubernetes Service
- **AKS** - Azure Kubernetes Service

### Basic Commands
```bash
# Create deployment
kubectl create deployment my-app --image=nginx

# Scale deployment
kubectl scale deployment my-app --replicas=3

# View pods
kubectl get pods

# View services
kubectl get services

# Apply configuration
kubectl apply -f deployment.yaml

# Delete resources
kubectl delete deployment my-app
```

## Common Use Cases
1. Microservices deployment
2. Continuous deployment pipelines
3. Auto-scaling applications
4. Multi-cloud deployments
5. Batch job processing

---

*Generated: 2026-03-14*
