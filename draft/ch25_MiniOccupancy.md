# 25장. 미니 Occupancy Network 실험

> **학습 목표**
> 이 장을 마치면 2D 이미지에서 3D 점유 복셀을 예측하는 **최소 파이프라인**을 처음부터 끝까지 돌려 본 경험을 갖게 된다. nuScenes mini 데이터셋을 써서 학습·시각화까지 해 보며, 카메라 내·외부 파라미터를 다루는 실전 감각을 익힌다. 6장에서 개념으로 배운 Occupancy Network가 왜 그런 구조로 설계되었는지, 그 한계가 어디에서 드러나는지를 손으로 확인한다.

---

## 25.1 실험의 크기와 범위

6장의 Tesla Occupancy Network를 그대로 재현하는 것은 개인 환경에서 무리다. 8대의 카메라, 시간적 융합, 다양한 보조 헤드가 얽힌 거대한 시스템이다. 이 장의 미니 버전은 훨씬 겸손하다. 단 한 대의 전방 카메라 이미지를 입력으로 받아, 차량 기준 전후 좌우 100m × 수직 8m의 공간을 0.5m 간격으로 쪼갠 200×200×16 크기의 점유 확률 볼륨을 출력한다. Lift-Splat-Shoot의 구조를 극도로 단순화한 뼈대이며, **차원이 어떻게 흐르는지** 머리로 이해하는 것이 최우선 목표다.

완성된 코드는 저자 GitHub 저장소의 `physical-ai-book/ch25_occ/` 아래에 공개된다. 이 장은 그 중 핵심 조각들을 서술적으로 짚어 간다.

---

## 25.2 nuScenes mini — 작지만 진짜인 자율주행 데이터

nuScenes는 2019년 nuTonomy(현 Motional)가 공개한 자율주행 데이터셋으로, 6개 카메라와 LiDAR, 레이더의 동기화된 로그가 들어 있다. 전체 버전은 수백 GB에 달하지만, 고맙게도 **mini 버전**이 있다. 약 400MB 크기로, 작지만 실제 주행 데이터의 구조를 모두 담고 있다. 연구용 라이선스라 학습과 실험에 자유롭게 쓸 수 있다.

설치와 로드는 간단하다.

```bash
wget -O nuscenes-mini.tgz https://www.nuscenes.org/data/v1.0-mini.tgz
tar -xzf nuscenes-mini.tgz
pip install nuscenes-devkit
```

```python
from nuscenes.nuscenes import NuScenes
nusc = NuScenes(version='v1.0-mini', dataroot='./nuscenes', verbose=False)
```

이제 `nusc.scene`, `nusc.sample` 같은 속성을 통해 장면과 샘플에 접근할 수 있다. 각 샘플은 특정 시점의 스냅샷이고, 그 안에 6대 카메라 이미지와 LiDAR 점군이 연결되어 있다. 우리의 미니 실험에서는 단일 카메라만 쓰지만, 이후 확장에서는 6대를 모두 활용할 수 있다.

---

## 25.3 라벨을 만든다 — LiDAR 점군을 복셀로 투영

Occupancy Network의 학습에는 3D 점유 라벨이 필요하다. 사람이 3D 공간의 25만 개 복셀에 일일이 라벨을 붙이는 것은 현실적이지 않으니, LiDAR 점군을 쓴다. 각 LiDAR 점을 차량 기준 좌표계의 복셀 격자에 투영하면 자연스럽게 점유 라벨이 생성된다.

```python
import numpy as np

def lidar_to_voxels(points, extent=(100, 100, 8), res=0.5):
    X, Y, Z = extent
    Vx, Vy, Vz = int(X/res), int(Y/res), int(Z/res)
    occ = np.zeros((Vx, Vy, Vz), dtype=np.float32)
    ix = ((points[:,0] + X/2) / res).astype(int)
    iy = ((points[:,1] + Y/2) / res).astype(int)
    iz = ((points[:,2] + Z/2) / res).astype(int)
    valid = (ix >= 0) & (ix < Vx) & (iy >= 0) & (iy < Vy) & (iz >= 0) & (iz < Vz)
    occ[ix[valid], iy[valid], iz[valid]] = 1.0
    return occ
```

