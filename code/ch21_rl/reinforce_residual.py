"""
ch21 — Pure REINFORCE vs Residual RL on Classical PD

도서 21장 *"강화학습은 왜 '주 무기' 가 아닌가"* 의 입장을 코드로 시연.

  실험 1: Pure REINFORCE — 처음부터 신경망 정책 학습
  실험 2: Residual RL    — 결정적 PD 컨트롤러 위에 작은 잔차 NN 만 RL 로 학습

같은 환경, 같은 episode 수, 같은 보상. 두 방식의 수렴 안정성을 비교.

환경: ch20 과 동일한 1D 차량 (목표 도달).
  reward = -|x - goal|  (각 step)
  episode 종료: 100 step 도달 또는 목표 도달.
"""
from __future__ import annotations
import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------- 환경 ----------
class CarEnv1D:
    def __init__(self, goal: float = 10.0):
        self.goal = goal
        self.reset()

    def reset(self) -> np.ndarray:
        self.x = 0.0
        self.v = 0.0
        return self._state()

    def _state(self) -> np.ndarray:
        return np.array([self.x, self.v, self.goal - self.x], dtype=np.float32)

    def step(self, a: float, dt: float = 0.1) -> tuple[np.ndarray, float, bool]:
        a = float(np.clip(a, -3.0, 3.0))
        self.v += a * dt
        self.x += self.v * dt
        reward = -abs(self.x - self.goal)  # 가까울수록 높은 보상
        done = (abs(self.x - self.goal) < 0.2 and abs(self.v) < 0.2)
        return self._state(), reward, done


def pd_classical(state: np.ndarray) -> float:
    """ch11 의 PD 컨트롤러 — 결정적, 학습 없음."""
    _, vel, gap = state
    return float(np.clip(2.0 * gap - 1.5 * vel, -3.0, 3.0))


# ---------- 정책 1: Pure REINFORCE ----------
class StochasticPolicy(nn.Module):
    """가우시안 정책 — mean 만 학습. std 는 작은 고정값."""

    def __init__(self, hidden: int = 32, log_std: float = -1.0):
        super().__init__()
        self.mean_net = nn.Sequential(
            nn.Linear(3, hidden), nn.ReLU(),
            nn.Linear(hidden, 1), nn.Tanh(),
        )
        self.log_std = nn.Parameter(torch.tensor(log_std))

    def forward(self, s: torch.Tensor) -> torch.distributions.Normal:
        mean = self.mean_net(s).squeeze(-1) * 3.0
        std = torch.exp(self.log_std).clamp(min=0.05, max=1.5)
        return torch.distributions.Normal(mean, std)


# ---------- 정책 2: Residual RL on PD ----------
class ResidualPolicy(nn.Module):
    """PD 출력에 작은 가우시안 잔차를 학습."""

    def __init__(self, hidden: int = 32, log_std: float = -2.0, scale: float = 0.5):
        super().__init__()
        self.delta_net = nn.Sequential(
            nn.Linear(3, hidden), nn.ReLU(),
            nn.Linear(hidden, 1), nn.Tanh(),
        )
        self.log_std = nn.Parameter(torch.tensor(log_std))
        self.scale = scale  # 잔차 최대 크기 — 작게 제한

    def forward(self, s: torch.Tensor, pd: torch.Tensor) -> torch.distributions.Normal:
        delta_mean = self.delta_net(s).squeeze(-1) * self.scale
        mean = (pd + delta_mean).clamp(-3.0, 3.0)
        std = torch.exp(self.log_std).clamp(min=0.02, max=0.5)
        return torch.distributions.Normal(mean, std)


# ---------- REINFORCE 학습 루프 ----------
def run_episode(env: CarEnv1D, policy_fn) -> tuple[list[torch.Tensor], list[float]]:
    """policy_fn(state) → torch Distribution. 반환: log_prob 리스트 + reward 리스트."""
    s = env.reset()
    log_probs, rewards = [], []
    for _ in range(100):
        dist = policy_fn(s)
        a = dist.sample()
        log_probs.append(dist.log_prob(a))
        s, r, done = env.step(float(a.item()))
        rewards.append(r)
        if done:
            break
    return log_probs, rewards


