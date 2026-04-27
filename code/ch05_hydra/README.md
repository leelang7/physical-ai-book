# Chapter 05 · HydraNet — 백본 · Neck · 멀티 헤드

도서 **5장 *"백본부터 헤드까지 — HydraNet의 구조"*** 와 1:1 로 연결되는 실습 코드.

## 이 디렉토리의 스크립트

| 파일 | 다루는 내용 |
|---|---|
| [`hydranet_skeleton.py`](hydranet_skeleton.py) | ResNet18 백본 + FPN Neck + 3 헤드 (Lane / Object / Sign) 의 골격 PyTorch 구현 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch05_hydra
python hydranet_skeleton.py
```

산출:
```
== HydraNet Mini — 헤드별 출력 텐서 ==
  lane     shape: [1, 4, 56, 56]    # 차선 분할 — 4 클래스 × 1/4 해상도
  obj_cls  shape: [1, 10, 28, 28]   # 객체 분류 — 10 클래스 × 1/8 해상도
  obj_reg  shape: [1, 4, 28, 28]    # 객체 박스 회귀 (cx, cy, w, h)
  sign     shape: [1, 20]           # 표지판 전역 분류 — 20 클래스
  총 파라미터  : 11.91 M
```

## 학습 포인트 (도서 본문 참조)

1. **하나의 백본, 여러 헤드** (5.2 절) — Tesla AI Day 가 보여 준 *"하나의 망에서 여러 작업"* 구조의 가장 작은 형태. 백본은 공유, 헤드만 분기.
2. **헤드별로 다른 해상도** (5.4 절) — 차선은 픽셀 단위 정밀도 필요 → 1/4 해상도 사용. 표지판은 *"있다 / 없다 / 무엇"* 만 알면 되니 전역 평균. 객체는 중간.
3. **FPN Neck 의 역할** (5.3 절) — 작은 객체(멀리 있는 차) 를 놓치지 않으려면 큰 해상도의 작은 채널과 작은 해상도의 큰 채널을 합쳐야 합니다. BiFPN 은 양방향이지만 본 데모는 단순 top-down.

## 다음 단계 — 학습으로 확장

본 코드는 *임의 초기화* 모델로 forward 만 합니다. 실제 학습은:

1. **8장 헤드 통합** : 같은 헤드들을 8대 카메라 입력에 맞춰 확장 → [`code/ch08_heads/`](../ch08_heads/) (M2 공개)
2. **24장 풀 실습** : BDD100K 와 YOLOv8 를 결합한 학습 가능한 미니 HydraNet → [`code/ch24_mini_hydra/`](../ch24_mini_hydra/) (M3 공개)

## 영상 · 이슈

- YouTube : *"All That AI · Tesla Book Ch.05"* (영상 누적 시 채널 검색)
- 이슈 / 질문 : https://github.com/leelang7/physical-ai-book/issues
