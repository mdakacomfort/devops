# Setting up ArgoCD with Minikube for Continuous Deployment

This guide walks you through setting up ArgoCD on a Minikube cluster to automatically deploy changes from a GitHub repository to your Kubernetes deployment, including troubleshooting common issues.

![Status](https://github.com/mdakacomfort/devops/blob/main/argocd/Images/Status.png)


## Prerequisites

- Minikube installed and running
- kubectl installed and configured to use your Minikube cluster
- A GitHub account and a repository with your Kubernetes manifests (You can clone my repo, but try to create your own)
- Git installed on your local machine
- Docker installed for building and pushing images

## Clone the repo (if you do not have your own)
```
https://github.com/mdakacomfort/devops/tree/main/argocd
```
## Project Structure

```
repo/
├── postgres/
│   ├── postgres-secret.yaml
│   ├── postgres-pvc.yaml
│   ├── postgres-deployment.yaml
│   └── postgres-service.yaml
├── flask-app/
│   ├── flask-app-deployment.yaml
│   └── flask-app-service.yaml
├── app/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
└── README.md
```

## Step 1: Install ArgoCD

1. Start your Minikube cluster:
   ```
   minikube start
   ```

2. Create the argocd namespace:
   ```
   kubectl create namespace argocd
   ```

3. Apply the ArgoCD installation manifest:
   ```
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

4. Wait for ArgoCD pods to be ready:
   ```
   kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=argocd-server -n argocd
   ```

## Step 2: Set Up FlaskApp

1. Create a flask-app-deployment.yaml file (contents are in the repo)


2. Create a flask-app-service.yaml (contents are in the repo)


3. Apply the deployments:
   ```
   kubectl apply -f flask-app-deployment.yaml
   kubectl apply -f flask-app-service.yaml
   ```


## Step 3: Set Up PostgreSQL
Create/Update your postgres-secret.yaml file:
```
apiVersion: v1
kind: Secret
metadata:
name: postgres-secret
type: Opaque
data:
POSTGRES_DB: <base64-encoded-db-name>
POSTGRES_USER: <base64-encoded-username>
POSTGRES_PASSWORD: <base64-encoded-password>
```
Replace <base64-encoded-*> with your actual base64 encoded values.

See URL for encoding credentials: https://www.base64encode.org/

Create a postgres-pvc.yaml file:
```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Create a postgres-deployment.yaml file:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:13
          env:
            - name: POSTGRES_DB
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_DB
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_PASSWORD
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
```

Create a postgres-service.yaml file:
```
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  type: ClusterIP
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432

```

Apply postgres deployments:

```
kubectl apply -f postgres-secret.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-service.yaml
kubectl apply -f postgres-deployment.yaml
```

   
## Step 4: Access ArgoCD UI

1. Port-forward the ArgoCD server:
   ```
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```

2. Access the ArgoCD UI at `https://localhost:8080`

3. Get the initial admin password:
   ```
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```

4. Log in with username `admin` and the password obtained in step 3.

## Step 5: Configure ArgoCD to Watch Your GitHub Repository

1. In the ArgoCD UI, click on '+ NEW APP'

2. Fill in the application details:
    - Application Name: Use a name that follows Kubernetes naming conventions (lowercase, alphanumeric, hyphens)
    - Project: Select 'default' or create a new project
    - Sync Policy: Choose 'Automatic' for auto-sync
    - Repository URL: Your GitHub repository URL (e.g., https://github.com/yourusername/yourrepo.git)
    - Revision: Main branch (or whichever branch you want to sync from)
    - Path: The path in your repo where Kubernetes manifests are located (in our case its `argo`)
    - Cluster: https://kubernetes.default.svc
    - Namespace: The namespace where you want to deploy your application

3. Click 'Create' to set up the application

![AppCreation](https://github.com/mdakacomfort/devops/blob/main/argocd/Images/AppCreation.png)


## Troubleshooting

### Permission Denied When Creating Application

If you encounter a "permission denied" error:

1. Check ArgoCD's server role:
   ```
   kubectl get clusterrolebinding -n argocd | grep argocd-server
   ```

2. If no result, create a ClusterRoleBinding for ArgoCD:
   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRoleBinding
   metadata:
     name: argocd-server-clusterrolebinding
   roleRef:
     apiGroup: rbac.authorization.k8s.io
     kind: ClusterRole
     name: cluster-admin
   subjects:
   - kind: ServiceAccount
     name: argocd-server
     namespace: argocd
   ```
   Save this to `argocd-clusterrolebinding.yaml` and apply:
   ```
   kubectl apply -f argocd-clusterrolebinding.yaml
   ```

### Project Not Found

If you see an error about a project not found, create the project first:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: your-project-name
  namespace: argocd
spec:
  description: Description of your project
  sourceRepos:
  - '*'
  destinations:
  - namespace: '*'
    server: https://kubernetes.default.svc
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
```
Save this to `argocd-project.yaml` and apply:
```
kubectl apply -f argocd-project.yaml
```
![Status](https://github.com/mdakacomfort/devops/blob/main/argocd/Images/Status.png)

## Step 6: Set Up Python

Create an app.py file:
```
import os
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

def get_db_connection():
connection = psycopg2.connect(
dbname=os.environ.get('POSTGRES_DB'),
user=os.environ.get('POSTGRES_USER'),
password=os.environ.get('POSTGRES_PASSWORD'),
host='postgres-service',
port=5432
)
return connection

@app.route('/')
def index():
return "Welcome to the Flask App with PostgreSQL!"

@app.route('/data')
def get_data():
conn = get_db_connection()
cur = conn.cursor()
cur.execute('SELECT version();')
db_version = cur.fetchone()
cur.close()
conn.close()
return jsonify({"PostgreSQL Version": db_version})

if __name__ == "__main__":
app.run(host='0.0.0.0', port=5000)
```

Create a Dockerfile in the app/ directory:
```
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```
Create a requirements.txt file:
```
Flask==2.0.1
Werkzeug==2.0.1
psycopg2-binary==2.9.3
```
Build and push your Docker image:
```
docker login
docker build -t yourdockerhubusername/flask-app:latest .
docker push yourdockerhubusername/flask-app:latest
```


## Step 6: Testing the Application

Port-forward the Flask application service:
```
kubectl port-forward svc/flask-app-service 5000:5000
```
Access the application:

Welcome page: http://localhost:5000/

Database info: http://localhost:5000/data

![Diff](https://github.com/mdakacomfort/devops/blob/main/argocd/Images/Diff.png)

## Troubleshooting
Check Pod Status
```
kubectl get pods
```
View Pod Logs
```
kubectl logs <pod-name>
```
Check Environment Variables
```
kubectl exec <pod-name> -- env | grep POSTGRES
```
Test Database Connection from Pod
```
kubectl exec -it <pod-name> -- /bin/bash
python
>>> import os
>>> import psycopg2
>>> conn = psycopg2.connect(dbname=os.environ.get('POSTGRES_DB'), user=os.environ.get('POSTGRES_USER'), password=os.environ.get('POSTGRES_PASSWORD'), host='postgres-service', port=5432)
>>> cur = conn.cursor()
>>> cur.execute('SELECT version();')
>>> print(cur.fetchone())
```
Check PostgreSQL Service Accessibility
```
kubectl exec -it <pod-name> -- /bin/bash
nc -zv postgres-service 5432
```

## Additional Tips

- Always check ArgoCD server logs for detailed error messages:
  ```
  kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server
  ```
- Ensure your Kubernetes manifests are in the correct location in your repository
- Verify that the namespace you're deploying to exists in your cluster
- For Helm charts, ensure the path points to the directory containing the Chart.yaml file

## Additional Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/en/stable/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)

