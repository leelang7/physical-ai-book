# 부록 A. 수학 속성 복습 — 선형대수 · 확률 · 최적화

> 이 부록은 **사전 교재가 아니다**. 본문에서 쓰인 수학을 **빠르게 상기**하기 위한 요약이다. 더 깊은 학습이 필요하다면 Strang, Bishop, Boyd의 표준 교재를 참조하라.

---

## A.1 선형대수

### 벡터와 행렬
- 내적(dot product): `<x, y> = Σ x_i y_i`
- 외적(outer product): `x y^T ∈ R^{m×n}`
- 행렬곱: `(AB)_ij = Σ_k A_ik B_kj`

### 고유값·특이값
- 고유값: `Av = λv`
- SVD: `A = U Σ V^T` (모든 행렬에 존재)
- 응용: PCA, 저랭크 근사

### 텐서 연산 (PyTorch)
- `einsum`: `torch.einsum("bij,bjk->bik", A, B)`
- 배치 행렬곱: `torch.bmm`
- 고차원: attention의 softmax 연산이 SVD보다 단순해 보이지만 내부는 여전히 행렬곱 기반

---

## A.2 미분과 역전파

### 체인 룰
`dL/dx = dL/dy · dy/dx`

### 자코비안
- `J_f(x) ∈ R^{m×n}` where `f: R^n → R^m`
- Forward-mode AD = Jvp(Jacobian-vector product)
- Reverse-mode AD = Vjp (역전파)

### 그래디언트 체크
수치 그래디언트와 분석 그래디언트 차이:
```
(f(x+ε) - f(x-ε)) / (2ε) ≈ df/dx
```

---

## A.3 확률

### 기본 분포
- Bernoulli, Categorical
- Gaussian: `N(μ, σ²)`
- Multivariate Gaussian: `N(μ, Σ)`

### 베이즈 정리
`p(θ|x) = p(x|θ) p(θ) / p(x)`

### KL 발산
`KL(p || q) = Σ p(x) log(p(x)/q(x))`
- 비대칭
- 정보 이득 측도

### 크로스 엔트로피
`H(p, q) = -Σ p(x) log q(x)`
- 분류 손실의 기본

### Entropy
`H(p) = -Σ p(x) log p(x)`
- 탐색·Regularization에 사용

---

## A.4 최적화

### 경사하강법 계열
- SGD: `θ ← θ - η ∇L`
- Momentum, Nesterov
- AdaGrad, RMSProp, Adam, AdamW

### Learning Rate 스케줄
- Cosine Annealing: `η_t = η_min + (η_max - η_min)·(1 + cos(π·t/T))/2`
- Warmup + Decay
- One-cycle

### 정규화
- L2 (weight decay)
- Dropout
- Label Smoothing
- Mixup, CutMix

### 제약 최적화
- Lagrangian: `L = f - λ·g`
- KKT 조건

---

## A.5 신경망 특화 수학

### Softmax
`softmax(z)_i = exp(z_i) / Σ exp(z_j)`
- Overflow 방지: `softmax(z) = softmax(z - max(z))`

### Attention
```
Attn(Q, K, V) = softmax(QK^T / √d_k) V
```
- 계산 복잡도: `O(N² d)`

### Convolution
`(f * g)(t) = Σ_τ f(τ) g(t - τ)`
- PyTorch의 conv는 사실 **상관(correlation)** 이지만 관행상 convolution으로 부름

---

## A.6 차량·로봇 특화

### 호모지니어스 좌표
`[x, y, 1]^T` — 투영 변환의 편의

### 회전 행렬
3D: Rx, Ry, Rz 조합, 또는 Rodrigues 공식

### 쿼터니언
`q = w + xi + yj + zk` — 짐벌락 없는 회전 표현

### 칼만 필터
- 예측: `x_t|t-1 = F x_t-1|t-1`
- 업데이트: `x_t|t = x_t|t-1 + K(y_t - H x_t|t-1)`

---

## A.7 책 안에서 "속성" 필요할 때 참고
- 1장 Bitter Lesson: 이 부록 필요 없음
- 5장 Attention: A.5 참조
- 9장 MultiPath: A.3(Gaussian Mixture)
- 15장 저정밀 연산: A.1(행렬곱 FP 오차)
- 21장 PPO: A.3, A.4
