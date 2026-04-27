"""
ch04 — 화이트밸런스 두 알고리즘 비교

도서 4장의 ISP 파이프라인에서 디모자이크 직후 단계인 White Balance(WB)를
가장 흔한 두 방식으로 구현한다.

  1) Gray-World  — 장면 전체 평균이 회색이라는 가정. 가장 단순·빠름.
  2) Max-RGB     — 각 채널의 최댓값이 흰색이라는 가정. 하이라이트가 있으면 잘 동작.

색온도가 치우친 이미지(예: 노을·형광등) 에 두 방식을 적용해
어느 쪽이 더 자연스러운지 확인한다.

실행:
    python white_balance.py
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import cv2


def gray_world_wb(img: np.ndarray) -> np.ndarray:
    """Gray-World — 채널별 평균이 같아지도록 게인 조정."""
    img = img.astype(np.float32)
    means = img.reshape(-1, 3).mean(axis=0) + 1e-6
    gain = means.mean() / means
    return np.clip(img * gain, 0, 255).astype(np.uint8)


def max_rgb_wb(img: np.ndarray) -> np.ndarray:
    """Max-RGB — 채널별 상위 1% 평균이 같아지도록 게인 조정."""
    img = img.astype(np.float32)
    flat = img.reshape(-1, 3)
    top = np.percentile(flat, 99, axis=0) + 1e-6
    gain = top.max() / top
    return np.clip(img * gain, 0, 255).astype(np.uint8)


def make_warm_cast(size: int = 256) -> np.ndarray:
    """일출 시간대처럼 R 채널에 게인이 더 들어간 합성 이미지."""
    img = np.zeros((size, size, 3), dtype=np.uint8)
    for y in range(size):
        for x in range(size):
            img[y, x, 0] = min(255, 80 + (x + y) // 2)   # R 강세
            img[y, x, 1] = min(255, 60 + x // 4)
            img[y, x, 2] = min(255, 30 + y // 6)         # B 약함
    # 흰색 점광원 — Max-RGB 가 잡아내야 할 신호
    cv2.circle(img, (size // 4, size // 4), 12, (255, 255, 255), -1)
    return img


def main() -> None:
    here = Path(__file__).resolve().parent
    src = make_warm_cast(size=256)

    out_gw = gray_world_wb(src)
    out_mx = max_rgb_wb(src)

    for name, im in [("src_warm", src), ("wb_grayworld", out_gw), ("wb_maxrgb", out_mx)]:
        cv2.imwrite(str(here / f"{name}.png"), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))

    print(f"  산출 파일: {here}/(src_warm|wb_grayworld|wb_maxrgb).png")
    print("  육안 비교: 흰 점광원이 회색이 아닌 흰색으로 복원됐는지 확인.")


if __name__ == "__main__":
    main()
