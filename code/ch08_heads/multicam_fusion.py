"""
ch08 — 8 카메라 → BEV 융합 → 3 헤드 통합

도서 8장 *"Lane · Sign · Object 헤드의 통합 운용"* 의 골격.
ch05 의 HydraNet (단일 카메라) 을 8 카메라로 확장하고,
각 카메라 특징을 BEV 공간에서 융합한 뒤 동일한 3개 헤드를 돌린다.

  8 카메라 → 공유 backbone → cross-camera 융합 → BEV → 3 heads
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F


class TinyBackbone(nn.Module):
    """공유 가중치 카메라 백본 — 8 카메라 동일 처리."""

    def __init__(self, in_ch: int = 3, out_ch: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, 16, 3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(32, out_ch, 3, padding=1), nn.ReLU(),
        )

    def forward(self, x):
        return self.net(x)


class CrossCameraFusion(nn.Module):
    """8 카메라 특징을 단일 BEV 그리드로 융합.

    실제 Tesla 시스템은 각 카메라의 extrinsic 행렬로 BEV 좌표 변환 후 융합.
    데모는 단순 concat + 1×1 conv 로 단축.
    """

    def __init__(self, per_cam_ch: int = 32, bev_xy: tuple[int, int] = (32, 32),
                 fused_ch: int = 64):
        super().__init__()
        self.X, self.Y = bev_xy
        self.fused_ch = fused_ch
        # 8 카메라 × per_cam_ch 채널 → BEV
        self.proj = nn.Conv2d(8 * per_cam_ch, fused_ch, 1)

    def forward(self, cam_feats: list[torch.Tensor]) -> torch.Tensor:
        # 모든 카메라 특징을 BEV 해상도로 리샘플 후 concat
        bev_feats = [
            F.interpolate(f, size=(self.Y, self.X), mode="bilinear", align_corners=False)
            for f in cam_feats
        ]
        merged = torch.cat(bev_feats, dim=1)  # (B, 8*C, Y, X)
        return F.relu(self.proj(merged))      # (B, fused_ch, Y, X)


class TripleHead(nn.Module):
    """Lane(BEV seg) · Sign(global cls) · Object(BEV bbox) 3개 헤드."""

    def __init__(self, in_ch: int = 64, n_lane: int = 4, n_sign: int = 20):
        super().__init__()
        self.lane = nn.Conv2d(in_ch, n_lane, 1)
        self.obj_cls = nn.Conv2d(in_ch, 10, 3, padding=1)
        self.obj_reg = nn.Conv2d(in_ch, 4, 3, padding=1)
        self.sign_gap = nn.AdaptiveAvgPool2d(1)
        self.sign_fc = nn.Linear(in_ch, n_sign)

    def forward(self, bev: torch.Tensor) -> dict[str, torch.Tensor]:
        return {
            "lane":    self.lane(bev),
            "obj_cls": self.obj_cls(bev),
            "obj_reg": self.obj_reg(bev),
            "sign":    self.sign_fc(self.sign_gap(bev).flatten(1)),
        }


class MultiCamHydraNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = TinyBackbone()       # 8 카메라 공유
        self.fusion = CrossCameraFusion()
        self.heads = TripleHead()

    def forward(self, cams: torch.Tensor) -> dict[str, torch.Tensor]:
        # cams: (B, 8, 3, H, W) — 8 카메라 RGB
        B, N, C, H, W = cams.shape
        # 8 카메라 → 단일 배치로 펼쳐서 공유 백본 적용
        x = cams.reshape(B * N, C, H, W)
        feat = self.backbone(x)              # (B*N, 32, H/4, W/4)
        _, FC, FH, FW = feat.shape
        feat = feat.reshape(B, N, FC, FH, FW)
        cam_feats = [feat[:, i] for i in range(N)]
        bev = self.fusion(cam_feats)         # (B, 64, Y, X)
        return self.heads(bev)


def demo() -> None:
    torch.manual_seed(0)
    model = MultiCamHydraNet().eval()

    # 8 카메라 × 3채널 × 64×64 입력 (작게 — 데모 속도)
    cams = torch.randn(1, 8, 3, 64, 64)

    with torch.no_grad():
        out = model(cams)

    print("== MultiCam HydraNet (8 카메라 + BEV 융합 + 3 헤드) ==")
    print(f"  입력  : 8 cameras, each 3×64×64")
    print(f"  BEV 융합 후 → 3 헤드 출력:")
    for name, t in out.items():
        if isinstance(t, torch.Tensor):
            print(f"    {name:8s} : {list(t.shape)}")

    n_params = sum(p.numel() for p in model.parameters()) / 1e3
    print(f"\n  파라미터 : {n_params:.1f} K")
    print(f"  의미     : 카메라마다 같은 백본 — 가중치 공유 → 8× 효율")


if __name__ == "__main__":
    demo()
