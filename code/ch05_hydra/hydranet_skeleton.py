"""
ch05 — HydraNet 스켈레톤 (백본 + BiFPN 일부 + 멀티 헤드)

도서 5장 *"백본부터 헤드까지 — HydraNet의 구조"* 에서 설명한
3대 구성 (CNN/ViT 백본 · BiFPN/FPN · 다중 헤드) 을 가장 단순한
PyTorch 모듈로 구성한다. 학습용이 아니라 *구조의 흐름* 을 손에
잡히게 보여 주는 것이 목적.

  - Backbone     : ResNet18 의 마지막 4 단계 출력 (C2, C3, C4, C5)
  - Neck         : 단순 FPN top-down (BiFPN 의 정신적 축소판)
  - Heads        : 3개 — Lane (HxW segmentation) · Object (BBox) · Sign (cls)
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet18


class FPNNeck(nn.Module):
    """ResNet18 4단계 출력 → 채널 정렬 + top-down 합산."""

    def __init__(self, channels: tuple[int, ...] = (64, 128, 256, 512), out_ch: int = 128):
        super().__init__()
        self.lateral = nn.ModuleList(nn.Conv2d(c, out_ch, 1) for c in channels)
        self.smooth  = nn.ModuleList(nn.Conv2d(out_ch, out_ch, 3, padding=1) for _ in channels)

    def forward(self, feats: list[torch.Tensor]) -> list[torch.Tensor]:
        # feats: [C2, C3, C4, C5] (해상도 큰→작은 것은 reverse)
        lat = [conv(f) for conv, f in zip(self.lateral, feats)]
        # top-down 합산
        out = [lat[-1]]
        for i in range(len(lat) - 2, -1, -1):
            up = F.interpolate(out[-1], size=lat[i].shape[-2:], mode="nearest")
            out.append(lat[i] + up)
        out = list(reversed(out))
        return [smooth(o) for smooth, o in zip(self.smooth, out)]


class LaneHead(nn.Module):
    """차선 분할 — 입력 해상도와 같은 크기의 1채널 마스크."""

    def __init__(self, in_ch: int = 128, n_classes: int = 4):
        super().__init__()
        self.proj = nn.Conv2d(in_ch, n_classes, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.proj(x)  # (B, K, H, W)


class ObjectHead(nn.Module):
    """객체 검출 — 작은 anchor-free 헤드 (cls + reg)."""

    def __init__(self, in_ch: int = 128, n_cls: int = 10):
        super().__init__()
        self.cls = nn.Conv2d(in_ch, n_cls, 3, padding=1)
        self.reg = nn.Conv2d(in_ch, 4,    3, padding=1)  # (cx, cy, w, h)

    def forward(self, x):
        return self.cls(x), self.reg(x)


class SignHead(nn.Module):
    """전역 분류 — 표지판 종류 (예: 속도제한 30/50/70 등 K개)."""

    def __init__(self, in_ch: int = 128, n_cls: int = 20):
        super().__init__()
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fc  = nn.Linear(in_ch, n_cls)

    def forward(self, x):
        return self.fc(self.gap(x).flatten(1))


class HydraNetMini(nn.Module):
    def __init__(self):
        super().__init__()
        # ResNet18 백본 (사전학습 가중치 미로드 — 데모 속도 우선)
        rn = resnet18(weights=None)
        self.stem  = nn.Sequential(rn.conv1, rn.bn1, rn.relu, rn.maxpool)
        self.layer1, self.layer2, self.layer3, self.layer4 = rn.layer1, rn.layer2, rn.layer3, rn.layer4
        self.neck = FPNNeck()
        self.lane_head = LaneHead()
        self.obj_head  = ObjectHead()
        self.sign_head = SignHead()

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        x = self.stem(x)
        c2 = self.layer1(x)   # /4
        c3 = self.layer2(c2)  # /8
        c4 = self.layer3(c3)  # /16
        c5 = self.layer4(c4)  # /32
        p2, p3, p4, p5 = self.neck([c2, c3, c4, c5])

        lane = self.lane_head(p2)             # 가장 큰 해상도 사용
        obj_cls, obj_reg = self.obj_head(p3)  # 중간 해상도
        sign = self.sign_head(p5)             # 가장 작은 해상도 (전역)

        return {
            "lane":    lane,
            "obj_cls": obj_cls,
            "obj_reg": obj_reg,
            "sign":    sign,
        }


def demo() -> None:
    torch.manual_seed(0)
    model = HydraNetMini().eval()
    img = torch.randn(1, 3, 224, 224)  # 단일 카메라 입력 가짜

    with torch.no_grad():
        out = model(img)

    print("== HydraNet Mini — 헤드별 출력 텐서 ==")
    for name, tensor in out.items():
        if isinstance(tensor, torch.Tensor):
            print(f"  {name:8s} shape: {list(tensor.shape)}")

    # 파라미터 수
    n_params = sum(p.numel() for p in model.parameters()) / 1e6
    print(f"\n  총 파라미터  : {n_params:.2f} M")
    print("  메모리 추정  : ~{:.0f} MB (FP32)".format(n_params * 4))


if __name__ == "__main__":
    demo()
