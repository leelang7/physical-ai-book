# 24장. 미니 HydraNet 만들기 — YOLOv8에서 멀티태스크로

> **학습 목표**
> 이 장은 이 책의 실습 골격이 되는 프로젝트다. 5장에서 개념으로 다룬 HydraNet을, 친숙한 YOLOv8 백본 위에 차선 · 객체 · 주행 가능 영역의 세 헤드를 붙여 실제로 학습시키고 추론해 본다. BDD100K 데이터셋을 활용하며, Uncertainty Weighting 기반의 손실 균형을 실전에 적용한다. RTX 3060~4070급 GPU에서 돌릴 수 있는 크기로 설계되어 있어, 독자가 자기 손으로 **감각을 익히는** 것이 목표다.

---

## 24.1 프로젝트가 겨냥하는 것

이 장의 결과물은 소박하지만 명확하다. 한 장의 카메라 이미지를 입력으로 받아 세 가지를 동시에 예측하는 모델이다. 첫째, 10개 클래스(차량·트럭·버스·오토바이·자전거·보행자·라이더·신호등·표지판·기타)의 바운딩 박스를 검출한다. 둘째, 최대 4개의 차선을 찾아 각 차선을 72개의 점으로 표현한다. 셋째, 주행 가능 영역을 160×160 크기의 이진 마스크로 분할한다. 목표 성능은 RTX 3060 기준 40FPS 이상이다. Tesla FSD의 수십분의 일 규모지만, **개념이 어떻게 코드로 바뀌는지** 체감하기에는 충분하다.

전체 프로젝트는 저자 GitHub 저장소의 `physical-ai-book/ch24_hydra/` 아래에 공개된다. 책에서는 핵심 부분만 다루되, 코드의 연결 관계를 명확히 짚어간다.

---

## 24.2 데이터셋 — 왜 BDD100K인가

자율주행 멀티태스크의 사실상 표준 데이터셋이 **Berkeley DeepDrive 100K(BDD100K)** 다. 이미지 10만 장, 1만 개 시퀀스, 날씨·시간·날짜·장소 메타데이터, 객체 박스·차선·주행 가능 영역·세그멘테이션 라벨까지 모두 포함한다. 비상업 연구용 라이선스이므로 교육과 개인 연구에 자유롭게 쓸 수 있다.

데이터를 다운로드하면 크기가 만만찮다. 전체는 약 200GB다. 학습 실험에는 10k 이미지 정도의 서브셋으로 충분하다. 공식 배포판을 쪼개거나, 공식 small 분할을 사용하면 된다. 저자는 수업에서 8GB 남짓의 서브셋을 준비해 둔다. 이 정도면 RTX 3060의 메모리에서도 50 에폭을 돌릴 수 있다.

데이터 로더는 각 태스크를 함께 반환하도록 설계한다. PyTorch의 `Dataset` 클래스를 상속받아 `__getitem__`에서 이미지와 함께 세 종류의 라벨을 한 묶음으로 주는 구조다. 이 로더의 정확성이 학습 성패를 가른다. 라벨 좌표가 이미지 증강(flip, crop, resize)에 맞춰 변환되지 않으면 모델이 학습하지 못한다.

---

## 24.3 백본 — YOLOv8 위에 짓기

YOLOv8의 백본을 재활용하는 이유는 세 가지다. 이미 **잘 학습된** 가중치가 있고, **성숙한 구현**이 Ultralytics 라이브러리에서 제공되며, 저자의 기존 저장소(`Yolov8-custom`)로 친숙한 출발점을 제공한다. 굳이 새 백본을 만들 필요가 없다.

YOLOv8의 model 구조에서 P3, P4, P5 피처맵을 꺼내는 부분이 조금 까다롭다. Ultralytics의 `DetectionModel`은 레이어가 리스트 형태로 되어 있어, 인덱스로 접근한다. 정확한 인덱스는 버전마다 약간씩 다르므로 `print(model.model)`로 확인하는 것이 안전하다.

