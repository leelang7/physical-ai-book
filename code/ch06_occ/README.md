# Chapter 06 · Occupancy Network — 3D 점유 공간을 박스 없이

도서 **6장** *"Occupancy Network — 3D 점유 공간을 박스 없이"* 와 1:1 연결.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`mini_occupancy.py`](mini_occupancy.py) | Lift-Splat-Shoot 축소판 — 2D 이미지 특징 → 3D voxel 점유 확률 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch06_occ
python mini_occupancy.py
```

출력 (참고):
```
입력 특징    : [1, 64, 28, 28]
Voxel 점유   : [1, 32, 32, 8]  (X×Y×Z = 32×32×8)
파라미터     : 17.0 K
```

## 학습 포인트 (도서 본문)

1. **박스 없는 표현** (6.2 절) — Tesla 가 객체 검출(bbox) 의존을 줄이고 *공간 점유* 자체를 학습. 트럭 뒤에 매달린 사다리, 떨어진 매트리스 같은 *"객체 카테고리에 없는 장애물"* 도 잡힘.
2. **Lift-Splat-Shoot** (6.3 절) — 픽셀마다 *깊이 분포* 를 예측 → 3D voxel 에 가중 분배 → voxel별 점유 분류. 카메라만으로 LiDAR 같은 3D 표현 만들기.
3. **본 데모는 단일 카메라 가짜 입력** — 실제는 8 카메라 + 카메라 외부 파라미터 필요. 진짜 학습은 [ch25](../ch25_mini_occ/) (M3) 에서 nuScenes 로.

## 다음

- [ch07 BEV](../ch07_bev/) — 평면 BEV vs 부피 Occupancy 비교
- [ch25 Mini Occupancy 풀 실습](../ch25_mini_occ/) (M3)
