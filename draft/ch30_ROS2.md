# 30장. ROS2로 올리는 자율주행 · 로보틱스 스택

> **학습 목표**
> 이 장을 마치면 ROS2 Humble의 기본 구조(노드, 토픽, 서비스, 액션, 수명 주기 노드)를 산업 현장의 언어로 이해하고, 앞선 장들에서 만든 비전·계획 모듈을 **ROS2 노드**로 감싸서 MentorPi·CARLA·Isaac Lab 세 환경에서 동일한 인터페이스로 돌릴 수 있게 된다. Tesla가 ROS를 쓰지 않는다는 점을 알면서도, 왜 독자가 ROS2를 배워야 하는지에 대한 답도 함께 얻는다.

---

## 30.1 왜 ROS2를 배워야 하는가 — Tesla는 안 쓰는데

먼저 해소해야 할 오해가 있다. Tesla는 ROS를 쓰지 않는다. 회사가 초창기부터 자체 메시징 시스템과 커스텀 런타임을 구축해왔고, 성능·실시간성·보안상의 이유로 이 결정을 계속 유지한다. openpilot 역시 ROS가 아니라 자체 `cereal`+`zmq` 기반으로 움직인다(26장). 이렇게만 보면 "Tesla 책에 ROS2 장이 왜 필요한가" 하는 의문이 자연스럽다.

답은 이렇다. 당신이 Tesla에 취업할 확률은 매우 낮고, 당신이 **Tesla가 아닌 어디선가** 자율주행·로보틱스 업무를 하게 될 확률은 매우 높다. 현대차그룹, Boston Dynamics, 삼성 Harman, 42dot, 네이버 랩스, 레인보우로보틱스, 그리고 이 분야에서 일어나는 거의 모든 오픈소스 연구는 **ROS2 Humble** 또는 **Jazzy**를 공용 미들웨어로 쓴다. Waymo와 Cruise 내부 시스템은 비공개이지만, 핵심 개념(토픽·메시지·시간 동기화)은 ROS와 거의 동형이다. ROS2를 이해하지 못하면 코드베이스 하나를 읽어 나가는 것조차 힘들다. 이 책이 Tesla를 축으로 잡으면서도 ROS2 장을 두는 이유가 여기에 있다.

또 하나의 이유는 **교육 효과**다. 앞선 29개 장에서 우리는 비전 모델, 예측 모듈, Neural Planner, Control 같은 조각들을 각자의 Python 스크립트로 만들었다. 이 조각들을 하나의 **실행되는 시스템**으로 묶으려면 반드시 미들웨어가 필요하다. ROS2는 그 공정을 강제로 배우게 하는 훌륭한 도구다. 파일로 데이터를 주고받는 어설픈 방식에서 벗어나, 노드끼리 실시간 메시지로 통신하는 감각을 익히는 것이 이 장의 부가 목적이다.

---

## 30.2 ROS2 Humble의 마음속 모델

ROS2를 잘 쓰려면 아키텍처의 머릿속 모델을 한 번 올바르게 세워두는 것이 관건이다. ROS1에서 ROS2로 넘어오면서 가장 크게 바뀐 부분은 **중앙 마스터(roscore)의 제거**와 **DDS(Data Distribution Service) 미들웨어의 도입**이다. ROS1에서는 하나의 마스터가 모든 노드를 등록하고 주소록을 관리했다. 마스터가 죽으면 전체가 무너졌다. ROS2는 DDS 위에서 노드가 서로를 **직접** 찾는다. 마스터가 없고, 발행자와 구독자가 네트워크 상에서 알아서 만난다. 이 차이가 실시간성·내고장성·보안에서 큰 의미를 갖는다.

