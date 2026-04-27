"""
ch04 — Bayer 패턴 디모자이크 (RGGB → RGB)

도서 4장 *"카메라 센서와 이미지 신호 처리(ISP)"* 의 핵심 단계인
디모자이크(demosaicing) 를 두 가지 방식으로 비교한다.

  1) bilinear  — 가장 단순한 보간. 빠르지만 가장자리에 색 번짐(zipper artifact) 발생.
  2) edge-aware (EA) — OpenCV 의 그래디언트 기반 디모자이크.
                       Malvar–He–Cutler 류의 5×5 보정과 같은 계열.

실행:
    python bayer_demosaic.py

산출:
    out_bilinear.png · out_malvar.png · diff.png  (스크립트와 같은 폴더)
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import cv2


def rgb_to_bayer_rggb(rgb: np.ndarray) -> np.ndarray:
    """RGB 이미지 → 한 채널 Bayer (RGGB 패턴) 모자이크 시뮬레이션.

    실제 카메라 센서는 픽셀당 하나의 색 필터만 갖는다. 학습용으로
    완성된 RGB 에서 색 정보를 떼어내 센서 출력처럼 만든다.
    """
    h, w, _ = rgb.shape
    bayer = np.zeros((h, w), dtype=rgb.dtype)
    bayer[0::2, 0::2] = rgb[0::2, 0::2, 0]   # R
    bayer[0::2, 1::2] = rgb[0::2, 1::2, 1]   # G (R-row)
    bayer[1::2, 0::2] = rgb[1::2, 0::2, 1]   # G (B-row)
    bayer[1::2, 1::2] = rgb[1::2, 1::2, 2]   # B
    return bayer


def demosaic_bilinear(bayer: np.ndarray) -> np.ndarray:
    """OpenCV 의 단순 bilinear 디모자이크 — 비교 기준선.

    주의: OpenCV 의 "BayerBG" 라벨은 (0,0)=R, (0,1)=G, (1,0)=G, (1,1)=B
    인 우리 RGGB 시뮬레이션과 일치한다. OpenCV 명명이 직관의 반대.
    """
    return cv2.cvtColor(bayer, cv2.COLOR_BayerBG2RGB)


def demosaic_edge_aware(bayer: np.ndarray) -> np.ndarray:
    """OpenCV 의 Edge-Aware 디모자이크 — 그래디언트 기반 보정.

    Malvar–He–Cutler 5×5 와 같은 계열로, 가장자리 색 번짐을 크게 줄인다.
    """
    return cv2.cvtColor(bayer, cv2.COLOR_BayerBG2RGB_EA)


def make_synthetic_target(size: int = 256) -> np.ndarray:
    """본 스크립트가 단독으로 동작하도록 합성 이미지 생성.

    부드러운 색 그라디언트 + 도형(원·사각) 으로 디모자이크가
    실제 풍경에서 만나는 패턴을 모사. 의도적으로 가장자리가 부드러워
    bilinear 와 edge-aware 의 차이가 PSNR 로도 잘 드러나도록 한다.
    """
    img = np.zeros((size, size, 3), dtype=np.uint8)
    # 부드러운 색 그라디언트 (R 가로, G 대각, B 세로)
    xs = np.linspace(0, 255, size, dtype=np.float32)
    ys = np.linspace(0, 255, size, dtype=np.float32)
    img[:, :, 0] = xs[None, :]
    img[:, :, 1] = (xs[None, :] + ys[:, None]) / 2
    img[:, :, 2] = ys[:, None]
    # 도형 추가 (가장자리에서 디모자이크 차이 부각)
    cv2.circle(img, (size // 2, size // 2), size // 6, (255, 255, 255), 2)
    cv2.rectangle(img, (size // 6, size // 6), (size // 3, size // 3), (40, 220, 40), 2)
    return img


def main() -> None:
    here = Path(__file__).resolve().parent
    target = make_synthetic_target(size=256)

    bayer = rgb_to_bayer_rggb(target)
    rgb_bil = demosaic_bilinear(bayer)
    rgb_ea  = demosaic_edge_aware(bayer)
    diff = cv2.absdiff(rgb_bil, rgb_ea) * 8  # 차이 강조

    cv2.imwrite(str(here / "out_target.png"),    cv2.cvtColor(target,  cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(here / "out_bilinear.png"),  cv2.cvtColor(rgb_bil, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(here / "out_edge_aware.png"), cv2.cvtColor(rgb_ea, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(here / "out_diff.png"),      cv2.cvtColor(diff,    cv2.COLOR_RGB2BGR))

    psnr_bil = cv2.PSNR(target, rgb_bil)
    psnr_ea  = cv2.PSNR(target, rgb_ea)

    print(f"  bilinear   PSNR : {psnr_bil:6.2f} dB")
    print(f"  edge-aware PSNR : {psnr_ea:6.2f} dB")
    print(f"  개선폭          : {psnr_ea - psnr_bil:+.2f} dB")
    print(f"\n  산출 파일: {here}/out_*.png")


if __name__ == "__main__":
    main()
