# 16장. 대규모 분산 학습 — FSDP · Pipeline · Tensor Parallel

> **학습 목표**
> 이 장을 마치면 DDP·FSDP·Tensor Parallel·Pipeline Parallel 각각의 차이를 자신의 언어로 설명할 수 있고, 수백억 파라미터 모델을 어느 방식으로 쪼개야 하는지 판단할 수 있다. PyTorch에서 FSDP를 이용한 기본 학습 코드를 작성하고, 자율주행 파운데이션 모델의 실제 분산 구성을 그려낸다.

---

## 16.1 왜 분산 학습이 필요한가

단일 H100 GPU의 메모리는 80GB다. 이는 수십억 파라미터 모델 하나조차 fp16으로 겨우 담을 수 있는 수준이다. 학습에는 파라미터 외에도 옵티마이저 상태와 gradient, 활성화가 추가로 필요하므로 실제 수용 가능한 모델은 더 작다. 자율주행 파운데이션 모델은 수백억 파라미터를 넘어서는 추세이고, 데이터는 수 TB에서 수 PB 단위다. 혼자 학습할 수 있는 규모가 아니다.

분산 학습의 목표는 두 가지다. **메모리**를 여러 GPU로 나누어 큰 모델을 담을 수 있게 하는 것, 그리고 **연산**을 병렬화해 학습 시간을 줄이는 것이다. 이 두 목표가 서로 긴장한다. 메모리를 나누면 통신이 늘어나고, 통신이 늘면 전체 속도가 느려진다. 좋은 분산 설계는 이 trade-off의 스윗 스팟을 찾는다.

---

## 16.2 네 가지 병렬화 전략

분산 학습에는 네 개의 큰 축이 있다.

**Data Parallel**이 가장 단순한 방식이다. 모델 전체를 각 GPU에 복사해 두고, 다른 미니배치를 각 GPU가 처리한 뒤, gradient를 all-reduce로 동기화한다. PyTorch의 `DistributedDataParallel(DDP)` 이 이 방식의 표준 구현이다. 구현이 쉽고 효율적이지만 **모델이 단일 GPU에 들어가야 한다**는 제약이 있다. 수십억 파라미터 모델에서는 이 제약이 곧 벽이 된다.

**Fully Sharded Data Parallel(FSDP)** 는 이 제약을 뚫는다. 모델 파라미터·gradient·옵티마이저 상태를 여러 GPU에 **샤딩**해 각자가 일부만 보관한다. forward와 backward 시점에 필요한 부분을 all-gather로 임시로 모으고, 쓰임이 끝나면 다시 버린다. 이 방식이 Microsoft의 ZeRO-3와 사상적으로 같다. 장점은 매우 큰 모델을 학습할 수 있다는 것이고, 단점은 통신 오버헤드가 DDP보다 크다는 것이다. 실무에서 가장 자주 쓰이는 기본값이다.

**Tensor Parallel(TP)** 은 한 레이어 내부의 **행렬을 쪼갠다**. 예를 들어 (d, 4d) 크기의 linear 레이어를 (d, 2d) 두 개로 분할해 두 GPU가 각각 처리한 뒤 결과를 합친다. NVIDIA의 Megatron-LM이 이 방식의 대표다. 매우 큰 레이어가 있는 모델(LLM의 MLP block 같은)에서 유효하며, 빠른 통신 인프라(NVLink)가 필수다. 구현이 까다롭고 디버깅이 어렵다.

**Pipeline Parallel(PP)** 은 모델을 **레이어 덩어리**로 분할해 GPU 간 파이프라인으로 흘린다. GPU 0이 첫 4개 레이어, GPU 1이 다음 4개, 이렇게 이어진다. 메모리 절약 효과가 크지만, 파이프라인 버블(앞 GPU의 결과를 기다리며 뒷 GPU가 놀고 있는 시간)이 발생한다. 이 버블을 줄이기 위한 1F1B, Interleaved 같은 스케줄링 기법들이 있다.

---

## 16.3 3D / 4D Parallelism — 조합하는 기술

GPT-4급 대형 모델의 학습은 네 가지 전략을 **섞어 쓴다**. 전형적인 조합이 다음과 같다.

```
외부 축: Data Parallel × Pipeline Parallel
내부 축: Tensor Parallel × Sequence Parallel
```

예를 들어 1024개 GPU를 쓴다면 (8 PP) × (8 TP) × (16 DP) = 1024로 분할하는 식이다. 각 축의 크기는 모델 구조·네트워크 토폴로지·GPU 메모리에 따라 정해진다. 이 조합을 **3D Parallelism**, 여기에 Sequence Parallel을 더하면 **4D Parallelism**이라 부른다.

자율주행 파운데이션 모델의 경우, 시간 축 입력(수 초의 영상)이 매우 길기 때문에 Sequence Parallel이 유용하다. Pipeline Parallel은 여러 카메라의 처리 단계를 GPU 간에 나누기 좋고, Tensor Parallel은 큰 Transformer 블록에 적용할 수 있다. Dojo의 2D 메시 토폴로지는 Tensor Parallel을 자연스럽게 지원하는 구조이기도 하다.

---

## 16.4 PyTorch FSDP — 최소 예제

PyTorch에서 FSDP를 설정하는 최소 코드는 다음과 같다.