ROS2의 기본 단위는 **노드(Node)** 다. 각 노드는 하나의 독립 프로세스이며, 자기 일만 한다. 카메라 드라이버 노드가 이미지를 읽어 `/camera/image_raw` 토픽에 퍼블리시하면, 차선 감지 노드가 그걸 구독해서 `/lane/markings`를 내보낸다. Planning 노드가 다시 그걸 받아 `/planned_trajectory`를 퍼블리시하고, 컨트롤 노드가 최종적으로 `/cmd_vel`을 차량 드라이버에게 넘긴다. **노드 하나가 하나의 일만 하고, 토픽이 그들 사이의 파이프가 된다.** 이 단순한 구조가 대규모 시스템의 유지보수성을 결정적으로 높인다. Tesla 내부 시스템도 사상은 비슷하다. 이름만 cereal·zmq·자체 스케줄러일 뿐, "노드·메시지·QoS"라는 삼각 구조는 동형이다.

토픽 외에도 동기 요청이 필요한 경우를 위한 **서비스**(Request/Reply)와, 시간이 걸리는 작업을 위한 **액션(goal/feedback/result)** 이 있다. 그리고 ROS2가 특히 신경 써서 설계한 **수명 주기 노드(Lifecycle Node)** 가 있다. 이는 노드가 Unconfigured → Inactive → Active → Finalized 같은 상태를 명시적으로 갖게 하는 기능이다. 자율주행처럼 "일단 초기화만 해두고, 사용자가 스위치를 눌러야 실제 제어를 시작하는" 시스템에 자연스럽게 들어맞는 추상이다.

---

## 30.3 실전 — 카메라 노드와 차선 감지 노드를 쓴다

이 장은 ROS2 의 **설치**가 아니라 **활용**에 집중한다. ROS2 Humble 설치 절차와 워크스페이스 설정은 23장(개발 환경 구축) 에 이미 정리되어 있으므로, 그 위에서 바로 노드를 띄우는 이야기로 들어간다.

이 장의 첫 실습은 29장의 MentorPi 위에서 진행한다. 먼저 카메라 노드를 띄운다. `v4l2_camera` 패키지는 ROS2 Humble에서 가장 안정적인 USB 카메라 드라이버이고, MentorPi의 Pi Camera와 USB 웹캠 모두를 다룬다. 런치 파일은 다음과 같이 간결하다.

```python
# launch/bringup_camera.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='camera',
            parameters=[{
                'video_device': '/dev/video0',
                'image_size': [1280, 720],
                'pixel_format': 'YUYV',
            }],
            remappings=[('image_raw', '/camera/image_raw')],
        ),
    ])
```

이 런치를 돌리면 `/camera/image_raw`에 초당 30프레임의 이미지가 흐르기 시작한다. 이걸 받아 차선을 감지하는 노드를 하나 짠다. 이 노드가 앞선 장에서 만든 차선 감지 모델을 감싸는 얇은 래퍼다.

```python
# src/lane_detector_node.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseArray, Pose
from cv_bridge import CvBridge
import torch
from my_lane_model import MiniLaneHead   # 8장에서 쓴 모델

class LaneDetectorNode(Node):
    def __init__(self):
        super().__init__('lane_detector')
        self.bridge = CvBridge()
        self.model = MiniLaneHead().cuda().eval()
        self.sub = self.create_subscription(Image, '/camera/image_raw',
                                            self.on_image, 10)
        self.pub = self.create_publisher(PoseArray, '/lane/markings', 10)

    def on_image(self, msg: Image):
        img = self.bridge.imgmsg_to_cv2(msg, 'rgb8')
        tensor = preprocess(img).unsqueeze(0).cuda()
        with torch.no_grad():
            points = self.model(tensor)[0].cpu().numpy()
        out = PoseArray()
        out.header = msg.header
        for x, y in points:
            p = Pose(); p.position.x = float(x); p.position.y = float(y)
            out.poses.append(p)
        self.pub.publish(out)

def main():
    rclpy.init()
    rclpy.spin(LaneDetectorNode())

if __name__ == '__main__':
    main()
```

이 작은 예제가 보여주는 것은 중요하다. **8장에서 만든 딥러닝 모델이 코드는 단 20줄 남짓의 ROS 래퍼만으로 산업 시스템의 구성원이 된다.** 이 래퍼를 쓰는 순간, 같은 모델이 MentorPi에서도, CARLA 시뮬에서도, Isaac Lab에서도 돌아간다. 입력 토픽 주소만 바꾸면 된다.

---

