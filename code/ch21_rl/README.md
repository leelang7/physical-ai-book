# Chapter 21 · RL 은 왜 "주 무기" 가 아닌가

도서 **21장** *"강화학습은 왜 '주 무기' 가 아닌가 — 모방 위에 얹는 보조 도구로"* 와 1:1 연결.

책의 입장을 **코드 실행 결과로 명백히 시연**:

- **Pure REINFORCE**: 처음부터 신경망 정책을 RL 로 학습 → 불안정
- **Residual RL**: 결정적 PD 컨트롤러 위에 작은 잔차만 RL 로 학습 → 안정

## 스크립트

| 파일 | 내용 |
|---|---|
| [`reinforce_residual.py`](reinforce_residual.py) | 같은 1D 차량 환경 + 같은 400 episode + 같은 학습률. Pure REINFORCE vs Residual RL on PD 누적 보상 비교 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch21_rl
python reinforce_residual.py
```

## 실측 결과 (CPU 1~2분)

```
실험 1: Pure REINFORCE 400 episodes
  최종 50 ep 평균 누적 보상: -5502 ± 1181

실험 2: Residual RL (PD + 잔차) 400 episodes
  최종 50 ep 평균 누적 보상:  -220 ± 99

개선폭: +5282  (보상 25배, 안정성 12배)
```

같은 환경, 같은 episode 수. 차이는 *"NN 이 행동 전체를 학습하느냐 vs 잔차만 학습하느냐"* 뿐.

## 학습 포인트 (도서 본문)

1. **Pure RL 의 한계** (21.2 절) — Sample 효율이 처참. 시뮬레이터에서 100만 step 굴려도 *실 차량* 한 시간 분량 안 됨. Reward shaping 도 한 달은 깎아야 함.
2. **Residual RL 의 안정성** (21.4 절) — 베이스라인(PD·BC) 이 *최악의 행동* 을 막아주고, NN 은 *"여기서 살짝만 더"* 의 잔차만 학습. 안전 + 학습 효율 둘 다.
3. **본 데모는 1D toy** — 실차에선 더 큰 격차. Tesla / Wayve / Comma.ai 도 *모방학습 + (드물게) 잔차 RL* 패턴이지 *pure RL* 은 안 씀.

## Residual RL 핵심 코드

```python
class ResidualPolicy(nn.Module):
    def forward(self, state, pd_action):
        delta = self.delta_net(state) * 0.5      # 잔차 ±0.5
        mean = (pd_action + delta).clamp(-3, 3)  # 베이스라인 + 잔차
        return Normal(mean, std)
```

PD 출력을 mean 의 시작점으로 → NN 잔차가 그 위에 작은 분산만 추가.

## 다음

- [ch20 BC + DAgger](../ch20_bc_dagger/) — IL (RL 의 *진짜 주 무기*)
- [ch11 Control](../ch11_control/) — PD + Residual NN (supervised 잔차)
- [ch22 VLA](../ch22_vla/) — Vision-Language-Action 통합
