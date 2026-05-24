"""
ch22 — VLA (Vision-Language-Action) + System 1/2 주파수 분리

도서 22장 *"World Model 과 VLA(Vision-Language-Action)"* 의 두 핵심 사상:

  1) VLA 구조 — (Vision 인코더, Language 인코더, Action 디코더) 세 모듈
  2) System 1/2 — 빠른 반응 정책 + 느린 추론 정책의 주파수 분리

  System 2 (느림, 큰 모델)  : 1 Hz 로 *목표 임베딩* 업데이트
  System 1 (빠름, 작은 모델) : 10 Hz 로 *목표 임베딩 + 관측* 받아 행동 출력

실제 OpenVLA / RT-2 의 모델은 수십억 파라미터라 CPU 로 못 돌리니,
본 데모는 *동일 구조의 가짜 모델* + *주파수 분리 시뮬레이션* 에 집중.
"""
from __future__ import annotations
import time
import torch
import torch.nn as nn


# ---------- VLA 3-모듈 구조 (전체 데이터 흐름) ----------
class MockVisionEncoder(nn.Module):
    """실제: ViT 또는 ResNet (수억 파라미터). 데모: 작은 conv 백본."""

    def __init__(self, in_ch: int = 3, out_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, 16, 3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(32, out_dim),
        )

    def forward(self, img: torch.Tensor) -> torch.Tensor:
        return self.net(img)


class MockLanguageEncoder(nn.Module):
    """실제: T5 / Llama 같은 LLM (수십억 파라미터). 데모: embedding lookup + MLP."""

    def __init__(self, vocab_size: int = 50, max_len: int = 8, out_dim: int = 64):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, 32)
        self.proj = nn.Sequential(
            nn.Linear(32 * max_len, 128), nn.ReLU(),
            nn.Linear(128, out_dim),
        )
        self.max_len = max_len

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        # token_ids: (B, L) — 패딩 0
        B, L = token_ids.shape
        if L < self.max_len:
            pad = torch.zeros(B, self.max_len - L, dtype=token_ids.dtype, device=token_ids.device)
            token_ids = torch.cat([token_ids, pad], dim=1)
        emb = self.embed(token_ids[:, :self.max_len])  # (B, L, 32)
        return self.proj(emb.flatten(1))


class ActionDecoder(nn.Module):
    """vision + language 결합 → 행동 분포 mean."""

    def __init__(self, vis_dim: int = 64, lang_dim: int = 64, action_dim: int = 4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(vis_dim + lang_dim, 128), nn.ReLU(),
            nn.Linear(128, action_dim), nn.Tanh(),
        )

    def forward(self, vis_feat: torch.Tensor, lang_feat: torch.Tensor) -> torch.Tensor:
        return self.net(torch.cat([vis_feat, lang_feat], dim=-1))


class FullVLA(nn.Module):
    """VLA 풀 파이프라인 — 단일 호출에 vision + language + action 모두 처리.

    실제 RT-2 / OpenVLA 의 추론 구조. 한 번 호출이 무거우므로 (수억 FLOPs)
    제어 주파수 직접 적용 불가 → System 1/2 분리 패턴 필요.
    """

    def __init__(self):
        super().__init__()
        self.vision = MockVisionEncoder()
        self.language = MockLanguageEncoder()
        self.action = ActionDecoder()

    def forward(self, img: torch.Tensor, tokens: torch.Tensor) -> torch.Tensor:
        v = self.vision(img)
        l = self.language(tokens)
        return self.action(v, l)


# ---------- System 1/2 주파수 분리 패턴 ----------
class System2Slow(nn.Module):
    """1 Hz 로 호출. 무거운 vision + language → *목표 임베딩* 생성."""

    def __init__(self):
        super().__init__()
        self.vision = MockVisionEncoder()       # 무거움
        self.language = MockLanguageEncoder()   # 무거움
        self.fuse = nn.Linear(128, 32)          # 목표 임베딩 차원

    def forward(self, img: torch.Tensor, tokens: torch.Tensor) -> torch.Tensor:
        v = self.vision(img)
        l = self.language(tokens)
        return self.fuse(torch.cat([v, l], dim=-1))


