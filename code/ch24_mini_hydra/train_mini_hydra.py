"""
ch24 — Mini HydraNet 학습 가능 버전 (합성 데이터)

도서 24장 *"미니 HydraNet 만들기 — YOLOv8 에서 시작"* 의 핵심.
ch05 (forward only, 11.9M params) 의 *학습 가능 축소판* (200 step CPU 학습).

  실제 BDD100K + YOLOv8 풀 학습은 GPU + 데이터셋 필요.
  본 데모는 합성 데이터로 *3 헤드 동시 학습 가능* 임만 시연.

데이터: 64×64 RGB 합성 이미지에 다음을 심음
  - 가로 직선 (차선) → Lane segmentation 정답
  - 정사각형 (객체) → Object detection bbox 정답
  - 색상 (빨강/녹색/파랑) → Sign classification 정답
"""
from __future__ import annotations
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------- 합성 데이터셋 ----------
def make_synthetic_sample(rng: np.random.Generator, size: int = 64) -> dict:
    """RGB 이미지 + 3 헤드 정답 한 세트."""
    img = np.zeros((3, size, size), dtype=np.float32)

    # 1) 색상 → Sign 분류 (3 클래스)
    sign_cls = int(rng.integers(0, 3))
    tint = np.zeros(3)
    tint[sign_cls] = 0.2
    img += tint[:, None, None]

    # 2) 가로 직선 (lane) — 무작위 위치
    lane_y = int(rng.integers(size // 4, 3 * size // 4))
    lane_mask = np.zeros((size, size), dtype=np.float32)
    lane_mask[lane_y - 1:lane_y + 1, :] = 1.0
    img[:, lane_y - 1:lane_y + 1, :] = 1.0  # 흰 선

    # 3) 정사각형 (object) — 무작위 위치/크기
    box_size = int(rng.integers(8, 20))
    bx = int(rng.integers(0, size - box_size))
    by = int(rng.integers(0, size - box_size))
    img[:, by:by + box_size, bx:bx + box_size] = 0.8
    # bbox 정답: (cx, cy, w, h) 정규화 좌표
    obj_bbox = np.array([
        (bx + box_size / 2) / size,
        (by + box_size / 2) / size,
        box_size / size,
        box_size / size,
    ], dtype=np.float32)

    # 가우시안 노이즈
    img += rng.normal(0, 0.05, size=img.shape).astype(np.float32)
    img = np.clip(img, 0, 1)

    return {
        "img": img,
        "lane_mask": lane_mask,
        "obj_bbox": obj_bbox,
        "sign_cls": sign_cls,
    }


def make_batch(batch: int = 32, size: int = 64, seed: int | None = None) -> dict:
    rng = np.random.default_rng(seed)
    samples = [make_synthetic_sample(rng, size) for _ in range(batch)]
    return {
        "img":       torch.tensor(np.stack([s["img"]       for s in samples])),
        "lane_mask": torch.tensor(np.stack([s["lane_mask"] for s in samples])),
        "obj_bbox":  torch.tensor(np.stack([s["obj_bbox"]  for s in samples])),
        "sign_cls":  torch.tensor([s["sign_cls"]  for s in samples], dtype=torch.long),
    }


# ---------- Mini HydraNet ----------
class TinyBackbone(nn.Module):
    def __init__(self, in_ch: int = 3, out_ch: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, 16, 3, padding=1), nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),  # 64 → 32
            nn.Conv2d(32, out_ch, 3, padding=1), nn.ReLU(),
        )

    def forward(self, x):
        return self.net(x)


class MiniHydraNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = TinyBackbone()
        # Lane: 32×32 으로 다운샘플된 채로 segmentation
        self.lane_head = nn.Conv2d(32, 1, 1)
        # Object: BBox 4 값을 GAP 후 회귀
        self.obj_head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(32, 4), nn.Sigmoid(),
        )
        # Sign: 전역 분류 3 클래스
        self.sign_head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(32, 3),
        )

    def forward(self, x):
        f = self.backbone(x)
        return {
            "lane":  self.lane_head(f).squeeze(1),     # (B, 32, 32)
            "obj":   self.obj_head(f),                  # (B, 4)
            "sign":  self.sign_head(f),                 # (B, 3)
        }


