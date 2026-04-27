# Environment — 실습 공통 개발 환경

도서 *"테슬라처럼 만드는 비전 자율주행과 피지컬 AI"* (이석창 지음, All That AI · Vol.01) 의 ch04 ~ ch25 실습이 공유하는 개발 환경 구축 디렉토리입니다. 도서 23장(개발 환경 구축) 의 본문과 1:1 로 연결됩니다.

## 두 갈래 설치 경로

### A. Docker (권장 · 가장 빠름)

GPU 가 있는 Ubuntu / WSL2 환경에서 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) 만 설치돼 있으면 5분에 끝납니다.

```bash
cd code/environment
docker build -t physical-ai-book:latest .
docker run --rm -it --gpus all \
    -p 8888:8888 -v $(pwd)/../..:/workspace \
    physical-ai-book:latest
```

브라우저에서 `http://localhost:8888` 열면 Jupyter Lab 이 뜹니다.

### B. 네이티브 (venv 기반)

도커 없이 본인 컴퓨터에 직접 설치하시려면:

```bash
cd code/environment
bash setup.sh
source .venv/bin/activate
```

`setup.sh` 가 (1) 시스템 패키지 → (2) 파이썬 venv → (3) `requirements.txt` 설치 → (4) CUDA 동작 확인 까지 한 번에 처리합니다.

## 환경 변수 (`.env`)

대용량 데이터셋 경로 등을 본인 환경에 맞춰 설정합니다.

```bash
cp .env.sample .env
# .env 열어서 DATA_DIR, NUSCENES_ROOT, BDD100K_ROOT 등 수정
```

각 장의 노트북은 [python-dotenv](https://pypi.org/project/python-dotenv/) 로 이 값을 읽습니다.

## 별도 환경이 필요한 장

| 장 | 별도 환경 | 위치 |
|---|---|---|
| ch27 Isaac Lab | NVIDIA Isaac Sim 4.x · 별도 설치 가이드 | [code/ch27_isaac_lab/](../ch27_isaac_lab/) |
| ch29 MentorPi 실증 | HiWonder MentorPi + ROS2 Humble (실 하드웨어) | [code/ch29_mentorpi/](../ch29_mentorpi/) |
| ch30 ROS2 통합 | ROS2 Humble (Ubuntu 22.04 권장) | [code/ch30_ros2/](../ch30_ros2/) |

위 세 장은 본 `environment/` 와 별도로 각 디렉토리의 안내를 따르세요.

## 검증된 시스템 사양

| 항목 | 권장 |
|---|---|
| OS | Ubuntu 22.04 LTS · Windows 11 + WSL2 · macOS 14 (M2/M3, CPU 만) |
| Python | 3.11 |
| CUDA | 12.4 (GPU 학습 시) |
| GPU | NVIDIA RTX 30/40 시리즈 12GB+ (ch24, ch25 학습 기준) |
| RAM | 32GB+ (대형 모델 학습 시 64GB 권장) |
| 저장 | SSD 500GB+ (nuScenes mini · BDD100K 합산 시) |

GPU 가 없는 노트북에서도 ch04 ISP, ch11 Control, ch20 BC 일부 등 **CPU 만으로 돌아가는 노트북** 이 있습니다. 각 장 README 의 *"GPU 필요 여부"* 표시를 참고하세요.

## 문제 해결

- **CUDA 인식 안 됨** : `nvidia-smi` 가 호스트에서 동작하는지 먼저 확인. WSL2 라면 Windows 측 NVIDIA 드라이버 최신화
- **OpenCV import 실패** : `apt install libgl1 libglib2.0-0 libsm6 libxext6` (Dockerfile 에는 이미 포함)
- **PyTorch 와 CUDA 버전 불일치** : `requirements.txt` 의 `torch==2.5.1` 이 CUDA 12.4 에 빌드된 휠. 본인 CUDA 가 다르면 [pytorch.org/get-started](https://pytorch.org/get-started/locally/) 에서 휠 명령 재확인

기타 문제는 [Issues](https://github.com/leelang7/physical-ai-book/issues) 에 제보해 주세요.
