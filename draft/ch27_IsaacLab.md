# 27장. Isaac Lab으로 Physical AI 에이전트 학습

> **학습 목표**
> 이 장을 마치면 NVIDIA Isaac Lab 환경에서 사족보행 에이전트를 GPU 병렬 시뮬레이션으로 학습시켜 본 경험을 갖게 된다. 사전 학습된 VLA 모델인 OpenVLA를 가상 팔로봇에 연결하는 방법을 익히고, Domain Randomization을 실전에 적용한다. 21장에서 다룬 강화학습의 한계를 이 실습에서 **자기 손으로** 체감한다.

---

## 27.1 Isaac Lab — NVIDIA의 로봇 학습 플랫폼

2021년 NVIDIA가 공개한 Isaac Gym은 로봇 강화학습의 판도를 바꾼 도구였다. 수만 개의 시뮬레이션 환경을 GPU에서 병렬로 돌려, 사족보행 학습 시간을 4시간에서 10분으로 줄였다. 2024년 NVIDIA는 이를 **Isaac Lab**으로 개편해 Omniverse Kit과 PhysX 5, Warp을 통합한 현대적 프레임워크로 확장했다. 공식 지원 로봇에는 ANYmal, Spot, Go2, Franka, Allegro, H1, GR00T 등이 포함된다. 자율주행이 아닌 Physical AI를 공부하는 데 가장 완성도 높은 환경이다.

Isaac Lab의 핵심 가치는 **GPU 병렬성**에 있다. 한 GPU에서 4096~16384개의 환경이 동시에 돌아가고, 각 환경에서 서로 다른 초기 조건이나 외란을 시뮬레이션한다. 이 병렬성이 Domain Randomization을 실질적으로 가능하게 한다. 21장에서 언급한 Sim2Real 전략의 핵심 자원이 여기서 비로소 구체화된다.

설치는 23장에서 안내한 대로다. 이 장에서는 이미 설치가 완료되어 있다는 가정에서 출발한다.

---

## 27.2 첫 실험 — Unitree Go2 사족보행

Isaac Lab의 내장 예제 중 가장 교육적인 것이 Unitree Go2의 거친 지형 보행 학습이다. 한 줄의 명령으로 시작할 수 있다.

```bash
./isaaclab.sh --python source/standalone/workflows/rl_games/train.py \
    --task Isaac-Velocity-Rough-Unitree-Go2-v0 \
    --num_envs 4096 --headless
```

`--num_envs 4096`이 병렬 환경의 수다. RTX 4090 기준 이 설정에서 약 30분 안에 안정적인 거친 지형 보행이 수렴한다. RTX 3060 정도면 환경 수를 2048로 줄여야 메모리가 맞는다. 수렴 속도는 환경 수에 거의 비례한다.

학습 중에 Tensorboard로 지표를 모니터링한다. 가장 중요한 지표는 **에피소드 평균 보상**이다. 보상이 오르다가 정체되고, 간혹 떨어지는 패턴이 정상이다. 떨어지는 구간은 정책이 새로운 전략을 탐색하는 신호다. 저자의 수업에서 학생이 가장 자주 묻는 질문이 "보상이 떨어지는데 학습을 중단해야 하나요"인데, 답은 "아니오"다. 안정적 상승은 수십만 스텝이 지나서야 보인다.

---

## 27.3 커스텀 태스크 만들기 — 장애물 회피

내장 예제를 돌려본 뒤의 자연스러운 다음 단계는 커스텀 태스크 제작이다. Isaac Lab의 환경은 `TaskEnv` 또는 `ManagerBasedRLEnv`의 서브클래스로 정의된다. 세 가지를 정의해야 한다. 관측 공간, 행동 공간, 보상 함수.

관측 공간은 로봇의 관절 각도와 속도, 몸체 자세, IMU 신호, 그리고 주변 장애물 정보다. 행동 공간은 관절 목표 각도 또는 토크 명령이다. 보상 함수는 태스크의 목적을 수치화한 것이다. "목표 방향으로 전진", "장애물로부터 일정 거리 유지", "몸체 안정성"의 세 항을 가중합한 형태가 기본이다.

