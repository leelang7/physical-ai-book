# Chapter 07 · BEV(Bird's-Eye View) 와 Vector Space

도서 **7장** *"BEV(Bird's-Eye View) 변환과 Vector Space"* 와 1:1 연결.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`learned_ipm.py`](learned_ipm.py) | 고전 IPM (homography) 의 한계 + Learned IPM (cross-attention 으로 BEV 직접 생성) — BEVFormer 핵심 메커니즘의 축소판 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch07_bev
python learned_ipm.py
```

출력 (참고):
```
== 고전 IPM (참고용 좌표 예시) ==
  4점 매핑 + 한계 안내

== Learned IPM (신경망 attention) ==
  입력 카메라 특징 : [1, 64, 28, 28]
  BEV 출력         : [1, 64, 32, 32]
  파라미터         : 78.0 K
```

## 학습 포인트 (도서 본문)

1. **고전 IPM 의 한계** (7.2 절) — 지면 평탄 가정. 오르막·범프·카메라 흔들림에서 정확도 급락. `cv2.getPerspectiveTransform` 만 쓰면 곡선 도로에서 차선이 휘어 보임.
2. **BEVFormer 의 공간 attention** (7.4 절) — BEV 그리드 셀이 *"내가 어떤 픽셀을 봐야 할까"* 학습. Cross-attention 의 query = BEV cell, key/value = 이미지 픽셀.
3. **Vector Space 의 의미** (7.5 절) — Tesla 의 *"vector space"* 는 단순 BEV 가 아니라 차선·표지·차량·보행자가 *벡터 객체* 로 표현된 통합 공간. 본 데모는 BEV 그리드까지만.

## 다음

- [ch08 8 카메라 BEV 융합](../ch08_heads/) — 8 카메라 → 단일 BEV 통합
- ch06 Occupancy 와의 비교: BEV = 2D 평면, Occupancy = 3D 부피
