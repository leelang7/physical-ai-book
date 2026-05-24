# Chapter 29 · MentorPi 비전 자율주행 통합 파이프라인

도서 **29장** *"MentorPi 로 해보는 비전 자율주행 실증"* 와 1:1 연결.

실제 MentorPi (HiWonder 소형 로봇) 가 없어도 *파이프라인 전체 구조*
를 CPU 시뮬레이션으로 확인. 카메라 → BEV → 차선 → 조향 → DAgger 로깅
6 단계가 한 파일로 묶여 있음.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`mentorpi_pipeline.py`](mentorpi_pipeline.py) | 6 단계 통합 파이프라인 50 step 시뮬레이션 + DAgger 로깅 패턴 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch29_mentorpi
python mentorpi_pipeline.py
```

## 6 단계 흐름

| 단계 | 함수 | 이전 장 연계 |
|---|---|---|
| 1. 캘리브레이션 | `mock_calibration` | (실제: ROS2 `camera_calibration` 노드) |
| 2. 카메라 프레임 | `synthetic_camera_frame` | (실제: `/camera/image_raw` 토픽) |
| 3. BEV 변환 | `bev_transform` | [ch07 BEV](../ch07_bev/) 의 고전 IPM |
| 4. 차선 검출 | `detect_lanes` | (단순 이진화 — 실제는 ch08 헤드 사용) |
| 5. 조향 계산 | `steering_from_lanes` | [ch11 Control](../ch11_control/) Pure Pursuit |
| 6. DAgger 로깅 | `DAggerLogger` | [ch20 BC + DAgger](../ch20_bc_dagger/) 의 데이터 수집 패턴 |

## 실측 결과 (CPU 1초)

```
50 스텝 (5초) 시뮬레이션
  학생-전문가 불일치 평균: 0.0435 rad
  최대 불일치 (DAgger 효과 큰 구간): 0.1391 rad
  전문가 조향 평균: +0.0262 rad
  학생   조향 평균: +0.0213 rad
```

## 학습 포인트 (도서 본문)

1. **이전 장들의 통합** (29.2 절) — ch04 ISP, ch07 BEV, ch11 Control, ch20 DAgger 가 *한 파이프라인* 에 묶임. 책의 8 부 30 장 전체가 결국 이 실증을 위한 빌딩 블록.
2. **CPU 시뮬레이션 → 실 로봇 이식 4시간** (29.6 절) — 본 데모의 인터페이스를 ROS2 토픽으로 바꾸면 그대로 작동. 학생들이 보통 이 단계에서 *"한 번 굴려보면 모든 게 명확해진다"* 고 함.
3. **DAgger 로깅의 실전 패턴** (29.5 절) — 학생 정책으로 굴리면서 *전문가 (사람 조이스틱)* 의 정답을 동시 기록. 디스크 누적 후 야간 BC 재학습.

## 실제 MentorPi 실행 절차 (도서 29.4 절)

```
1) ROS2 노드 mentorpi_camera 실행 → /camera/image_raw 발행
2) calibration.py → ~/.ros/camera_info/mentorpi.yaml 저장
3) bev_node.py → /bev_image 토픽
4) lane_follower.py → /cmd_vel 발행 (자율 모드)
5) joy_dagger.py → 사람이 위험 시 개입, 데이터 추가 수집
6) 디스크 누적 데이터로 야간 BC 재학습 (ch20 의 dagger_loop)
```

위 6 단계 노드의 코드 골격이 본 파이프라인 안에 모두 들어 있음. ROS2 토픽 구독·발행만 추가하면 실 로봇 동작.

## 한계 — 본 데모는 시뮬레이션

- 실제 카메라 캘리브레이션 X (mock K 행렬)
- 실제 도로 X (회색 + 흰 선 합성)
- 실제 학생 NN X (전문가 + 노이즈)
- 실제 모터 명령 X (수치만 계산)

목적: *MentorPi 가 손에 들어오기 전에도 코드 구조 확인 + 학생들이 시뮬레이션으로 디버깅*.

## 다음 — 실 로봇 환경

- `ros2_mentorpi/` 패키지 (M4 공개) — ROS2 노드로 변환된 본 파이프라인
- [ch30 ROS2](../ch30_ros2/) (M4) — 토픽·런치파일·QoS 패턴
- HiWonder MentorPi 하드웨어 가이드 — 책 부록 D 또는 별도 문서
