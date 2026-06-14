# Chapter 26 · openpilot 리버스 엔지니어링

도서 **26장** *"openpilot 리버스 엔지니어링"* 와 1:1 연결.

Comma.ai 의 openpilot 은 *오픈된 자율주행 스택* — 모델 아키텍처·추론 코드·실차 적용까지 모두 공개. **Tesla 의 *closed* 시스템을 *open* 으로 학습** 하는 가장 빠른 길.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`openpilot_analysis.py`](openpilot_analysis.py) | supercombo 모델 구조 / ONNX 추론 패턴 / 우리 책과의 연결 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch26_openpilot
python openpilot_analysis.py
```

## 실제 모델 분석을 원한다면

```bash
git clone https://github.com/commaai/openpilot
cd openpilot
git lfs install
git lfs pull
ls models/supercombo.onnx   # ONNX 모델

pip install onnxruntime
python  # 그 다음 openpilot_analysis.py 의 [2] 패턴 그대로 실행
```

## 학습 포인트

1. **모델은 작다** (26.2 절) — supercombo 는 6~8M params. Tesla FSD 도 차량 추론용은 *작은 양자화 모델*. *대형 모델은 학습 서버*, *작은 모델은 차량*.
2. **출력이 풍부함** (26.3 절) — plan + lane + road_edge + lead + desire_pred. 단일 forward → 모든 task. 우리 책의 ch05/ch24 HydraNet 의 실증.
3. **Features Buffer = Temporal modeling** (26.4 절) — 99 step × 512 dim 의 이전 feature 누적. RNN 없이도 시계열 안정성 확보. Tesla 도 비슷한 패턴.
4. **Desire / Traffic 입력** (26.5 절) — 운전자 의도·신호등 같은 기호적 입력 포함. VLA (ch22) 의 *언어/명령 입력* 단순화.

## 다음

- [ch05 HydraNet](../ch05_hydra/) / [ch24 Mini HydraNet](../ch24_mini_hydra/) — 우리 책의 멀티헤드 구현
- [ch22 VLA](../ch22_vla/) — 기호적 입력의 확장 버전
- [ch17 Quantization](../ch17_quant/) — supercombo 도 양자화돼 차량에 배포
