# 11장. Control Net — 스티어링·가속·제동의 뉴럴 출력

> **학습 목표**
> 이 장을 마치면 Planning과 Control의 역할 분리를 이해하고, 차량 동역학의 기본 모형인 Bicycle Model을 자신의 말로 설명할 수 있다. PID, Pure Pursuit, MPC, Neural Controller 각각의 강점과 한계를 비교하고, 실무에서 가장 안전하게 쓰이는 **Residual NN** 구조가 왜 선호되는지 이해한다. 100km/h의 고속에서 Control 루프 지연이 얼마나 결정적인지도 수치로 감을 잡는다.

---

## 11.1 Planning과 Control — 같은 일을 하는 것 아닌가

처음 자율주행을 공부하는 이가 자주 헷갈리는 지점이 Planning과 Control의 경계다. 둘 다 "차가 어떻게 움직일지"를 결정하는 일처럼 보이기 때문이다. 구분의 열쇠는 **시간 축과 추상 수준**에 있다.

Planning은 6초 정도의 미래를 보고, "어느 차선으로, 어떤 곡률의 궤적으로 이동할 것인가"라는 비교적 추상적인 결정을 내린다. 결과물은 일련의 waypoint들이다. Control은 그 waypoint들을 따라가기 위해 **지금 이 순간** 스티어링을 몇 도 돌리고, 가속 페달을 몇 퍼센트 밟고, 브레이크를 얼마만큼 눌러야 하는지를 결정한다. 시간 단위가 다르다. Planning은 100~500ms 주기로 갱신되는 반면, Control은 10~50ms 주기로 훨씬 빠르게 돌아간다.

이 분리 덕에 각 모듈은 자신의 강점을 최대한 활용할 수 있다. Planning은 상황 이해와 전략 수립에 집중하고, Control은 빠르고 안정적인 추종에 집중한다. 물론 End-to-End 접근이 이 경계를 모호하게 만들고 있지만, 2026년 현재 상용 시스템에서는 여전히 둘이 분리되어 있으며 Control은 상대적으로 "학습보다 물리"가 지배하는 영역이다.

---

## 11.2 Bicycle Model — 4륜 자동차를 2륜으로 단순화하는 이유

자동차는 4개의 바퀴를 갖고 있지만, 제어 수학에서는 보통 앞바퀴 하나와 뒷바퀴 하나만 있는 **Bicycle Model**로 단순화한다. 이 단순화가 놀랍도록 잘 작동한다. 이유는 자동차의 대부분의 조향 동작이 좌우 대칭이고, 뒷바퀴가 구동/조향되지 않는 한 그 운동을 하나의 점으로 취급해도 무방하기 때문이다.

Bicycle Model의 상태는 네 변수다. 차량의 평면 위 위치 (x, y), 방향각 θ, 그리고 속도 v다. 입력은 두 개의 변수, 조향각 δ와 가속도 a다. 차량의 길이에 해당하는 휠베이스 L은 차종마다 다른 상수다(Model 3의 경우 2.875m). 운동 방정식은 익숙한 형태다.

```
ẋ = v · cos(θ)
ẏ = v · sin(θ)
θ̇ = (v / L) · tan(δ)
v̇ = a
```

이 네 식이 Control 설계의 출발점이 된다. 이보다 정밀한 모델도 있다(Dynamic Bicycle Model은 타이어 마찰과 횡력까지 고려한다). 그러나 저속에서는 위 간단한 모델로 충분하고, 복잡도를 높일지의 결정은 주행 속도와 요구 정밀도에 따라 달라진다.

---

## 11.3 고전 컨트롤러들 — PID, Pure Pursuit, MPC

Control의 고전적 세 축은 PID, Pure Pursuit, 그리고 MPC다.

**PID**는 모든 제어 수업의 첫 주제다. 제어 목표(target)와 현재 값(measurement)의 차이(error)에 비례하고, 그 적분에 비례하고, 그 미분에 비례하는 세 항의 합으로 제어 입력을 낸다. 단순하고 튼튼하다. 자율주행에서는 차선 추종의 가로(lateral) 제어에 **Stanley Controller**라는 변종이 자주 쓰인다. Stanley는 PID의 사상을 유지하되 차선으로부터의 거리 오차와 방향각 오차를 분리해 가중한다.

