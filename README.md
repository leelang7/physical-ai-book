# 테슬라처럼 만드는 비전 자율주행과 피지컬 AI

> 카메라 한 대에서 Optimus까지, 픽셀이 핸들이 되는 여정.
> **All That AI · Vol. 01**

국내에 한국어로 된 **Tesla Vision-only · End-to-End · Physical AI** 교재가 없다는 답답함에서 출발한 집필 프로젝트의 공개 저장소입니다. 자율주행 차량(FSD) 에서 휴머노이드(Optimus) 와 VLA 모델까지, "사람이 보는 그대로를 공학으로 옮긴다" 는 한 줄기의 이야기로 꿰어 냈습니다.

> **광합성을 구현한 것이 태양광 발전이고, 뇌를 구현한 것이 신경망이라면,
> 사람이 보는 그대로를 구현한 것이 Tesla 의 비전 신경망입니다.**

---

## 저자

**이석창 (Seokchang Lee)** · Adjunct Professor / AI Specialist Lecturer
Korea IT Academy · 미래융합교육원 · Elice Group · EST soft · 한국기술교육대학교

- 📧 [leescvsir@gmail.com](mailto:leescvsir@gmail.com)
- 🌐 GitHub · [github.com/leelang7](https://github.com/leelang7)
- ▶️ YouTube · [All That AI (@aidoer)](https://www.youtube.com/@aidoer)

2026년 발표 논문 *"See-ParkingNet: A Robust Imitation Learning Framework for Autonomous Mobile Robots via Geometric Perturbation of Synthetic Experts"* 와 2025년 한국장애인개발원 이사장상 · 서울AI허브재단 이사장상 등의 수상 이력을 갖고 있으며, 본 교재가 표방하는 **"모방학습 + DAgger 주력, 강화학습은 보조"** 입장의 학술적 근거를 이 연구가 직접 제공합니다.

---

## 이 책의 핵심 입장

1. **Vision-only · End-to-End** — LiDAR·HD Map 중심의 고전 교재와 반대 방향. Tesla 가 2024년 FSD v12 에서 보여 준 *"픽셀이 핸들이 되는"* 세상을 한 줄기로 풀어냅니다.
2. **Physical AI 로의 확장** — 자율주행에서 멈추지 않고 Optimus · Isaac Lab · VLA · World Model 까지 한 파트(5장 분량) 로 이어 갑니다. 자율주행차와 휴머노이드가 **같은 뇌, 다른 몸** 이라는 관점.
3. **모방학습 주력, 강화학습은 보조** — 국내 학생·엔지니어가 실제 성과를 내는 경로는 BC → HG-DAgger 루프입니다. 20장이 이 파트의 엔진룸이고, 21장은 RL 의 정당한 영역과 고장 패턴을 정직하게 다룹니다.
4. **"계산이 아니라 인식"** — 모듈형은 이진화 · 미분 · 특징점을 **계산** 합니다. 신경망은 **인식** 합니다. 이 대조가 세대 전환의 본질이고 책 전체의 뼈대입니다.
5. **강의 · 영상 · 코드 3중 동반** — 본 저장소는 책의 실습 코드 베이스이며, 각 장 QR 코드가 YouTube *All That AI* 해설 영상으로 이어집니다.

---

## 구성

전체 원고는 **8부 30장 + 부록 4개**, 약 436,000자 분량입니다. 집필은 서술형(prose) 문체, 1인칭 강사 목소리, 한국적 비유 중심으로 일관됩니다.

| 부 | 장 | 주제 |
|---|---|---|
| 1부 | 1~3 | 자율주행의 세 번의 물결 · Vision-only · End-to-End |
| 2부 | 4~8 | ISP · HydraNet · Occupancy · BEV · Vector Space · Lane / Sign / Object |
| 3부 | 9~11 | 궤적 예측 · Neural Planner · Control |
| 4부 | 12~14 | Fleet Data Engine · Auto-labeling · Simulation |
| 5부 | 15~17 | Dojo · 분산 학습 · Shadow / OTA |
| 6부 | 18~22 | Physical AI · Optimus · **모방학습 + DAgger** · 강화학습의 자리 · World Model / VLA |
| 7부 | 23~27 | 환경 구축 · Mini HydraNet · Mini Occupancy · openpilot · Isaac Lab |
| 8부 | 28~30 | 미래 · **MentorPi 실증** · **ROS2 통합** |
| 부록 | A~D | 수학 속성 복습 · 핵심 논문 50선 · 한/영 용어집 · 저자 연계 가이드 |

---

## 저장소 구조

```
physical-ai-book/
├── draft/            # 본문 원고(서문·목차·30장·부록 4개, v2.0)
├── ebook/
│   ├── 전체원고_v2.0.md         # 한 파일로 묶인 최종 원고 (448k자)
│   ├── cover/                  # 표지 SVG 3안(A Red Column · B Swiss · C Neon)
│   ├── 책소개_상세.md
│   ├── 메타데이터.md
│   ├── 가격전략.md
│   ├── 표지_컨셉.md
│   ├── 제출가이드_부크크.md
│   ├── 제출가이드_유페이퍼.md
│   ├── 검증_리포트.md
│   └── 출판_체크리스트.md       # v2.0 기준 단계별 발송 가이드
├── code/             # 장별 실습 코드 스텁 (출간 일정에 맞춰 채워짐)
│   ├── README.md                # 공개 로드맵 M1~M5
│   ├── environment/             # Docker · requirements · setup.sh
│   ├── ch04_isp/ ... ch30_ros2/ # 16개 장 스텁 디렉토리
├── scripts/          # 빌드·내보내기 도구
│   ├── build_manuscript.sh      # 원고 단일 MD·PDF·EPUB 빌드
│   └── export_cover.md          # SVG → PNG 내보내기 4가지 방법
├── assets/           # (예정) 다이어그램 · 화보 자료
└── references/       # (예정) 참조 자료
```

각 장별 실습 노트북은 `code/README.md` 의 공개 로드맵(M1~M5, 20주)에 따라 순차 공개됩니다.

---

## 전자책 출간 계획

본 원고는 **부크크(Bookk) 와 유페이퍼(Upaper) 동시 전자책 출간** 을 목표로 준비되어 있습니다. 출간 시 교보문고 · 예스24 · 알라딘 에서 검색 가능합니다.

- 정가 : 19,900원
- 런칭 할인 : 14,900원 (첫 4주)
- 부크크 POD 종이책 전환 예정 (초기 전자책 판매 누적 후)

---

## 라이선스

- **본문 원고** (`draft/`, `ebook/*.md`) : © 2026 Seokchang Lee. All rights reserved. 상업적 재배포·재출판은 저자의 사전 서면 동의가 필요합니다.
- **실습 코드** (향후 추가될 `ch*/` 폴더 내부) : **MIT License** 로 공개 예정.
- **상표 면책** : 본 저장소와 도서에 언급되는 Tesla · Autopilot · FSD · Optimus · Dojo · Waymo · Mobileye · NVIDIA · Wayve · Comma.ai · Figure · 1X · Boston Dynamics · Unitree 등의 상표는 각 소유자의 자산이며, 저자와 직접적인 제휴·후원 관계는 없습니다. 본서는 교육 목적의 비공식 해설입니다.

---

## 기여 · 오탈자 제보

- 책 오타·오류 : 이 저장소의 [Issues](https://github.com/leelang7/physical-ai-book/issues) 에 제보해 주세요.
- 실습 코드 개선 : Pull Request 환영합니다.
- 커뮤니티·질문 : YouTube *All That AI* 댓글 또는 저자 이메일.

여러분의 피드백 하나하나가 개정판을 만듭니다. 독자와 함께 자라는 책을 지향합니다.
