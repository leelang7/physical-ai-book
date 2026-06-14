# Chapter 13 · Auto-labeling — Pseudo-Label

도서 **13장** *"Auto-labeling — 사람 없이 라벨을"* 와 1:1 연결.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`pseudo_label.py`](pseudo_label.py) | two-moons toy + 100 라벨 baseline + 3 라운드 pseudo-labeling (confidence > 0.9) |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch13_autolabel
python pseudo_label.py
```

## 결과 (참고)

```
Baseline (100 라벨)        : 98.8%
+pseudo 라운드 1 (958)     : 98.4%
+pseudo 라운드 2 (1918)    : 98.0%
+pseudo 라운드 3 (2869)    : 98.2%
```

two-moons 가 이미 쉬워서 baseline 98.8%. 진짜 학습 효과는 *어려운 데이터* + *작은 라벨* 일 때 더 큼.

## 학습 포인트

1. **Pseudo-label 의 기본 원리** (13.2 절) — 작은 라벨로 학습한 teacher → 무라벨에 추정 → 확신 높은 것만 학습 데이터에 추가 → 반복.
2. **Confidence 필터링의 중요성** (13.3 절) — 낮은 confidence pseudo-label 은 오히려 모델을 망침. 보통 0.9 이상만 사용.
3. **Tesla Auto-labeler 의 진짜 비밀** (13.5 절) — 단순 self-training 이 아니라 *오프라인 LiDAR 모델* 같은 더 강한 teacher 활용. 카메라 모델은 student. 본 데모는 self-training 단순화.

## 다음

- [ch12 Trigger](../ch12_trigger/) — Auto-labeling 입력 데이터 선별
- [ch20 BC + DAgger](../ch20_bc_dagger/) — DAgger 도 pseudo-label 의 일종 (전문가가 teacher)
