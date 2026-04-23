# 26장. openpilot 리버스 엔지니어링

> **학습 목표**
> 이 장을 마치면 Comma.ai의 openpilot이 어떤 구조로 움직이는지 모듈 수준에서 설명할 수 있게 된다. Tesla FSD와 openpilot을 직접 비교하면서 두 시스템의 공통점과 차이점을 이해하고, openpilot의 핵심 모델인 supercombo.onnx를 파이썬에서 로드해 입출력을 탐색해 본다. 실제 차량 적용의 법적·안전 고려사항도 함께 짚는다.

---

## 26.1 openpilot이 특별한 이유

레스토랑 셰프의 세계에 비유해 보면 이해가 쉽습니다. 유명 셰프는 자기 **시그니처 레시피** 를 공개하지 않습니다. 메뉴판에 *"진한 소고기 육수"* 라고만 적혀 있고, 어떻게 몇 시간을 우려냈는지는 주방장 머릿속에만 있죠. 자율주행도 같습니다. Tesla · Waymo · Mobileye 모두 소스 코드는 영업비밀 금고에 넣어 둡니다. 그런 세계에서 *"내 레시피 전부 공개합니다. 심지어 레스토랑 차리시려면 매뉴얼도 드릴게요"* 라고 선언한 이상한 셰프가 있습니다. Comma.ai 가 2016년부터 공개해 온 **openpilot** 이 그 존재입니다.

자율주행은 대부분의 업체에서 비공개다. Tesla, Waymo, Mobileye 모두 소스 코드를 공개하지 않는다. 그런 세계에서 **오픈소스로 공개된 실전 ADAS 시스템**이 하나 있다. San Diego의 스타트업 Comma.ai가 2016년부터 개발해 온 **openpilot**이다. GitHub의 `github.com/commaai/openpilot` 저장소에서 누구나 소스를 읽을 수 있고, 라이선스가 MIT라 학습과 연구에 자유롭게 쓸 수 있다.

openpilot이 지원하는 차량은 2026년 기준 200종이 넘는다. 현대·기아 차량 다수를 포함한다. comma 3X라는 자체 하드웨어나 comma devkit으로 실제 차량에 연결되며, 고속도로 차선 유지와 스마트 크루즈 컨트롤을 주된 기능으로 한다. Tesla FSD만큼 도심 자율 주행은 지원하지 않지만, 고속도로에서는 놀라울 만큼 부드럽게 동작한다.

이 장이 openpilot을 다루는 이유는 분명하다. **Tesla FSD를 공개적으로 엿볼 수 있는 유일한 창구**이기 때문이다. 구조의 철학, 모델의 입출력, 계획과 제어의 분담이 Tesla의 그것과 놀랄 만큼 닮았다. openpilot을 한 번 뜯어 본 개발자는 이 책의 앞 장들에서 배운 개념들이 **실제 코드로 어떻게 구현되는지**를 구체적으로 확인한 사람이 된다.

---

## 26.2 전체 아키텍처 — 메시지 버스로 연결된 모듈들

openpilot의 구조를 한 번에 그려 보면 다음과 같다. 카메라(road, wide, driver 세 대)가 영상을 캡처해 `modeld`라는 모듈에 전달한다. `modeld`가 신경망 모델을 돌려 경로·차선·선행 차량·의도 같은 예측을 생성한다. 이 예측이 `controlsd`로 전달되고, `controlsd` 안의 Planner와 Controller가 조합되어 최종 CAN 메시지가 만들어진다. 이 메시지가 `pandad`를 통해 차량의 CAN 버스로 송신된다. EPS는 스티어링을 받고, 엔진 제어 유닛은 가속과 제동을 받는다.

```
[Cameras] → modeld → [Path, Lane, Lead, Desire, Meta]
                           │
                           ▼
              [controlsd — Planner + Controller]
                           │
                           ▼
                 [pandad — CAN 송신]
                           │
                           ▼
              [Vehicle (EPS, AEB, ACC)]
```

각 모듈은 **독립 프로세스**로 돌아가며, 메시지 버스를 통해 통신한다. 이 메시지 버스가 30장에서 다룬 ROS2와 비슷한 철학이지만, ROS를 쓰지 않는다는 점이 특이하다. openpilot은 자체 라이브러리 `cereal`(메시지 스키마)과 `zmq`(전송)를 조합해 자기만의 가벼운 메시징 시스템을 만들었다. 자동차 환경의 실시간성과 경량성에 특화된 선택이다. Tesla의 내부 시스템도 공개되지는 않았지만, 이와 비슷하게 ROS를 쓰지 않는 자체 미들웨어를 운용한다. 두 회사의 비슷한 선택이 산업적 맥락을 시사한다.

---

## 26.3 supercombo.onnx — openpilot의 뇌

