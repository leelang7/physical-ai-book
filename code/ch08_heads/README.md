# Chapter 08 · Lane · Sign · Object 헤드의 통합 운용

도서 **8장** *"Lane · Sign · Object 헤드의 통합 운용"* 와 1:1 연결.
ch05 HydraNet (단일 카메라) 을 8 카메라로 확장한 버전.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`multicam_fusion.py`](multicam_fusion.py) | 8 카메라 → 공유 백본 → cross-camera 융합 → BEV → 3 헤드 (Lane / Sign / Object) |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch08_heads
python multicam_fusion.py
```

출력 (참고):
```
8 cameras 3×64×64 → BEV 융합 후 3 헤드:
  lane     : [1, 4, 32, 32]
  obj_cls  : [1, 10, 32, 32]
  obj_reg  : [1, 4, 32, 32]
  sign     : [1, 20]
파라미터 : 40.4 K
```

## 학습 포인트 (도서 본문)

1. **공유 백본 = 8× 효율** (8.2 절) — 카메라마다 다른 가중치를 쓰지 않고 *공유* 백본으로 8 카메라를 같은 방식으로 처리. 메모리·연산·학습 데이터 효율 8배.
2. **BEV 융합이 정답** (8.3 절) — 카메라별 출력을 따로 후처리하지 않고, *공통 BEV 공간* 에 모은 다음 그 위에서 헤드를 돌림. 카메라 간 일관성 자동 보장.
3. **헤드는 ch05 와 같음** (8.4 절) — Lane 분할, Object 검출, Sign 분류. 백본·융합만 8 카메라로 확장.

## 다음

- [ch05 단일 카메라 HydraNet](../ch05_hydra/) — 단일 카메라 버전과 비교
- [ch24 Mini HydraNet 풀 학습](../ch24_mini_hydra/) (M3) — BDD100K + YOLOv8 로 실제 학습
