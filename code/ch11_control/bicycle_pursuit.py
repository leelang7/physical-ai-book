"""
ch11 — Bicycle Model + Pure Pursuit + Residual Neural Net

도서 11장 *"Control Net — 스티어링·가속·제동의 뉴럴 출력"* 의 골격.
고전 제어 (Bicycle 운동 모델 + Pure Pursuit 경로 추종) 위에 신경망이
*잔차* 만 추가 학습하는 *Residual Control* 패턴을 보여준다.

  고전 제어    : 100% 결정적 — 90% 상황에서 충분
  Residual NN  : 나머지 10% (마찰계수 변화·바람·차량 노후) 만 보정

이 *고전 + 잔차* 패턴이 실차 적용에 가장 안전하다 (도서 11.5 절).
"""
from __future__ import annotations
import math
import numpy as np
import torch
import torch.nn as nn


# ---------- 1) Bicycle 운동 모델 ----------
class BicycleModel:
    """자전거 모델 — 자동차 운동학의 표준 단순화.

    상태 : (x, y, yaw, v)
    입력 : (steer rad, accel m/s²)
    파라미터 : 휠베이스 L (앞축~뒷축 거리)
    """
    def __init__(self, L: float = 2.8):
        self.L = L
        self.x = self.y = self.yaw = 0.0
        self.v = 5.0  # m/s

    def step(self, steer: float, accel: float, dt: float = 0.1) -> None:
        self.x   += self.v * math.cos(self.yaw) * dt
        self.y   += self.v * math.sin(self.yaw) * dt
        self.yaw += self.v / self.L * math.tan(steer) * dt
        self.v   = max(0.0, self.v + accel * dt)

    def state(self) -> tuple[float, float, float, float]:
        return self.x, self.y, self.yaw, self.v


# ---------- 2) Pure Pursuit — 기하학적 경로 추종 ----------
def pure_pursuit(state, path: np.ndarray, L: float = 2.8, lookahead: float = 5.0) -> float:
    """현재 상태에서 lookahead 만큼 앞의 경로 점을 향한 조향각.

    path : (N, 2) — 추종할 경로의 (x, y) 점들
    return : steer (rad)
    """
    x, y, yaw, _ = state
    # 가장 가까운 경로 점에서 lookahead 거리만큼 앞의 점 선택
    dists = np.linalg.norm(path - np.array([x, y]), axis=1)
    nearest = int(dists.argmin())
    target_idx = min(nearest + max(1, int(lookahead)), len(path) - 1)
    tx, ty = path[target_idx]

    # 차량 좌표계 기준 lookahead 점의 좌측 거리
    dx = tx - x
    dy = ty - y
    local_x = math.cos(-yaw) * dx - math.sin(-yaw) * dy
    local_y = math.sin(-yaw) * dx + math.cos(-yaw) * dy

    Ld = math.hypot(dx, dy)
    if Ld < 1e-3 or local_x < 1e-3:
        return 0.0
    # Pure Pursuit 공식
    steer = math.atan2(2 * L * local_y, Ld * Ld)
    return float(np.clip(steer, -0.6, 0.6))


# ---------- 3) Residual NN — 고전 제어 위에 잔차만 학습 ----------
class ResidualController(nn.Module):
    """입력 : 상태 6차원 + 고전 제어 출력 2차원 = 8 → 잔차 2차원."""
    def __init__(self, hidden: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(8, hidden), nn.ReLU(),
            nn.Linear(hidden, 2), nn.Tanh(),
        )
        # 잔차는 작게 — 고전 제어를 크게 흔들지 않도록 스케일 제한
        self.register_buffer("scale", torch.tensor([0.05, 0.5]))  # ±0.05rad, ±0.5m/s²

    def forward(self, state6, classical2):
        x = torch.cat([state6, classical2], dim=-1)
        return self.net(x) * self.scale


# ---------- 4) 통합 데모 ----------
def make_sine_path(length: float = 80.0, amplitude: float = 4.0, dx: float = 0.5) -> np.ndarray:
    """가짜 사인파 경로 — 차량이 추종할 곡선."""
    xs = np.arange(0, length, dx)
    ys = amplitude * np.sin(2 * math.pi * xs / 40.0)
    return np.stack([xs, ys], axis=-1)


def main() -> None:
    torch.manual_seed(0)
    path = make_sine_path()
    car = BicycleModel()
    res_nn = ResidualController().eval()

    n_steps = 200
    dt = 0.1
    log_classical = []
    log_residual = []

    with torch.no_grad():
        for _ in range(n_steps):
            state = car.state()
            # 고전 제어
            steer_c = pure_pursuit(state, path, L=car.L)
            accel_c = 0.0  # 정속

            # Residual NN — 가짜 학습 안 한 모델이지만 구조만 확인
            s6 = torch.tensor([
                state[0], state[1], state[2], state[3],
                path[0, 0], path[0, 1],
            ], dtype=torch.float32)
            c2 = torch.tensor([steer_c, accel_c], dtype=torch.float32)
            delta = res_nn(s6.unsqueeze(0), c2.unsqueeze(0)).squeeze(0).numpy()
            steer_total = float(np.clip(steer_c + delta[0], -0.6, 0.6))
            accel_total = float(np.clip(accel_c + delta[1], -3.0, 3.0))

            log_classical.append((steer_c, accel_c))
            log_residual.append((steer_total, accel_total))
            car.step(steer_total, accel_total, dt)

    log_c = np.array(log_classical)
    log_r = np.array(log_residual)
    print("== Bicycle Model + Pure Pursuit + Residual NN ==")
    print(f"  200 step (20s) 시뮬레이션 완료")
    print(f"  최종 위치   : x={car.x:5.1f}m  y={car.y:5.1f}m  yaw={math.degrees(car.yaw):+.1f}°  v={car.v:.1f}m/s")
    print(f"  고전 조향 평균: {log_c[:, 0].mean():+.4f} rad")
    print(f"  잔차 조향 평균: {(log_r[:, 0] - log_c[:, 0]).mean():+.4f} rad")
    print(f"  잔차 가속 평균: {(log_r[:, 1] - log_c[:, 1]).mean():+.4f} m/s²")
    print(f"\n  Residual NN 가 학습 안 됐으므로 잔차는 거의 0 — 구조만 확인용.")
    print(f"  실제 학습 시 잔차가 *고전이 못 잡는 비정상 상황* 만 보정하도록 훈련.")


if __name__ == "__main__":
    main()
