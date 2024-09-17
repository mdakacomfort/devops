FROM python:3.9-slim

WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Add the trusted hosts to bypass SSL verification issues
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy the rest of the application
COPY . .

CMD ["python", "app.py"]

