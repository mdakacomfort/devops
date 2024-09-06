# Configure Prometheus & Grafana: A Step-by-Step Guide

## Why Monitor Your Systems?

How do you identify issues when something goes wrong, or measure success when optimizing a system? Monitoring tools provide critical insights to detect problems early and validate improvements effectively.


![Head](https://github.com/mdakacomfort/devops/grafana_prometheus/Images/Head.png)

## Prerequisites

.NET 6 SDK

Docker

Docker Compose


## Step 1: Create a .NET API

Create a simple boilerplate dotnet API with 

`dotnet new webapi --name WeatherAPI`

`cd WeatherAPI`

Add Prometheus NuGet packages

`dotnet add package prometheus-net --version 7.0.0`

`dotnet add package prometheus-net.AspNetCore --version 7.0.0`

Modify Program.cs to enable Prometheus metrics:

```
app.UseRouting();

// Capture metrics about all received HTTP requests.
`app.UseHttpMetrics();`

app.UseEndpoints(endpoints =>
{
endpoints.MapControllers();
// Enable the /metrics page to export Prometheus metrics.
endpoints.MapMetrics();
});

// Remove the following line if present (**this requires an SSL certificate**):
// app.UseHttpsRedirection();
```

## Step 2: Implement Custom Metrics

Create AppMetrics.cs

```
using Prometheus;

namespace WeatherAPI
{
    public class AppMetrics
    {
        public static readonly Counter WeatherRequestCount = Metrics
            .CreateCounter("weather_request_total", "Number of weather API calls.");
        
        public static readonly Gauge LastRequestDuration = Metrics
            .CreateGauge("weather_last_request_duration", "Duration of last request.");
        
        public static readonly Histogram CallDuration = Metrics
            .CreateHistogram("weather_request_duration", "Histogram of weather API call duration.",
                new HistogramConfiguration
                {
                    Buckets = new double[] { 0.1, 0.2, 0.5, 0.7, 1 }
                });
    }
}
```

Update WeatherForecastController.cs

```
[HttpGet(Name = "GetWeatherForecast")]
public IEnumerable<WeatherForecast> Get()
{
    AppMetrics.WeatherRequestCount.Inc();
    
    using (AppMetrics.CallDuration.NewTimer())
    {
        var stopWatch = new Stopwatch();
        stopWatch.Start();

        var data = Enumerable.Range(1, 5).Select(index => new WeatherForecast
        {
            Date = DateTime.Now.AddDays(index),
            TemperatureC = Random.Shared.Next(-20, 55),
            Summary = Summaries[Random.Shared.Next(Summaries.Length)]
        }).ToArray();

        Thread.Sleep(Random.Shared.Next(100, 1000));

        AppMetrics.LastRequestDuration.Set(stopWatch.ElapsedMilliseconds);

        return data;
    }
}
```

## Step 3: Set Up Prometheus and Grafana

Create docker-compose.yml

```
version: "3.9"
services:
  prometheus:
    image: bitnami/prometheus
    container_name: prometheus
    ports:
      - '9090:9090'
    volumes:
      - ./prometheus.yml:/opt/bitnami/prometheus/conf/prometheus.yml

  grafana:
    image: grafana/grafana
    container_name: grafana
    depends_on:
      - prometheus
    ports:
      - '3000:3000'
```
Create prometheus.yml

```
global:
  scrape_interval: 5s
  evaluation_interval: 5s
scrape_configs:
  - job_name: 'metrics_collection'
    static_configs:
      - targets: ['host.docker.internal:5000']
```
Note: Replace '5000' with your API's port if different.

## Step 4: Run the Project
Start your .NET API:

`dotnet build`

`dotnet run`

In a new terminal, start Prometheus and Grafana

`docker-compose up -d`

Access Grafana at http://localhost:3000 (login: admin/admin)

Add Prometheus as a data source:

    URL: http://prometheus:9090

![Datasource](https://github.com/mdakacomfort/devops/grafana_prometheus/Images/Datasource.png)

Create a new dashboard with these example queries:

Request Rate: `sum(rate(weather_request_total[1m])) * 60`

Last Request Duration: `weather_last_request_duration`

Request Duration Heatmap: 
`sum by (le) (increase(weather_request_duration_bucket[1m]))`

## Next Steps
Explore more Prometheus metrics and Grafana visualizations

Set up alerting based on your metrics

Integrate this monitoring setup into your CI/CD pipeline

Happy monitoring!
