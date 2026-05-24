"""
ch06 — Mini Occupancy Network (Lift-Splat-Shoot 축소판)

도서 6장 *"Occupancy Network — 3D 점유 공간을 박스 없이"* 의 핵심 사상을
가장 단순한 PyTorch 모듈로 구현. 객체 박스 대신 *각 voxel 이 점유돼 있는가* 라는
픽셀 수준 표현을 학습한다.

  Lift   : 2D 이미지 특징 → D 깊이 분포
  Splat  : 깊이별 가중치로 3D voxel 그리드에 흩뿌림
  Shoot  : voxel 별 점유 확률 출력

실제 LSS / Tesla Occupancy Network 의 핵심 흐름을 그대로 따르되,
입력은 단일 카메라 가짜 특징으로 단순화.
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F


class LiftSplatShoot(nn.Module):
    """단일 카메라 특징 (B, C, H, W) → 3D voxel 점유 확률 (B, X, Y, Z).

    실제 시스템은 8 카메라 + 카메라 외부 파라미터(extrinsic) 가 필요한데
    본 데모는 한 카메라만, 외부 파라미터 없이 정렬된 voxel 그리드 가정.
    """

    def __init__(
        self,
        in_ch: int = 64,
        depth_bins: int = 16,
        voxel_shape: tuple[int, int, int] = (32, 32, 8),  # X, Y, Z
        feat_ch: int = 32,
    ):
        super().__init__()
        self.D = depth_bins
        self.X, self.Y, self.Z = voxel_shape
        self.feat_ch = feat_ch

        # Lift: 입력 특징 → (depth_distribution, lifted_features) 두 분기
        self.lift = nn.Conv2d(in_ch, depth_bins + feat_ch, 1)

        # Shoot: voxel 별 점유 확률
        self.shoot = nn.Sequential(
            nn.Conv3d(feat_ch, 16, 3, padding=1), nn.ReLU(),
            nn.Conv3d(16, 1, 1),
        )

    def forward(self, img_feat: torch.Tensor) -> torch.Tensor:
        """img_feat: (B, in_ch, H, W) → occupancy: (B, X, Y, Z)."""
        B, _, H, W = img_feat.shape

        # 1. Lift — 깊이 분포 + 특징 채널
        x = self.lift(img_feat)                          # (B, D+F, H, W)
        depth_logits = x[:, :self.D]                     # (B, D, H, W)
        feats        = x[:, self.D:]                     # (B, F, H, W)
        depth_dist   = F.softmax(depth_logits, dim=1)    # 픽셀별 깊이 확률

        # 2. Splat — 각 깊이 빈에서 특징×확률 곱한 후 voxel 그리드로 풀
        # outer product: (B, D, F, H, W)
        lifted = depth_dist.unsqueeze(2) * feats.unsqueeze(1)
        # 단순화: depth 축을 Z 로, 이미지 H/W 를 X/Y 로 직접 매핑
        # 실제 LSS 는 카메라 frustum→ego frame 변환 필요. 데모는 생략.
        lifted = lifted.permute(0, 2, 3, 4, 1)           # (B, F, H, W, D)

        # Voxel 그리드 크기로 보간
        voxel = F.interpolate(
            lifted.reshape(B, self.feat_ch, H, W * self.D),
            size=(self.Y, self.X * self.Z),
            mode="bilinear",
            align_corners=False,
        ).reshape(B, self.feat_ch, self.Y, self.X, self.Z)
        voxel = voxel.permute(0, 1, 3, 2, 4)             # (B, F, X, Y, Z)

        # 3. Shoot — voxel 점유 확률
        occ_logits = self.shoot(voxel).squeeze(1)        # (B, X, Y, Z)
        return torch.sigmoid(occ_logits)


def demo() -> None:
    torch.manual_seed(0)
    model = LiftSplatShoot()
    model.eval()

    # 가짜 카메라 특징 — (배치 1, 64채널, 28×28 해상도)
    img_feat = torch.randn(1, 64, 28, 28)

    with torch.no_grad():
        occ = model(img_feat)

    print("== Mini Occupancy Network ==")
    print(f"  입력 특징    : {list(img_feat.shape)}")
    print(f"  Voxel 점유   : {list(occ.shape)}  (X×Y×Z = 32×32×8)")
    print(f"  점유 확률 범위: {occ.min().item():.3f} ~ {occ.max().item():.3f}")
    print(f"  평균 점유율   : {occ.mean().item():.3f}")

    n_params = sum(p.numel() for p in model.parameters()) / 1e3
    print(f"\n  파라미터     : {n_params:.1f} K")
    print(f"  특징         : 박스 없이 3D 공간을 직접 표현 → 비정형 장애물·돌출물 인식 가능")


if __name__ == "__main__":
    demo()
