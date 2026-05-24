# Chapter 24 · Mini HydraNet — 학습 가능 버전

도서 **24장** *"미니 HydraNet 만들기 — YOLOv8 에서 시작"* 와 1:1 연결.

[ch05 HydraNet](../ch05_hydra/) 는 forward-pass 만 (11.9M params, 학습 없음).
ch24 는 **실제 학습 + 평가** 까지 — 14K params 작은 모델, 합성 데이터,
CPU 30~60초.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`train_mini_hydra.py`](train_mini_hydra.py) | 합성 데이터 + 3 헤드 (Lane / Object / Sign) 동시 학습 + 학습 전후 평가 비교 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch24_mini_hydra
python train_mini_hydra.py
```

## 실측 결과 (CPU 30~60초)

```
학습 전: sign 36.2%  bbox L1 0.235  lane IoU 0.000
200 step 학습 ...
학습 후: sign 100%   bbox L1 0.117  lane IoU 0.948
```

3 헤드가 한 백본을 공유하며 **동시에** 수렴.

## 합성 데이터 디자인

64×64 RGB 이미지에 세 정답을 동시에 심어 멀티태스크 학습이 의미 있게 됨:

| 헤드 | 정답 신호 | 평가 메트릭 |
|---|---|---|
| Lane (segmentation) | 무작위 y 위치의 가로 흰 직선 | IoU (32 해상도) |
| Object (bbox 회귀) | 8~20 px 무작위 정사각형 | L1 (정규화 좌표) |
| Sign (분류 3-way) | 전체 색조 0.2 만큼 R / G / B 채널 강세 | Accuracy |

ch05 의 8 클래스 분류 + 8 채널 객체 detection 등의 *진짜 풀 task* 는 BDD100K + YOLOv8 + GPU 가 필요해 본 데모는 *최소한* 으로 단순화.

## 학습 포인트 (도서 본문)

1. **멀티태스크 손실** (24.3 절) — 세 손실을 **합산** 해서 backprop. 가중치 비율은 데이터·task 난이도에 따라 조정 (본 데모는 1:1:1 단순화).
2. **공유 백본의 진가** (24.4 절) — 14K params 백본 1개가 3 헤드 모두에 신호 → 단일 헤드 학습보다 데이터 효율 ↑, 일반화 ↑. ch08 의 8 카메라 공유와 같은 원리.
3. **합성 데이터의 한계** (24.5 절) — 너무 깔끔해서 100% 달성. 실제 BDD100K 는 occlusion · 조명 변화 · 클래스 불균형 등으로 mAP 60~70% 도 도전.

## 핵심 학습 루프 (15 줄)

```python
opt = torch.optim.Adam(model.parameters(), lr=3e-3)
for step in range(200):
    data = make_batch(batch=32, seed=step)
    pred = model(data["img"])
    lane_loss = BCE(pred["lane"], data["lane_mask"])
    obj_loss  = SmoothL1(pred["obj"], data["obj_bbox"])
    sign_loss = CrossEntropy(pred["sign"], data["sign_cls"])
    loss = lane_loss + obj_loss + sign_loss      # 합산
    opt.zero_grad(); loss.backward(); opt.step()
```

이 패턴이 ch05 forward 만 보던 모델을 *실제로 학습하는 시스템* 으로 만듦.

## 다음

- [ch05 HydraNet forward](../ch05_hydra/) — 11.9M params, 학습 없는 구조 확인
- [ch08 8 카메라 HydraNet](../ch08_heads/) — 멀티 카메라 BEV 융합
- [ch25 Mini Occupancy](../ch25_mini_occ/) — Occupancy Network 학습 가능 버전
