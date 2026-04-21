# 테슬라로 배우는 비전 자율주행과 피지컬 AI — 초안 (Draft v1.1)

> **저자**: 이석창 (Seok Chang Lee) · AI Instructor @ Elice Group / Korea IT Academy / 미래융합교육원
> **GitHub**: https://github.com/leelang7 · **YouTube**: https://www.youtube.com/@aidoer
> **작성 시점**: 2026-04-20
> **최근 개정**: v1.0 → v1.1 (전 장 서술형 재작성, MentorPi·ROS2 두 장 신설, 시뮬·강화학습 한계와 사례 보강)

이 폴더는 "**테슬라로 배우는 비전 자율주행과 피지컬 AI**" 교재의 초안 원고입니다.

---

## v1.1의 변경 요약

저자 피드백을 반영해 대폭 개정했습니다.

1. **문체를 전면 서술형으로 재작성**했습니다. 개조식 bullet·표 나열을 최소화하고, 각 절이 문단으로 이어지는 "책다운" 전개로 모두 교체했습니다. 기록은 `C:/Users/leesc/.claude/projects/.../memory/feedback_prose_style.md`에 남겨 이후 모든 집필에도 유지됩니다.
2. **MentorPi 실증 장을 신설**([ch29](ch29_MentorPi_실증.md))했습니다. 카메라를 MentorPi에 직접 장착해 차선 추종, BEV, E2E 모방 학습을 한 학기 분량으로 재현하는 경험을 다룹니다.
3. **ROS2 통합 장을 신설**([ch30](ch30_ROS2.md))했습니다. Tesla가 ROS를 쓰지 않음에도 왜 독자가 ROS2를 배워야 하는지, MentorPi·CARLA·Isaac Lab을 같은 인터페이스로 엮는 실전을 담았습니다.
4. **시뮬레이션의 진짜 한계와 사례를 확충**([ch14](ch14_Simulation.md))했습니다. Waymo 애리조나 모래바람, Cruise 2023 사고, 공기 물리의 모델링 실패, "스스로 시험지 내는" 구조적 편향 네 가지를 구체 사례로 다룹니다.
5. **강화학습의 한계와 실패 사례를 보강**([ch21](ch21_RL_Sim2Real.md))했습니다. 보상 해킹·탐색의 사치·Sim2Real 비대칭성·분포 외 실패 네 가지 패턴과, 2022~2025년 성공 3건과 좌절 3건의 구체적 사례를 담았습니다.

---

## 파일 목록

### 프론트 매터
- [00_기획안.md](00_기획안.md)
- [00_서문.md](00_서문.md)
- [00_이책의_사용법.md](00_이책의_사용법.md)
- [01_목차.md](01_목차.md)

### 1부 · 자율주행의 패러다임 전환
- [ch01_자율주행의_세번의_물결.md](ch01_자율주행의_세번의_물결.md)
- [ch02_왜_카메라만_쓰는가.md](ch02_왜_카메라만_쓰는가.md)
- [ch03_E2E_자율주행.md](ch03_E2E_자율주행.md)

### 2부 · 비전 기반 인식
- [ch04_카메라와_ISP.md](ch04_카메라와_ISP.md)
- [ch05_HydraNet.md](ch05_HydraNet.md)
- [ch06_OccupancyNetwork.md](ch06_OccupancyNetwork.md)
- [ch07_BEV_VectorSpace.md](ch07_BEV_VectorSpace.md)
- [ch08_Lane_Sign_Object.md](ch08_Lane_Sign_Object.md)

### 3부 · 예측·계획·제어
- [ch09_Prediction.md](ch09_Prediction.md)
- [ch10_NeuralPlanner.md](ch10_NeuralPlanner.md)
- [ch11_Control.md](ch11_Control.md)

### 4부 · 데이터 엔진
- [ch12_FleetData_Trigger.md](ch12_FleetData_Trigger.md)
- [ch13_AutoLabeling.md](ch13_AutoLabeling.md)
- [ch14_Simulation.md](ch14_Simulation.md) — **한계·사례 확충**

