# Chapter 27 · Isaac Lab — Physical AI 에이전트 학습

도서 **27장** *"Isaac Lab 으로 Physical AI 에이전트 학습"* 와 1:1 연결.

NVIDIA Isaac Sim 4.x + Isaac Lab 별도 설치 필요. 본 디렉토리는 *코드 골격 + 설치 가이드*.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`isaac_lab_skeleton.py`](isaac_lab_skeleton.py) | Go2 사족보행 환경 + Franka 팔 + OpenVLA 통합 코드 패턴 |

## 환경 설치

### 하드웨어 요구
- **GPU**: NVIDIA RTX 30/40 시리즈 12GB+ (4096 환경 병렬 시 24GB)
- **OS**: Ubuntu 22.04 LTS
- **디스크**: ~100GB (Isaac Sim + 자산)

### 설치 단계

```bash
# 1) Isaac Sim 4.x 설치
# https://docs.omniverse.nvidia.com/isaacsim/latest/installation/install_workstation.html
# Omniverse Launcher 로 GUI 설치 (가장 간편)

# 2) Isaac Lab 클론
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab
./isaaclab.sh --install rsl_rl   # 학습 라이브러리 설치

# 3) 환경 검증
./isaaclab.sh -p source/standalone/tutorials/03_envs/run_cartpole_rl_env.py
```

### 실행 (Go2 보행)

```bash
cd IsaacLab
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Unitree-Go2-v0 \
    --num_envs 4096 \
    --headless
# 학습 1000 iter ≈ 1~2 시간 (RTX 4090)
```

## 학습 포인트

1. **물리 시뮬레이션의 진가** (27.2 절) — Isaac Sim 은 PhysX 기반으로 *접촉·마찰·관성* 정확히 시뮬레이션. CARLA 가 *주행* 이라면, Isaac 은 *로봇*.
2. **4096 환경 병렬 학습** (27.3 절) — Tesla 와 같은 *수억 step* 학습이 RTX 1대로 가능. *On-policy RL (PPO)* 이 합리적 시간 안에 수렴.
3. **Franka + OpenVLA 통합** (27.5 절) — *언어 명령* → *팔 제어*. ch22 의 System 1/2 패턴이 실 로봇 시뮬레이션에 적용.

## 다음

- [ch22 VLA](../ch22_vla/) — System 1/2 구조 (Isaac Lab 에서 실증)
- [ch21 RL](../ch21_rl/) — Pure RL 의 어려움 (Isaac 4096 환경이 *왜* 필요한지)
- [ch30 ROS2](../ch30_ros2/) — Isaac 시뮬 → 실 로봇 이식 경로
