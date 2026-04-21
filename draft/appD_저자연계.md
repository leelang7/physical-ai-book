# 부록 D. 저자 YouTube "All That AI" · GitHub 저장소 가이드

이 책은 영상과 코드가 **함께 있을 때 완성**됩니다. 이 부록은 저자의 온라인 자료와 교재의 장을 **1:1로 연결**합니다.

---

## D.1 YouTube — "All That AI" (@aidoer)

채널: https://www.youtube.com/@aidoer

### 플레이리스트 (예정 커리큘럼)
1. **Tesla Vision Book · Part 1~2** — 자율주행 개론부터 HydraNet까지
2. **Tesla Vision Book · Part 3** — 예측·계획·제어
3. **Tesla Vision Book · Part 4~5** — Data Engine · Dojo · 배포
4. **Tesla Vision Book · Part 6** — Physical AI · Optimus · VLA
5. **Tesla Vision Book · Hands-on** — 실습 전용

### 장별 QR 링크 (예)
각 장 마지막에 **QR 코드**가 배치됩니다. 스캔하면 해당 플레이리스트의 **첫 영상**으로 바로 연결됩니다.

> 💡 **영상 활용법** — 책을 먼저 읽고, 이해가 안 되는 부분만 영상으로 보완하라.
> 또는 영상을 먼저 보고, 코드 수준의 디테일을 책에서 찾으라.

---

## D.2 GitHub — `leelang7/physical-ai-book` (예정)

저장소 구조 (책 출간과 동시에 공개):

```
physical-ai-book/
├── README.md
├── environment/          # Docker, requirements
├── ch04_isp/             # 4장 실습
├── ch05_hydra/           # 5장 실습
├── ch06_occ/             # 6장 실습
├── ch07_bev/             # 7장 실습
├── ch08_heads/           # 8장 실습
├── ch09_pred/            # 9장 실습
├── ch10_planner/         # 10장 실습
├── ch11_control/         # 11장 실습
├── ch12_trigger_miner/   # 12장 실습
├── ch13_auto_label/      # 13장 실습
├── ch14_carla/           # 14장 실습
├── ch15_dojo_concepts/   # 15장 요약 노트북
├── ch16_fsdp_demo/       # 16장 실습
├── ch17_quant/           # 17장 실습
├── ch18_physical_ai/     # 18장 노트북
├── ch19_optimus/         # 19장 노트북
├── ch20_bc/              # 20장 실습 — Behavior Cloning
├── ch21_rl/              # 21장 실습 — PPO
├── ch22_vla/             # 22장 실습 — OpenVLA
├── ch23_env/             # 23장 환경
├── ch24_mini_hydra/      # 24장 풀 실습
├── ch25_mini_occ/        # 25장 풀 실습
├── ch26_openpilot/       # 26장 분석
├── ch27_isaac_lab/       # 27장 실습
├── errata.md             # 정오표
└── LICENSE (MIT)
```

---

## D.3 저자의 다른 저장소 (관련 실습 활용)

- `leelang7/Yolov8-custom` — 24장 배경 자료
- `leelang7/Yolov8-tracking` — 8장, 9장 추적 연동
- `leelang7/mediapipe-pose-detection` — 20장 모방 학습 데이터 생성 팁
- `leelang7/Yolov5-object-distance-estimation` — 6장 보조 자료
- `leelang7/Mlops-api-server` — 17장 배포 MLOps 연계
- `leelang7/Visual-intelligence-sys` — 종합 참고

---

## D.4 정오표·이슈

- 책 내용 오류/오타: `leelang7/physical-ai-book/issues` 에 템플릿에 맞춰 제보
- 실습 코드 오류: 같은 저장소에 PR 환영
- 저자 연락: leescvsir@gmail.com

---

## D.5 독자 커뮤니티

- Discord 서버 (예정): 독자·학생 모임
- 오프라인 스터디: Elice·KIT 캠퍼스에서 정기 개최
- 기업 출강·세미나: 저자 이메일로 문의

---

## D.6 이 책을 강의·부트캠프 교재로 채택한다면

- PPT 슬라이드(저자 제작): 요청 시 제공
- 실습 데이터 미러: 일부 데이터는 저작권상 제공 어려움, 나머지는 저장소에 포함
- 평가 문항: 각 장의 연습문제 + 중간·기말 시험 템플릿 별도 제공

---

이 책이 **끝나는 순간**이 공부의 시작입니다.
유튜브와 GitHub에서 **다음 영상·다음 커밋**으로 독자와 만나길 기대합니다.