## 30.4 시간 동기화와 QoS — 실수로 망가뜨리지 않기

ROS2로 처음 시스템을 올리는 사람이 거의 예외 없이 부딪히는 두 가지 함정이 있다. 하나는 **시간 동기화**, 다른 하나는 **QoS(Quality of Service) 설정**이다.

시간 동기화부터 보자. 자율주행은 본질적으로 여러 센서의 데이터를 **같은 시점의 세계**로 해석해야 하는 문제다. 카메라는 30Hz, LiDAR는 10Hz, IMU는 200Hz. 각각의 메시지 헤더에는 발생 시각(stamp)이 찍혀 있고, 하류 노드는 그 스탬프를 기준으로 데이터를 정렬해야 한다. ROS2는 `message_filters` 라이브러리로 이를 돕는다. 두 개 이상의 토픽을 대략 같은 시각의 짝으로 동기화해 콜백을 호출해주는 `ApproximateTimeSynchronizer`가 가장 많이 쓰이는 도구다. 8장의 Lane/Sign/Object 헤드를 동시에 돌리며 "같은 프레임에서의 결과만 합쳐야 하는" 상황이 바로 이 동기화의 실사용 예다.

QoS는 더 까다롭다. ROS2는 DDS 위에서 메시지의 **신뢰성**(reliable vs best-effort), **히스토리**(keep-last vs keep-all), **큐 깊이**, **내구성**(volatile vs transient-local)을 각각 설정할 수 있다. 카메라 이미지 같은 고대역 데이터는 `BEST_EFFORT + KEEP_LAST 1`이 맞고, 제어 명령 같은 중요 메시지는 `RELIABLE + KEEP_LAST 10`이 맞다. 이걸 반대로 설정하면 이미지는 네트워크가 막혀서 재전송되다 타임아웃이 나고, 제어 명령은 유실되어 차량이 엉뚱한 순간에 움직인다. 저자는 수업에서 QoS를 잘못 건 채로 "왜 우리 로봇이 갑자기 1초간 멈췄다 움직이는가"를 몇 시간 추적한 학생을 매 학기 한두 명씩 본다. 이 두 가지는 **개념을 먼저 이해하고** 실수를 피하는 것이 유일한 치료법이다.

---

## 30.5 시뮬과 실물의 같은 인터페이스 — 이 장의 결정적 미덕

30장을 이 책에 넣는 가장 큰 이유가 여기에 있다. 잘 설계된 ROS2 인터페이스 위에서는, **MentorPi 실물, CARLA 시뮬, Isaac Lab 환경이 거의 같은 코드로 동작한다.** 이 "같은 인터페이스"가 자율주행·로보틱스 엔지니어링의 생산성 비결이다.

저자의 교육 과정에서 확인된 구체적인 흐름은 이렇다. 학생은 먼저 CARLA 시뮬에서 차선 감지 + Neural Planner + Control을 ROS2 노드 조합으로 만든다. 토픽은 `/camera/image_raw`, `/lane/markings`, `/planned_trajectory`, `/cmd_vel`이다. 이 조합이 시뮬에서 잘 돌면, 같은 노드들을 MentorPi로 옮긴다. 바뀌는 것은 **카메라 드라이버 노드 하나**와 **컨트롤 변환 노드 하나** 뿐이다. CARLA의 ROS 브리지가 내보내는 토픽 이름과, MentorPi의 v4l2 카메라가 내보내는 토픽 이름이 같도록 리매핑만 해두면, 중간의 인식·계획 노드들은 **단 한 줄도 고치지 않고** 그대로 돌아간다. 이게 전부다.

이 경험을 한 번 해 본 학생은 인터뷰에서 "저는 자율주행 소프트웨어를 한 번 처음부터 끝까지 만들어 봤습니다"라고 말할 수 있다. 실제로 그렇다. 소규모지만, Tesla 스택의 축소판을 **미들웨어 수준**에서 올려 본 것이다. 이 경험의 가치가 ROS2 장을 넣은 가장 큰 이유다.

---

## 30.6 고급 주제 — Nav2, Autoware Universe, 그리고 그 너머

