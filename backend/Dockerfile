FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch (500MB instead of 2GB)
RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Rest of dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir \
    fastapi "uvicorn[standard]" pydantic "pydantic[email]" email-validator python-multipart \
    "python-jose[cryptography]" argon2-cffi pymongo python-dotenv \
    certifi authlib httpx itsdangerous \
    pillow numpy scikit-learn timm albumentations \
    reportlab cloudinary

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
