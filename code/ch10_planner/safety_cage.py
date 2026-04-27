"""
ch10 — Safety Cage 의 가장 단순한 형태

도서 10.7 절 *"신뢰는 하되 감시한다"* 의 사상을 룰 기반으로 구현.
Neural Planner 가 내놓은 (steer, accel) 명령을 받아, 안전 기준을 어기는
경우 무시하거나 완화한다. 실제 차량 ECU 의 safety filter 와 같은 위치.

규칙 (도서 본문 표 10.3):
  R1) 전방 TTC < 1.0s  → accel = min(accel, -2.0)  # 강제 감속
  R2) lane_offset > 1.5m → 조향을 차선 중앙 방향으로 -0.3 rad 추가
  R3) 조향 변화량 > 0.6 rad/step  → 0.6 으로 클리핑 (jerk 억제)
  R4) accel < -5.0 또는 > 4.0    → 차량 한계 클리핑
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class CageState:
    """이전 스텝의 명령 — jerk 억제용."""
    last_steer: float = 0.0


def safety_cage(
    state: np.ndarray,        # shape (6,) — TinyNeuralPlanner 의 입력과 동일
    cmd: np.ndarray,          # shape (2,) — (steer, accel)
    cage: CageState,
) -> tuple[np.ndarray, list[str]]:
    """필터링된 명령과 발동된 규칙 목록을 반환."""
    steer, accel = cmd.astype(np.float32)
    triggered: list[str] = []

    front_ttc = state[3]
    lane_offset = state[1]

    # R1) 전방 임박 충돌 — 강제 감속
    if front_ttc < 1.0 and accel > -2.0:
        accel = -2.0
        triggered.append("R1_front_ttc_brake")

    # R2) 차선 이탈 — 중앙으로 보정
    if abs(lane_offset) > 1.5:
        bias = -0.3 if lane_offset > 0 else 0.3
        steer = steer + bias
        triggered.append(f"R2_lane_recover({bias:+.2f})")

    # R3) 조향 jerk 억제
    delta = steer - cage.last_steer
    if abs(delta) > 0.6:
        steer = cage.last_steer + np.sign(delta) * 0.6
        triggered.append("R3_steer_jerk_clip")

    # R4) 가속도 한계
    if accel > 4.0:
        accel = 4.0
        triggered.append("R4_accel_max")
    elif accel < -5.0:
        accel = -5.0
        triggered.append("R4_decel_max")

    cage.last_steer = float(steer)
    return np.array([steer, accel], dtype=np.float32), triggered


def demo() -> None:
    cage = CageState()

    # 시나리오 — 전방 0.8초 TTC, 좌측 차선 침범 1.8m, 신경망이 가속을 명령
    state = np.array([15.0, 1.8, 0.1, 0.8, 4.5, 4.5], dtype=np.float32)
    cmd_nn = np.array([0.05, +1.5], dtype=np.float32)  # 약한 우조향 + 가속

    print("== Safety Cage 데모 ==")
    print(f"  입력 상태  : ttc={state[3]:.1f}s, lane_off={state[1]:+.1f}m")
    print(f"  NN 명령    : steer={cmd_nn[0]:+.3f}, accel={cmd_nn[1]:+.2f}")

    cmd_safe, fired = safety_cage(state, cmd_nn, cage)
    print(f"  필터 후    : steer={cmd_safe[0]:+.3f}, accel={cmd_safe[1]:+.2f}")
    print(f"  발동 규칙  : {fired if fired else '없음'}")


if __name__ == "__main__":
    demo()
