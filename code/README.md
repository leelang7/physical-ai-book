# physical-ai-book · 실습 코드

이 폴더는 **"테슬라처럼 만드는 비전 자율주행과 피지컬 AI"** (이석창 지음, All That AI · Vol.01) 의 장별 실습 코드 저장소입니다. 도서 각 장에서 언급된 코드 스니펫의 **완성된 실행본** 과 학습·추론·시각화 스크립트가 순차적으로 공개됩니다.

## 장별 디렉토리

| 디렉토리 | 연동 장 | 내용 |
|---|---|---|
| `environment/` | 23장 | Docker, requirements, venv setup |
| `ch04_isp/` | 4장 | Bayer 디모자이크 + 화이트밸런스 |
| `ch05_hydra/` | 5장 | HydraNet 백본·FPN·3헤드 (forward) |
| `ch06_occ/` | 6장 | Mini Occupancy (LSS forward) |
| `ch07_bev/` | 7장 | 고전 IPM vs Learned IPM (attention) |
| `ch08_heads/` | 8장 | 8 카메라 + BEV 융합 + 3 헤드 |
| `ch09_pred/` | 9장 | TinyPred 다중 모달 + score collapse |
| `ch10_planner/` | 10장 | Neural Planner + 4 규칙 Safety Cage |
| `ch11_control/` | 11장 | Bicycle + Pure Pursuit + Residual NN |
| `ch12_trigger/` | 12장 | Fleet Data Trigger 4 종 + Edge Miner |
| `ch13_autolabel/` | 13장 | Pseudo-label 3 라운드 self-training |
| `ch14_carla/` | 14장 | CARLA 데이터 수집 골격 + 설치 가이드 |
| `ch16_distributed/` | 16장 | DDP · FSDP · Pipeline 호출 패턴 + 메모리 추정 |
| `ch17_quant/` | 17장 | PTQ INT8 양자화 + ONNX export |
| `ch20_bc_dagger/` | 20장 | BC + DAgger 1D 차량 환경 |
| `ch21_rl/` | 21장 | Pure REINFORCE vs Residual RL on PD |
| `ch22_vla/` | 22장 | VLA 3 모듈 + System 1/2 주파수 분리 |
| `ch24_mini_hydra/` | 24장 | Mini HydraNet 학습 가능 버전 |
| `ch25_mini_occ/` | 25장 | Mini Occupancy 학습 가능 + sparse 함정 |
| `ch26_openpilot/` | 26장 | supercombo 모델 구조 분석 |
| `ch27_isaac_lab/` | 27장 | Isaac Lab Go2 + Franka + OpenVLA 골격 |
| `ch29_mentorpi/` | 29장 | MentorPi 6 단계 통합 파이프라인 |
| `ch30_ros2/` | 30장 | ROS2 노드 5 종 + 런치 + QoS 패턴 |

## 현재 상태 (2026-05-25)

| 디렉토리 | 상태 |
|---|---|
| `environment/` | ✅ 동작 (Docker · venv · requirements) |
| **M1 + M2 + M3** (14개 장) | ✅ **공개 완료** — 모두 CPU + 합성 입력으로 즉시 동작 |
| **M4 추가 (8개 장)** | ✅ **공개 완료 (조기)** — ch12 · ch13 · ch14 · ch16 · ch17 · ch26 · ch27 · ch30 |

**총 22 개 장 디렉토리가 모두 공개됨.** CPU 친화 데모 14 개 + 외부 환경 의존 골격 8 개 (CARLA · Isaac Lab · ROS2 · openpilot 등).

## 공개 일정 (출간일 2026-04-27 기준)

- **M1 (~ 2026-05-25)** — ✅ **2026-04-29** : ch04 · ch05 · ch09 · ch10
- **M2 (~ 2026-06-22)** — ✅ **2026-05-08** (6주 조기) : ch06 · ch07 · ch08 · ch11
- **M3 (~ 2026-07-20)** — ✅ **2026-05-25** (8주 조기) : ch20 · ch21 · ch22 · ch24 · ch25 · ch29
- **M4 (~ 2026-08-17)** — ✅ **2026-05-25** (12주 조기) : ch12 · ch13 · ch14 · ch16 · ch17 · ch26 · ch27 · ch30
- **M5 (~ 2026-09-14)** — 📋 예정 : 도커 이미지 Hub 배포 + 전체 통합 노트북

각 마일스톤은 GitHub Release 태그 (`v1.1`, `v1.2`, ... `v1.5`) 로 박힙니다. 우측 *"Watch → Releases only"* 를 켜 두시면 코드 공개 시 알림이 옵니다.

## 라이선스

실습 코드 : **MIT License** (본문 원고는 저자 권리 보유)

## 이슈 · 기여

- 버그 제보 : [Issues](https://github.com/leelang7/physical-ai-book/issues)
- 기여 : Pull Request 환영
- 이메일 : leescvsir@gmail.com
- YouTube : [@aidoer (All That AI)](https://www.youtube.com/@aidoer)
