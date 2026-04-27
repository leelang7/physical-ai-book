# Chapter 09 · TinyPred — 다중 모달 궤적 예측

도서 **9장 *"다중 에이전트 궤적 예측 (Prediction)"*** 와 1:1 로 연결되는 실습 코드. MultiPath++ 의 정신적 축소판입니다.

## 이 디렉토리의 스크립트

| 파일 | 다루는 내용 |
|---|---|
| [`tiny_pred.py`](tiny_pred.py) | 과거 1초 → 미래 3초, K=3 후보 + 점수 헤드. Winner-takes-all 손실로 200 step 학습 후 검증 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch09_pred
python tiny_pred.py
```

## 본 데모가 보여 주는 것

학습이 끝나면 한 입력에 대한 K=3 후보의 3초 후 끝점 (x, y) 를 출력합니다. 예를 들어:

```
mode 0 (w=1.00) : 끝점 (x, y) = (-0.03, +14.93)   # 직진
mode 1 (w=0.00) : 끝점 (x, y) = (-1.99, +0.0)     # 좌회전
mode 2 (w=0.00) : 끝점 (x, y) = (+1.49, +0.0)     # 우회전
```

세 끝점이 서로 다른 x 값을 갖는 것 → **궤적 다중 모달 학습 성공**.

다만 점수 가중치(w) 가 한 모드에 1.00 으로 쏠려 있다면 — **score collapse** 입니다. 후보들은 *"왼쪽·직진·오른쪽"* 으로 잘 갈라졌지만, 점수 헤드가 *"무조건 직진"* 만 골라 버리는 함정. 도서 9.5 절이 이 문제를 다룹니다.

## 학습 포인트 (도서 본문 참조)

1. **단일 평균의 함정** (9.3 절) — 학습 데이터에 좌·우 회피가 섞여 있을 때 단일 출력 모델의 평균은 *"직진"* 입니다. K=3 후보 + 점수 구조로 풀어냅니다.
2. **Winner-Takes-All 의 약점** (9.4 절) — *"가장 가까운 후보만 학습"* 패턴은 궤적 다중 모달은 잘 배우지만, **점수 다양성** 은 잘 못 배웁니다. 본 데모도 이 약점을 그대로 보여 줍니다.
3. **현실 모델의 보강** (9.5 절) — MultiPath++ 는 (a) 사전 anchor 궤적, (b) 보조 다양성 손실(diversity loss), (c) 점수 헤드를 위한 별도 회귀 정답을 추가해 collapse 를 막습니다. 이 디렉토리의 다음 노트북에서 다룰 예정 (M3).

## 다음 단계

- **anchor 기반 학습** — 24개의 사전 궤적 anchor 위에서 잔차만 학습 (M3 추가)
- **MultiPath++ 풀 구현** — Waymo Open Motion 데이터셋 사용 (M3 추가)
- **계획과의 연동** — 9장의 예측이 10장 Neural Planner 에 어떻게 입력되는지 → [`code/ch10_planner/`](../ch10_planner/)

## 영상 · 이슈

- YouTube : *"All That AI · Tesla Book Ch.09"* (영상 누적 시 채널 검색)
- 이슈 / 질문 : https://github.com/leelang7/physical-ai-book/issues
