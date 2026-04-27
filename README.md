# 테슬라처럼 만드는 비전 자율주행과 피지컬 AI

> 카메라 한 대에서 Optimus 까지, 픽셀이 핸들이 되는 여정.
> **All That AI · Vol.01** · 이석창 (Seokchang Lee) 지음

도서 *"테슬라처럼 만드는 비전 자율주행과 피지컬 AI"* 의 **공식 컴패니언 저장소** 입니다. 책 본문은 부크크에서 구매하실 수 있고, 이 저장소에는 **장별 실습 코드 · QR 코드 · 정오표** 가 단계별로 공개됩니다.

> 광합성을 구현한 것이 태양광 발전이고, 뇌를 구현한 것이 신경망이라면,
> 사람이 보는 그대로를 구현한 것이 Tesla 의 비전 신경망입니다.

---

## 📖 도서 구매

- **부크크 전자책** : https://bookk.co.kr/bookStore/69eb15e3ee2f092c79a5fc74
- **유페이퍼 전자책** : (등록 후 갱신)
- **교보문고 · 예스24 · 알라딘** : 유페이퍼 제휴 노출 (등록 후 갱신)

정가 19,900원 · 런칭 4주 한정 14,900원 · 8부 30장 + 부록 4개 · 220페이지.

---

## 책의 핵심 입장

1. **Vision-only · End-to-End** — LiDAR · HD Map 중심의 고전 교재와 반대 방향. Tesla 가 2024년 FSD v12 에서 보여 준 *"픽셀이 핸들이 되는"* 세상을 한 줄기로 풀어냅니다.
2. **Physical AI 로의 확장** — 자율주행에서 멈추지 않고 Optimus · Isaac Lab · VLA · World Model 까지. 자율주행차와 휴머노이드가 *"같은 뇌, 다른 몸"* 이라는 관점.
3. **모방학습 주력, 강화학습은 보조** — 국내 학생·엔지니어가 실제 성과를 내는 경로는 BC → HG-DAgger 루프입니다. 저자의 2026년 *See-ParkingNet* 논문이 이 입장의 학술적 근거입니다.
4. **계산이 아니라 인식** — 모듈형은 이진화 · 미분 · 특징점을 *계산* 합니다. 신경망은 *인식* 합니다. 이 대조가 세대 전환의 본질이고 책 전체의 뼈대입니다.
5. **강의 · 영상 · 코드 3중 동반** — 본 저장소(코드) + YouTube *All That AI* (영상) + 책(본문) 이 1:1 로 묶입니다.

---

## 이 저장소에 있는 것

```
physical-ai-book/
├── README.md
├── LICENSE
├── errata.md                    # 정오표 (이슈 수집 후 누적)
├── code/                        # 장별 실습 코드 (M1~M5 단계 공개)
│   ├── README.md                # 공개 로드맵
│   ├── environment/
│   ├── ch04_isp/  ch05_hydra/  ch06_occ/  ch07_bev/  ch08_heads/
│   ├── ch09_pred/ ch10_planner/ ch11_control/
│   ├── ch20_bc_dagger/ ch21_rl/ ch22_vla/
│   ├── ch24_mini_hydra/ ch25_mini_occ/ ch27_isaac_lab/
│   └── ch29_mentorpi/ ch30_ros2/
├── ebook/
│   ├── cover/                   # 표지 아트 (A Red Column · B Swiss · C Neon)
│   └── qr/                      # 장별 QR PNG 31개 + 독자 안내
└── scripts/
    └── build_qr.py              # QR 재생성 스크립트
```

책 본문(원고·PDF) 은 이 저장소에 포함되지 않습니다. 부크크·유페이퍼에서 구매하셔야 합니다.

---

## 실습 코드 공개 로드맵

| 시점 | 공개 내용 |
|---|---|
| **M1 (출간+4주)** | environment · ch04 · ch05 · ch09 · ch10 |
| **M2 (출간+8주)** | ch06 · ch07 · ch08 · ch11 |
| **M3 (출간+12주)** | ch20 · ch21 · ch22 · ch24 · ch25 · ch29 |
| **M4 (출간+16주)** | ch27 · ch30 |
| **M5 (출간+20주)** | 전 장 + Docker 이미지 공개 |

자세한 내용은 [code/README.md](code/README.md) 참고.

---

## QR 코드 사용법

각 장 끝의 QR 은 [ebook/qr/](ebook/qr/) 의 같은 번호 PNG 와 1:1 대응합니다. 책 출간(v1.0) 시점에는 모두 YouTube 채널 메인(`@aidoer`)으로 연결되며, 영상이 누적되는 대로 *"Tesla Book Ch.XX"* 일관된 제목으로 채널 안에서 검색하실 수 있습니다.

---

## 저자

**이석창 (Seokchang Lee)** · Adjunct Professor / AI Specialist Lecturer
Korea IT Academy · 미래융합교육원 · Elice Group · EST soft · 한국기술교육대학교

- 📧 [leescvsir@gmail.com](mailto:leescvsir@gmail.com)
- 🌐 GitHub · [github.com/leelang7](https://github.com/leelang7) (112+ 공개 저장소)
- ▶️ YouTube · [All That AI (@aidoer)](https://www.youtube.com/@aidoer)

2026년 발표 논문 *"See-ParkingNet: A Robust Imitation Learning Framework for Autonomous Mobile Robots via Geometric Perturbation of Synthetic Experts"* 와 2025년 한국장애인개발원 이사장상 · 서울AI허브재단 이사장상 · 고용노동부 수상 등의 이력이 있습니다.

---

## 기여 · 오탈자 제보

- **책 오류 / 오타** : [Issues](https://github.com/leelang7/physical-ai-book/issues) 에 제보 → [errata.md](errata.md) 에 누적
- **실습 코드 개선** : Pull Request 환영
- **강의 · 부트캠프 채택 문의** : leescvsir@gmail.com (강사용 평가 가이드 별도 제공)
- **커뮤니티 · 질문** : YouTube *All That AI* 댓글

여러분의 피드백 하나하나가 개정판을 만듭니다.

---

## 라이선스

- **실습 코드** ([code/](code/), [scripts/](scripts/)) : **MIT License** ([LICENSE](LICENSE))
- **표지 · QR PNG** ([ebook/cover/](ebook/cover/), [ebook/qr/](ebook/qr/)) : 자유 재배포 가능 (출처 표기 권장)
- **책 본문** : © 2026 Seokchang Lee. All rights reserved. 본 저장소에는 포함되지 않으며, 상업적 재배포 · 재출판은 저자의 사전 서면 동의가 필요합니다.
- **상표 면책** : Tesla · Autopilot · FSD · Optimus · Dojo · Waymo · Mobileye · NVIDIA · Wayve · Comma.ai · Figure · 1X · Boston Dynamics · Unitree 등의 상표는 각 소유자의 자산이며, 저자와의 직접적인 제휴 · 후원 관계는 없습니다. 본서 및 본 저장소는 교육 목적의 비공식 해설 자료입니다.