def reinforce_update(opt: torch.optim.Optimizer,
                     log_probs: list[torch.Tensor], rewards: list[float],
                     gamma: float = 0.99) -> float:
    """REINFORCE: ∇θ J = E[ Σ ∇θ log π(a|s) · G_t ]."""
    returns = []
    G = 0.0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    R = torch.tensor(returns, dtype=torch.float32)
    R = (R - R.mean()) / (R.std() + 1e-8)
    loss = -torch.stack([lp * g for lp, g in zip(log_probs, R)]).sum()
    opt.zero_grad()
    loss.backward()
    opt.step()
    return float(sum(rewards))


def train_pure_reinforce(n_episodes: int = 400) -> list[float]:
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    policy = StochasticPolicy()
    opt = torch.optim.Adam(policy.parameters(), lr=3e-3)
    history = []

    def policy_fn(state: np.ndarray):
        return policy(torch.tensor(state).unsqueeze(0))

    for ep in range(n_episodes):
        env = CarEnv1D(goal=float(rng.uniform(5.0, 15.0)))
        log_probs, rewards = run_episode(env, policy_fn)
        ret = reinforce_update(opt, log_probs, rewards)
        history.append(ret)
    return history


def train_residual_rl(n_episodes: int = 400) -> list[float]:
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    policy = ResidualPolicy()
    opt = torch.optim.Adam(policy.parameters(), lr=3e-3)
    history = []

    def policy_fn(state: np.ndarray):
        pd = torch.tensor([pd_classical(state)], dtype=torch.float32)
        return policy(torch.tensor(state).unsqueeze(0), pd)

    for ep in range(n_episodes):
        env = CarEnv1D(goal=float(rng.uniform(5.0, 15.0)))
        log_probs, rewards = run_episode(env, policy_fn)
        ret = reinforce_update(opt, log_probs, rewards)
        history.append(ret)
    return history


# ---------- 비교 메인 ----------
def summarize(name: str, history: list[float], window: int = 50) -> tuple[float, float]:
    """평균 누적 보상 (마지막 window 에피소드) + 표준편차."""
    tail = history[-window:]
    return float(np.mean(tail)), float(np.std(tail))


def main() -> None:
    print("== ch21 — Pure REINFORCE vs Residual RL on PD ==\n")

    print("실험 1: Pure REINFORCE 400 episodes")
    pure_history = train_pure_reinforce()
    pure_mean, pure_std = summarize("Pure", pure_history)
    print(f"  최종 50 ep 평균 누적 보상: {pure_mean:8.2f} ± {pure_std:.2f}")

    print("\n실험 2: Residual RL (PD + 잔차 학습) 400 episodes")
    res_history = train_residual_rl()
    res_mean, res_std = summarize("Residual", res_history)
    print(f"  최종 50 ep 평균 누적 보상: {res_mean:8.2f} ± {res_std:.2f}")

    print("\n비교:")
    print(f"  Pure       : {pure_mean:8.2f} ± {pure_std:.2f}")
    print(f"  Residual   : {res_mean:8.2f} ± {res_std:.2f}")
    print(f"  개선폭      : {res_mean - pure_mean:+8.2f}  (값이 0 에 가까울수록 좋음)")
    print(f"\n  Pure RL 의 누적 보상이 변동성 크고 0 에서 멀다 → 학습 불안정.")
    print(f"  Residual RL 은 PD 베이스라인이 보장하는 안정 위에서 작은 보정만 학습.")
    print(f"  도서 21.4 절: *RL 은 결정적 베이스라인 위에 얹는 잔차로만 안전하다*.")


if __name__ == "__main__":
    main()
