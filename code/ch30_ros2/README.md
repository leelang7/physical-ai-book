# Chapter 30 · ROS2 — Humble 기반 노드 패턴

도서 **30장** *"ROS2 로 올리는 자율주행 · 로보틱스 스택"* 와 1:1 연결.

ch29 의 MentorPi 단일 파이프라인을 **ROS2 노드 5개로 분할** 한 패턴.
ROS2 Humble + Ubuntu 22.04 별도 설치 필요. 본 디렉토리는 *골격 + 설치 가이드*.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`ros2_node_skeleton.py`](ros2_node_skeleton.py) | Publisher / Subscriber / Control / Launch / QoS 5 패턴 일괄 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch30_ros2
python ros2_node_skeleton.py   # 골격 출력만
```

## ROS2 Humble 설치 (Ubuntu 22.04)

```bash
# 1) ROS2 Humble 데비안 패키지 설치
sudo apt update && sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
    | sudo tee /etc/apt/sources.list.d/ros2.list
sudo apt update && sudo apt install -y ros-humble-desktop python3-colcon-common-extensions

# 2) 환경 활성화
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# 3) 패키지 빌드 + 실행
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python mentorpi_pkg
# 본 디렉토리의 코드를 src/mentorpi_pkg/mentorpi_pkg/ 에 복사
cd ~/ros2_ws && colcon build --packages-select mentorpi_pkg
source install/setup.bash
ros2 launch mentorpi_pkg bringup.launch.py
```

## 5 가지 노드 패턴

1. **Publisher** — 카메라 → `/camera/image_raw` (30 Hz timer)
2. **Subscriber + Republisher** — `/camera` → BEV 변환 → `/bev_image`
3. **Control** — `/bev_image` → 차선 검출 → `/cmd_vel`
4. **Launch file** — 4 노드 한 번에 실행
5. **QoS** — 실시간 제어 (`BEST_EFFORT`) vs 로깅 (`RELIABLE`) 패턴

## 학습 포인트

1. **노드 분할 = 디버깅 용이** (30.2 절) — 한 파일 (ch29 mentorpi_pipeline.py) → 5 노드. 각자 독립 프로세스. 한 노드만 죽어도 시스템 계속 동작.
2. **Topic = 비동기 메시지** (30.3 절) — Publisher 가 Subscriber 를 직접 알 필요 X. ROS2 미들웨어가 매칭. *카메라가 1대든 N대든 같은 코드*.
3. **QoS 가 실시간 안정성 결정** (30.5 절) — Best Effort = 빠름 + 데이터 손실 OK (제어), Reliable = 느림 + 손실 없음 (로깅). 잘못 고르면 *부하 상황에서 차량이 멈춤*.

## 다음

- [ch29 MentorPi 통합 파이프라인](../ch29_mentorpi/) — 본 노드들의 *단일 파일 원본*
- [ch27 Isaac Lab](../ch27_isaac_lab/) — Isaac 시뮬레이션 → 본 ROS2 노드 그대로 이식 가능
