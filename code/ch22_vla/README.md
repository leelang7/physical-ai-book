# Chapter 22 · VLA + System 1/2 주파수 분리

도서 **22장** *"World Model 과 VLA(Vision-Language-Action)"* 와 1:1 연결.

두 핵심 사상을 코드로:
1. VLA = (Vision Encoder + Language Encoder + Action Decoder)
2. System 1/2 분리 — 무거운 모델은 1 Hz, 가벼운 정책은 10 Hz

## 스크립트

| 파일 | 내용 |
|---|---|
| [`vla_system12.py`](vla_system12.py) | VLA 3-모듈 구조 + System 1/2 추론 속도 비교 + 3초 제어 루프 시뮬레이션 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch22_vla
python vla_system12.py
```

## 실측 결과 (CPU 1초)

```
[1] 추론 속도 비교
  FullVLA  단일 모델 추론: 1156 회/초
  System 1 (작은 정책) 추론: 57542 회/초
  속도비: System 1 이 약 50× 빠름

[2] 제어 루프 (System 2 1Hz, System 1 10Hz, 3초)
  System 2 호출: 3 회
  System 1 호출: 30 회
```

## 학습 포인트 (도서 본문)

1. **VLA 의 3 모듈 분해** (22.2 절) — Vision (ViT/ResNet) + Language (LLM) + Action (MLP). 본 데모는 작은 mock 으로 *구조* 만 재현. 실제 OpenVLA / RT-2 는 수십억 파라미터 + GPU 필요.
2. **System 1/2 분리** (22.4 절) — Daniel Kahneman 의 *시스템 1 (빠른 직관) / 시스템 2 (느린 추론)* 개념 차용. 모든 step 마다 LLM 전체를 굴리지 못하니, System 2 가 *목표 임베딩* 만 가끔 갱신하고 System 1 이 그 임베딩 + 가벼운 관측으로 빠른 제어.
3. **본 데모는 toy 모델로도 50× 차이** — 실제 OpenVLA (7B 파라미터) 는 차이가 10000× 이상. System 1/2 분리가 *선택* 이 아니라 *필수*.

## 핵심 코드

```python
class System2Slow(nn.Module):     # 1 Hz — Vision + Language + 융합
    def forward(self, img, tokens):
        return self.fuse(cat(vision(img), language(tokens)))

class System1Fast(nn.Module):     # 10 Hz — 목표 임베딩 + 관측 → 행동
    def forward(self, goal, obs):
        return self.net(cat(goal, obs))

# 제어 루프
if step % 10 == 0:                # 1 Hz
    goal = sys2(img, tokens)
action = sys1(goal, current_obs)  # 10 Hz
```

이게 Tesla FSD / Figure / OpenVLA 의 실제 제어 구조와 동일.

## 한계 — 실제 학습은 별도

- 본 데모의 mock 모델은 *추론 구조* 만 시연. 학습은 안 함
- 실제 OpenVLA 학습 = Open X-Embodiment 데이터셋 + 8 × A100 GPU
- 추론 시연도 7B 파라미터 모델 다운로드 + GPU 필요

본 디렉토리는 *Tesla 책 본문 22장의 사상 검증* 까지가 목표.

## 다음

- [ch20 BC + DAgger](../ch20_bc_dagger/) — VLA 학습의 베이스라인 (모방학습)
- [ch27 Isaac Lab](../ch27_isaac_lab/) — Franka + OpenVLA 통합 (M4 공개)
