# Chapter 14 · CARLA 시뮬레이션 — 데이터 수집

도서 **14장** *"시뮬레이션과 Corner Case 증강"* 와 1:1 연결.

CARLA 0.9.15 가 별도 설치돼야 실행 가능. 본 디렉토리는 *어떻게 쓰는가* 의 패턴.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`carla_collect_demo.py`](carla_collect_demo.py) | CARLA 데이터 수집 코드 골격 + 환경 확인 |

## CARLA 설치

CARLA 는 무거워서 본 저장소에 포함 불가. 두 가지 경로:

### A. Docker (권장)
```bash
docker pull carlasim/carla:0.9.15
docker run --rm -it --gpus all --network=host \
    carlasim/carla:0.9.15 \
    ./CarlaUE4.sh -RenderOffScreen
```

### B. Native (Ubuntu 22.04, NVIDIA GPU)
```bash
# https://carla.readthedocs.io/en/0.9.15/start_quickstart/
sudo apt install python3-pip
pip install --user carla==0.9.15

# CARLA 서버 시작 (별도 터미널)
./CarlaUE4.sh
```

## 실행

CARLA 서버가 떠 있는 상태에서:
```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
pip install --user carla==0.9.15
cd ../ch14_carla
python carla_collect_demo.py
```

## 학습 포인트

1. **시뮬레이션의 진짜 가치** (14.2 절) — 사고 상황·드문 케이스를 *안전하게* 학습. CARLA 는 *비· 안개·야간·돌발 보행자* 등을 명령 한 줄로.
2. **Sim2Real 격차** (14.4 절) — CARLA 학습 모델은 실 차량에서 그대로 안 됨. *Domain randomization* (텍스처·조명·노이즈) + *adversarial augmentation* 필수.
3. **Corner Case 증강** (14.5 절) — CARLA 가 진가를 발휘하는 곳. 실 데이터에선 100만 km 굴려야 만나는 사건을 시뮬에서 1시간에 1000번 생성.

## 다음

- [ch20 BC + DAgger](../ch20_bc_dagger/) — CARLA 수집 데이터로 BC 학습
- [ch21 RL](../ch21_rl/) — CARLA 에서 강화학습 실험 (CarRacing 류 환경)
- [ch27 Isaac Lab](../ch27_isaac_lab/) — NVIDIA Isaac Lab 의 카메라 시뮬레이션
