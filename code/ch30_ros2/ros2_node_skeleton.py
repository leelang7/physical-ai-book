"""
ch30 — ROS2 노드 골격 (Humble)

도서 30장 *"ROS2 로 올리는 자율주행 · 로보틱스 스택"* 의 노드 패턴.
ROS2 Humble + colcon 설치 필요. 본 파일은 *구조* 만.

ch29 의 MentorPi 파이프라인을 ROS2 노드로 분할:
  - camera_publisher.py  : /camera/image_raw 발행
  - bev_node.py          : /camera → /bev_image 변환
  - lane_follower.py     : /bev → /cmd_vel
  - joy_dagger.py        : 사람 조이스틱 입력 동시 기록

본 파일은 모든 노드의 *최소 골격* 을 한 번에 모은 형태.
"""
from __future__ import annotations


def show_publisher_node():
    print("""
# camera_publisher.py — 카메라 → 토픽
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        self.publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        self.cap = cv2.VideoCapture(0)  # USB 카메라
        self.bridge = CvBridge()
        self.timer = self.create_timer(1/30, self.publish_frame)  # 30 Hz

    def publish_frame(self):
        ret, frame = self.cap.read()
        if ret:
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            msg.header.stamp = self.get_clock().now().to_msg()
            self.publisher.publish(msg)

def main():
    rclpy.init()
    rclpy.spin(CameraPublisher())
""")


def show_subscriber_node():
    print("""
# bev_node.py — /camera → /bev_image (ch29 의 bev_transform 호출)
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class BevNode(Node):
    def __init__(self):
        super().__init__('bev_node')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.on_image, 10)
        self.pub = self.create_publisher(Image, '/bev_image', 10)

    def on_image(self, msg):
        img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        bev = bev_transform(img)  # ch29 의 함수
        bev_msg = self.bridge.cv2_to_imgmsg(bev, 'bgr8')
        bev_msg.header = msg.header  # 시간 동기화
        self.pub.publish(bev_msg)
""")


def show_control_node():
    print("""
# lane_follower.py — /bev → /cmd_vel
from geometry_msgs.msg import Twist

class LaneFollower(Node):
    def __init__(self):
        super().__init__('lane_follower')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, '/bev_image', self.on_bev, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

    def on_bev(self, msg):
        bev = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        left, right = detect_lanes(bev)         # ch29 함수
        steer = steering_from_lanes(left, right, bev.shape[1])
        cmd = Twist()
        cmd.linear.x = 0.5  # 0.5 m/s 직진
        cmd.angular.z = steer
        self.pub.publish(cmd)
""")


def show_launch_file():
    print("""
# bringup.launch.py — 모든 노드 한 번에 실행
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='mentorpi_pkg', executable='camera_publisher'),
        Node(package='mentorpi_pkg', executable='bev_node'),
        Node(package='mentorpi_pkg', executable='lane_follower'),
        Node(package='mentorpi_pkg', executable='joy_dagger'),
    ])

# 실행:
# ros2 launch mentorpi_pkg bringup.launch.py
""")


def show_qos_pattern():
    print("""
# QoS — 실시간 제어 vs 디버깅 데이터의 차이
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

# 실시간 제어 (지연 < 신뢰성)
realtime_qos = QoSProfile(
    depth=1,
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
)

# 로깅·데이터 수집 (신뢰성 > 지연)
logging_qos = QoSProfile(
    depth=100,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
)

# ch29 의 DAggerLogger 는 logging_qos 로 — 한 프레임도 놓치면 안 됨
""")


def main():
    print("== ch30 ROS2 노드 패턴 — Humble ==\n")
    print("ROS2 환경 (Ubuntu 22.04 + Humble) 없이는 실행 불가.")
    print("본 파일은 *구조* 만 보여줌.\n")

    print("[1] Publisher — 카메라 토픽 발행")
    show_publisher_node()
    print("[2] Subscriber + Republisher — BEV 변환")
    show_subscriber_node()
    print("[3] Control — /cmd_vel 발행")
    show_control_node()
    print("[4] Launch file — 모든 노드 일괄 실행")
    show_launch_file()
    print("[5] QoS — 실시간 vs 로깅 패턴")
    show_qos_pattern()

    print("\n  실제 실행: ROS2 설치 가이드는 README 참조.")


if __name__ == "__main__":
    main()
