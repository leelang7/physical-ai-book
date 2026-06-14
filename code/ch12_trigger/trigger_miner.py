"""
ch12 — Fleet Data Trigger 와 Edge Case Miner

도서 12장 *"플릿 데이터 수집과 Trigger 디자인"* 의 핵심.
대규모 차량 데이터에서 *"학습에 가치 있는 프레임"* 만 골라내는 trigger 패턴.

데이터 100% 를 학습에 쓰는 게 아니라, 모델이 *틀렸을 만한 프레임* 만 골라
데이터 엔진의 진가가 살아남. Tesla 의 Auto-labeler + Miner 가 동일 원리.

본 데모: 합성 100 프레임 시퀀스에서 4 종 trigger 로 *interesting* 프레임 추출.
"""
from __future__ import annotations
import numpy as np


# ---------- 합성 프레임 시퀀스 ----------
def make_frame_log(n_frames: int = 100, seed: int = 0) -> list[dict]:
    """가짜 차량 로그 — 각 프레임에 모델 예측, GT 일부, 차량 상태 포함."""
    rng = np.random.default_rng(seed)
    log = []
    for t in range(n_frames):
        # 평상시: 모델 예측 ≈ GT, 가속도 작음
        is_edge = rng.random() < 0.08  # 8% edge case 비율
        model_steer = rng.normal(0, 0.05)
        gt_steer = model_steer + rng.normal(0, 0.05)  # 평소엔 비슷
        accel = rng.normal(0, 0.5)
        if is_edge:
            # 엣지 케이스: 큰 불일치, 급가속/급제동, 의외의 조향
            gt_steer = model_steer + rng.normal(0, 0.5)  # 크게 다름
            accel = rng.normal(0, 3.0)
        log.append({
            "t": t,
            "model_steer": float(model_steer),
            "gt_steer": float(gt_steer),
            "accel": float(accel),
            "speed_mps": float(rng.uniform(5, 25)),
            "is_edge_truth": is_edge,  # 정답 라벨 (평가용)
        })
    return log


# ---------- 4 종 Trigger ----------
def trigger_disagreement(frame: dict, thresh: float = 0.3) -> bool:
    """T1: 모델 vs GT (또는 운전자) 의 큰 조향 불일치."""
    return abs(frame["model_steer"] - frame["gt_steer"]) > thresh


def trigger_sudden_brake(frame: dict, thresh: float = -2.0) -> bool:
    """T2: 급제동 (운전자 개입 신호)."""
    return frame["accel"] < thresh


def trigger_sudden_accel(frame: dict, thresh: float = 2.5) -> bool:
    """T3: 급가속 (위험 회피 가능성)."""
    return frame["accel"] > thresh


def trigger_high_speed_steer(frame: dict, speed_thresh: float = 20.0,
                             steer_thresh: float = 0.2) -> bool:
    """T4: 고속에서 큰 조향 — 차선 변경 또는 회피."""
    return frame["speed_mps"] > speed_thresh and abs(frame["gt_steer"]) > steer_thresh


# ---------- Miner ----------
def mine_interesting(log: list[dict]) -> dict[str, list[int]]:
    """각 trigger 별로 *interesting* 프레임 인덱스 리스트 반환."""
    triggers = {
        "T1_disagreement": trigger_disagreement,
        "T2_sudden_brake": trigger_sudden_brake,
        "T3_sudden_accel": trigger_sudden_accel,
        "T4_highspeed_steer": trigger_high_speed_steer,
    }
    selected: dict[str, list[int]] = {name: [] for name in triggers}
    for i, frame in enumerate(log):
        for name, fn in triggers.items():
            if fn(frame):
                selected[name].append(i)
    return selected


def evaluate_recall(log: list[dict], selected: dict[str, list[int]]) -> dict[str, float]:
    """Miner 가 *진짜 edge case* 를 얼마나 잡았는지 (recall)."""
    truth = {i for i, f in enumerate(log) if f["is_edge_truth"]}
    all_selected = set()
    for ids in selected.values():
        all_selected |= set(ids)
    if not truth:
        return {"recall": 0.0, "precision": 0.0}
    hit = len(truth & all_selected)
    return {
        "recall": hit / len(truth),
        "precision": hit / max(1, len(all_selected)),
    }


# ---------- 데모 ----------
def main() -> None:
    log = make_frame_log(n_frames=200, seed=42)
    n_edge = sum(1 for f in log if f["is_edge_truth"])
    print(f"== ch12 Trigger + Miner 데모 ==\n")
    print(f"  총 {len(log)} 프레임, 그 중 {n_edge} 개가 *진짜 edge case* (truth)")
    print()

    selected = mine_interesting(log)
    print(f"[Trigger 별 선택된 프레임 수]")
    for name, ids in selected.items():
        print(f"  {name:22s} : {len(ids):3d} 프레임")

    total = set()
    for ids in selected.values():
        total |= set(ids)
    print(f"\n  중복 제거 후 총 선택: {len(total)} 프레임 ({100 * len(total) / len(log):.1f}%)")
    print(f"  = 전체 데이터 중 {100 * len(total) / len(log):.0f}% 만 학습 큐로 보냄")

    metrics = evaluate_recall(log, selected)
    print(f"\n[성능]")
    print(f"  Recall    : {100 * metrics['recall']:.1f}%  (진짜 edge case 중 잡힌 비율)")
    print(f"  Precision : {100 * metrics['precision']:.1f}%  (선택 프레임 중 진짜 edge 비율)")
    print(f"\n  의미: 전체 200 프레임 중 ~30~50 프레임 ({len(total)}p) 만 학습에 쓰면 됨.")
    print(f"  Tesla 의 fleet data engine 도 같은 원리 — 데이터 양이 아니라 *희소성* 이 핵심.")


if __name__ == "__main__":
    main()
