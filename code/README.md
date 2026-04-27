# physical-ai-book · 실습 코드

이 폴더는 **"테슬라처럼 만드는 비전 자율주행과 피지컬 AI"** (이석창 지음, All That AI · Vol.01) 의 장별 실습 코드 저장소입니다. 도서 각 장에서 언급된 코드 스니펫의 **완성된 실행본** 과 학습·추론·시각화 스크립트가 순차적으로 공개됩니다.

## 장별 디렉토리

| 디렉토리 | 연동 장 | 내용 |
|---|---|---|
| `environment/` | 23장 | Docker, requirements, Conda env |
| `ch04_isp/` | 4장 | Bayer → RGB 디모자이크 노트북 |
| `ch05_hydra/` | 5장 | HydraNet 백본·BiFPN·헤드 모듈 |
| `ch06_occ/` | 6장 | Mini Occupancy Network (nuScenes-mini) |
| `ch07_bev/` | 7장 | Learned IPM · BEVFormer 축소판 |
| `ch08_heads/` | 8장 | Lane · Sign · Object 3헤드 통합 |
| `ch09_pred/` | 9장 | TinyPred 다중 모달 궤적 예측 |
| `ch10_planner/` | 10장 | Neural Planner + Safety Cage |
| `ch11_control/` | 11장 | Bicycle Model · Pure Pursuit · Residual NN |
| `ch20_bc_dagger/` | 20장 | BC · DAgger 루프 · MentorPi 연동 |
| `ch21_rl/` | 21장 | CartPole PPO · Residual RL 데모 |
| `ch22_vla/` | 22장 | OpenVLA 추론 · System 1/2 분리 |
| `ch24_mini_hydra/` | 24장 | BDD100K + YOLOv8 확장 풀 실습 |
| `ch25_mini_occ/` | 25장 | nuScenes mini 기반 Occupancy 파이프라인 |
| `ch27_isaac_lab/` | 27장 | Go2 보행 · Franka + OpenVLA |
| `ch29_mentorpi/` | 29장 | MentorPi 실증 — 캘리브레이션 · Lane · BEV · DAgger |
| `ch30_ros2/` | 30장 | ROS2 노드 · 런치 파일 · QoS 예제 |

## 현재 상태 (2026-04-27 출간일 기준)

| 디렉토리 | 상태 |
|---|---|
| `environment/` | ✅ **부트 가능** — Dockerfile · `requirements.txt` · `setup.sh` · `.env.sample` 제공. 자세한 사용법은 [environment/README.md](environment/README.md) |
| `ch*/` 16개 | 📋 README 스텁만 존재. 본격 코드는 아래 M1~M5 일정대로 누적됨 |

지금 당장 동작 가능한 것은 *공통 개발 환경 구축* 입니다. 본문을 따라 읽으면서 환경부터 갖춰 두시고, 각 장 코드는 일정에 맞춰 들러 주세요.

## 공개 일정 (출간일 기준 T+N 주)

- **M1 (T+4주, ~ 2026-05-25)** — ch04 ISP · ch05 HydraNet · ch09 Prediction · ch10 Planner 1차 공개
- **M2 (T+8주, ~ 2026-06-22)** — ch06 Occupancy · ch07 BEV · ch08 Heads · ch11 Control 추가
- **M3 (T+12주, ~ 2026-07-20)** — ch20 BC/DAgger · ch21 RL · ch22 VLA · ch24 Mini HydraNet · ch25 Mini Occ · ch29 MentorPi 추가
- **M4 (T+16주, ~ 2026-08-17)** — ch27 Isaac Lab · ch30 ROS2 추가
- **M5 (T+20주, ~ 2026-09-14)** — 전 장 완성 + 도커 이미지 Hub 배포

각 마일스톤은 GitHub Release 태그 (`v1.1`, `v1.2`, ... `v1.5`) 로 박힙니다. 우측 *"Watch → Releases only"* 를 켜 두시면 코드 공개 시 알림이 옵니다.

## 라이선스

실습 코드 : **MIT License** (본문 원고는 저자 권리 보유)

## 이슈 · 기여

- 버그 제보 : [Issues](https://github.com/leelang7/physical-ai-book/issues)
- 기여 : Pull Request 환영
- 이메일 : leescvsir@gmail.com
- YouTube : [@aidoer (All That AI)](https://www.youtube.com/@aidoer)