이 단순한 함수 한 개가 데이터 준비의 핵심이다. 주의할 점은 LiDAR의 점군이 **ego 좌표계**에 있어야 한다는 것이다. nuScenes의 원본은 글로벌 좌표계라, 차량 자세로 변환하는 전처리가 필요하다. `nuscenes-devkit`이 제공하는 유틸리티 함수를 활용한다. 이 변환을 빼먹으면 학습이 전혀 진행되지 않는데, 저자가 수업에서 가장 자주 목격한 실수 중 하나다.

---

## 25.4 미니 모델의 구조

모델은 6장에서 이미 본 단순화된 Lift-Splat 구조다. 이미지 인코더, 깊이 분포 헤드, 특징 헤드, 그리고 복셀 인코더가 뼈대다. 아래 코드가 그 골격이다.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MiniOcc(nn.Module):
    def __init__(self, D=41, C=32, voxel=(200, 200, 16)):
        super().__init__()
        self.D = D; self.C = C; self.voxel = voxel
        self.img_enc = nn.Sequential(
            nn.Conv2d(3, 32, 7, stride=2, padding=3), nn.SiLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), nn.SiLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.SiLU(),
        )
        self.depth_head = nn.Conv2d(64, D, 1)
        self.feat_head = nn.Conv2d(64, C, 1)
        self.voxel_enc = nn.Sequential(
            nn.Conv3d(C, 32, 3, padding=1), nn.SiLU(),
            nn.Conv3d(32, 1, 1),
        )

    def forward(self, img):
        feat = self.img_enc(img)
        alpha = self.depth_head(feat).softmax(1)
        c = self.feat_head(feat)
        weighted = alpha.unsqueeze(2) * c.unsqueeze(1)
        pooled = weighted.mean(dim=[-2, -1])
        pooled = pooled.permute(0, 2, 1).unsqueeze(-1).unsqueeze(-1)
        voxel = F.interpolate(pooled, size=self.voxel, mode='trilinear',
                              align_corners=False)
        logits = self.voxel_enc(voxel)
        return logits.sigmoid()
```

이 코드의 `splat` 부분은 극도로 단순화되어 있다. 제대로 된 구현에서는 각 픽셀의 각 깊이 값이 어느 3D 좌표에 해당하는지 카메라 파라미터로 계산하고, `scatter_add`로 해당 복셀에 특징을 누적한다. 본격 구현은 25.6절에서 다룬다.

---

## 25.5 학습 루프 — 무엇을 최소화하는가

Occupancy 예측의 학습 신호는 Binary Cross Entropy다. 각 복셀에 대해 "점유인가 아닌가"를 이진 분류로 본다.

```python
def train_step(model, img, gt_occ, opt):
    logits = model(img)
    loss = F.binary_cross_entropy_with_logits(logits.squeeze(1),
                                              gt_occ.float())
    opt.zero_grad(); loss.backward(); opt.step()
    return loss.item()
```

RTX 3060에서 배치 4, 30 에폭을 돌리면 약 3~4시간이 걸린다. 학습률은 AdamW의 1e-4에서 시작해 CosineAnnealing으로 낮춰 간다.

여기서 중요한 이슈가 **클래스 불균형**이다. 현실 공간의 대부분은 비어 있다. 25만 개 복셀 가운데 점유된 복셀은 수천 개 수준이다. 단순 BCE로 학습하면 모델이 "전부 비어 있음"으로 예측하는 것만으로도 손실이 낮아진다. 이 문제의 해결책이 **Focal Loss**다. 쉬운 샘플(대부분 비어 있는 복셀)의 기여를 줄이고, 어려운 샘플(점유된 복셀이나 경계 부분)에 집중한다. 저자의 실험에서 Focal Loss로 교체하면 IoU가 약 15%p 개선된다.

---

## 25.6 결과 시각화 — BEV와 3D

학습된 모델의 출력을 눈으로 보는 과정이 개념 이해의 핵심이다. BEV 시각화는 간단하다. 3D 볼륨의 z축을 최대값으로 projection하면 탑뷰 점유 지도가 나온다.

```python
import matplotlib.pyplot as plt

def show_bev(occ, threshold=0.5):
    bev = (occ.max(axis=0) > threshold).astype(int)
    plt.imshow(bev.T, origin='lower', cmap='gray_r')
    plt.title("BEV Occupancy")
    plt.show()
