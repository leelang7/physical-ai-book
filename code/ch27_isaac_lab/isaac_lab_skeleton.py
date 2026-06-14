"""
ch27 — Isaac Lab 으로 Physical AI 에이전트 학습 (골격)

도서 27장 *"Isaac Lab 으로 Physical AI 에이전트 학습"* 의 코드 패턴.
NVIDIA Isaac Sim 4.x + Isaac Lab 별도 설치 필요. 본 파일은 *구조* 만 보여줌.

실제 워크플로 (도서 27.3 절):
  1) Isaac Sim 4.x 설치 (RTX GPU + ~100GB 디스크 + Ubuntu 22.04)
  2) Isaac Lab 클론 + 환경 빌드
  3) 본 골격 코드 적용
  4) torchrun 으로 분산 학습
"""
from __future__ import annotations


def show_env_skeleton():
    print("""
# Isaac Lab 환경 구조 (omni.isaac.lab.envs.RLTaskEnv 상속)
import torch
from omni.isaac.lab.envs import RLTaskEnv, RLTaskEnvCfg
from omni.isaac.lab.scene import InteractiveSceneCfg
from omni.isaac.lab.assets import ArticulationCfg
from omni.isaac.lab.sim import SimulationCfg

class Go2WalkingEnvCfg(RLTaskEnvCfg):
    # 시뮬레이션 — RTX 4090 1대당 4096 환경 병렬
    sim: SimulationCfg = SimulationCfg(dt=1/200, render_interval=1)
    decimation: int = 4  # 50 Hz 정책
    episode_length_s: float = 20.0
    num_envs: int = 4096

    # 장면 — Go2 사족보행 로봇
    scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096, env_spacing=2.5)

    # 관측·행동 차원
    observations: dict = {
        "policy": {
            "base_lin_vel": 3, "base_ang_vel": 3, "projected_gravity": 3,
            "velocity_commands": 3, "joint_pos": 12, "joint_vel": 12,
            "actions": 12,
        }
    }
    actions: dict = {"joint_torque": 12}

    # 보상 함수 — 책 27.4 절의 multi-component reward
    rewards: dict = {
        "track_lin_vel_xy_exp":  {"weight": 1.0},
        "track_ang_vel_z_exp":   {"weight": 0.5},
        "lin_vel_z_l2":          {"weight": -2.0},
        "joint_torques_l2":      {"weight": -1e-5},
        "joint_acc_l2":          {"weight": -2.5e-7},
        "action_rate_l2":        {"weight": -0.01},
    }
""")


def show_training_pattern():
    print("""
# 학습 명령 (Isaac Lab + RSL-RL)
# torchrun --nproc_per_node=1 \\
#     -m omni.isaac.lab_tasks \\
#     --task Isaac-Go2-Walk-v0 \\
#     --headless \\
#     --num_envs 4096 \\
#     --max_iterations 1000

# 학습 1000 iter ≈ 50M 환경 step ≈ 1~2 시간 (RTX 4090)
# 결과: 평지 보행 → 12m/s 달리기까지 자동 학습
""")


def show_franka_vla():
    print("""
# Franka 팔 + OpenVLA (책 27.5 절)
# 1) Isaac Lab 의 Franka environment
# 2) OpenVLA 7B 모델 호출
# 3) "컵을 들어 옆에 놓아라" 같은 자연어 → 7-DOF 제어

from omni.isaac.lab.assets import FrankaCfg
from transformers import AutoModelForVision2Seq, AutoProcessor

robot = FrankaCfg(...)
camera = CameraCfg(...)
vla = AutoModelForVision2Seq.from_pretrained("openvla/openvla-7b")
processor = AutoProcessor.from_pretrained("openvla/openvla-7b")

# 1 Hz 로 VLA, 30 Hz 로 IK 추적 — ch22 의 System 1/2 패턴
""")


def main():
    print("== ch27 Isaac Lab — Physical AI 에이전트 학습 (골격) ==\n")
    print("이 파일은 Isaac Lab 이 설치돼 있다고 *가정* 한 패턴입니다.")
    print("실제 import 시도는 안 함 — 설치 안 된 환경에서도 *구조 학습* 가능.\n")

    print("[1] Go2 사족보행 RL 환경 (Isaac Lab)")
    show_env_skeleton()
    print("[2] 학습 명령")
    show_training_pattern()
    print("[3] Franka 팔 + OpenVLA 통합 (책 27.5 절)")
    show_franka_vla()

    print("\n  설치 가이드: README 참조.")
    print("  하드웨어: RTX 4090 / A100 권장. 4096 환경 병렬 시 24GB VRAM 필요.")


if __name__ == "__main__":
    main()
