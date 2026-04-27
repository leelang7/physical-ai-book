"""
ch10 — Neural Planner + Safety Cage 합본 롤아웃

100 스텝(약 5초, 50ms/step) 의 가짜 시나리오에서 두 모듈이 어떻게
협력해 안전한 궤적을 만들어 내는지 보여 준다.

실행:
    python rollout_demo.py
"""
from __future__ import annotations
import numpy as np
import torch
from mini_planner import TinyNeuralPlanner
from safety_cage import safety_cage, CageState


def synthetic_scenario(t: float) -> np.ndarray:
    """t 초 시점의 가짜 관측 — 점차 가까워지는 전방 차량."""
    speed = 15.0 - 1.5 * t                       # 자연스러운 감속
    lane_off = 0.3 * np.sin(0.3 * t)             # 차선 내 미세 진동
    head_err = 0.02 * np.cos(0.3 * t)
    front_ttc = max(0.4, 2.5 - 0.6 * t)          # 전방 차 점점 가까워짐 (3초 부근에서 위험)
    left_ttc = 4.5
    right_ttc = 4.5
    return np.array([speed, lane_off, head_err, front_ttc, left_ttc, right_ttc],
                    dtype=np.float32)


def main() -> None:
    torch.manual_seed(42)
    model = TinyNeuralPlanner()
    model.eval()
    cage = CageState()

    n_steps = 100
    dt = 0.05

    fired_log: list[str] = []
    nn_history = []
    safe_history = []

    with torch.no_grad():
        for i in range(n_steps):
            t = i * dt
            state = synthetic_scenario(t)

            cmd_nn = model(torch.tensor(state).unsqueeze(0)).squeeze(0).numpy()
            cmd_safe, fired = safety_cage(state, cmd_nn, cage)

            nn_history.append(cmd_nn)
            safe_history.append(cmd_safe)
            for r in fired:
                fired_log.append(f"t={t:5.2f}s  {r}")

    nn_arr = np.array(nn_history)
    safe_arr = np.array(safe_history)

    print(f"== 100-step 롤아웃 (5.0s) ==")
    print(f"  NN 평균   : steer={nn_arr[:,0].mean():+.3f}, accel={nn_arr[:,1].mean():+.2f}")
    print(f"  Safe 평균 : steer={safe_arr[:,0].mean():+.3f}, accel={safe_arr[:,1].mean():+.2f}")
    print(f"  안전 개입 : {len(fired_log)} 회")
    print()
    if fired_log:
        print("  최초 5회 개입 로그:")
        for line in fired_log[:5]:
            print(f"   {line}")


if __name__ == "__main__":
    main()
