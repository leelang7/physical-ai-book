"""
ch09 — TinyPred — 다중 모달 궤적 예측의 가장 단순한 형태

도서 9장 *"다중 에이전트 궤적 예측 (Prediction)"* 의 핵심 사상인
*"한 에이전트의 미래는 하나의 궤적이 아니라 여러 가능성의 분포"* 를
3개 모드 + 점수 헤드로 흉내낸다. MultiPath++ 의 정신적 축소판.

입력  : 과거 1초 (10 스텝, 100ms) 의 (x, y, vx, vy) 시퀀스
출력  : 미래 3초 (30 스텝) 의 K=3 후보 궤적 + K개 모드 점수

학습 손실 (도서 9.4 절 winner-takes-all):
  - 정답 미래 궤적과 가장 가까운 후보 k* 만 골라 그 후보의 L2 손실
  - 그 k* 가 가장 높은 점수가 되도록 cross-entropy
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F


class TinyPred(nn.Module):
    """과거 (T_in, 4) → 미래 K 개 (T_out, 2) + 모드 점수 (K,)."""

    def __init__(
        self,
        t_in: int = 10,
        t_out: int = 30,
        k: int = 3,
        hidden: int = 128,
    ):
        super().__init__()
        self.t_in, self.t_out, self.k = t_in, t_out, k
        self.encoder = nn.Sequential(
            nn.Flatten(),
            nn.Linear(t_in * 4, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
        )
        self.traj_head  = nn.Linear(hidden, k * t_out * 2)
        self.score_head = nn.Linear(hidden, k)

    def forward(self, past: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # past: (B, T_in, 4)
        h = self.encoder(past)
        traj  = self.traj_head(h).view(-1, self.k, self.t_out, 2)
        score = self.score_head(h)
        return traj, score


def winner_takes_all_loss(
    pred_traj: torch.Tensor,    # (B, K, T_out, 2)
    pred_score: torch.Tensor,   # (B, K)
    gt_future: torch.Tensor,    # (B, T_out, 2)
) -> torch.Tensor:
    """도서 9.4 절의 단순화된 학습 손실.

    정답 궤적에 가장 가까운 후보만 회귀 학습 + 그 후보 점수 최대화.
    이 패턴이 *"왼쪽 회피와 오른쪽 회피의 평균이 직진"* 함정을 막는다.
    """
    # 후보별 평균 L2 거리 (B, K)
    diff = pred_traj - gt_future.unsqueeze(1)        # (B, K, T_out, 2)
    dist = diff.pow(2).sum(-1).sqrt().mean(-1)        # (B, K)

    # 가장 가까운 후보 k*
    best_k = dist.argmin(dim=-1)                      # (B,)

    # 회귀 손실 — 가장 가까운 후보만
    reg_loss = dist.gather(1, best_k.unsqueeze(1)).mean()

    # 분류 손실 — 가장 가까운 후보의 점수 ↑
    cls_loss = F.cross_entropy(pred_score, best_k)

    return reg_loss + cls_loss


def make_synthetic_episode(batch: int = 8, t_in: int = 10, t_out: int = 30):
    """원 궤적 시뮬레이션 — 직진/좌회전/우회전 중 무작위.

    각 샘플의 정답 미래는 세 모드 중 하나로 분기되므로, 단일 출력 NN 은
    *"평균"* 으로 수렴해 처참한 손실을 보인다. Mixture 가 진가를 발한다.
    """
    past, future = [], []
    for _ in range(batch):
        mode = torch.randint(0, 3, ()).item()  # 0: 직진, 1: 좌, 2: 우
        # 과거 — 일정 속도로 직진 (모든 모드 공통)
        t_past = torch.linspace(-1.0, 0.0, t_in).unsqueeze(-1)
        x_past = torch.zeros_like(t_past)
        y_past = t_past * 5.0
        vx = torch.zeros_like(t_past)
        vy = torch.full_like(t_past, 5.0)
        p = torch.cat([x_past, y_past, vx, vy], dim=-1)
        past.append(p)

        # 미래 — 모드별 분기
        t_fut = torch.linspace(0.0, 3.0, t_out)
        if mode == 0:        # 직진
            xf = torch.zeros_like(t_fut)
            yf = t_fut * 5.0
        elif mode == 1:      # 좌회전 (-x 방향으로 곡선)
            xf = -2.0 * (1 - torch.cos(t_fut * 0.7))
            yf = t_fut * 5.0
        else:                # 우회전
            xf = +2.0 * (1 - torch.cos(t_fut * 0.7))
            yf = t_fut * 5.0
        f = torch.stack([xf, yf], dim=-1)
        future.append(f)

    return torch.stack(past), torch.stack(future)


def demo() -> None:
    torch.manual_seed(0)
    model = TinyPred()
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)

    print("== TinyPred — 200 step 미니 학습 (직진/좌회전/우회전 무작위) ==")
    for step in range(200):
        past, future = make_synthetic_episode(batch=64)
        traj, score = model(past)
        loss = winner_takes_all_loss(traj, score, future)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 40 == 0:
            print(f"  step {step:3d}  loss={loss.item():.3f}")

    # 검증 — 같은 입력에 대해 K개 후보가 어디로 갈라지는지
    past, _ = make_synthetic_episode(batch=1)
    with torch.no_grad():
        traj, score = model(past)
    weights = torch.softmax(score, dim=-1)[0]
    end_xy = traj[0, :, -1, :]   # 각 모드의 3초 후 (x, y)

    print("\n== 검증 — 한 입력에 대한 3 모드의 3초 후 도착점 ==")
    for k in range(3):
        print(f"  mode {k} (w={weights[k]:.2f}) : 끝점 (x, y) = ({end_xy[k, 0]:+.2f}, {end_xy[k, 1]:+.2f})")

    print("\n  ※ 세 모드의 끝점 x 좌표가 서로 다르면 다중 모달 학습 성공.")
    print("    한 모드만 점수가 1.00 으로 쏠리면 mode collapse — README 참고.")


if __name__ == "__main__":
    demo()