openpilot의 핵심 신경망은 `supercombo.onnx`라는 단일 파일이다. 약 70MB 크기의 ONNX 모델로, 모든 공개 저장소에서 다운로드할 수 있다. 이 모델 하나가 차선·경로·선행 차량·의도·속도 예측을 **한 번의 forward pass에** 모두 출력한다. 5장에서 본 HydraNet의 공개 버전이라 할 만하다.

입력은 현재 프레임과 직전 프레임의 광각·표준 두 카메라 영상이다. 출력은 여러 갈래로 나뉜다. Path는 여러 후보 궤적이고, Lane은 좌우 차선의 파라미터, Lead는 선행 차량의 ID와 거리·속도, Desire는 운전자의 차선 변경 의도, Meta는 장기적인 속도와 조향의 예측이다. 이 출력 구조가 Tesla FSD의 Vector Space 개념과 매우 유사하다.

이 모델을 파이썬에서 로드하는 것은 어렵지 않다.

```python
import onnx
import onnxruntime as ort

m = onnx.load("supercombo.onnx")
for inp in m.graph.input:
    print(inp.name, [d.dim_value for d in inp.type.tensor_type.shape.dim])
```

이 짧은 코드만으로 supercombo의 입력 시그니처를 볼 수 있다. 여러 개의 입력 텐서가 있는데, 카메라 이미지 외에도 이전 프레임의 히든 상태가 포함된다. Recurrent한 구조를 띄고 있다는 뜻이다. 이 반복 구조가 시간적 일관성을 유지하는 기제다.

---

## 26.4 FSD와의 비교 — 공통점과 격차

openpilot과 Tesla FSD를 나란히 놓고 비교하면 많은 것이 드러난다. 카메라 수에서 먼저 차이가 난다. openpilot은 3대(road 광각·표준, driver 모니터링용), FSD는 8대다. Occupancy Network의 유무가 결정적 차이다. openpilot은 Occupancy가 없고 2D 기반의 Vector 출력에 머무른다. FSD는 3D Occupancy를 생성 모델의 핵심 자원으로 삼는다. 데이터 규모도 비교할 수 없이 다르다. openpilot은 커뮤니티 기반의 수십만 마일, FSD는 수억 마일 단위다.

계획 단계의 차이도 크다. openpilot은 파라메트릭 경로 출력과 MPC 기반 컨트롤러의 고전적 조합이다. FSD v12 이후는 End-to-End 신경망이 계획과 제어의 일부까지 대체한 단계에 있다. 차선 변경도 openpilot에서는 운전자의 방향지시등 조작으로 시작되는 반면, FSD는 차량이 스스로 판단한다.

이 격차에도 불구하고 openpilot의 구조적 철학은 FSD의 **한 세대 앞 선배**에 해당한다. openpilot을 공부해 두면 FSD의 많은 부분이 익숙해진다. 오픈소스의 가치는 이 "가르치는 선배"로서의 역할에 있다.

---

## 26.5 코드 읽기 — 추천하는 순서

openpilot 저장소는 방대하다. 처음 보면 어디서부터 읽어야 할지 막막하다. 저자가 수업에서 제시하는 순서는 이렇다.

첫째, `cereal/log.capnp`에서 시작한다. 이 파일이 openpilot의 모든 메시지 스키마를 정의한다. 어떤 데이터가 어떤 구조로 오가는지를 한 번 보면 전체 시스템의 인터페이스가 눈에 들어온다. Capnproto 문법은 Protocol Buffer와 비슷하니 처음 보는 사람도 금방 읽을 수 있다.

둘째, `selfdrive/modeld/modeld.py`를 읽는다. 모델 추론을 담당하는 모듈인데, ONNX 모델을 어떻게 로드하고 입력을 어떻게 준비하며 출력을 어떻게 발행하는지가 담겨 있다. 우리 실습의 모델 래퍼와 비교하면 구조가 놀랄 만큼 비슷하다.

셋째, `selfdrive/controls/controlsd.py`를 읽는다. 상위 제어 로직이다. modeld의 출력을 받아 Planner와 Controller로 넘기는 흐름이 여기에 있다. 함수 이름이 서술적이라 읽기 어렵지 않다.

넷째, `selfdrive/controls/lib/longitudinal_mpc_lib/`를 읽는다. 종방향(가속·제동) MPC의 실제 구현이다. 11장에서 개념으로 다룬 MPC가 자동차 환경에서 어떻게 구체화되는지를 볼 수 있다. 상태 벡터의 구성, 비용 함수의 가중치, 제약 조건의 처리가 모두 담겨 있다.

이 네 파일을 이해하면 openpilot의 80%가 이해된다. 나머지 20%는 차량별 어댑터와 UI다.

---

## 26.6 실습 — supercombo 모델을 직접 돌려 보기

가장 교육적인 실습은 supercombo를 로드해 더미 입력으로 돌려 보는 것이다. 모델의 입출력 시그니처가 생생히 드러난다.

