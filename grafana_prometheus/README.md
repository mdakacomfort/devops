# Kubernetes Monitoring with Prometheus and Grafana

This project demonstrates how to set up a Kubernetes cluster with Minikube and implement monitoring using Prometheus and Grafana.

![Cluster](https://github.com/mdakacomfort/devops/blob/main/grafana_prometheus/Images/Cluster.png)


## Prerequisites

- Docker
- Minikube 
- kubectl 
- helm (optional, for easy Grafana installation)

## Clone the repo (if you do not have your own)
```
https://github.com/mdakacomfort/devops/tree/main/grafana_prometheus
```
## Repo layout

```
repo/
├── prometheus/
│   ├── prometheus-config.yaml
│   ├── prometheus-deployment.yaml
│   ├── prometheus-rbac.yaml
├── purchase-app-deployment/
│   ├── purhcase-app-deployment.yaml
├── Images/
│   ├── Cluster.png
│   ├── Deployment.png
│   ├── Kubernetes.png
│   ├── Promethues.png
└── README.md
```

## Setup Steps

1. Start your Minikube cluster:
    ```
    minikube start --driver=docker
    ```

2. Enable Minikube addons:
    ```
    minikube addons enable metrics-server
    minikube addons enable dashboard
    ```

3. Create a namespace for our monitoring setup:
    ```
    kubectl create namespace ansible
    ```

4. Set up RBAC for Prometheus. Create a file named prometheus-rbac.yaml:
    ```
    < contents of prometheus-rbac.yaml are in the repo >
    ```

5. Apply the RBAC configuration
    ```
    kubectl apply -f prometheus-rbac.yaml
    ```
   
6. Create a ConfigMap for Prometheus. Create a file named prometheus-config.yaml
    ```
    < contents of prometheus-config.yaml are in the repo >
    ```

7. Apply the ConfigMap   
    ```
    kubectl apply -f prometheus-config.yaml
    ```
   
8. Deploy Prometheus. Create a file named prometheus-deployment.yaml
    ```
    < contents of prometheus-deployment.yaml are in the repo >
    ```
   
9. Apply the Prometheus deployment and service:
    ```
    kubectl apply -f prometheus-deployment.yaml
    ```
   
10. Deploy a sample application with Prometheus metrics. Create a file named purchase-app-deployment.yaml
    ```
    < contents of purchase-app-deployment.yaml are in the repo >
    ```

11. Apply the purchase app deployment:
    ```
    kubectl apply -f purchase-app-deployment.yaml
    ```

12. Install Grafana
    ```
    kubectl create deployment grafana --image=grafana/grafana:latest -n ansible
    kubectl expose deployment grafana --type=NodePort --port=3000 -n ansible
    ```

13. Access Prometheus and Grafana
- a. For Prometheus:
    ```
    kubectl port-forward -n ansible svc/prometheus 9090:9090
    ```
Then access Prometheus at: http://localhost:9090  

- b. For Grafana:   
    ```
    kubectl port-forward -n ansible svc/grafana 3000:3000
    ```
Then access Grafana at: http://localhost:3000  

![Deployment](https://github.com/mdakacomfort/devops/blob/main/grafana_prometheus/Images/Deployment.png)

- c. For Kubernetes Dashboard:     
    ```
    minikube dashboard --url
    ```
- This will print the URL, which you can then open in your preferred browser.
- Note: Keep the terminal running while you're using the dashboard. To stop it, press Ctrl+C.

    ```
    minikube service prometheus -n ansible
    minikube service grafana -n ansible
    ```
    
14. Configure Grafana
- Log in to Grafana (default credentials: admin/admin)
- Add Prometheus as a data source (use the Prometheus service URL: http://prometheus:9090)
- Import dashboards (e.g., dashboard ID: 315, 741, 747)

Note: When using port-forwarding, keep the terminal windows open. Each service (Prometheus and Grafana) will need its own terminal window for port-forwarding.

![Kubernetes](https://github.com/mdakacomfort/devops/blob/main/grafana_prometheus/Images/Kubernetes.png)

## Troubleshooting

- If pods are not showing up in Prometheus, check their labels and annotations. 
- Verify RBAC permissions if Prometheus can't scrape certain resources. 
- Check pod logs for any errors:
    ```
    kubectl logs -l app=purchase-app -n ansible -c nginx-exporter
    ```

## Next Steps

- Set up alerting rules in Prometheus
- Create custom Grafana dashboards
- Implement log aggregation with tools like Loki

## Contributing
Feel free to submit issues or pull requests to improve this project.
