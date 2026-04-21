# 부록 C. 한/영 용어집

| 한국어 | English | 등장 장 | 짧은 설명 |
|---|---|---|---|
| 자율주행 | Autonomous Driving | 1 | SAE Level 0~5 체계 |
| 모듈형 파이프라인 | Modular Pipeline | 1, 3 | Perception→Prediction→Planning→Control |
| 엔드 투 엔드 | End-to-End (E2E) | 1, 3, 10 | 입력→출력 단일 신경망 |
| 비전 전용 | Vision-only | 2 | 카메라만 사용하는 접근 |
| 빛감지측거(라이다) | LiDAR | 2 | 레이저 기반 3D 스캐너 |
| 레이더 | Radar | 2 | 전파 기반 거리·속도 측정 |
| 고해상도 지도 | HD Map | 1, 2 | 센티미터급 정밀 지도 |
| 허드라넷 | HydraNet | 5 | 하나의 백본 + 다중 헤드 |
| 백본 | Backbone | 5 | 공통 특징 추출기 |
| 넥 | Neck | 5 | 다중 스케일 특징 융합 |
| 헤드 | Head | 5 | 태스크별 출력 모듈 |
| 조감도 변환 | BEV (Bird's-Eye View) | 7 | 탑뷰 좌표계 변환 |
| 벡터 공간 | Vector Space | 7 | 엔티티 기반 희소 표현 |
| 점유 네트워크 | Occupancy Network | 6 | 3D 점유 확률 예측 |
| 리프트-스플랫 | Lift-Splat-Shoot | 6, 7 | 2D→3D 투영 기법 |
| 교차주의 | Cross-Attention | 5, 7 | 쿼리가 다른 소스를 읽음 |
| 변형 가능 주의 | Deformable Attention | 7 | 일부 지점만 주목 |
| 궤적 예측 | Trajectory Prediction | 9 | 미래 에이전트 움직임 |
| 다중 모달 예측 | Multi-modal Prediction | 9 | K개 후보 궤적 |
| 신경망 계획자 | Neural Planner | 10 | 학습된 경로 계획 |
| 모방 학습 | Imitation Learning / BC | 10, 20 | 전문가 행동 복제 |
| 선호 학습 | Preference Learning | 10, 22 | 사람 랭킹 기반 학습 |
| 확산 정책 | Diffusion Policy | 10, 20 | 노이즈 제거 생성 정책 |
| 모델 예측 제어 | MPC | 11 | 미래 계획을 매 스텝 재계산 |
| 이륜차 모델 | Bicycle Model | 11 | 차량 동역학 근사 |
| 플릿 러닝 | Fleet Learning | 12 | 대규모 차량의 집단 학습 |
| 트리거 | Trigger | 12 | 데이터 업로드 조건 |
| 자동 라벨링 | Auto-labeling | 13 | 사람 없는 라벨 생성 |
| 지식 증류 | Knowledge Distillation | 13, 17 | Teacher→Student |
| 자기지도 학습 | Self-supervised Learning | 13 | 라벨 없이 표현 학습 |
| 영역 무작위화 | Domain Randomization | 14, 21 | 시뮬 파라미터 흔들기 |
| Sim2Real | Sim-to-Real | 21 | 시뮬→실물 이식 |
| 월드 모델 | World Model | 22 | 미래 관측 생성 모델 |
| VLA | Vision-Language-Action | 22 | 영상·언어·행동 통합 |
| 도조 | Dojo | 15 | Tesla AI 전용 슈퍼컴퓨터 |
| 샤딩 | Sharding | 16 | 파라미터 분할 저장 |
| FSDP | Fully Sharded Data Parallel | 16 | PyTorch 대규모 분산 |
| 파이프라인 병렬 | Pipeline Parallel | 16 | 레이어 단위 분할 |
| 텐서 병렬 | Tensor Parallel | 16 | 레이어 내부 분할 |
| 섀도우 모드 | Shadow Mode | 17 | 출력 로그만 하는 모델 |
| OTA | Over-The-Air | 17 | 무선 업데이트 |
| 양자화 | Quantization | 17 | FP→INT 변환 |
| 가지치기 | Pruning | 17 | 가중치 제거 |
| 피지컬 AI | Physical AI | 18 | 물리 세계에서 행동하는 AI |
| 임바디드 AI | Embodied AI | 18 | 몸을 가진 AI |
| 휴머노이드 | Humanoid | 18, 19 | 사람형 로봇 |
| 자유도 | Degree of Freedom (DoF) | 19 | 관절 독립 축 수 |
| 원격 조작 | Teleoperation | 19, 20 | 사람이 로봇 원격 제어 |
| 모션 캡처 | Motion Capture | 20 | 사람 동작 기록 |
| 운동 감각 교시 | Kinesthetic Teaching | 20 | 로봇 직접 움직임 |
| 역강화학습 | Inverse RL | 20 | 보상 함수 역추론 |
| 영지식 전이 | Zero-shot Transfer | 20, 22 | 학습 없이 이식 |
| 커리큘럼 러닝 | Curriculum Learning | 27 | 쉬움→어려움 순차 학습 |
| 근접 정책 최적화 | PPO | 21 | On-policy RL 표준 |
| 소프트 행위자 비평가 | SAC | 21 | Off-policy RL |
| 비상 제동 | AEB (Auto Emergency Brake) | 10, 11 | 자동 긴급 제동 |
| 기능 안전 | Functional Safety | 28 | ISO 26262 |
| 의도된 기능 안전 | SOTIF | 28 | ISO 21448 |
| 사이버보안 | Cybersecurity | 17, 28 | ISO 21434 |
| 사전 학습 | Pretraining | 5, 13, 22 | 큰 데이터로 기초 학습 |
| 미세 조정 | Fine-tuning | 22, 27 | 특화 데이터로 마무리 |