```python
import onnxruntime as ort
import numpy as np

sess = ort.InferenceSession("supercombo.onnx",
                            providers=["CUDAExecutionProvider"])

for inp in sess.get_inputs():
    print(inp.name, inp.shape)

dummy = {}
for i in sess.get_inputs():
    shape = [d if isinstance(d, int) else 1 for d in i.shape]
    dummy[i.name] = np.random.randn(*shape).astype(np.float32)

outs = sess.run(None, dummy)
for o, v in zip(sess.get_outputs(), outs):
    print(o.name, v.shape)
```

이 코드가 성공적으로 돌면, supercombo의 입력에 어떤 텐서들이 들어가고 출력이 어떤 모양인지를 직접 확인할 수 있다. 다음 단계는 실제 주행 영상을 입력에 맞는 포맷으로 변환해서 의미 있는 출력을 얻는 것이다. Comma.ai 공식 저장소에 샘플 주행 영상과 전처리 스크립트가 있으니 참고하면 된다.

CARLA에서 찍은 영상으로 supercombo를 돌려 보는 실험도 재미있다. Tesla의 실 도로 데이터로 학습된 모델이 CARLA의 합성 영상에서 어떻게 동작하는지를 관찰하면, 14장의 Sim2Real Gap이 얼마나 현실적인 문제인지 생생하게 느낄 수 있다.

---

## 26.7 한국 환경에 맞게 커스터마이징하기

openpilot을 한국에서 쓰려면 몇 가지 현지화가 필요하다. 버스 전용 차선과 가변 차로는 Lane 후처리에 특별한 로직이 필요하고, 한국 차선의 색 패턴(흰색과 황색이 다른 의미)을 활용하려면 Lane 모델을 재학습해야 하는 경우도 있다. 한국의 좁은 이면도로와 무단횡단 보행자에 대한 대응도 글로벌 모델의 약점이다.

해결 방법은 두 가지다. 첫째, 기존 모델 위에 한국 데이터를 추가해 fine-tune하는 접근이다. comma.ai는 자사 모델의 학습 데이터를 100% 공개하지는 않지만, 파이프라인은 공개된다. 둘째, CARLA로 한국형 교차로·다차로 시나리오를 증강 생성해 fine-tune하는 접근이다. 두 방법을 조합하면 글로벌 openpilot 대비 한국 도로에서 눈에 띄게 안정적인 버전이 만들어진다.

실제로 국내 개발자 커뮤니티에서 **한국형 openpilot 포크**가 있다. 중국 커뮤니티에도 비슷한 포크가 있다. 오픈소스의 장점이 이 지역 특화에 있다. Tesla의 FSD가 한국 도로에 완전히 적응하려면 본사의 결정이 필요하지만, openpilot은 누구나 만질 수 있다.

---

## 26.8 실 차량 적용 — 법적 주의

이 장을 마무리하며 빠뜨릴 수 없는 경고가 있다. **실제 차량에 openpilot을 장착해 공도에서 운용하는 것은 법적·안전적 위험을 동반한다**. 한국에서는 자율주행차법이 임시운행 허가 없이 공도에서 자율 기능을 쓰는 것을 제한한다. 차량의 ADAS를 임의로 개조하는 것도 주의해야 한다. comma 3X 설치 자체가 위법은 아니지만, 그 기능을 공도에서 사용한 중 사고가 나면 책임은 전적으로 운전자에게 있다.

저자는 교육 맥락에서 openpilot을 **코드를 읽고, 시뮬레이터에서 돌려 보며, 개념을 익히는 용도**로만 권한다. 실 차량 적용은 개인의 판단이지만, 반드시 사전에 법적 상황과 보험 영향을 확인해야 한다. 자율주행의 안전은 물리적 문제이므로, 호기심과 책임은 분리될 수 없다.

---

## 장말 정리

openpilot은 공개된 실전 ADAS 시스템으로, Tesla FSD의 공학적 구조를 엿볼 수 있는 가장 가까운 창구다. supercombo 하나의 모델이 차선·경로·선행 차량·의도를 한 번에 출력하고, controlsd가 이를 MPC 기반 제어로 변환한다. 카메라 수와 Occupancy의 유무, End-to-End 깊이에서 FSD와 차이가 있지만, 구조적 철학은 놀랄 만큼 닮았다. 코드를 읽고 supercombo를 돌려 보는 경험이 FSD 이해를 한 단계 깊게 만든다. 실 차량 적용은 법적 주의가 필수다.

## 연습문제

1. supercombo의 입력 텐서들이 각각 무엇을 의미하는지 추정해 짧은 설명을 붙여 보라. 카메라 프레임, 이전 히든 상태, 차량 상태 같은 가능성을 고려하라.
2. openpilot과 FSD의 기술적 격차 세 가지와, 그것을 좁히기 위해 필요한 요소 세 가지를 대응시켜라.
3. 본인이 운전하는 한국 차종이 openpilot에 지원되는지 확인하고, 지원되지 않는다면 가장 가까운 지원 차종을 보고하라.
