# Chapter 16 · 분산 학습 — DDP · FSDP · Pipeline

도서 **16장** *"대규모 분산 학습 — FSDP · Pipeline · Tensor Parallel"* 와 1:1 연결.

다중 GPU 환경이 없어도 *호출 패턴 + 메모리 추정* 은 확인 가능. 본 디렉토리는 *코드 골격 + 이론값* 까지.

## 스크립트

| 파일 | 내용 |
|---|---|
| [`ddp_skeleton.py`](ddp_skeleton.py) | DDP / FSDP / Pipeline 의 호출 패턴 + 7B 모델 메모리 추정 |

## 실행

```bash
cd code/environment && bash setup.sh && source .venv/bin/activate
cd ../ch16_distributed
python ddp_skeleton.py
```

## 학습 포인트

1. **DDP 가 시작점** (16.2 절) — 모델이 GPU 1대에 들어가면 DDP. 들어가면 끝.
2. **FSDP 가 한계 돌파** (16.3 절) — 모델이 GPU 1대에 안 들어가면 FSDP. 파라미터·gradient·optimizer state 를 N GPU 에 분할 → 메모리 1/N.
3. **Pipeline 은 마지막 수단** (16.4 절) — FSDP 로도 안 되면 Pipeline. 레이어를 GPU 마다 다른 게 쌓아 직렬 처리. 구현 복잡, 디버깅 어려움.

## 실제 학습 명령

```bash
# DDP (8 GPU)
torchrun --nproc_per_node=8 train.py

# FSDP (다중 노드)
torchrun --nproc_per_node=8 --nnodes=4 --node_rank=$NODE_RANK \
    --master_addr=$HEAD_IP train_fsdp.py
```

본 데모는 *호출 흐름* 만 보여줌. 진짜 학습은 H100 · A100 클러스터 + InfiniBand 필요.

## 다음

- [ch24 Mini HydraNet](../ch24_mini_hydra/) — 단일 GPU 로 학습 가능한 작은 모델
- [ch17 Quantization](../ch17_quant/) — 학습 후 모델을 차량에 배포할 때