```python
import torch.nn as nn
from ultralytics.nn.tasks import DetectionModel

class YoloBackbone(nn.Module):
    def __init__(self, variant="n"):
        super().__init__()
        model = DetectionModel(cfg=f"yolov8{variant}.yaml")
        self.stem = nn.Sequential(*model.model[:10])
    def forward(self, x):
        feats = []
        for i, layer in enumerate(self.stem):
            x = layer(x)
            if i in (4, 6, 9):
                feats.append(x)
        return feats
```

이 코드는 하나의 예시이며, YOLOv8의 정확한 버전에 맞춰 조정이 필요하다. 저자 저장소의 최신 코드가 업데이트된 인덱스를 반영한다.

---

## 24.4 세 개의 헤드 — 각자의 출력 형식

**Detection Head**는 anchor-free 구조다. 각 피처맵 위치에서 클래스 확률, 바운딩 박스 좌표, 객체 존재 여부를 세 갈래로 예측한다. 세 예측이 1x1 컨볼루션으로 간단히 나온다.

```python
class DetectionHead(nn.Module):
    def __init__(self, c, num_classes=10):
        super().__init__()
        self.cls = nn.Conv2d(c, num_classes, 1)
        self.reg = nn.Conv2d(c, 4, 1)
        self.obj = nn.Conv2d(c, 1, 1)
    def forward(self, feat):
        return self.cls(feat), self.reg(feat), self.obj(feat)
```

**Lane Head**는 Row Anchor 방식을 단순화한 구조다. 이미지의 수직 72개 행 각각에서 차선이 존재하는 열을 분류 문제로 푼다. 최대 4개의 차선을 각기 다른 채널로 예측한다.

```python
class LaneHead(nn.Module):
    def __init__(self, c, num_lanes=4, num_rows=72, num_griding=100):
        super().__init__()
        self.num_lanes = num_lanes
        self.num_rows = num_rows
        self.num_griding = num_griding
        self.conv = nn.Sequential(
            nn.Conv2d(c, 128, 3, padding=1), nn.SiLU(),
            nn.AdaptiveAvgPool2d((num_rows, num_griding)),
        )
        self.fc = nn.Linear(128 * num_rows * num_griding,
                            num_lanes * num_rows * num_griding)
    def forward(self, feat):
        x = self.conv(feat).flatten(1)
        return self.fc(x).view(-1, self.num_lanes, self.num_rows, self.num_griding)
```

**Drivable Head**는 이진 세그멘테이션이다. 피처맵을 업샘플링해 원본의 1/4 크기(160×160)로 출력한다. 완전한 원본 해상도로 가지 않는 이유는 **속도**다. 160×160으로도 주행 가능 영역의 개략을 표현하기에 충분하다.

```python
class DrivableHead(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.up = nn.Sequential(
            nn.Conv2d(c, 64, 3, padding=1), nn.SiLU(),
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1), nn.SiLU(),
            nn.ConvTranspose2d(32, 1, 4, stride=2, padding=1),
        )
    def forward(self, feat):
        return self.up(feat)
```

---

## 24.5 통합 모델과 학습 루프

이 세 헤드를 한 모델로 묶는 구조가 최종 MiniHydra다.

```python
class MiniHydra(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = YoloBackbone("n")
        self.det = DetectionHead(c=256)
        self.lane = LaneHead(c=256)
        self.driv = DrivableHead(c=256)
    def forward(self, x):
        P3, P4, P5 = self.backbone(x)
        det = self.det(P4)
        lane = self.lane(P3)
        driv = self.driv(P3)
        return det, lane, driv
```

손실은 5장에서 다룬 Uncertainty Weighting을 적용한다. 각 태스크의 불확실성 σ가 학습 파라미터가 되어, 태스크별 손실의 가중치를 자동으로 조정한다. 이 간단한 변경이 수동 튜닝의 고역을 덜어준다.