```

3D 시각화는 `open3d` 같은 라이브러리를 쓰면 멋지다. 점유된 복셀을 3D 포인트 클라우드로 변환해 브라우저 위젯이나 별도 창에서 돌려 볼 수 있다.

```python
import open3d as o3d

def show_3d(occ, threshold=0.5):
    zs, ys, xs = np.where(occ > threshold)
    pts = np.stack([xs, ys, zs], axis=1).astype(float) * 0.5
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)
    o3d.visualization.draw_geometries([pcd])
```

결과를 처음 볼 때 인상적인 점은 "**도로 표면 평면**이 자연스럽게 나타난다"는 것이다. 앞쪽에 차량이 있으면 직육면체 덩어리가 잡힌다. 정면 먼 거리에서는 예측이 덜 정확하고, 옆쪽 측면도 약하다. 단일 카메라로는 원리적 한계가 있음을 시각적으로 체감할 수 있다. 이 한계가 왜 Tesla가 8대 카메라를 쓰는지에 대한 가장 설득력 있는 답이다.

---

## 25.7 결과가 이상할 때 — 디버깅 체크리스트

미니 Occupancy Network가 제대로 학습되지 않는 경우, 순서대로 점검할 것들이 있다. 먼저 카메라의 내·외부 파라미터 변환이 맞는지 확인한다. 좌표계 하나만 어긋나도 전체가 깨진다. 그 다음 LiDAR 라벨의 좌표계를 점검한다. 글로벌 좌표계가 아닌 ego 좌표계로 변환되었는지 반드시 확인한다. 복셀 해상도가 너무 거칠거나 너무 미세하지 않은지도 살핀다. 0.5m가 실험용으로 적당하다. 마지막으로 클래스 불균형이다. BCE 대신 Focal Loss로 교체하면 많은 문제가 해결된다.

이 네 가지 중 한 곳이 틀리면 다른 곳을 아무리 고쳐도 결과가 나아지지 않는다. 저자가 수업에서 "학생들이 반나절을 헤매다 강사가 옆에서 보니 5분 안에 찾아지는" 에피소드의 원인이 대부분 이 네 가지 가운데 하나다.

---

## 25.8 다음 확장 — 다중 카메라와 시간적 융합

이 미니 버전이 탄탄해지면 확장 방향이 열린다. 첫째, **6대 카메라**로 확장한다. nuScenes는 이미 6대를 지원하므로, 각 카메라의 내·외부 파라미터를 정확히 사용하면 360° BEV가 만들어진다. 성능이 크게 오르지만 메모리 요구도 같이 오른다. 둘째, **시간적 융합**을 추가한다. 과거 5프레임의 예측을 현재 좌표계로 정렬해 누적한다. 가려짐(occlusion) 문제가 크게 완화된다. 셋째, **Occupancy Flow**를 헤드로 추가한다. 각 복셀의 속도 벡터까지 예측하면 간단한 예측(Prediction) 기능까지 겸하게 된다.

이 확장들은 저자 저장소의 `physical-ai-book/ch25_occ/advanced/` 아래에서 단계별로 제공된다. 기본 버전을 돌려본 뒤 하나씩 추가해 가는 경로가 권장된다.

---

## 장말 정리

미니 Occupancy Network는 6장의 개념을 손으로 체감시키는 도구다. nuScenes mini와 Lift-Splat의 단순화 버전으로 RTX 3060에서도 돌릴 수 있으며, 시각화가 개념 이해의 결정적 열쇠다. 단일 카메라의 한계가 예측의 방향성 편차로 드러나고, 이것이 다중 카메라의 필요성을 자연스럽게 설명한다. 클래스 불균형·좌표계·라벨 변환의 세 가지가 가장 흔한 실패 원인이다.

## 연습문제

1. 본 구현의 `MiniOcc`에서 Lift-Splat의 splat 부분을 **제대로** 구현하려면 어떤 수정이 필요한지 단계별로 서술하라.
2. Focal Loss와 일반 BCE로 각각 학습시킨 후 IoU 차이를 측정하고 결과를 보고하라.
3. 단일 카메라와 6대 카메라 + temporal fusion 설정에서의 메모리와 추론 시간을 비교 측정하라.
