"""
ch14 — CARLA 시뮬레이터 데이터 수집 (골격)

도서 14장 *"시뮬레이션과 Corner Case 증강"* 의 *코드 골격*.
CARLA 0.9.15 가 별도 설치돼 있어야 실행 가능 — 본 파일은 *어떻게 수집하는가* 의
패턴만 보여줌. CARLA 설치는 nvidia-docker 또는 별도 인스톨러 필요.

설치 안 된 환경에서도 import 만 시도하고, 구조는 print 로 보여줌.

실제 워크플로:
  1) CARLA 서버 실행 (Docker 또는 Native)
  2) 본 스크립트로 차량 + 카메라 스폰
  3) Autopilot 로 주행 → 카메라 + 제어 명령 디스크 저장
  4) BC 학습 데이터로 활용 (ch20)
"""
from __future__ import annotations
import sys


def try_import_carla() -> bool:
    try:
        import carla  # noqa
        return True
    except ImportError:
        return False


def collect_pattern() -> None:
    """CARLA 가 있다고 가정한 코드 골격 — print 로 표시."""
    print("""
# CARLA 데이터 수집 의사 코드 (carla 0.9.15)
import carla
import numpy as np
from pathlib import Path

# 1) 서버 연결
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

# 2) 차량 + 카메라 스폰
blueprint = world.get_blueprint_library().filter('vehicle.tesla.model3')[0]
spawn = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(blueprint, spawn)
vehicle.set_autopilot(True)

cam_bp = world.get_blueprint_library().find('sensor.camera.rgb')
cam_bp.set_attribute('image_size_x', '1280')
cam_bp.set_attribute('image_size_y', '720')
camera_tf = carla.Transform(carla.Location(x=1.5, z=2.4))
camera = world.spawn_actor(cam_bp, camera_tf, attach_to=vehicle)

# 3) 카메라 + 제어 동시 수집
out = Path('/data/carla_run_001')
out.mkdir(parents=True, exist_ok=True)
def on_frame(image):
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = array.reshape((image.height, image.width, 4))[:, :, :3]
    np.save(out / f'{image.frame:06d}.npy', array)
    # 동시에 차량 상태도 기록
    ctrl = vehicle.get_control()
    with open(out / 'control.csv', 'a') as f:
        f.write(f'{image.frame},{ctrl.steer},{ctrl.throttle},{ctrl.brake}\\n')

camera.listen(on_frame)

# 4) N 초 동안 굴림
import time
time.sleep(60)
camera.stop()
vehicle.destroy()
camera.destroy()
""")


def main() -> None:
    print("== ch14 CARLA 데이터 수집 (골격) ==\n")
    has = try_import_carla()
    print(f"CARLA 모듈 import: {'✓ 가능' if has else '✗ 미설치 (정상 — 본 데모는 환경 안내용)'}")
    print()
    if has:
        print("CARLA 가 설치돼 있어도 서버가 켜져 있어야 실제 실행 가능합니다.")
        print("아래 의사 코드를 자신의 환경에서 실행하시면 됩니다.")
    else:
        print("CARLA 미설치 — 아래 패턴 그대로 사용하시려면 환경 안내 (README 참조)")
    collect_pattern()


if __name__ == "__main__":
    main()