```python
import omni.isaac.lab.envs as envs

class ObstacleTask(envs.ManagerBasedRLEnv):
    def reset(self):
        ...
    def step(self, action):
        ...
    def _get_obs(self):
        ...
    def _get_reward(self):
        ...
```

실제 구현의 디테일은 Isaac Lab 공식 가이드를 따르는 것이 가장 안전하다. 이 장에서 강조하고 싶은 점은 **보상 설계의 어려움**이다. 초보자는 보상을 희박하게 주는 실수를 자주 한다. 목표 도달 시에만 +1을 주는 보상은 수렴하지 않는다. 중간 단계의 부분 성공에도 작은 보상을 주고, 위험 행동에는 작은 페널티를 주어야 한다. **Curriculum Learning**이 또 다른 해법이다. 처음에는 쉬운 환경에서 시작하고, 에피소드 성공률이 일정 수준을 넘으면 난이도를 올린다. 이 점진적 접근이 복잡한 태스크의 학습을 가능하게 한다.

---

## 27.4 OpenVLA 연결 — 언어로 로봇 조종하기

Isaac Lab의 Franka 팔 환경에 22장의 OpenVLA를 연결해 보는 실험은 이 장의 절정이다. 자연어 명령으로 가상 로봇을 조종할 수 있다.

```python
from transformers import AutoModelForVision2Seq, AutoProcessor
import torch
import numpy as np

processor = AutoProcessor.from_pretrained("openvla/openvla-7b")
model = AutoModelForVision2Seq.from_pretrained(
    "openvla/openvla-7b", torch_dtype=torch.bfloat16
).to("cuda")

def vla_policy(image_rgb, instruction):
    inputs = processor(images=image_rgb, text=instruction,
                       return_tensors="pt").to(model.device)
    action = model.predict_action(**inputs,
                                  unnorm_key="bridge_orig")
    return action  # 7D end-effector delta
```

이 함수를 Isaac Lab의 Franka 환경의 제어 루프에 끼워 넣으면 된다. 주의할 점은 OpenVLA의 추론 시간이다. 7B 파라미터 모델이므로 한 번의 forward pass에 수십 ms가 걸린다. 실시간 제어에 그대로 쓰면 움직임이 뚝뚝 끊긴다. 해결책이 22장에서 언급한 **System 1 / System 2 분리**다. OpenVLA(System 2)가 0.5초마다 고수준 end-effector 목표를 정하고, 작은 PD 컨트롤러(System 1)가 1kHz로 그 목표를 추종한다. 이 분리가 자연스러운 움직임을 만든다.

이 실습의 교육적 가치는 크다. "AI에게 말로 시키고, 로봇이 그 말을 해석해 움직이는" 한 순간을 자기 환경에서 만들어 본 경험이 이후의 학습 전체에 영향을 준다. 저자의 수강생 중 한 분이 이 실습을 마친 뒤 "로봇공학이 처음으로 내 일처럼 느껴졌다"고 말한 적이 있다.

---

## 27.5 Domain Randomization을 실전에 적용하기

21장에서 이론으로 다룬 Domain Randomization을 Isaac Lab에서 구체화해 보자. 물리 파라미터를 매 에피소드마다 무작위로 변경하는 방식이 가장 기본이다.

```python
def randomize_physics(env):
    env.scene["robot"].root_physx_view.set_masses(
        env.scene["robot"].data.default_mass *
        (0.8 + 0.4 * torch.rand_like(env.scene["robot"].data.default_mass))
    )
```

이 예는 로봇의 질량을 기본값의 80%에서 120%까지 흔든다. 비슷한 방식으로 마찰 계수, 모터의 토크 한계, 센서 노이즈 수준을 모두 무작위화할 수 있다. Isaac Lab은 이 무작위화를 위한 `EventTerm`이라는 기능을 제공한다. 선언적으로 "이 이벤트는 매 에피소드 시작 시에 이 파라미터를 이 범위에서 흔든다"고 기술하면 된다.

