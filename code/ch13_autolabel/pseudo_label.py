"""
ch13 — Auto-labeling 의 가장 단순한 형태 (Pseudo-Label)

도서 13장 *"Auto-labeling — 사람 없이 라벨을"* 의 핵심.
*소량의 사람 라벨* 로 모델 학습 → 모델이 *대량 무라벨 데이터* 에 라벨 추정 →
신뢰도 높은 추정만 골라 학습 데이터에 추가 → 반복.

Tesla 의 Auto-labeler 도 같은 원리. 사람이 직접 라벨링 못하는 수억 프레임에
다른 강한 모델 (오프라인 LiDAR 모델 등) 이 *teacher* 로 작용해 학습 라벨 생성.

본 데모: 2D 점 분류 toy. 100 라벨 + 1000 무라벨 → pseudo-labeling 으로 confidence
       threshold 위 것만 학습 데이터로 추가.
"""
from __future__ import annotations
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------- 합성 데이터 ----------
def make_two_moons(n: int, noise: float = 0.15, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """전형적 비선형 분류 toy — 두 반달 형태."""
    rng = np.random.default_rng(seed)
    n_a, n_b = n // 2, n - n // 2
    theta = rng.uniform(0, np.pi, n_a)
    A = np.stack([np.cos(theta), np.sin(theta)], axis=-1)
    theta = rng.uniform(0, np.pi, n_b)
    B = np.stack([1 - np.cos(theta), 0.5 - np.sin(theta)], axis=-1)
    X = np.concatenate([A, B], axis=0) + rng.normal(0, noise, (n, 2))
    y = np.concatenate([np.zeros(n_a, dtype=np.int64),
                        np.ones(n_b, dtype=np.int64)], axis=0)
    perm = rng.permutation(n)
    return X[perm].astype(np.float32), y[perm]


# ---------- Teacher 모델 ----------
class Classifier(nn.Module):
    def __init__(self, hidden: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 2),
        )

    def forward(self, x):
        return self.net(x)


def train(model: Classifier, X: np.ndarray, y: np.ndarray, n_epochs: int = 200) -> float:
    Xt = torch.tensor(X)
    yt = torch.tensor(y)
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    for _ in range(n_epochs):
        logits = model(Xt)
        loss = F.cross_entropy(logits, yt)
        opt.zero_grad()
        loss.backward()
        opt.step()
    return float(loss.item())


def evaluate(model: Classifier, X: np.ndarray, y: np.ndarray) -> float:
    model.eval()
    with torch.no_grad():
        logits = model(torch.tensor(X))
        acc = (logits.argmax(-1).numpy() == y).mean()
    model.train()
    return float(acc)


# ---------- Pseudo-labeling ----------
def pseudo_label(model: Classifier, X_unlabeled: np.ndarray,
                 conf_thresh: float = 0.95) -> tuple[np.ndarray, np.ndarray]:
    """모델 확률이 conf_thresh 이상인 샘플만 골라 (X_sel, y_pred) 반환."""
    model.eval()
    with torch.no_grad():
        probs = F.softmax(model(torch.tensor(X_unlabeled)), dim=-1).numpy()
    confidence = probs.max(axis=-1)
    pseudo = probs.argmax(axis=-1)
    mask = confidence > conf_thresh
    model.train()
    return X_unlabeled[mask], pseudo[mask].astype(np.int64)


# ---------- 데모 ----------
def main() -> None:
    torch.manual_seed(0)

    # 학습 데이터 100개 (사람 라벨) + 무라벨 1000개 + 평가 500개
    X_train, y_train = make_two_moons(100, seed=1)
    X_unlab, _y_hidden = make_two_moons(1000, seed=2)
    X_test, y_test = make_two_moons(500, seed=3)

    print("== ch13 Pseudo-labeling 데모 ==\n")

    # 1) Baseline — 100 라벨만으로 학습
    base = Classifier()
    train(base, X_train, y_train)
    acc_base = evaluate(base, X_test, y_test)
    print(f"[Baseline] 100 라벨만으로 학습: 정확도 {100 * acc_base:.1f}%")

    # 2) Pseudo-labeling 라운드
    teacher = Classifier()
    teacher.load_state_dict(base.state_dict())  # baseline 으로 시작
    X_cum, y_cum = X_train, y_train

    for r in range(1, 4):
        X_sel, y_sel = pseudo_label(teacher, X_unlab, conf_thresh=0.90)
        if len(X_sel) == 0:
            print(f"[라운드 {r}] confidence > 0.9 인 샘플 없음 — 중단")
            break
        X_cum = np.concatenate([X_cum, X_sel], axis=0)
        y_cum = np.concatenate([y_cum, y_sel], axis=0)
        teacher = Classifier()
        train(teacher, X_cum, y_cum)
        acc = evaluate(teacher, X_test, y_test)
        print(f"[라운드 {r}] +{len(X_sel)} pseudo-labels  누적 {len(X_cum)}  정확도 {100 * acc:.1f}%")

    print(f"\n  의미: 사람 라벨 100 → pseudo 추가 → 무라벨 데이터 활용 → 성능 ↑")
    print(f"  Tesla Auto-labeler 도 동일 원리 — *강한 teacher* + *대량 무라벨* + *confidence 필터링*")


if __name__ == "__main__":
    main()
