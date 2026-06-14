"""
ch26 — openpilot 모델 분석 골격

도서 26장 *"openpilot 리버스 엔지니어링"* 의 분석 코드 패턴.
openpilot 의 핵심 모델 (supercombo) 은 ONNX 로 배포돼 *오픈 분석 가능*.

본 데모는:
  1) 가짜 supercombo 모델 구조 (ONNX 가 없을 때를 위한 mock)
  2) ONNX import + 모델 분석 흐름
  3) 입출력 텐서 shape 분석 + 모델 통계

실제 openpilot 모델 다운로드:
    git clone https://github.com/commaai/openpilot
    cd openpilot/models
    git lfs pull   # supercombo.onnx 가 LFS 로 분리돼 있음
"""
from __future__ import annotations
import os


def show_openpilot_architecture():
    print("""
# openpilot supercombo 모델 구조 (commaai/openpilot 2024 ~)
#
# 입력 (BCHW):
#   - input_imgs:    (B, 12, H, W) — 현재 + 과거 6 프레임 (YUV)
#   - big_input_imgs:(B, 12, H, W) — wide-angle 카메라 추가
#   - desire:        (B, 100, 8)   — 운전자 의도 (lane change 등)
#   - traffic:       (B, 100, 2)   — 신호등 상태
#   - lateral_control_params: 차량 제어 파라미터
#   - prev_desired_curv: 이전 곡률
#   - features_buffer: (B, 99, 512) — 이전 timestep feature
#
# 출력:
#   - plan:        (B, 4955)  — 5초 미래 궤적 (10 modes × T × xyz)
#   - lane_lines:  (B, 528)   — 차선 4개
#   - road_edges:  (B, 264)   — 도로 가장자리
#   - lead:        (B, 102)   — 선두 차량
#   - desire_pred: (B, 32)    — 다음 의도 예측
#   - meta:        (B, 80)    — 기타 메타데이터
#
# 파라미터 수: 약 6~8 M (작음!)
# 추론 속도 : ~20 ms on Comma 3 (Snapdragon 845)
""")


def show_inference_pattern():
    print("""
# ONNX Runtime 추론 패턴
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession(
    "supercombo.onnx",
    providers=["CPUExecutionProvider"],
)

# 입력 준비 — 실제는 차량 카메라 + 의도 등
B = 1
inputs = {
    "input_imgs":     np.random.rand(B, 12, 128, 256).astype(np.float32),
    "big_input_imgs": np.random.rand(B, 12, 128, 256).astype(np.float32),
    "desire":         np.zeros((B, 100, 8), dtype=np.float32),
    "traffic":        np.zeros((B, 100, 2), dtype=np.float32),
    "lateral_control_params": np.zeros((B, 2), dtype=np.float32),
    "prev_desired_curv":      np.zeros((B, 100, 1), dtype=np.float32),
    "features_buffer":        np.zeros((B, 99, 512), dtype=np.float32),
}

outputs = session.run(None, inputs)
plan, lane_lines, road_edges, lead, desire_pred, meta = outputs

# plan 디코딩 — 10 modes 중 가장 높은 점수 모드 선택
plan = plan.reshape(B, 5, 991)  # 5 modes (timesteps)
""")


def show_architecture_insights():
    print("""
# 도서 26.4 절 — openpilot 모델에서 *배울 점*

1) 모델은 작다 (6~8 M params)
   - Tesla FSD 도 차량 추론 모델 자체는 1~2 B 정도로 추정
   - 거대 모델 → 차량 칩 → 양자화로 압축 (ch17)

2) 출력이 매우 풍부함
   - plan + lane + road_edge + lead + desire_pred + meta
   - 모든 task 가 한 망에서 — HydraNet 의 실증 (ch05/ch24)

3) 입력 features_buffer 가 *Temporal modeling*
   - 99 step × 512 dim — RNN 처럼 직전 feature 누적
   - 단순 frame-by-frame 추론보다 안정적

4) Desire / Traffic 인풋
   - 운전자 의도와 신호등 같은 *기호적 입력* 도 포함
   - VLA (ch22) 의 *언어/명령 입력* 의 단순화 버전
""")


def try_load_onnx() -> str | None:
    """ONNX Runtime 이 설치돼 있고 supercombo.onnx 가 로컬에 있으면 로드 시도."""
    try:
        import onnxruntime as ort  # noqa
    except ImportError:
        return "onnxruntime 미설치 (pip install onnxruntime)"
    candidates = [
        "supercombo.onnx",
        "models/supercombo.onnx",
        os.path.expanduser("~/openpilot/models/supercombo.onnx"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return f"발견: {p}"
    return "supercombo.onnx 미발견 (commaai/openpilot 클론 + git lfs pull 필요)"


def main():
    print("== ch26 openpilot 모델 분석 ==\n")
    status = try_load_onnx()
    print(f"[로컬 환경 확인]  {status}\n")
    print("[1] supercombo 아키텍처")
    show_openpilot_architecture()
    print("[2] ONNX Runtime 추론 패턴")
    show_inference_pattern()
    print("[3] 우리 책의 사상과 연결")
    show_architecture_insights()
    print("  실제 분석은 commaai/openpilot 의 selfdrive/modeld/ 디렉토리를 함께 보세요.")


if __name__ == "__main__":
    main()
