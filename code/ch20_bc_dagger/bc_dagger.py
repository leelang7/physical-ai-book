"""
ch20 — Behavior Cloning + DAgger 가장 단순한 형태

도서 20장 *"모방 학습과 DAgger — Physical AI 의 첫 길"* 의 핵심 사상을
1D 차량 환경으로 시연한다. 같은 문제를 두 방식으로 풀어 *오차 누적* 의
차이를 숫자로 확인.

  BC      : 전문가 trajectory 만으로 학습 → 분포 이동(distribution shift)
            로 인한 오차 누적
  DAgger  : 학생이 굴린 trajectory 에 전문가 라벨 추가 → 학생의 상태 분포
            를 학습 데이터에 포함시켜 오차 누적 억제

환경:
  1D 차량을 목표 위치로 보내기
  상태 (3): 현재 위치, 속도, 목표까지 거리
  행동 (1): 가속도 (±3 m/s²)
  전문가  : PD 컨트롤러 (도서 20.3 절의 "이상적 전문가" 단순화)
"""
from __future__ import annotations
import numpy as np
import torch
import torch.nn as nn


# ---------- 환경 ----------
class CarEnv:
    """1D 차량. step(a) 는 가속도 받아 dt=0.1s 시뮬레이션."""

    def __init__(self, goal: float = 10.0):
        self.goal = goal
        self.reset()

    def reset(self) -> np.ndarray:
        self.x = 0.0
        self.v = 0.0
        return self._state()

    def _state(self) -> np.ndarray:
        return np.array([self.x, self.v, self.goal - self.x], dtype=np.float32)

    def step(self, a: float, dt: float = 0.1) -> tuple[np.ndarray, bool]:
        a = float(np.clip(a, -3.0, 3.0))
        self.v += a * dt
        self.x += self.v * dt
        done = abs(self.x - self.goal) < 0.1 and abs(self.v) < 0.1
        return self._state(), done


# ---------- 전문가 정책 (결정적 PD) ----------
def expert_policy(state: np.ndarray) -> float:
    """단순 PD 컨트롤러 — 도서 20.3 절의 *이상적 전문가* 단순화."""
    _, vel, gap = state
    return float(np.clip(2.0 * gap - 1.5 * vel, -3.0, 3.0))


# ---------- 학생 신경망 ----------
class PolicyNet(nn.Module):
    def __init__(self, hidden: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1), nn.Tanh(),
        )

    def forward(self, s: torch.Tensor) -> torch.Tensor:
        return self.net(s).squeeze(-1) * 3.0  # 행동 범위 ±3


# ---------- 데이터 수집 ----------
def collect_expert_episodes(n_eps: int = 20, max_steps: int = 100,
                            rng: np.random.Generator | None = None) -> list[tuple[np.ndarray, float]]:
    rng = rng or np.random.default_rng(0)
    data = []
    for _ in range(n_eps):
        env = CarEnv(goal=float(rng.uniform(5.0, 15.0)))
        s = env.reset()
        for _ in range(max_steps):
            a = expert_policy(s)
            data.append((s.copy(), a))
            s, done = env.step(a)
            if done:
                break
    return data


# ---------- 학습 ----------
def train(model: PolicyNet, data: list[tuple[np.ndarray, float]],
          n_epochs: int = 100, lr: float = 3e-3) -> float:
    S = torch.tensor(np.stack([d[0] for d in data]), dtype=torch.float32)
    A = torch.tensor([d[1] for d in data], dtype=torch.float32)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for _ in range(n_epochs):
        pred = model(S)
        loss = ((pred - A) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return float(loss.item())


# ---------- 평가 ----------
def evaluate(model: PolicyNet, n_eps: int = 10, max_steps: int = 150) -> tuple[float, float]:
    """평균 최종 오차(m) + 성공률(%) 반환."""
    rng = np.random.default_rng(123)
    errors, successes = [], 0
    model.eval()
    with torch.no_grad():
        for _ in range(n_eps):
            env = CarEnv(goal=float(rng.uniform(5.0, 15.0)))
            s = env.reset()
            for _ in range(max_steps):
                a = model(torch.tensor(s).unsqueeze(0)).item()
                s, done = env.step(a)
                if done:
                    successes += 1
                    break
            errors.append(abs(s[0] - env.goal))
    model.train()
    return float(np.mean(errors)), 100.0 * successes / n_eps


# ---------- DAgger 루프 ----------
def dagger_loop(model: PolicyNet, n_rounds: int = 5, n_eps_per_round: int = 5,
                rng: np.random.Generator | None = None) -> tuple[PolicyNet, list[tuple[float, float]]]:
    """학생 정책으로 굴리며 전문가에게 라벨링 → 데이터 추가 → 재학습."""
    rng = rng or np.random.default_rng(42)
    dataset: list[tuple[np.ndarray, float]] = []
    history: list[tuple[float, float]] = []

    for r in range(n_rounds):
        # 1) 학생이 굴린 trajectory 의 상태들 수집
        for _ in range(n_eps_per_round):
            env = CarEnv(goal=float(rng.uniform(5.0, 15.0)))
            s = env.reset()
            for _ in range(100):
                model.eval()
                with torch.no_grad():
                    a_student = model(torch.tensor(s).unsqueeze(0)).item()
                model.train()
                # 2) 전문가에게 *학생이 도달한 상태* 의 정답을 질의
                a_expert = expert_policy(s)
                dataset.append((s.copy(), a_expert))
                # 학생 행동으로 환경 진행 — 학생의 상태 분포 그대로
                s, done = env.step(a_student)
                if done:
                    break
        # 3) 누적 데이터로 재학습
        train(model, dataset, n_epochs=30)
        err, succ = evaluate(model, n_eps=10)
        history.append((err, succ))
    return model, history


# ---------- 데모 ----------
def main() -> None:
    torch.manual_seed(0)
    rng = np.random.default_rng(0)

    # BC 의 한계를 드러내려고 일부러 데이터를 적게 (3 에피소드만)
    print("== Behavior Cloning (전문가 데이터 3 에피소드만) ==")
    expert_data = collect_expert_episodes(n_eps=3, rng=rng)
    bc_model = PolicyNet()
    bc_loss = train(bc_model, expert_data, n_epochs=200)
    bc_err, bc_succ = evaluate(bc_model)
    print(f"  학습 데이터  : {len(expert_data)} 쌍 (작은 데이터셋)")
    print(f"  최종 손실    : {bc_loss:.4f}")
    print(f"  롤아웃 오차  : {bc_err:.3f} m")
    print(f"  성공률       : {bc_succ:.0f}%")

    print("\n== DAgger (같은 BC 시작점에서 5 라운드 데이터 추가) ==")
    dagger_model = PolicyNet()
    train(dagger_model, expert_data, n_epochs=200)  # 같은 BC 초기화
    _, history = dagger_loop(dagger_model, n_rounds=5, n_eps_per_round=3)
    for i, (err, succ) in enumerate(history, 1):
        print(f"  라운드 {i}: 오차 {err:.3f} m, 성공률 {succ:.0f}%")
    final_err, final_succ = history[-1]
    print(f"\n  BC → DAgger 개선:")
    print(f"    오차    : {bc_err:.3f} → {final_err:.3f} m  ({(final_err - bc_err):+.3f})")
    print(f"    성공률  : {bc_succ:.0f}% → {final_succ:.0f}%")
    print(f"\n  의미: DAgger 는 학생이 *실제로 도달한 상태* 에서 정답을 학습 →")
    print(f"  분포 이동 (distribution shift) 해소 → 오차 누적 억제 (도서 20.5 절)")


if __name__ == "__main__":
    main()
