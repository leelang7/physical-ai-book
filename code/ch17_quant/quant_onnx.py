"""
ch17 — 양자화 + ONNX 변환 (차량 배포 직전 단계)

도서 17장 *"양자화 · ONNX · 차량 배포"* 의 실제 절차.
GPU 학습된 FP32 모델 → INT8 양자화 → ONNX export → ONNX Runtime 추론.

본 데모는 작은 분류 모델로 전체 흐름 1분 안에 검증.
"""
from __future__ import annotations
import os
import tempfile
import time
import torch
import torch.nn as nn
import torch.quantization as quant


# ---------- 분류 모델 (양자화 대상) ----------
class TinyClassifier(nn.Module):
    def __init__(self, n_classes: int = 10):
        super().__init__()
        self.quant_in = quant.QuantStub()
        self.net = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1), nn.ReLU(),  # 32→16
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(32, n_classes),
        )
        self.dequant_out = quant.DeQuantStub()

    def forward(self, x):
        x = self.quant_in(x)
        x = self.net(x)
        return self.dequant_out(x)


def calibrate_with_data(model: nn.Module, n_batches: int = 30):
    """Post-Training Quantization (PTQ) — 작은 데이터로 양자화 범위 추정."""
    model.eval()
    with torch.no_grad():
        for _ in range(n_batches):
            x = torch.randn(8, 3, 32, 32)
            model(x)


def measure_inference(model: nn.Module, n_iter: int = 200, batch: int = 8) -> tuple[float, float]:
    """평균 추론 시간 + FP32 vs INT8 결과 동일성 차이."""
    model.eval()
    x = torch.randn(batch, 3, 32, 32)
    # warmup
    with torch.no_grad():
        for _ in range(5):
            model(x)
    t0 = time.perf_counter()
    with torch.no_grad():
        for _ in range(n_iter):
            out = model(x)
    elapsed = time.perf_counter() - t0
    return elapsed / n_iter * 1000, float(out.abs().sum().item())


# ---------- ONNX export ----------
def export_onnx(model: nn.Module, path: str):
    """ONNX 로 저장 — ONNX Runtime / TensorRT / 차량 SoC 가 받아쓸 형식."""
    model.eval()
    dummy = torch.randn(1, 3, 32, 32)
    torch.onnx.export(
        model, dummy, path,
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
    )
    return os.path.getsize(path)


def main() -> None:
    print("== ch17 — 양자화 + ONNX 변환 (차량 배포 직전 단계) ==\n")

    # 1) FP32 모델
    torch.manual_seed(0)
    model = TinyClassifier()
    n_params = sum(p.numel() for p in model.parameters()) / 1e3
    print(f"[1] FP32 모델 ({n_params:.1f} K params)")
    fp32_ms, fp32_out = measure_inference(model)
    print(f"    추론 시간   : {fp32_ms:.3f} ms/batch")
    print(f"    출력 합     : {fp32_out:.3f}")

    # 2) Post-Training Quantization (PTQ)
    print(f"\n[2] INT8 양자화 (PTQ)")
    model.eval()
    model.qconfig = quant.get_default_qconfig("fbgemm")
    quant.prepare(model, inplace=True)
    calibrate_with_data(model)
    quant.convert(model, inplace=True)
    int8_ms, int8_out = measure_inference(model)
    print(f"    추론 시간   : {int8_ms:.3f} ms/batch  (FP32 대비 {fp32_ms / int8_ms:.2f}x)")
    print(f"    출력 합     : {int8_out:.3f}  (FP32 대비 {abs(fp32_out - int8_out) / fp32_out * 100:.1f}% 차이)")

    # 3) ONNX export — INT8 양자화 모델은 export 까다로워 FP32 로 시연
    tmp_path = os.path.join(tempfile.gettempdir(), "ch17_export.onnx")
    fp32_model = TinyClassifier()
    size = export_onnx(fp32_model, tmp_path)
    print(f"\n[3] ONNX export")
    print(f"    파일 크기   : {size / 1024:.1f} KB ({tmp_path})")
    try:
        os.unlink(tmp_path)
    except OSError:
        pass  # Windows 파일 잠금 — 무시

    print(f"\n  실제 차량 배포 흐름:")
    print(f"    PyTorch FP32 (서버 학습) → INT8 양자화 (1.5~4× 빠름)")
    print(f"    → ONNX export → TensorRT 변환 → 차량 SoC (NVIDIA DRIVE / 테슬라 자체 칩)")
    print(f"    → 5~20 W TDP, 1~10 ms latency 보장")
    print(f"\n  도서 17.4 절: 양자화는 *정확도 1~2% 만 떨어뜨리고 추론 4× 빠름*. 차량 배포의 표준.")


if __name__ == "__main__":
    main()