Domain Randomization의 효과는 학습 중에는 잘 드러나지 않는다. 보상이 더 천천히 오른다. 무작위화가 없는 환경보다 수렴이 느린 것이 당연하다. 그러나 **실제 로봇에 이식했을 때** 효과가 나타난다. 무작위화 없이 학습한 정책은 실물에서 즉시 넘어지지만, 잘 설계된 Domain Randomization으로 학습한 정책은 실물에서도 안정적으로 걷는다. 이 장에서 실물 로봇으로 이식하는 부분까지 실습하기는 어렵지만, 시뮬레이션 안에서도 이식성을 추정할 수 있다. 학습된 정책을 학습에 없던 파라미터 조합(더 넓은 마찰 범위)에서 평가하는 방식이다.

---

## 27.6 Humanoid H1 — Optimus의 원리 맛보기

시간과 하드웨어가 허락한다면 Unitree H1 보행도 시도할 만하다. 사족보행보다 확실히 어렵다. 이족보행은 균형이 훨씬 예민하다.

```bash
./isaaclab.sh --python source/standalone/workflows/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-H1-v0 \
    --num_envs 4096 --headless --max_iterations 3000
```

RTX 4090에서 약 2시간 안에 평지 보행이 안정화된다. 이 H1 정책의 원리가 Optimus의 보행 제어에 가장 가깝다. Tesla Optimus의 공식 오픈소스는 없지만, H1이 그 원리의 대리인 역할을 한다. 이 학습을 돌려 보면 19장의 제어 3계층 구조가 왜 필요한지, 이족보행의 ZMP 안정화가 얼마나 민감한지가 머리가 아니라 눈으로 이해된다.

---

## 27.7 Isaac Lab의 한계 — 무엇이 여전히 어려운가

냉정하게 Isaac Lab의 한계도 짚어야 한다. 접촉 모델링은 여전히 완전하지 않다. 손가락으로 섬세하게 물체를 집는 작업은 시뮬에서와 실물에서 차이가 크다. 촉각 시뮬레이션도 기본 지원이 약하다. 손끝 압력 센서를 모델링하려면 별도 확장이 필요하다. 실 로봇으로의 이식도 Domain Randomization만으로 완전하지 않다. System Identification과 Adaptive Policy가 추가로 필요하다.

이런 한계들이 이 장의 실습이 "완성된 Physical AI"를 만들어 주지 못하는 이유다. 그러나 "처음부터 끝까지 Physical AI 에이전트를 학습시켜 본 경험"의 가치는 분명하다. 어떤 모듈이 어떻게 연결되는지, 어디서 막히고 어디서 풀리는지를 한 번이라도 만져 본 사람은 논문을 읽을 때도 완전히 다른 시선을 갖게 된다.

---

## 장말 정리

Isaac Lab은 GPU 병렬 시뮬레이션의 현대적 표준이다. Go2의 거친 지형 보행, Franka + OpenVLA로 언어 기반 조종, H1의 이족 보행까지 한 장 안에서 시도해 볼 수 있다. Domain Randomization이 실전 이식의 핵심이며, System 1 / System 2 분리가 VLA의 실시간성 한계를 푸는 열쇠다. 접촉 모델링과 촉각 시뮬레이션의 불완전함이 여전히 남은 과제이지만, 이 실습의 경험이 Physical AI 학습의 본격적 출발점이 된다.

## 연습문제

1. Go2의 거친 지형 환경에서 성공률이 80%에서 더 오르지 않을 때, Curriculum Learning을 어떻게 설계할지 단계별로 제안하라.
2. OpenVLA의 추론 지연을 줄이기 위한 세 가지 기법(양자화·증류·System 1/2 분리)의 효과를 수치로 예상하라.
3. Isaac Lab에서 "한국 주방 환경에서 쌀통의 쌀을 그릇에 담기"라는 태스크를 설계한다면, 관측·행동·보상을 각각 어떻게 정의할지 서술하라.
