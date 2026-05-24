"""
ch07 — Learned IPM (BEV 변환) — 신경망이 직접 학습하는 Inverse Perspective Mapping

도서 7장 *"BEV(Bird's-Eye View) 변환과 Vector Space"* 의 핵심.
고전 IPM 은 *지면이 평평하다* 는 가정 위에서 homography 행렬로 픽셀을 매핑한다.
하지만 도로는 평평하지 않고 (오르막·내리막·범프), 차도 흔들린다.

Learned IPM 은 *고정 homography* 대신 *neural attention* 으로 BEV 그리드 각
셀이 *어디 픽셀에 attention 할지* 직접 학습한다. BEVFormer 의 핵심 메커니즘
(공간 attention) 의 축소판.

본 데모는 단일 front 카메라 → BEV 그리드 (X×Y) 변환만.
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F


class LearnedIPM(nn.Module):
    """Front camera 특징 (B, C, H, W) → BEV 특징 (B, C, Y, X)."""

    def __init__(
        self,
        in_ch: int = 64,
        bev_xy: tuple[int, int] = (32, 32),   # X (forward), Y (lateral)
        hidden: int = 64,
    ):
        super().__init__()
        self.X, self.Y = bev_xy
        self.hidden = hidden

        # BEV 그리드 각 셀에 학습 가능한 query embedding
        self.bev_query = nn.Parameter(torch.randn(self.X * self.Y, hidden) * 0.02)

        # 이미지 특징 → key / value 투영
        self.to_kv = nn.Conv2d(in_ch, hidden * 2, 1)

        # 출력 투영
        self.out_proj = nn.Linear(hidden, hidden)

    def forward(self, img_feat: torch.Tensor) -> torch.Tensor:
        B, _, H, W = img_feat.shape
        N_bev = self.X * self.Y

        # KV — 이미지 픽셀별
        kv = self.to_kv(img_feat)                          # (B, 2H, H, W)
        k, v = kv.chunk(2, dim=1)                          # (B, H, H, W) 각각
        k = k.flatten(2).transpose(1, 2)                   # (B, HW, H)
        v = v.flatten(2).transpose(1, 2)                   # (B, HW, H)

        # Q — BEV 그리드 query
        q = self.bev_query.unsqueeze(0).expand(B, -1, -1)  # (B, N_bev, H)

        # Cross-attention: BEV 그리드 셀이 이미지 픽셀들을 살펴봄
        attn = torch.softmax(q @ k.transpose(-1, -2) / (self.hidden ** 0.5), dim=-1)
        bev = attn @ v                                     # (B, N_bev, H)
        bev = self.out_proj(bev)

        # (B, hidden, Y, X) 형태로 정렬
        return bev.transpose(1, 2).reshape(B, self.hidden, self.Y, self.X)


def classical_ipm_homography_demo() -> None:
    """고전 IPM 의 한계 — 고정 homography 매트릭스의 가정.

    실제 카메라 자세·지면 굴곡이 변하면 매트릭스가 더 이상 맞지 않음.
    """
    # 도서 7.2 절의 단순화된 예: 가상 카메라 4 점 → 지면 4 점 매핑
    src_pts = torch.tensor([
        [100., 200.], [540., 200.],
        [50.,  400.], [590., 400.],
    ])
    dst_pts = torch.tensor([
        [200., 0.],   [440., 0.],
        [200., 480.], [440., 480.],
    ])
    print("== 고전 IPM (참고용 좌표 예시) ==")
    print("  src(이미지) → dst(BEV) 4점:")
    for s, d in zip(src_pts, dst_pts):
        print(f"    {s.tolist()}  →  {d.tolist()}")
    print("  실제 사용 시 cv2.getPerspectiveTransform 으로 H 행렬 계산.")
    print("  한계: 지면 평탄 가정. 오르막 도로/카메라 흔들림에서 정확도 급락.")


def demo() -> None:
    torch.manual_seed(0)
    classical_ipm_homography_demo()

    print("\n== Learned IPM (신경망 attention) ==")
    model = LearnedIPM().eval()
    img_feat = torch.randn(1, 64, 28, 28)
    with torch.no_grad():
        bev = model(img_feat)
    print(f"  입력 카메라 특징 : {list(img_feat.shape)}")
    print(f"  BEV 출력         : {list(bev.shape)}  (Y×X = 32×32)")

    n_params = sum(p.numel() for p in model.parameters()) / 1e3
    print(f"  파라미터         : {n_params:.1f} K")
    print(f"\n  특징: BEV 그리드 각 셀이 어느 픽셀에 attention 할지 학습 →")
    print(f"  지면 굴곡·카메라 흔들림에 자동 적응.")


if __name__ == "__main__":
    demo()
