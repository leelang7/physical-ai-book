"""
ch10 — Neural Planner 의 가장 단순한 형태

도서 10장 *"Neural Planner — 비용 함수를 신경망에 녹이기"* 의 핵심 사상을
가장 작은 형태로 보여 준다. 입력은 차량 상태와 도로/장애물 요약,
출력은 (조향각, 가속도) 두 값. 학습은 별도 스크립트로 분리하고
이 파일은 모델 아키텍처 + 임의 초기화 추론 데모만 담당한다.

도서 10.5 절 "Mixture of Trajectories" 의 사상은 본 코드의
`MixtureHead` 가 K개의 후보를 한 번에 출력하는 식으로 흉내낸다.
"""
from __future__ import annotations
import torch
import torch.nn as nn


class TinyNeuralPlanner(nn.Module):
    """단일 모드 Neural Planner — (state) → (steer, throttle).

    state 차원 (도서 10.2 절 표):
      0  ego_speed      m/s
      1  lane_offset    m   (좌+ / 우-)
      2  heading_error  rad
      3  front_ttc      s   (충돌까지의 시간, 무한대는 5.0 으로 클리핑)
      4  left_ttc       s
      5  right_ttc      s
    """

    def __init__(self, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 2),
            nn.Tanh(),  # 출력 [-1, 1] — 학습 시 단위 변환은 control 단에서
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:  # (B, 6) -> (B, 2)
        out = self.net(state)
        # 채널별 스케일: 조향 ±0.5 rad, 가속도 ±3 m/s^2
        scale = torch.tensor([0.5, 3.0], device=out.device)
        return out * scale


class MixtureHead(nn.Module):
    """다중 모달 출력 — K 개 궤적 후보 + 점수.

    도서 10.5 절 *"왼쪽으로 피해? 오른쪽으로 피해?"* 의 두 모드 같은
    상황에서 단일 평균 출력의 함정을 피하기 위한 표준 패턴.
    """

    def __init__(self, k: int = 3, hidden: int = 64):
        super().__init__()
        self.k = k
        self.shared = nn.Sequential(nn.Linear(6, hidden), nn.ReLU())
        self.traj = nn.Linear(hidden, k * 2)   # K modes × (steer, throttle)
        self.score = nn.Linear(hidden, k)      # K mode logits

    def forward(self, state):
        h = self.shared(state)
        traj = self.traj(h).view(state.shape[0], self.k, 2)
        score = self.score(h)  # logits — 학습 시 cross-entropy
        return traj, score


def demo() -> None:
    torch.manual_seed(0)
    model = TinyNeuralPlanner()
    mix = MixtureHead(k=3)

    # 가짜 상태 — 좌측 차선 침범 + 전방 차 1.5초 내 충돌 예상
    state = torch.tensor([[15.0, 0.7, 0.05, 1.5, 4.5, 4.5]])

    steer_throttle = model(state)
    traj, score = mix(state)

    print("== Tiny Neural Planner ==")
    print(f"  입력 상태   : speed=15m/s, lane_off=+0.7m, head_err=0.05rad, ttc=1.5s")
    print(f"  단일 출력   : steer={steer_throttle[0,0]:+.3f} rad, accel={steer_throttle[0,1]:+.2f} m/s²")
    print()
    print("== Mixture Head (3 modes) ==")
    weights = torch.softmax(score, dim=-1)[0]
    for k in range(3):
        s, a = traj[0, k]
        print(f"  mode {k} (w={weights[k]:.2f}) : steer={s:+.3f} rad, accel={a:+.2f} m/s²")


if __name__ == "__main__":
    demo()
