# Chapter 12 · Fleet Data Trigger 와 Edge Case Miner

도서 **12장** *"플릿 데이터 수집과 Trigger 디자인"* 와 1:1 연결.

대규모 차량 데이터에서 *학습에 가치 있는* 소수 프레임만 골라내는 패턴.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`trigger_miner.py`](trigger_miner.py) | 200 프레임 합성 로그 + 4 종 trigger (불일치 / 급제동 / 급가속 / 고속 조향) |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch12_trigger
python trigger_miner.py
```

## 결과 (참고)

```
총 200 프레임, 진짜 edge case 약 16개 (~8%)
T1_disagreement     : 20+ 프레임
T2_sudden_brake     : ~10
T3_sudden_accel     : ~10
T4_highspeed_steer  : ~5
중복 제거 총: ~30~50 (15~25%)
Recall ~70~90% / Precision ~30~50%
```

## 학습 포인트

1. **데이터 *양* 이 아니라 *희소성*** (12.2 절) — Tesla 가 8M 차량 굴려도 99% 는 평범한 직진 → 학습에 의미 X. *모델이 틀린* 1% 만 라벨링·학습.
2. **Trigger 설계가 데이터 엔진의 핵심** (12.4 절) — Tesla 는 100 종 이상 trigger 운영. 본 데모는 4 종 뼈대.
3. **Precision vs Recall 트레이드오프** (12.5 절) — Recall 높이면 라벨링 비용 ↑, Precision 높이면 놓치는 edge ↑. 양쪽 균형이 미너 디자인의 art.

## 다음

- [ch13 Auto-labeling](../ch13_autolabel/) — Trigger 로 모은 프레임 자동 라벨링
- [ch20 BC + DAgger](../ch20_bc_dagger/) — DAgger 도 본질적으로 trigger + 라벨링