### 5부 · 학습 인프라와 MLOps
- [ch15_Dojo.md](ch15_Dojo.md)
- [ch16_DistributedTraining.md](ch16_DistributedTraining.md)
- [ch17_OTA_Shadow.md](ch17_OTA_Shadow.md)

### 6부 · 피지컬 AI
- [ch18_PhysicalAI_개관.md](ch18_PhysicalAI_개관.md)
- [ch19_Optimus.md](ch19_Optimus.md)
- [ch20_ImitationLearning.md](ch20_ImitationLearning.md)
- [ch21_RL_Sim2Real.md](ch21_RL_Sim2Real.md) — **한계·사례 확충**
- [ch22_WorldModel_VLA.md](ch22_WorldModel_VLA.md)

### 7부 · 실습 프로젝트
- [ch23_환경구축.md](ch23_환경구축.md)
- [ch24_MiniHydraNet.md](ch24_MiniHydraNet.md)
- [ch25_MiniOccupancy.md](ch25_MiniOccupancy.md)
- [ch26_openpilot.md](ch26_openpilot.md)
- [ch27_IsaacLab.md](ch27_IsaacLab.md)
- [ch28_미래와윤리.md](ch28_미래와윤리.md)

### 8부 · 현장과 맞닿기 (신설)
- [ch29_MentorPi_실증.md](ch29_MentorPi_실증.md) — **신규**
- [ch30_ROS2.md](ch30_ROS2.md) — **신규**

### 부록
- [appA_수학속성복습.md](appA_수학속성복습.md)
- [appB_논문120선.md](appB_논문120선.md)
- [appC_용어집.md](appC_용어집.md)
- [appD_저자연계.md](appD_저자연계.md)

### 프로젝트 운영
- [REQUESTS.md](REQUESTS.md) — 저자 추가 자료 요청 목록

---

## 초안 현황 (v1.1, 2026-04-20 개정)

| 구분 | 상태 |
|---|---|
| 기획안·목차·서문 | 서술형 개정 완료 |
| 1~30장 본문 | 전 장 서술형 초안 완료 |
| 부록 A~D | 완료 |
| 실습 코드 저장소 | GitHub 별도 작업 필요 |
| 그림·다이어그램 | 텍스트 설명 중심, 이미지 교체 필요 |
| 교열·편집 | 저자 톤·문체 3차 윤문 필요 |
| 저자 검토 | 대기 |

---

## 다음 단계

1. 저자 검토 의견에 따라 전 장을 한 번 더 읽으면서 저자 고유 어휘·사례로 한 번 더 손보는 3차 개정을 진행합니다.
2. 저자 GitHub에 `physical-ai-book` 저장소를 생성하고 24·25·27·29·30장의 실습 코드를 차례로 올립니다.
3. 본문 다이어그램을 Mermaid·Excalidraw로 초안화한 뒤, 출판사의 디자이너가 최종 교체하도록 전달합니다.
4. 3~5명의 베타 리더(수강생·동료 강사)에게 읽혀 1차 피드백을 모읍니다.
5. 출판사(한빛·위키북스·제이펍 등)와 접촉해 판형·분량·일정을 협의합니다.

---

## 저자 승인이 필요한 항목 (다음 턴에 알려주시면 반영)

- 가제 세 안 가운데 최종 선택 (혹은 새 제안)
- 목표 페이지수(400 / 500 / 600 / 분권)
- 실습 저장소명 확정 (`physical-ai-book` 그대로 OK?)
- 강화·축소가 필요한 특정 장
- 저자의 실무 사례 중 반드시 책에 녹여내고 싶은 에피소드(1~3개)

---

*초안 v1.1은 전 장이 서술형으로 재작성된 상태입니다. 저자님의 경험·톤이 한 번 더 3차 교정에서 주입되면 출간 수준에 근접합니다.*
