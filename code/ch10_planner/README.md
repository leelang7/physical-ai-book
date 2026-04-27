# Chapter 10 · Neural Planner — 비용 함수를 신경망에 녹이기

도서 **10장** 의 실습 코드. *"신뢰는 하되 감시한다"* 라는 10.7 절의 원칙을 가장 단순한 모델 + 룰 기반 안전 필터의 조합으로 구현한다.

## 이 디렉토리의 스크립트

| 파일 | 역할 |
|---|---|
| [`mini_planner.py`](mini_planner.py) | (state)→(steer, accel) 단일 모드 MLP + 다중 모드 `MixtureHead` (10.5 절 *"왼쪽으로 피해? 오른쪽으로 피해?"*) |
| [`safety_cage.py`](safety_cage.py) | 4가지 안전 규칙 (전방 TTC · 차선 이탈 · 조향 jerk · 가속도 한계) 으로 NN 명령을 검열 |
| [`rollout_demo.py`](rollout_demo.py) | 5초 (100 스텝) 가짜 시나리오에서 두 모듈이 협력하는 모습 시연 |

## 실행

```bash
# 환경 활성화
cd code/environment && bash setup.sh && source .venv/bin/activate

# 1) Planner 단독 — 단일 모드 + Mixture 출력 비교
cd ../ch10_planner
python mini_planner.py

# 2) Safety Cage 단독 — 4가지 규칙 시연
python safety_cage.py

# 3) 통합 롤아웃 — Cage 가 NN 의 무모함을 어떻게 막아내는지
python rollout_demo.py
```

`rollout_demo.py` 의 출력에서 *"안전 개입 횟수"* 가 0 보다 크게 나오면, 무작위 초기화된 NN 이 제안한 명령을 Cage 가 안전한 범위로 끌어내렸다는 의미입니다.

## 학습 포인트 (도서 본문 참조)

1. **단일 평균의 함정** (10.5 절) — 학습 데이터에 *"왼쪽 회피"* 와 *"오른쪽 회피"* 가 섞여 있을 때, 단일 모드 MLP 의 출력은 *"직진"* 으로 수렴해 버립니다. `MixtureHead` 의 K 모드 + 점수 구조가 표준 해법.
2. **Safety Cage 는 NN 을 대체하지 않는다** (10.7 절) — 룰 기반 cage 는 NN 의 *"극단적 실수"* 만 잡고, 평상시는 통과시킵니다. 99% 의 케이스에서 NN 이 자유롭게 운전하되, 1% 의 위기 상황에서만 룰이 발동.
3. **TTC 1.0초 라는 숫자** (10.7 절) — 사람의 평균 반응 시간 0.7초 + 제동 거리 보정. 이보다 짧아지면 인간도 못 피하므로 cage 가 강제 감속을 명령합니다.

## 다음 단계 — 학습 가능한 모델로 확장

본 디렉토리는 *임의 초기화* 모델로 데모만 합니다. 실제 학습은 다음 단계에서:

1. **모방 학습** : 인간 주행 로그(예: nuScenes)에서 (state, expert_action) 쌍을 추출 → BC 손실로 학습 ([code/ch20_bc_dagger/](../ch20_bc_dagger/) 와 연계)
2. **Mixture 학습** : 10.5 절의 *"가장 가까운 후보의 점수만 올리는"* winner-takes-all 패턴을 cross-entropy 로 구현
3. **HG-DAgger** : 학습된 NN 이 실수하는 상황만 사람이 라벨링해 추가 학습 (도서 20.5 절)

M3 (~ 2026-07-20) 에 nuScenes 기반 학습 노트북이 본 디렉토리에 추가됩니다.

## 영상 · 이슈

- YouTube : *"All That AI · Tesla Book Ch.10"* (영상 누적 시 채널 검색)
- 이슈 / 질문 : https://github.com/leelang7/physical-ai-book/issues
