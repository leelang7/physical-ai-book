"""
ch16 — 대규모 분산 학습 (FSDP · Pipeline · Tensor Parallel) 골격

도서 16장 *"대규모 분산 학습 — FSDP · Pipeline · Tensor"* 의 코드 패턴.
실제 FSDP 학습은 NCCL + 다중 GPU 가 필요. 본 데모는:

  1) 단일 GPU 에서 *DDP / FSDP 가 어떻게 호출되는지* 패턴만 보여줌
  2) 동기화 시간·메모리 계산 같은 *이론값* 을 숫자로 출력

CPU 만 있어도 import 와 호출 흐름은 확인 가능.
"""
from __future__ import annotations
import os
import torch
import torch.nn as nn


def show_ddp_pattern():
    print("""
# DistributedDataParallel (DDP) 패턴 — 가장 단순한 데이터 병렬
import torch.distributed as dist
import torch.nn.parallel as parallel

dist.init_process_group("nccl", rank=RANK, world_size=WORLD_SIZE)
model = MyModel().cuda(LOCAL_RANK)
model = parallel.DistributedDataParallel(model, device_ids=[LOCAL_RANK])

# 학습 루프는 일반적인 코드와 같음 — DDP 가 알아서 gradient 동기화
for batch in loader:
    out = model(batch)
    loss = criterion(out, target)
    loss.backward()       # ← 여기서 all-reduce 자동 발생
    optimizer.step()
""")


def show_fsdp_pattern():
    print("""
# Fully Sharded Data Parallel (FSDP) — 파라미터·옵티마이저·gradient 모두 분할
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy

dist.init_process_group("nccl", rank=RANK, world_size=WORLD_SIZE)
model = MyModel().cuda(LOCAL_RANK)
model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,   # ZeRO-3 등가
    auto_wrap_policy=transformer_auto_wrap_policy,
)
# 이후 학습 루프는 DDP 와 동일하지만:
#   - 메모리 사용량 1/N (N = GPU 수)
#   - 통신량 2~3x (forward + backward 둘 다 gather/reduce)
""")


def show_pipeline_pattern():
    print("""
# Pipeline Parallel — 레이어를 GPU 별로 분할
from torch.distributed.pipeline.sync import Pipe

# 8 레이어 모델 → 4 GPU 에 2 레이어씩
layers = [Layer1(), Layer2(), Layer3(), Layer4(),
          Layer5(), Layer6(), Layer7(), Layer8()]
chunks = [
    nn.Sequential(layers[0], layers[1]).cuda(0),
    nn.Sequential(layers[2], layers[3]).cuda(1),
    nn.Sequential(layers[4], layers[5]).cuda(2),
    nn.Sequential(layers[6], layers[7]).cuda(3),
]
model = Pipe(nn.Sequential(*chunks), chunks=4)
# 4 chunks → 4-way pipeline. micro-batch 가 GPU 0→1→2→3 순서로 흘러감.
""")


def memory_estimate():
    """7B 파라미터 모델의 메모리 추정."""
    n_params_b = 7
    bytes_per_param = 4  # FP32
    fp16_bytes = 2
    print(f"\n[메모리 추정 — 7B Llama 류 모델]\n")
    full_fp32 = n_params_b * 1e9 * bytes_per_param / 1e9
    print(f"  파라미터 FP32          : {full_fp32:.1f} GB")
    print(f"  옵티마이저 Adam (m, v) : {2 * full_fp32:.1f} GB")
    print(f"  gradient FP32          : {full_fp32:.1f} GB")
    print(f"  합계 (DDP 단일 GPU)    : {4 * full_fp32:.1f} GB  ← H100 80GB 도 빠듯")
    print()
    n_gpu = 8
    print(f"  FSDP {n_gpu} GPU 분할   : {4 * full_fp32 / n_gpu:.1f} GB/GPU")
    print(f"    → 단일 GPU 만으론 학습 불가능한 모델도 8 GPU 면 가능")


def show_environment():
    print(f"\n[현재 환경 확인]")
    print(f"  torch 버전        : {torch.__version__}")
    print(f"  CUDA 가용         : {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU 개수          : {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"    GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        print(f"  GPU 없음 → 본 패턴은 *코드 골격* 으로만 참고")
    rank = int(os.environ.get("RANK", "0"))
    world = int(os.environ.get("WORLD_SIZE", "1"))
    print(f"  분산 환경 변수    : RANK={rank}  WORLD_SIZE={world}")


def main():
    print("== ch16 — FSDP · Pipeline · Tensor Parallel 패턴 ==")
    show_environment()
    print("\n[1] DDP (Data Parallel) — 가장 단순")
    show_ddp_pattern()
    print("[2] FSDP (Fully Sharded) — 메모리 1/N")
    show_fsdp_pattern()
    print("[3] Pipeline Parallel — 레이어 분할")
    show_pipeline_pattern()
    memory_estimate()
    print("\n  실제 학습: torchrun --nproc_per_node=8 train.py")
    print("  도서 16.5 절: 단일 GPU 학습이 막힌 순간이 분산 학습의 *시작점*.")


if __name__ == "__main__":
    main()
