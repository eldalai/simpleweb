FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and ibm-iaccess in a single step
RUN apt update && \
    apt install -y unixodbc unixodbc-dev odbcinst curl && \
    curl https://public.dhe.ibm.com/software/ibmi/products/odbc/debs/dists/1.1.0/ibmi-acs-1.1.0.list | tee /etc/apt/sources.list.d/ibmi-acs-1.1.0.list && \
    apt update && \
    apt install -y ibm-iaccess && \
    rm -rf /var/lib/apt/lists/*  # Clean up cache to reduce layer size

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