class System1Fast(nn.Module):
    """10 Hz 로 호출. 작은 MLP — *목표 임베딩 + 가벼운 관측* → 행동."""

    def __init__(self, goal_dim: int = 32, obs_dim: int = 8, action_dim: int = 4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(goal_dim + obs_dim, 64), nn.ReLU(),
            nn.Linear(64, action_dim), nn.Tanh(),
        )

    def forward(self, goal: torch.Tensor, obs: torch.Tensor) -> torch.Tensor:
        return self.net(torch.cat([goal, obs], dim=-1))


# ---------- 데모: 추론 시간 측정 + 주파수 분리 이득 ----------
def benchmark_inference():
    torch.manual_seed(0)

    # 1) FullVLA 단일 호출 — System 1 시도 시 너무 느림
    full = FullVLA().eval()
    img = torch.randn(1, 3, 224, 224)
    tokens = torch.randint(1, 50, (1, 8))

    # warmup
    with torch.no_grad():
        for _ in range(3):
            full(img, tokens)

    t0 = time.perf_counter()
    n_full = 0
    with torch.no_grad():
        while time.perf_counter() - t0 < 1.0:
            full(img, tokens)
            n_full += 1
    print(f"  FullVLA  단일 모델 추론: {n_full} 회/초  (System 1 으로 쓰기엔 너무 느림 — 실제 모델은 더 느림)")

    # 2) System 1/2 분리
    sys2 = System2Slow().eval()
    sys1 = System1Fast().eval()
    obs_light = torch.randn(1, 8)

    # System 2 한 번 호출 → 목표 임베딩
    with torch.no_grad():
        goal = sys2(img, tokens)

    # System 1 만 반복 호출 (가벼운 obs 만 갱신)
    with torch.no_grad():
        for _ in range(3):
            sys1(goal, obs_light)

    t0 = time.perf_counter()
    n_fast = 0
    with torch.no_grad():
        while time.perf_counter() - t0 < 1.0:
            sys1(goal, obs_light)
            n_fast += 1
    print(f"  System 1 (작은 정책) 추론: {n_fast} 회/초")
    print(f"  속도비: System 1 이 FullVLA 보다 약 {n_fast / max(1, n_full):.1f}× 빠름")


def control_loop_simulation(t_max: float = 3.0):
    """3초 시뮬레이션. System 2 는 1 Hz, System 1 은 10 Hz 호출."""
    torch.manual_seed(0)
    sys2 = System2Slow().eval()
    sys1 = System1Fast().eval()

    img = torch.randn(1, 3, 224, 224)
    tokens = torch.randint(1, 50, (1, 8))
    obs = torch.randn(1, 8)
    goal = None

    s2_count, s1_count = 0, 0
    t = 0.0
    dt = 0.1

    with torch.no_grad():
        while t < t_max:
            # System 2: 1 Hz (매 1.0초)
            if int(t * 10) % 10 == 0:
                goal = sys2(img, tokens)
                s2_count += 1
            # System 1: 10 Hz (매 0.1초)
            _ = sys1(goal, obs)
            s1_count += 1
            t += dt

    print(f"\n  {t_max:.1f}초 시뮬레이션 결과:")
    print(f"    System 2 호출: {s2_count} 회  (1 Hz)")
    print(f"    System 1 호출: {s1_count} 회  (10 Hz)")
    print(f"    System 2 가 1 Hz 만 호출되어도 정책 안전 (목표 임베딩은 1초 단위로 충분히 신선)")


def main():
    print("== ch22 — VLA 구조 + System 1/2 주파수 분리 ==\n")

    print("[1] 추론 속도 비교")
    benchmark_inference()

    print("\n[2] 제어 루프 시뮬레이션 (System 2 = 1 Hz, System 1 = 10 Hz)")
    control_loop_simulation()

    print("\n핵심: 무거운 VLA 모델 전체를 10 Hz 로 굴리는 건 불가능 →")
    print("      System 2 (무거움) 1 Hz 로 목표만 갱신, System 1 (가벼움) 10 Hz 로 행동.")
    print("      도서 22.4 절 — Tesla / Figure / OpenVLA 모두 이 패턴.")


if __name__ == "__main__":
    main()
