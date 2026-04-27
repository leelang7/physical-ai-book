# Chapter 04 · ISP — Bayer 디모자이크와 화이트밸런스

도서 **4장 *"카메라 센서와 이미지 신호 처리(ISP)"*** 와 1:1 로 연결되는 실습 코드입니다.

## 이 디렉토리의 스크립트

| 파일 | 다루는 내용 | 실행 시간 (CPU) |
|---|---|---|
| [`bayer_demosaic.py`](bayer_demosaic.py) | RGGB 모자이크 시뮬레이션 + bilinear vs Malvar 디모자이크 PSNR 비교 | ~1초 |
| [`white_balance.py`](white_balance.py) | Gray-World · Max-RGB 두 화이트밸런스 알고리즘 비교 | ~1초 |

GPU 불필요. `code/environment/` 의 공용 환경에서 그대로 동작합니다.

## 실행

```bash
# 환경 활성화 (한 번만)
cd code/environment && bash setup.sh && source .venv/bin/activate

# 디모자이크 데모
cd ../ch04_isp
python bayer_demosaic.py

# 화이트밸런스 데모
python white_balance.py
```

산출 PNG 는 같은 디렉토리에 저장됩니다.

## 학습 포인트 (도서 본문 참조)

1. **디모자이크가 왜 어려운가** — 픽셀당 색 정보가 1/3 만 남는 정보 손실 문제. 단순 보간(bilinear)은 가장자리에서 색 번짐(zipper artifact) 발생. Malvar 5×5 그래디언트 보정이 표준 ISP 의 출발점.
2. **PSNR 만으로는 평가 부족** — Malvar 가 PSNR 에서 1~2 dB 우위지만, 실제로는 색 노이즈 · 해상도 보존 등 시각적 평가가 더 중요합니다 (도서 4.4 절).
3. **WB 는 "어느 게 흰색인가" 가정** — Gray-World 와 Max-RGB 결과 차이를 직접 보면, 자율주행 카메라가 *터널 진입* · *일몰* 같은 색온도 급변 상황에서 왜 통합 ISP 가 필요한지 체감 가능합니다.

## 다음 단계

- **5장 HydraNet** : ISP 출력을 받아서 신경망 백본이 어떻게 처리하는지 → [`code/ch05_hydra/`](../ch05_hydra/)
- **8장 Heads** : 멀티 카메라 헤드 통합 → [`code/ch08_heads/`](../ch08_heads/)

## 영상 · 이슈

- YouTube : *"All That AI · Tesla Book Ch.04"* (영상 누적 시 채널 검색)
- 이슈 / 질문 : https://github.com/leelang7/physical-ai-book/issues