**Pure Pursuit**은 기하학적 컨트롤러다. 경로 위의 "미리 바라볼 점(look-ahead point)"을 정한 뒤, 그 점을 향해 핸들을 꺾는 각도를 단순한 기하로 계산한다. 저속 주차, 간단한 차선 추종에서 많이 쓰인다. 직관적이고 튜닝이 쉽다. 단점은 빠른 동역학에서 불안정해진다는 것이다.

**MPC(Model Predictive Control)** 는 현대 고급 컨트롤러의 표준이다. 미래 N 스텝의 제어 입력 시퀀스를 최적화 문제로 풀되, 차량 동역학 모델을 제약으로 건다. 매 스텝마다 이 최적화를 **다시 계산**하는 것이 핵심이다(Receding Horizon). 이 방식의 장점은 제약 조건(최대 속도, 최대 조향각, 장애물과의 거리)을 자연스럽게 다룰 수 있다는 것이다. 계산량이 크지만, 고성능 컨트롤러에서 가장 자주 선택된다. Tesla는 HW3 시절까지 MPC와 PID의 조합을 썼고, HW4 이후에도 MPC는 Safety Cage의 Fallback 역할로 남아 있다.

---

## 11.4 Neural Controller — 뉴럴로 저수준 제어?

여기서 자연스러운 의문이 든다. "궤적 추종 같은 잘 정의된 문제는 PID/MPC로 이미 잘 풀리는데, 굳이 뉴럴을 써야 하나?" 답은 몇 가지 구체적 상황에 있다.

첫째, 고속에서 타이어와 노면의 비선형 마찰, 적재 변화에 따른 관성 분포 같은 물리는 Bicycle Model이 제대로 잡지 못한다. 이 영역에서 데이터로 학습된 모델이 잔차를 메울 수 있다. 둘째, 여러 센서(IMU, 휠속, 조향각)의 캘리브레이션 오차를 **공동 학습**으로 흡수할 수 있다. 셋째, Planner와 Controller를 **한 네트워크로 묶으면** gradient가 이어져 종단 최적화가 가능해진다. End-to-End FSD의 Neural Planner가 이미 Control 결정까지 함께 내리는 셈이다.

그러나 안전이 최우선인 자율주행에서 **순수한 Neural Controller**는 거의 없다. 대신 실무는 **Residual NN** 구조를 선호한다. 물리 기반 컨트롤러가 기본값을 내고, 그 위에 신경망이 작은 보정값을 덧얹는다.

```
δ_total = δ_MPC + α · δ_neural
a_total = a_MPC + α · a_neural
```

계수 α는 처음에는 0.1 같은 작은 값에서 시작해, 검증 데이터에서 안전성이 보장되면 단계적으로 올린다. 이 구조는 신경망의 이득과 물리 컨트롤러의 안전성을 동시에 취하는 합리적 절충이다.

---

## 11.5 Drive-by-Wire — 신호가 실제 바퀴를 돌리기까지

Control의 결정 δ, a가 일단 나오면, 그 신호는 차량의 **CAN 버스**를 통해 실제 액추에이터에게 전달된다. 스티어링은 EPS(Electric Power Steering)에 각도 명령을 내고, 가속은 전기 모터 토크 명령, 제동은 iBooster나 eBooster 같은 전자식 브레이크 시스템의 유압 명령으로 변환된다. Tesla는 브레이크에 일부 EHB(Electro-Hydraulic Brake)를 쓴다고 알려져 있다.

이 신호 체계는 자동차 제조사의 영역이다. 일반 개발자가 일상적으로 만지는 일은 드물다. CARLA 같은 시뮬레이터나 openpilot 같은 애프터마켓 플랫폼에서 개념적으로 접하는 정도가 보통이다. 그러나 "우리 시스템의 궤적이 실제로 어떻게 바퀴를 돌리는가"를 이해하는 것은 엔지니어의 사려 깊은 설계에 도움이 된다. 특히 지연과 대역폭의 물리적 한계 — CAN 버스는 초당 수천 개의 메시지만 안정적으로 나를 수 있다 — 가 설계 제약으로 작용한다.

---

## 11.6 지연과 안정성 — 100km/h의 150ms

