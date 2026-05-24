# Chapter 11 · Control Net — Bicycle + Pure Pursuit + Residual NN

도서 **11장** *"Control Net — 스티어링·가속·제동의 뉴럴 출력"* 와 1:1 연결.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`bicycle_pursuit.py`](bicycle_pursuit.py) | 자전거 운동 모델 + Pure Pursuit (기하학적 경로 추종) + 잔차 학습용 NN — 사인파 경로 200 step (20s) 시뮬레이션 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch11_control
python bicycle_pursuit.py
```

출력 (참고):
```
200 step (20s) 시뮬레이션 완료
최종 위치   : x=150.6m  y= 16.7m  yaw=-27.5°  v=13.0m/s
고전 조향 평균: +0.034 rad
잔차 조향 평균: -0.040 rad  (미학습 NN — 임의값)
```

## 학습 포인트 (도서 본문)

1. **Bicycle 모델** (11.2 절) — 자동차 운동학의 표준 단순화. 휠베이스 L · 조향 · 가속 4 변수로 (x, y, yaw, v) 상태를 진화. 충분히 정확하고 미분 가능.
2. **Pure Pursuit** (11.3 절) — 가장 단순한 경로 추종. *Lookahead* 거리만큼 앞의 경로 점을 향한 조향각을 기하학적으로 계산. 결정적·해석 가능.
3. **Residual NN** (11.5 절) — 고전 제어가 *못 잡는* 부분만 신경망이 보정. *"100% NN 대체"* 가 아니라 *"고전 + 잔차"*. 안전성과 학습 효율 모두 챙김. Tesla 도 ABS·전자제어장치 위에 NN 잔차를 얹는 구조.

## 잔차 크기 제한

```python
self.register_buffer("scale", torch.tensor([0.05, 0.5]))  # ±0.05rad, ±0.5m/s²
```

잔차 NN 의 출력 범위를 *작게 제한* 해서 고전 제어를 크게 흔들지 못하게. 학습이 잘못돼도 안전 마진 확보.

## 다음

- [ch10 Neural Planner](../ch10_planner/) — Planner 가 만든 궤적을 본 Control 이 추종
- [ch20 BC + DAgger](../ch20_bc_dagger/) (M3) — 잔차 NN 의 실제 학습은 모방학습 + DAgger 로
