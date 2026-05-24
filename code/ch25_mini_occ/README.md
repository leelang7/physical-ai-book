# Chapter 25 · Mini Occupancy Network — 학습 가능 버전

도서 **25장** *"미니 Occupancy Network 실험"* 와 1:1 연결.

[ch06 Mini Occupancy](../ch06_occ/) 는 forward-only LSS 구조.
ch25 는 **합성 3D 장면 → 카메라 렌더 → Occupancy 예측 학습** 의 완전한 루프.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`train_mini_occ.py`](train_mini_occ.py) | 16×16×4 voxel 그리드에 큐브 1~3개 → 탑뷰 32×32 렌더 → 2D→3D occupancy 학습 + 평가 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch25_mini_occ
python train_mini_occ.py
```

## 실측 결과 (CPU 2~3분)

```
학습 전: loss 0.7496  voxel IoU 0.040
400 step 학습 ...
학습 후: loss 0.2658  voxel IoU 0.117

개선:
  loss      : 0.7496 → 0.2658 (-65%)
  voxel IoU : 0.040 → 0.117 (3× 개선)
```

## 합성 데이터의 한계 — 정직한 평가

**IoU 0.117 은 좋은 수치 아닙니다.** 모델이 *학습은 하지만 본질적 한계* 가 있는 이유:

1. **탑뷰 단일 카메라 → Z 정보 손실** — 위에서 본 한 장으로는 객체 *높이* 를 추측할 수 없음. 실제 Tesla 는 8 카메라 + frustum 변환으로 깊이 단서 확보
2. **Sparse occupancy (~10%)** — `pos_weight=9` 로 균형 보정해도 학습 자체가 어려움
3. **데이터 자체가 작음** — voxel 16×16×4=1024 grid + 32×32 입력은 너무 좁아 학습 신호 부족

본 데모는 *학습 루프 구조가 정상* 임만 시연. **실제 IoU 0.5+** 는 nuScenes mini + 다중 카메라 + GPU 가 필요.

## 학습 포인트 (도서 본문)

1. **Sparse 데이터의 클래스 불균형** (25.3 절) — Occupancy 는 *대부분 빈 공간*. 단순 BCE 는 *"모두 0"* 으로 수렴. `pos_weight` 또는 focal loss 로 해결.
2. **카메라 한 대의 깊이 모호성** (25.4 절) — 본 데모는 탑뷰 한 장이라 Z 복원 불가. Tesla 는 *여러 시점* 의 광선 교차로 깊이 복원 (LSS의 핵심)
3. **합성→실제 격차** (25.5 절) — 깔끔한 합성에서 IoU 0.1 인 모델이 nuScenes 에선 더 떨어짐. *실제 학습은 별도 노트북* 으로 분리해야 정직.

## 핵심 손실 함수 (5 줄)

```python
pos_weight = torch.tensor([9.0])  # 점유 비율 ~10% 균형
loss = F.binary_cross_entropy_with_logits(
    logits, occ_gt, pos_weight=pos_weight
)
```

`pos_weight` 가 없으면 IoU 0 으로 collapse. **sparse occupancy 학습의 첫 함정**.

## 다음

- [ch06 Mini Occupancy forward](../ch06_occ/) — 9.6K params, 학습 없는 구조 확인
- [ch07 BEV](../ch07_bev/) — Bird's Eye View (다른 3D 표현 비교)
- 실제 nuScenes 학습 — M3 후반 별도 노트북 (GPU 필요)
