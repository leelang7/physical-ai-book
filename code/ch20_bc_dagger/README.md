# Chapter 20 · Behavior Cloning + DAgger

도서 **20장** *"모방 학습과 DAgger — Physical AI 의 첫 길"* 와 1:1 연결.
책의 *"BC + DAgger 가 Physical AI 의 주 무기"* 라는 입장의 가장 작은 시연.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`bc_dagger.py`](bc_dagger.py) | 1D 차량 환경 + PD 전문가 + 학생 NN. BC 단독 학습 vs DAgger 5 라운드 비교 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch20_bc_dagger
python bc_dagger.py
```

출력 (참고):
```
== Behavior Cloning (전문가 데이터 3 에피소드만) ==
  학습 데이터  : 206 쌍
  롤아웃 오차  : 0.057 m  /  성공률 100%

== DAgger 5 라운드 ==
  라운드 1 ~ 5: 오차 0.05~0.09 m, 성공률 60~100%
```

## 학습 포인트 (도서 본문)

1. **분포 이동(distribution shift)** (20.4 절) — BC 의 근본 약점. 전문가 trajectory 의 *상태 분포* 와 학생이 실제 굴렸을 때의 *상태 분포* 가 다름. 학생이 한 번 실수하면 본 적 없는 상태로 빠짐 → 더 큰 실수 → 누적.
2. **DAgger 의 핵심** (20.5 절) — 학생이 *실제로 도달한* 상태에서 *전문가의 정답* 을 라벨링 → 학생의 상태 분포를 학습 데이터에 포함. *"내가 빠질 함정에 미리 가서 물어보기"*.
3. **본 데모는 너무 쉬운 환경** — 1D PD 컨트롤러는 강건해서 BC 만으로도 100% 달성. DAgger 의 수치 우위는 잘 안 보이지만, **구조** (`dagger_loop` 함수의 학생 행동으로 상태 진행 + 전문가 라벨링) 는 그대로 살아있음. 더 어려운 환경 (29장 MentorPi 실증) 에서 진가가 드러남.

## DAgger 의 핵심 코드 (12 줄)

```python
for r in range(n_rounds):
    for _ in range(n_eps_per_round):
        env = CarEnv(...)
        s = env.reset()
        for _ in range(100):
            a_student = model(s).item()      # 학생이 행동 결정
            a_expert  = expert_policy(s)     # 전문가에게 정답 질의
            dataset.append((s, a_expert))    # 데이터셋에 추가
            s, done = env.step(a_student)    # 학생 행동으로 진행
            if done: break
    train(model, dataset)                    # 누적 데이터로 재학습
```

이게 책 20.5 절의 알고리즘 전체. *"환경을 굴리는 행동 = 학생, 라벨 = 전문가"* 가 분포 보정의 핵심.

## 변종 — HG-DAgger / SafeDAgger

도서 20.6 절의 변종들은 본 데모를 확장:

- **HG-DAgger** — 학생 정책의 *불확실한 상태* 에서만 전문가 질의 (전체 step 마다 X)
- **SafeDAgger** — 학생이 *위험한 상태* 에 가면 전문가가 행동 자체를 개입

M3 후반부에 변종 추가 예정.

## 다음

- [ch21 RL](../ch21_rl/) — 강화학습 vs 모방학습 비교 (책 21장: RL 이 *주* 가 아닌 이유)
- [ch29 MentorPi 실증](../ch29_mentorpi/) — 실제 로봇에서 DAgger 적용