Control 루프의 지연이 주행 안전에 미치는 영향은 생각보다 크다. 100km/h로 달리는 차량이 1초에 이동하는 거리는 약 27.8m다. 이 값에 루프 지연을 곱하면 그 지연 동안의 위치 오차가 된다. 지연이 10ms면 28cm, 50ms면 1.4m, 100ms면 2.8m, 150ms면 무려 4.2m다. 제어 신호가 실제 바퀴까지 닿는 동안 차가 이미 차선 하나를 넘어가 버릴 수도 있다는 뜻이다.

그래서 자율주행 시스템은 모듈마다 **지연 예산**을 엄격히 관리한다. IMU 루프는 500Hz 이상의 고속으로 돌고, 스티어링과 제동은 100Hz의 중속으로, 경로 재계획은 10Hz 정도의 저속으로 움직인다. 각 모듈이 제때 결과를 내지 못하면 전체 체인이 망가진다. 임베디드 실시간 시스템의 엄격한 설계 원칙이 자율주행에도 그대로 적용된다.

Control 루프의 설계 원칙은 몇 가지로 요약된다. 지연을 **예산화**하고, 각 스텝에서 그 예산을 넘지 않도록 코드를 짜고, 예산을 넘는 순간 **즉시 로그**를 남긴다. 실 차량의 인프라에서는 이를 위한 전용 RTOS(Real-Time OS)와 결정적 스케줄링이 쓰인다. 학생 프로젝트에서는 Linux의 PREEMPT_RT 패치나 ROS2의 실시간 실행기가 최소한의 근사가 될 수 있다.

---

## 11.7 간단한 실습 — Pure Pursuit과 Residual NN

MentorPi 같은 저속 플랫폼에서 Pure Pursuit와 Residual NN을 결합한 컨트롤러를 만들어 보는 것이 개념 이해에 가장 좋다.

```python
import numpy as np
import torch
import torch.nn as nn

def pure_pursuit(path, ego, L=2.875, lookahead=8.0):
    dists = np.linalg.norm(path - ego[:2], axis=1)
    idx_ahead = np.searchsorted(np.cumsum(np.diff(dists, prepend=0)), lookahead)
    idx_ahead = min(idx_ahead, len(path) - 1)
    target = path[idx_ahead]
    dx, dy = target - ego[:2]
    alpha = np.arctan2(dy, dx) - ego[2]
    delta = np.arctan2(2 * L * np.sin(alpha), lookahead)
    return delta

class ResidualControl(nn.Module):
    def __init__(self):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(16, 64), nn.SiLU(),
            nn.Linear(64, 64), nn.SiLU(),
            nn.Linear(64, 2),
        )
    def forward(self, state_feat):
        return self.mlp(state_feat)
```

실제 사용 흐름은 이렇다. Pure Pursuit가 δ_pp와 기본 가속도 a_base를 낸다. Residual NN이 상태 특징을 받아 (δ_res, a_res)를 낸다. 최종 출력은 두 신호를 가중합한 값이다. α를 0.3에서 시작해, 검증에서 안전이 보장되면 단계적으로 올린다.

---

## 장말 정리

Control은 Planning의 마지막 1km다. Bicycle Model을 기반으로 한 PID·Pure Pursuit·MPC의 고전 컨트롤러가 여전히 주력이며, 신경망은 그 위에 Residual로 얹히는 형태가 가장 안전한 실무 관행이다. Drive-by-Wire의 실제 구현은 OEM 영역이지만, 그 개념적 체계를 이해해야 지연과 대역폭의 한계 위에서 설계가 가능하다. 100km/h에서의 100ms는 2.8m의 위치 오차를 의미하는 만큼, 지연 예산 관리는 Control 설계의 생명선이다.

## 연습문제

1. 시속 100km/h 주행에서 Control 루프 지연이 50ms일 때 위치 오차와 안정성에 미치는 영향을 수치로 계산하라.
2. Neural Controller가 MPC를 완전히 대체하지 못하는 근본적 이유를 세 가지 들라.
3. Residual NN의 계수 α를 0.3에서 0.6으로 늘릴 때, 어떤 검증 단계를 거쳐야 하는지 체크리스트를 만들라.
