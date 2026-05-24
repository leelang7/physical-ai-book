"""
ch25 — Mini Occupancy Network 학습 가능 버전 (합성 3D 장면)

도서 25장 *"미니 Occupancy Network 실험"* 의 핵심.
[ch06 mini_occupancy.py](../ch06_occ/mini_occupancy.py) 는 forward-only.
ch25 는 *"3D 장면 생성 → 2D 카메라 렌더 → Occupancy 학습"* 의 완전한 루프.

데이터:
  - Voxel 그리드 16×16×4 안에 큐브 1~3 개 무작위 배치 → 정답 occupancy
  - 그 voxel 을 단일 카메라 (탑뷰 단순화) 로 투영 → 2D 이미지
  - 모델이 2D → 3D voxel occupancy 복원하도록 학습

목표:
  - 학습 후 voxel IoU 0.5 이상 (단순 합성에선 충분히 도달 가능)
"""
from __future__ import annotations
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------- 합성 3D 장면 ----------
def make_scene(rng: np.random.Generator,
               grid_xy: int = 16, grid_z: int = 4,
               n_cubes: int = 2) -> np.ndarray:
    """X×Y×Z voxel 그리드. 0/1 점유."""
    occ = np.zeros((grid_xy, grid_xy, grid_z), dtype=np.float32)
    n = int(rng.integers(1, n_cubes + 1))
    for _ in range(n):
        cube_size = int(rng.integers(2, 5))
        x = int(rng.integers(0, grid_xy - cube_size + 1))
        y = int(rng.integers(0, grid_xy - cube_size + 1))
        z = int(rng.integers(0, grid_z - 1))
        zh = min(grid_z - z, cube_size)
        occ[x:x + cube_size, y:y + cube_size, z:z + zh] = 1.0
    return occ


def render_topdown(occ: np.ndarray, img_size: int = 32) -> np.ndarray:
    """탑뷰 합성 — 각 (x, y) 칸의 최대 Z 점유를 *높이 명도* 로 표현.

    실제 카메라 투영은 frustum + 외부 파라미터가 필요하지만, 데모는 단순화.
    """
    grid_xy, _, grid_z = occ.shape
    # (x, y) 별로 가장 위 점유 voxel 의 z 인덱스 + 점유 여부
    has_occ = occ.any(axis=2).astype(np.float32)
    top_z = np.where(has_occ > 0,
                     grid_z - 1 - np.argmax(occ[:, :, ::-1], axis=2),
                     0)
    height_map = top_z / max(1, grid_z - 1) * has_occ
    # 그리드 → 이미지 해상도로 보간
    img = np.zeros((3, img_size, img_size), dtype=np.float32)
    # 채널 0: 점유 여부
    img[0] = _upscale(has_occ, img_size)
    # 채널 1: 높이
    img[1] = _upscale(height_map, img_size)
    # 채널 2: 노이즈 (현실 카메라의 잡음 시뮬레이션)
    img[2] = rng_noise(img_size)
    return img


def rng_noise(size: int) -> np.ndarray:
    return np.random.default_rng(None).uniform(0, 0.1, (size, size)).astype(np.float32)


def _upscale(small: np.ndarray, target: int) -> np.ndarray:
    """nearest-neighbor 단순 업샘플."""
    h, w = small.shape
    scale = target // h
    return np.repeat(np.repeat(small, scale, axis=0), scale, axis=1)


def make_batch(batch: int = 32, seed: int | None = None) -> tuple[torch.Tensor, torch.Tensor]:
    rng = np.random.default_rng(seed)
    imgs, occs = [], []
    for _ in range(batch):
        occ = make_scene(rng)
        img = render_topdown(occ)
        imgs.append(img)
        occs.append(occ)
    return (
        torch.tensor(np.stack(imgs)),    # (B, 3, 32, 32)
        torch.tensor(np.stack(occs)),    # (B, 16, 16, 4)
    )