```python
import torch
import torch.distributed as dist
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy

dist.init_process_group("nccl")
torch.cuda.set_device(dist.get_rank())

model = MyBigTransformer().cuda()

policy = transformer_auto_wrap_policy(
    transformer_layer_cls={MyTransformerBlock},
)
model = FSDP(model, auto_wrap_policy=policy, sharding_strategy="FULL_SHARD")

optim = torch.optim.AdamW(model.parameters(), lr=3e-4)

for batch in loader:
    optim.zero_grad()
    out = model(batch.cuda())
    loss = out.loss
    loss.backward()
    optim.step()
```

실행은 `torchrun --nnodes 1 --nproc_per_node 8 train.py` 같은 명령으로 한다. 이 작은 설정 하나로 단일 노드의 8 GPU에 모델이 분산된다. 실제 프로덕션에서는 활성화 체크포인팅, 혼합 정밀도, gradient clipping, learning rate 스케줄이 더 얹힌다.

---

## 16.5 자율주행 파운데이션 모델의 분산 관행

공개된 정보와 합리적 추정을 결합하면, Tesla FSD v13의 분산 구성은 다음과 같이 그려진다. 파라미터 규모는 30~100B 사이로 추정되고, 입력은 8 카메라의 최근 5초 영상에 센서 상태가 더해진다. 이 정도 크기에서 FSDP + Pipeline이 필수이고, Tensor Parallel이 대형 MLP 블록에 적용될 것이다. 시간 축의 길이 때문에 Sequence Parallel도 의미 있을 것으로 보인다.

학습 스텝 한 번에 들어가는 토큰 수를 계산해 보면, 한 GPU에서는 메모리가 터지기 쉽다는 것을 금방 알 수 있다. 여러 카메라의 수십 초 영상 + 여러 태스크 손실 + 대형 모델의 조합은 FSDP의 샤딩 없이는 담기조차 어렵다.

---

## 16.6 효율화 3종 세트 — Gradient Checkpointing, Flash Attention, Mixed Precision

분산 학습의 효율화 기법 가운데 가장 자주 쓰이는 세 가지가 있다.

**Gradient Checkpointing**은 중간 활성화를 저장하지 않고 backward 시 재계산하는 기법이다. 메모리를 크게 아끼는 대신 연산 시간이 약 30% 늘어난다. 큰 모델 학습에서는 이 trade-off가 거의 항상 유리하다. PyTorch의 `torch.utils.checkpoint.checkpoint_sequential`이 표준 구현이다.

**Flash Attention**은 15장에서 설명한 대로 Attention을 GPU의 SRAM에서 블록 단위로 계산해 DRAM 접근을 줄인다. 2~4배의 속도 향상과 메모리 절약을 동시에 준다. 2024년 이후로는 PyTorch가 자동으로 활성화한다.

**Mixed Precision**은 BF16을 기본으로 쓰고, 민감한 부분만 FP32를 유지한다. 속도와 메모리를 동시에 줄인다. `torch.cuda.amp.autocast`가 표준 인터페이스다. H100 이상에서는 FP8도 점차 실용화되고 있다.

이 세 기법을 함께 쓰면 같은 GPU 수로 **2~4배 더 큰 모델**을 학습할 수 있다. 실무의 기본 세팅이라 생각해도 좋다.

---

## 16.7 대규모 학습의 운영 — 장애와 복구

수천 GPU가 일주일 이상 학습을 돌리면 **하루에 수십 번씩 노드 장애**가 난다. 이 장애를 감지하고 복구하는 시스템이 대규모 학습의 숨은 절반이다.

체크포인트 저장이 첫 번째 안전망이다. 보통 1000 스텝마다 비동기로 저장하되, 학습 자체를 멈추지 않도록 한다. 장애가 나면 마지막 체크포인트에서 재시작한다. 자동 복구 시스템은 실패 노드를 제외하고 재분산하며, 전체 재시작 없이 계속 진행한다. Loss spike 감지는 학습이 **이상 수렴 상태**에 빠졌을 때 자동으로 롤백하는 기능이다. NaN이 발생하거나 loss가 갑자기 폭증하면 마지막 안정 체크포인트로 돌아간다.

Tesla, Google DeepMind, Meta, OpenAI 같은 대형 AI 조직은 모두 자체 학습 인프라 팀을 두고 이 문제를 다룬다. 학계에서 이런 규모의 학습이 드문 이유도 여기에 있다. 알고리즘만으로는 부족하고, **시스템 엔지니어링**이 성패를 가른다.

---

## 장말 정리

분산 학습의 네 축 — DP·FSDP·TP·PP — 은 각자의 강점과 제약이 다르다. 대형 모델 학습은 이들을 조합한 3D 또는 4D Parallelism으로 이루어진다. FSDP가 실무의 기본값이며, FlashAttention·BF16·Gradient Checkpointing이 효율화의 3종 세트다. 자율주행 파운데이션 모델은 긴 시간 축 입력과 대형 백본 때문에 이 모든 기법이 필요하다. 알고리즘 못지않게 장애·모니터링·복구 같은 **운영 측면**이 대규모 학습의 실제 성패를 가른다.

## 연습문제

1. FSDP와 Tensor Parallel의 차이를 "통신 패턴" 관점에서 대조적으로 설명하라.
2. Pipeline Parallel의 버블을 줄이는 1F1B와 Interleaved 스케줄링을 조사해 각자의 원리를 요약하라.
3. 본인이 가진 단일 GPU(예: 24GB)에서 FSDP 없이 학습 가능한 최대 파라미터 수를 대략 추산하고, FSDP를 쓰면 얼마까지 늘어날지 계산하라.
