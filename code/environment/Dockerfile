# Tesla Vision + Physical AI 실습 도커 이미지
# 베이스 : PyTorch 2.5 + CUDA 12.4 (NVIDIA Container Toolkit 필요)
#
# 빌드 :
#   cd code/environment
#   docker build -t physical-ai-book:latest .
#
# 실행 (Jupyter Lab) :
#   docker run --rm -it --gpus all \
#     -p 8888:8888 -v $(pwd)/../..:/workspace \
#     physical-ai-book:latest

FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
        git wget curl ca-certificates \
        ffmpeg libsm6 libxext6 libgl1 \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

EXPOSE 8888

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", "--port=8888", \
     "--no-browser", "--allow-root", \
     "--ServerApp.token=", "--ServerApp.password="]
