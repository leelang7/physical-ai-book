"""
ch29 — MentorPi 비전 자율주행 통합 파이프라인 (CPU 시뮬레이션)

도서 29장 *"MentorPi 로 해보는 비전 자율주행 실증"* 의 핵심 통합 패턴.

실제 MentorPi (HiWonder 소형 로봇) 가 없어도 *파이프라인 전체* 의 코드 구조를
한 파일로 확인. 카메라 입력 → 차선 검출 → 조향 → DAgger 데이터 로깅까지.

전체 흐름:
  1) 카메라 캘리브레이션 (intrinsic + extrinsic mock)
  2) 합성 카메라 프레임 (회색 도로 + 흰 차선)
  3) BEV 변환 (ch07 의 단순 호모그래피)
  4) 차선 검출 (이진화 + 최대 행 합)
  5) 조향 계산 (ch11 의 Pure Pursuit 단순화)
  6) DAgger 로깅 (s, a_student, a_expert) 디스크 저장 형식 시연
"""
from __future__ import annotations
import math
import numpy as np
import cv2


# ---------- 1) 카메라 캘리브레이션 ----------
def mock_calibration() -> dict:
    """체스보드 9×6 으로 캘리브레이션한 결과 (mock 값).

    실제 MentorPi 워크플로:
      1) ROS2 node camera_calibration 실행
      2) 체스보드 보드 들고 20~30 자세 촬영
      3) 자동으로 K, dist 계산
      4) ~/.ros/camera_info/mentorpi_camera.yaml 저장
    """
    K = np.array([
        [320.0,   0.0, 160.0],
        [  0.0, 320.0, 120.0],
        [  0.0,   0.0,   1.0],
    ], dtype=np.float32)
    dist = np.array([-0.12, 0.05, 0.0, 0.0, 0.0], dtype=np.float32)
    # 카메라 → 로봇 좌표 변환 (extrinsic) — 카메라가 로봇 앞쪽 10cm, 위쪽 5cm
    cam_to_robot = np.array([
        [1.0, 0.0, 0.0, 0.10],
        [0.0, 1.0, 0.0, 0.00],
        [0.0, 0.0, 1.0, 0.05],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)
    return {"K": K, "dist": dist, "cam_to_robot": cam_to_robot}


# ---------- 2) 합성 카메라 프레임 ----------
def synthetic_camera_frame(t: float, img_w: int = 320, img_h: int = 240,
                           noise_std: float = 5.0) -> np.ndarray:
    """가짜 도로 + 차선. t (초) 따라 차선이 좌우로 흔들림."""
    img = np.full((img_h, img_w, 3), 80, dtype=np.uint8)  # 회색 도로
    # 좌측 차선 (흰 선)
    offset = int(20 * math.sin(0.5 * t))
    left = img_w // 4 + offset
    right = 3 * img_w // 4 + offset
    cv2.line(img, (left, img_h - 10), (left, img_h // 2), (255, 255, 255), 3)
    cv2.line(img, (right, img_h - 10), (right, img_h // 2), (255, 255, 255), 3)
    # 노이즈
    noise = np.random.normal(0, noise_std, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return img


# ---------- 3) BEV 변환 (단순 호모그래피) ----------
def bev_transform(img: np.ndarray, bev_size: tuple[int, int] = (200, 200)) -> np.ndarray:
    """카메라 영상 → 탑뷰. ch07 의 고전 IPM 와 같은 구조."""
    H, W = img.shape[:2]
    src_pts = np.float32([
        [W // 4, H // 2],    [3 * W // 4, H // 2],
        [0,       H - 1],    [W - 1,       H - 1],
    ])
    dst_pts = np.float32([
        [bev_size[0] // 4, 0],            [3 * bev_size[0] // 4, 0],
        [bev_size[0] // 4, bev_size[1]],  [3 * bev_size[0] // 4, bev_size[1]],
    ])
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    return cv2.warpPerspective(img, M, bev_size)


# ---------- 4) 차선 검출 ----------
def detect_lanes(bev: np.ndarray, brightness_thresh: int = 200) -> tuple[int, int]:
    """BEV 의 하단 1/3 에서 좌·우 차선 x 위치 검출."""
    gray = cv2.cvtColor(bev, cv2.COLOR_BGR2GRAY)
    H, W = gray.shape
    roi = gray[2 * H // 3:, :]  # 하단 1/3
    mask = (roi > brightness_thresh).astype(np.uint8)
    col_sum = mask.sum(axis=0)
    # 좌측 절반에서 최대, 우측 절반에서 최대
    left_x = int(col_sum[:W // 2].argmax()) if col_sum[:W // 2].max() > 0 else -1
    right_x = int(col_sum[W // 2:].argmax() + W // 2) if col_sum[W // 2:].max() > 0 else -1
    return left_x, right_x


# ---------- 5) 조향 (Pure Pursuit 단순화) ----------
def steering_from_lanes(left_x: int, right_x: int, bev_width: int) -> float:
    """두 차선 중심과 BEV 중심의 편차를 기반으로 조향 [-0.5, 0.5] rad."""
    if left_x < 0 or right_x < 0:
        return 0.0  # 차선 못 찾으면 직진
    lane_center = (left_x + right_x) / 2
    bev_center = bev_width / 2
    error = (lane_center - bev_center) / bev_center  # [-1, 1]
    steering = float(np.clip(0.5 * error, -0.5, 0.5))
    return steering


# ---------- 6) DAgger 로깅 ----------
class DAggerLogger:
    """학생 정책으로 굴리면서 전문가 정답을 함께 기록.

    실제 MentorPi 에서는:
      - /camera/image_raw 토픽 구독 → state 저장
      - /joy 토픽으로 사람 조이스틱 입력 받음 → a_expert
      - 학생 NN 의 출력 → a_student
      - 디스크 저장 후 오프라인 학습
    """

    def __init__(self):
        self.entries: list[dict] = []

    def log(self, state: dict, a_student: float, a_expert: float):
        self.entries.append({
            "t": state["t"],
            "left_x": state["left_x"],
            "right_x": state["right_x"],
            "a_student": a_student,
            "a_expert": a_expert,
            "disagreement": abs(a_student - a_expert),
        })

    def summary(self) -> str:
        if not self.entries:
            return "  (no entries)"
        n = len(self.entries)
        disagree = [e["disagreement"] for e in self.entries]
        return (f"  총 {n} 스텝 기록\n"
                f"  학생-전문가 불일치 평균: {np.mean(disagree):.4f} rad\n"
                f"  최대 불일치: {max(disagree):.4f} rad  (DAgger 학습 효과 큰 구간)")


# ---------- 통합 데모 ----------
def main() -> None:
    print("== ch29 MentorPi 비전 자율주행 통합 파이프라인 (CPU 시뮬레이션) ==\n")

    cal = mock_calibration()
    print(f"[1] 카메라 캘리브레이션")
    print(f"    fx={cal['K'][0,0]:.1f}, fy={cal['K'][1,1]:.1f}, cx={cal['K'][0,2]:.1f}, cy={cal['K'][1,2]:.1f}")
    print(f"    cam→robot 변환: {cal['cam_to_robot'][:3, 3]} (m)")

    logger = DAggerLogger()
    n_steps = 50
    dt = 0.1

    print(f"\n[2~6] 50 스텝 (5초) 시뮬레이션 — 카메라 → 차선 → 조향 → DAgger 로깅")
    student_outputs, expert_outputs = [], []
    for i in range(n_steps):
        t = i * dt
        img = synthetic_camera_frame(t)
        bev = bev_transform(img)
        left_x, right_x = detect_lanes(bev)
        a_expert = steering_from_lanes(left_x, right_x, bev.shape[1])

        # 학생 정책 — 데모용 perturbation (실제론 NN 출력)
        a_student = a_expert + float(np.random.normal(0, 0.05))
        a_student = float(np.clip(a_student, -0.5, 0.5))

        state = {"t": t, "left_x": left_x, "right_x": right_x, "img_shape": img.shape}
        logger.log(state, a_student, a_expert)
        student_outputs.append(a_student)
        expert_outputs.append(a_expert)

    print(f"\n[로깅 요약]")
    print(logger.summary())

    s, e = np.array(student_outputs), np.array(expert_outputs)
    print(f"\n[조향 통계]")
    print(f"  전문가 조향 평균: {e.mean():+.4f} rad  (표준편차 {e.std():.4f})")
    print(f"  학생   조향 평균: {s.mean():+.4f} rad  (표준편차 {s.std():.4f})")

    print(f"\n[실제 MentorPi 실행 절차]")
    print(f"  1) ROS2 노드 mentorpi_camera 실행 (카메라 토픽 발행)")
    print(f"  2) calibration.py → ~/.ros/camera_info 저장")
    print(f"  3) bev_node.py 실행 → /bev_image 토픽")
    print(f"  4) lane_follower.py 실행 → /cmd_vel 발행")
    print(f"  5) joy_dagger.py → 위험 시 사람이 조이스틱 개입, 데이터 추가 수집")
    print(f"  6) 디스크에 누적된 (state, a_expert) 쌍으로 야간 BC 재학습")

    print(f"\n  도서 29.6 절: 본 파이프라인은 4시간 안에 실제 MentorPi 에 이식 가능.")


if __name__ == "__main__":
    main()
