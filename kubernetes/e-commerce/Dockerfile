FROM nginx:latest
COPY html/ /usr/share/nginx/html/            # HTML files
COPY nginx/default.conf /etc/nginx/conf.d/   # Custom Nginx config

#FROM python:3.9-slim
#WORKDIR /app
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#COPY src/product_catalog_service.py .
#CMD ["python", "product_catalog_service.py"]