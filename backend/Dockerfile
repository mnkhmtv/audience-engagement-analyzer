FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /usr/src/app

# System deps required by OpenCV/MediaPipe/ONNXRuntime
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --timeout 120 --retries 5 -r requirements.txt

COPY . .

# alembic.ini должен быть в корне проекта
# CMD переопределяется compose'ом; здесь на всякий случай:
# Run the app; DB tables are created at startup by init_db
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
