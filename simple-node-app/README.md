# DevOps Journey: CI/CD Pipeline with Jenkins and Kubernetes

Welcome! 
This project is designed to guide you through setting up a CI/CD pipeline using Jenkins and Kubernetes for a simple Node.js application. It's perfect for beginners looking to take their first steps into the world of DevOps.

## Project Overview

In this project, we'll:
- Create a simple Node.js application
- Containerize it with Docker
- Set up a CI/CD pipeline with Jenkins
- Deploy to Kubernetes (using Minikube)

This hands-on experience will introduce you to key DevOps concepts and tools.

## Prerequisites

- WSL (Ubuntu 22.04.3)
- Familiarity with Git
- A computer with at least 8GB RAM and 20GB free disk space

## Tools We'll Use

- Node.js and npm
- Docker
- Minikube (local Kubernetes cluster)
- kubectl (Kubernetes command-line tool)
- Jenkins

## Step-by-Step Guide

### 1. Set Up Your Development Environment

a. Install Node.js and npm: [Node.js Download](https://nodejs.org/)

b. Install Docker: [Docker Installation Guide](https://docs.docker.com/get-docker/)

c. Install Minikube: [Minikube Installation Guide](https://minikube.sigs.k8s.io/docs/start/)

d. Install kubectl: [kubectl Installation Guide](https://kubernetes.io/docs/tasks/tools/)

### 2. Create a Simple Node.js Application

a. Create a new directory for your project:
```bash
mkdir simple-node-app
cd simple-node-app
```

b. Initialize a new Node.js project:
```bash
npm init -y
```

c. Create `app.js` with the following content:
```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello World from Kubernetes!');
});

const port = 3000;
server.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```

### 3. Containerize the Application

a. Create a `Dockerfile`:
```dockerfile
FROM node:14
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD [ "node", "app.js" ]
```

b. Build and test the Docker image:
```bash
docker build -t simple-node-app .
docker run -p 3000:3000 simple-node-app
```

### 4. Set Up Minikube

a. Start Minikube:
```bash
minikube start
```

![Start](https://github.com/mdakacomfort/devops/tree/main/simple-node-app/Images/Start.png)

b. Enable necessary addons:
```bash
minikube addons enable ingress
minikube addons enable registry
minikube addons enable metrics-server
```

c. View addons:
```bash
minikube addons list
```
![Addons](https://github.com/mdakacomfort/devops/tree/main/simple-node-app/Images/Addons.png)

### 5. Deploy Jenkins to Minikube

a. Create a namespace for Jenkins:
```bash
kubectl create namespace jenkins
```

b. Create `jenkins-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
      volumes:
      - name: jenkins-home
        emptyDir: {}
```

c. Apply the deployment:
```bash
kubectl apply -f jenkins-deployment.yaml
```

d. Create a service for Jenkins:
```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: jenkins
  namespace: jenkins
spec:
  type: NodePort
  ports:
    - port: 8080
      targetPort: 8080
  selector:
    app: jenkins
EOF
```

e. Access Jenkins:
```bash
minikube service jenkins -n jenkins --url
```

### 6. Configure Jenkins

a. Get the initial admin password:
```bash
kubectl exec -it $(kubectl get pods -n jenkins -l app=jenkins -o jsonpath='{.items[0].metadata.name}') -n jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword
```

b. Install suggested plugins and create an admin user.


c. Install additional plugins: Kubernetes plugin, Docker Pipeline plugin.

![Plugins](https://github.com/mdakacomfort/devops/tree/main/simple-node-app/Images/Plugins.png)

d. Configure Kubernetes cloud in Jenkins:
- Manage Jenkins > Manage Nodes and Clouds > Configure Clouds
- Add a new Kubernetes cloud
- Kubernetes URL: https://kubernetes.default.svc
- Kubernetes Namespace: jenkins
- Credentials: - none -

### 7. Create a Jenkins Pipeline

a. Create a `Jenkinsfile` in your project root:
```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: docker
                    image: docker:dind
                    command:
                    - cat
                    tty: true
                    volumeMounts:
                    - name: docker-sock
                      mountPath: /var/run/docker.sock
                volumes:
                - name: docker-sock
                  hostPath:
                    path: /var/run/docker.sock
            '''
        }
    }
    stages {
        stage('Build') {
            steps {
                container('docker') {
                    sh 'docker build -t simple-node-app .'
                }
            }
        }
        stage('Test') {
            steps {
                container('docker') {
                    sh 'docker run simple-node-app npm test'
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
```

b. Create `deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simple-node-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: simple-node-app
  template:
    metadata:
      labels:
        app: simple-node-app
    spec:
      containers:
      - name: simple-node-app
        image: simple-node-app:latest
        ports:
        - containerPort: 3000
```

### 8. Run the Pipeline

a. Create a new pipeline job in Jenkins, pointing to your GitHub repository.

b. Run the pipeline and monitor its progress.

![Pipeline](https://github.com/mdakacomfort/devops/tree/main/simple-node-app/Images/Pipeline.png)

### 9. Verify Deployment

a. Check the deployment status:
```bash
kubectl get deployments
kubectl get pods
```

b. Access your application:
```bash
minikube service simple-node-app
```

## Troubleshooting

- If Jenkins can't connect to Kubernetes, ensure the Kubernetes plugin is configured correctly.
- For Docker socket issues, verify its accessibility in Minikube:
  ```bash
  minikube ssh
  ls -l /var/run/docker.sock
  ```
- If pods are not scheduling, check Minikube's resources:
  ```bash
  minikube status
  ```

## Next Steps in Your DevOps Journey

- Implement automated testing in your pipeline
- Explore continuous deployment strategies
- Learn about monitoring and logging in Kubernetes
- Dive into Infrastructure as Code (IaC) with tools like Terraform
- Explore configuration management tools like Ansible

Remember, DevOps is about continuous learning and improvement. Keep experimenting and building!

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.