소형 자율주행의 경우, 책 한 장만으로 처음부터 끝까지 다 만들기는 현실적이지 않다. 다행히 ROS2 생태계에는 두 개의 거대한 기반 스택이 있다. 로보틱스 내비게이션용 **Nav2**와, 자율주행 전용의 **Autoware Universe**가 그것이다.

Nav2는 SLAM으로 지도를 만들고, 전역 경로를 Dijkstra나 Theta\*로 계획하며, 국소 경로를 DWB 같은 고전 컨트롤러로 따라가는 완성된 내비게이션 프레임워크다. MentorPi에 LiDAR가 있으면 Nav2로 "방을 스스로 돌아다니는 로봇"을 반나절 안에 띄울 수 있다.

Autoware Universe는 일본 Tier IV 주도로 만들어지고 The Autoware Foundation이 관리하는 완성도 높은 **오픈소스 자율주행 스택**이다. Perception·Localization·Planning·Control 전 영역을 ROS2 노드 조합으로 제공한다. 실제 차량에 장착되는 스택이기 때문에 아키텍처의 품질이 대단히 높다. 이 장에서 만든 작은 노드들을 Autoware의 인터페이스 규격에 맞춰 교체해 넣으면, 그 자체로 작은 자율주행 스택이 된다. 저자가 책 후반 공개 예정인 확장 실습(`physical-ai-book/ext_autoware/`)이 이 작업을 단계별로 안내한다.

그 외에 ROS2 생태계에는 이미지 전송 최적화를 위한 `image_transport`, 동적 파라미터 관리를 위한 `parameter_server`, 로깅·리플레이를 위한 `rosbag2`, GUI 디버깅 도구인 `rqt`와 `rviz2`가 있다. 이 도구들을 순서대로 자기 손에 익히는 것이 30장 이후의 자기 학습 숙제다.

---

## 30.7 이 장이 끝난 뒤 당신이 할 수 있는 것

30장이 끝나면 독자는 세 가지 일을 할 수 있다. 첫째, 앞선 28개 장에서 만든 모든 Python 모델을 **ROS2 노드**로 감싸서 산업 표준 미들웨어 위에 올릴 수 있다. 둘째, **동일한 코드**로 MentorPi 실물·CARLA 시뮬·Isaac Lab을 넘나들며 실험을 이어 갈 수 있다. 셋째, **Autoware Universe** 같은 대형 오픈소스 스택을 읽어 내려갈 때 당황하지 않고, 필요한 부분만 교체해 자기 아이디어를 시험해 볼 수 있다.

Tesla는 ROS를 쓰지 않는다. 그러나 당신이 일할 곳은 십중팔구 ROS2를 쓴다. 이 장에서 얻은 도구가 당신의 다음 커리어 5년을 받쳐줄 가장 견고한 기반이 될 것이다.

---

## 장말 정리

ROS2는 Tesla가 쓰지 않는 도구지만, Tesla 바깥의 거의 모든 자율주행·로보틱스 현장에서 **공통 언어**다. 노드·토픽·서비스·액션·수명 주기라는 다섯 개념이 이 생태계의 뼈대이며, 시간 동기화와 QoS가 초보자의 가장 흔한 함정이다. 잘 설계된 ROS2 인터페이스 위에서는 MentorPi·CARLA·Isaac Lab이 **같은 코드로** 움직이며, 이 경험이 자율주행 엔지니어로서의 "처음부터 끝까지 만들어 봤다"는 자부심을 만든다.

## 연습문제

1. "카메라가 BEST_EFFORT QoS를 쓰는 게 왜 맞는가"와 "제어 명령이 RELIABLE QoS를 쓰는 게 왜 맞는가"를 각각 한 문단으로 서술하라. 반대로 설정했을 때 발생할 구체적 사고 시나리오를 덧붙여라.
2. 수명 주기 노드(Lifecycle Node)가 일반 노드보다 자율주행에 유리한 이유 3가지를 산문으로 서술하라.
3. 본인이 30.5절의 "시뮬 → 실물 이식"을 직접 해 본다고 가정하고, 바꿔야 하는 노드 2개와 그 이유를 자신의 말로 설명하라.
