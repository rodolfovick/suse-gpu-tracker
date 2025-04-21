# suse-gpu-tracker

Code to manage nodes with node-type equals to gpu-node.

## Introduction

The code is based on the provided Custom Resource Definition file:

```yaml
---
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: gputrackers.suse.tests.dev
spec:
  group: suse.tests.dev
  names:
    kind: GPUTracker
    listKind: GPUTrackerList
    plural: gputrackers
    singular: gputracker
    shortNames:
    - gputkr
  scope: Cluster
  versions:
  - name: v1
    schema:
      openAPIV3Schema:
        description: GPUTracker is the Schema for keeping track of number of GPU nodes in a cluster
        properties:
          apiVersion:
            description: 'APIVersion defines the versioned schema of this representation
              of an object. Servers should convert recognized schemas to the latest
              internal value, and may reject unrecognized values. More info:
              https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
            type: string
          metadata:
            type: object
          gpu_nodes:
            description: Comma separated list of GPU nodes
            type: string
        required:
        - gpu_nodes
        type: object
    served: true
    storage: true
```

The ideia is to create the CRD on the Kubernetes cluster and start a Kubernetes operator to manipulate the new nodes with ` ```node-type: gpu-node```.

## How to test

The development was done using **Minikube** as the Kubernetes distribution. 

The docker container that runs the operator was created locally, using the provided *Dockerfile*.

To make deployment easy, a simple **Helm Chart** was created.

### Create Docker image

```bash
cd docker
docker build -t gputracker-operator:v1
```

This will create a local image named gputracker-operator, version V1.

### Install Helm chart

```bash
cd kubernetes
helm install suse-gpu-tracker suse-gpu-tracker/
```

This will install the Helm Chart, adding the CRD and deploying the Kubernetes controller for suse-gpu-tracker.

### Create new nodes

To test the code, you can create a few nodes, with ```node-type: gpu-node```. The file gpu-node.yml is an example how to create the nodes. 

You can check the list of gpu-nodes with the command: ```kubectl get gputrackers.suse.tests.dev suse-gpu-tracker -o yaml```. All new nodes must appear on the gpu-nodes list.

The following tests were covered during development:

- Add a new node.
- Remove the node.
- Add multiple nodes.
- Remove multiple nodes.
- Modify an existing node, adding node-type equals to gpu-node.
- Modify an existing node, removing node-type equals to gpu-node.

**For testing, there is a PyTest script called test_gputracker.py that can be used to validate the test cases above.**