```python
model = MiniHydra().cuda()
sigma = nn.Parameter(torch.ones(3, device="cuda") * 1.0)
opt = torch.optim.AdamW(list(model.parameters()) + [sigma],
                        lr=1e-4, weight_decay=1e-4)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=100)

for epoch in range(100):
    for x, gt in train_loader:
        x = x.cuda()
        pred = model(x)
        L, comps = multitask_loss(pred, gt, sigma)
        opt.zero_grad(); L.backward(); opt.step()
    sched.step()
```

학습에는 RTX 4070 Ti 기준 한 에폭당 약 6~8분이 걸린다. 50~100 에폭이면 의미 있는 결과가 나온다.

---

## 24.6 기대할 수 있는 성능

저자가 BDD100K 80k 서브셋으로 50 에폭을 학습시킨 결과는 대략 다음과 같다. 객체 검출의 mAP50은 0.42 근처, 차선 검출의 행별 정확도는 72% 근처, 주행 가능 영역의 IoU는 0.74 근처다. 추론 FPS는 RTX 4070 Ti에서 55FPS가 나왔다. 이 수치는 Tesla FSD와 비교하면 장난감 수준이지만, **멀티태스크 구조의 감**을 잡기에는 충분하다.

정확도를 더 끌어올리고 싶다면 몇 가지 선택지가 있다. 백본을 YOLOv8s나 m으로 키우면 정확도가 오르고 속도는 느려진다. 데이터 증강을 강화하면 일반화가 개선된다. 학습 epoch를 200으로 늘리면 최종 성능이 약 5% 더 올라간다. 각 선택의 trade-off를 직접 실험하는 것이 이 장의 가치다.

---

## 24.7 추론과 시각화

학습이 끝나면 추론을 통해 결과를 확인한다. OpenCV로 원본 이미지 위에 검출 박스, 차선 점, 주행 가능 영역 마스크를 오버레이하면 시각적으로 성능을 평가할 수 있다. `matplotlib`이 학습 로그용이라면, `OpenCV`는 결과 시각화의 표준이다.

```python
model.eval()
with torch.no_grad():
    det, lane, driv = model(img.cuda())
# OpenCV로 오버레이
# - 바운딩 박스(빨강)
# - 차선 점(파랑)
# - drivable 반투명 마스크(초록)
```

저자 저장소에는 이 시각화를 자동화하는 `infer.py` 스크립트가 들어 있다. 단일 이미지, 영상 파일, 웹캠 세 가지 입력 모두를 지원한다. YouTube "All That AI" 채널에 이 결과를 영상으로 촬영한 컨텐츠가 같이 게시될 예정이다.

---

## 장말 정리

MiniHydra는 YOLOv8 백본에 Lane·Detection·Drivable 헤드를 얹은 멀티태스크 모델이다. BDD100K 데이터셋과 Uncertainty Weighting 손실을 조합해 RTX 3060~4070급에서 50 에폭 안에 의미 있는 결과를 얻을 수 있다. 이 작은 실습이 5장에서 다룬 HydraNet의 개념이 어떻게 코드로 내려오는지를 손으로 느끼게 한다. 다음 25장에서는 이 모델에 Occupancy Head까지 더해 3D 공간 이해로 확장한다.

## 연습문제

1. Drivable Head의 출력을 160×160으로 유지한 이유는 무엇인가. 이 해상도를 320×320으로 높이면 어떤 trade-off가 생기는지 추정하고, 실제로 수정해 속도를 측정하라.
2. 학습 중 차선 헤드의 성능이 오르지 않는다. 점검할 네 가지 항목을 우선순위 순서로 정리하라.
3. 본인의 GPU에서 이 모델을 학습시키고, `torch.profiler`로 병목 레이어를 분석해 어떤 부분이 가장 비싼지 보고하라.