# ---------- Mini Occupancy 모델 (학습 가능) ----------
class MiniOccupancyNet(nn.Module):
    """2D 이미지 → 3D voxel 점유.

    구조: backbone → BEV 변환 → Z 축으로 차원 확장 → 3D conv → occupancy
    """

    def __init__(self, grid_xy: int = 16, grid_z: int = 4):
        super().__init__()
        self.grid_xy, self.grid_z = grid_xy, grid_z

        # 2D backbone (Conv → 다운샘플)
        self.backbone = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),   # 32→16
        )
        # 채널을 Z 축으로 확장 (32 채널 → 4 Z 슬라이스 × 8 채널)
        self.lift = nn.Conv2d(32, grid_z * 8, 1)
        # 3D conv 로 voxel 점유 예측
        self.shoot = nn.Sequential(
            nn.Conv3d(8, 16, 3, padding=1), nn.ReLU(),
            nn.Conv3d(16, 1, 1),
        )

    def forward(self, img: torch.Tensor) -> torch.Tensor:
        B = img.shape[0]
        f2d = self.backbone(img)              # (B, 32, 16, 16)
        f_lifted = self.lift(f2d)             # (B, Z*8, 16, 16)
        # (B, 8, Z, 16, 16) 로 재구성
        f3d = f_lifted.reshape(B, 8, self.grid_z, self.grid_xy, self.grid_xy)
        # voxel logits — 결과는 (B, X, Y, Z) 형태로 정렬
        logits = self.shoot(f3d).squeeze(1)   # (B, Z, Y, X)
        return logits.permute(0, 3, 2, 1)     # (B, X, Y, Z)


# ---------- 학습 + 평가 ----------
def voxel_iou(pred: torch.Tensor, gt: torch.Tensor, thresh: float = 0.5) -> float:
    p = (torch.sigmoid(pred) > thresh).float()
    inter = (p * gt).sum(dim=(1, 2, 3))
    union = ((p + gt) > 0).float().sum(dim=(1, 2, 3))
    return float((inter / (union + 1e-6)).mean().item())


def train(model: MiniOccupancyNet, n_steps: int = 200, batch: int = 32):
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    # 양성 voxel 가중치 — 합성 데이터에서 점유 비율 ~10% 이라 9 가량으로 보정
    pos_weight = torch.tensor([9.0])
    history = []
    for step in range(n_steps):
        img, occ_gt = make_batch(batch=batch, seed=step)
        logits = model(img)
        loss = F.binary_cross_entropy_with_logits(logits, occ_gt, pos_weight=pos_weight)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 40 == 0:
            iou = voxel_iou(logits, occ_gt)
            history.append((step, loss.item(), iou))
            print(f"  step {step:3d}  loss={loss.item():.4f}  voxel IoU={iou:.3f}")
    return history


def evaluate(model: MiniOccupancyNet, n_batches: int = 5, batch: int = 32) -> dict:
    model.eval()
    ious, losses = [], []
    with torch.no_grad():
        for i in range(n_batches):
            img, occ_gt = make_batch(batch=batch, seed=9000 + i)
            logits = model(img)
            losses.append(F.binary_cross_entropy_with_logits(logits, occ_gt).item())
            ious.append(voxel_iou(logits, occ_gt))
    model.train()
    return {"loss": float(np.mean(losses)), "iou": float(np.mean(ious))}


def main() -> None:
    torch.manual_seed(0)
    model = MiniOccupancyNet()
    n_params = sum(p.numel() for p in model.parameters()) / 1e3

    print(f"== ch25 Mini Occupancy Network 학습 ({n_params:.1f} K params) ==\n")

    pre = evaluate(model)
    print(f"학습 전: loss {pre['loss']:.4f}  voxel IoU {pre['iou']:.3f}")

    print(f"\n400 step 학습 (CPU 2~3분):")
    train(model, n_steps=400)

    post = evaluate(model)
    print(f"\n학습 후: loss {post['loss']:.4f}  voxel IoU {post['iou']:.3f}")
    print(f"\n  개선:")
    print(f"    loss      : {pre['loss']:.4f} → {post['loss']:.4f}")
    print(f"    voxel IoU : {pre['iou']:.3f} → {post['iou']:.3f}")

    print(f"\n  의미: 2D 탑뷰 입력만으로 3D voxel 점유 예측 학습 — 책 25.4 절 핵심.")
    print(f"  실제 nuScenes mini + 다중 카메라 학습 = M3 후반 노트북 (GPU 필요).")


if __name__ == "__main__":
    main()