def multi_task_loss(pred: dict, target: dict) -> tuple[torch.Tensor, dict]:
    # Lane: 64→32 다운샘플된 마스크와 비교
    lane_gt = F.adaptive_max_pool2d(target["lane_mask"].unsqueeze(1), 32).squeeze(1)
    lane_loss = F.binary_cross_entropy_with_logits(pred["lane"], lane_gt)
    obj_loss  = F.smooth_l1_loss(pred["obj"], target["obj_bbox"])
    sign_loss = F.cross_entropy(pred["sign"], target["sign_cls"])
    total = lane_loss + obj_loss + sign_loss
    return total, {"lane": lane_loss.item(), "obj": obj_loss.item(), "sign": sign_loss.item()}


# ---------- 학습 + 평가 ----------
def train(model: MiniHydraNet, n_steps: int = 200, batch: int = 32, lr: float = 3e-3):
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    history = []
    for step in range(n_steps):
        data = make_batch(batch=batch, seed=step)
        pred = model(data["img"])
        loss, parts = multi_task_loss(pred, data)
        opt.zero_grad()
        loss.backward()
        opt.step()
        history.append(parts)
        if step % 40 == 0:
            print(f"  step {step:3d}  loss={loss.item():.4f}  "
                  f"lane={parts['lane']:.3f}  obj={parts['obj']:.3f}  sign={parts['sign']:.3f}")
    return history


def evaluate(model: MiniHydraNet, n_batches: int = 5, batch: int = 32) -> dict:
    """검증 — 학습 안 본 시드. sign 분류 정확도 + bbox L1 + lane IoU."""
    model.eval()
    sign_correct = 0
    sign_total = 0
    bbox_err = []
    lane_iou = []
    with torch.no_grad():
        for i in range(n_batches):
            data = make_batch(batch=batch, seed=9000 + i)
            pred = model(data["img"])
            # sign 정확도
            sign_correct += (pred["sign"].argmax(-1) == data["sign_cls"]).sum().item()
            sign_total += batch
            # bbox L1
            bbox_err.append((pred["obj"] - data["obj_bbox"]).abs().mean().item())
            # lane IoU (32 해상도)
            lane_pred = (torch.sigmoid(pred["lane"]) > 0.5).float()
            lane_gt = F.adaptive_max_pool2d(data["lane_mask"].unsqueeze(1), 32).squeeze(1)
            inter = (lane_pred * lane_gt).sum(dim=(1, 2))
            union = ((lane_pred + lane_gt) > 0).float().sum(dim=(1, 2))
            iou = (inter / (union + 1e-6)).mean().item()
            lane_iou.append(iou)
    model.train()
    return {
        "sign_acc": 100 * sign_correct / sign_total,
        "bbox_l1":  float(np.mean(bbox_err)),
        "lane_iou": float(np.mean(lane_iou)),
    }


def main() -> None:
    torch.manual_seed(0)
    model = MiniHydraNet()
    n_params = sum(p.numel() for p in model.parameters()) / 1e3

    print(f"== ch24 Mini HydraNet 학습 ({n_params:.1f} K params) ==\n")

    # 학습 전 평가
    pre = evaluate(model)
    print(f"학습 전: sign 정확도 {pre['sign_acc']:5.1f}%  bbox L1 {pre['bbox_l1']:.3f}  lane IoU {pre['lane_iou']:.3f}")

    print(f"\n200 step 학습 시작 (CPU ~30~60초):")
    train(model, n_steps=200)

    # 학습 후 평가
    post = evaluate(model)
    print(f"\n학습 후: sign 정확도 {post['sign_acc']:5.1f}%  bbox L1 {post['bbox_l1']:.3f}  lane IoU {post['lane_iou']:.3f}")
    print(f"\n  개선:")
    print(f"    sign 정확도: {pre['sign_acc']:5.1f}% → {post['sign_acc']:5.1f}%")
    print(f"    bbox L1   : {pre['bbox_l1']:.3f} → {post['bbox_l1']:.3f}")
    print(f"    lane IoU  : {pre['lane_iou']:.3f} → {post['lane_iou']:.3f}")

    print(f"\n  3 헤드가 한 백본을 공유하며 동시 학습 — 책 24.3 절의 핵심.")
    print(f"  실제 BDD100K + YOLOv8 풀 학습 = M3 후반 노트북 (GPU 필요).")


if __name__ == "__main__":
    main()
