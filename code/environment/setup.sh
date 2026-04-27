#!/usr/bin/env bash
# code/environment/setup.sh — Ubuntu 22.04 / WSL2 네이티브 부트스트랩
#
# 사용법:
#   cd code/environment
#   bash setup.sh
#
# 도커를 쓰는 경우 setup.sh 불필요 — Dockerfile 만 사용.

set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3.11}"
VENV_DIR="${VENV_DIR:-.venv}"

echo "== Tesla Vision + Physical AI 실습 환경 부트스트랩"
echo "   Python : $PYTHON_BIN"
echo "   venv   : $VENV_DIR"

# 1) 시스템 패키지 (sudo 권한 필요)
if [ "$(uname)" = "Linux" ]; then
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends \
        "$PYTHON_BIN" "${PYTHON_BIN}-venv" python3-pip \
        git ffmpeg libsm6 libxext6 libgl1 build-essential
fi

# 2) 가상 환경
if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# 3) Python 의존성
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4) 동작 확인 (CUDA 가용성)
python - <<'PY'
import torch
print(f"  torch        : {torch.__version__}")
print(f"  CUDA 가용    : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU          : {torch.cuda.get_device_name(0)}")
PY

echo
echo "== 완료. 다음 명령으로 환경 활성화:"
echo "   source code/environment/$VENV_DIR/bin/activate"
