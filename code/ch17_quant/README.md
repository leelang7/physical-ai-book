# Chapter 17 · 양자화 + ONNX (차량 배포 직전 단계)

도서 **17장** *"양자화 · ONNX · 차량 배포"* 와 1:1 연결.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`quant_onnx.py`](quant_onnx.py) | FP32 모델 → PTQ INT8 양자화 → ONNX export 전체 파이프라인 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch17_quant
python quant_onnx.py
```

## 결과 (참고)

```
FP32 추론   : 0.594 ms/batch
INT8 추론   : 0.660 ms/batch  (0.88× — 작은 모델/CPU 에선 양자화 손해)
정확도 차이 : 0.2%  (실제로 거의 동일)
ONNX 크기   : 22 KB
```

## **왜 CPU 데모에선 INT8 가 더 느린가**

PyTorch CPU 양자화는 *작은 모델 + 짧은 추론* 에서 오버헤드 (dequant/quant 노드) 가 더 큼. 진가는:

| 환경 | 효과 |
|---|---|
| CPU + 작은 모델 (본 데모) | 0.8× ~ 1.2× (이득 미미) |
| GPU + 큰 모델 (실제 차량 모델) | 1.5× ~ 4× |
| NVIDIA Jetson / TensorRT INT8 | 3× ~ 8× |
| Tesla FSD 칩 (자체 양자화) | 5× ~ 10× |

본 데모는 *흐름만* 시연. 진짜 이득은 *Edge 실리콘* 에서.

## 학습 포인트

1. **PTQ 가 가장 흔함** (17.2 절) — 학습 끝난 모델에 *작은 캘리브레이션 데이터* 만 흘려서 양자화 범위 측정. QAT (학습 중 양자화) 는 더 정확하지만 학습 코드 수정 필요.
2. **ONNX 가 *교환 표준*** (17.3 절) — PyTorch → ONNX → TensorRT / OpenVINO / 차량 SoC. 직접 SoC 코드 쓰는 회사 (Tesla) 도 있지만, 대부분 ONNX 경유.
3. **정확도 손실 1~2% 가 표준** (17.4 절) — 모델 크기에 따라. 매우 큰 모델은 0.5% 이하, 작은 모델은 3% 까지도. 양자화 *민감 레이어* (입출력 가까운) 는 FP16 으로 남기는 *mixed precision* 흔함.

## 다음

- [ch24 Mini HydraNet](../ch24_mini_hydra/) — 학습된 모델 → 본 디렉토리 패턴으로 양자화
- 실제 차량 배포 — Tesla 칩 / NVIDIA DRIVE Orin / Mobileye EyeQ6 의 SDK 별도 필요
