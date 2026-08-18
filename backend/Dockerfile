FROM python:3.11

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-base.txt .
COPY requirements-ai.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements-base.txt
RUN pip install --no-cache-dir -r requirements-ai.txt

RUN pip uninstall -y jax jaxlib || true

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
