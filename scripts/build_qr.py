#!/usr/bin/env python3
"""
build_qr.py — 장별 QR 코드 PNG 생성기

도서 30개 장 + 채널 메인 1개 = 총 31개 PNG 를 ebook/qr/ 에 생성한다.
초판(v1.0) 시점에는 YouTube 채널 메인으로 일괄 연결한다 (영상 미녹화 상태).
2쇄 또는 영상 누적 후에는 CHAPTER_URLS 의 값을 플레이리스트 URL 로 교체하면
같은 스크립트로 일괄 갱신된다.

사용법:
    pip install --user qrcode[pil]
    python scripts/build_qr.py
"""
from __future__ import annotations
from pathlib import Path
import qrcode
from qrcode.constants import ERROR_CORRECT_M

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ebook" / "qr"

CHANNEL_URL = "https://www.youtube.com/@aidoer"

# 영상 녹화·플레이리스트 발급 후 아래 값을 교체하면 일괄 갱신된다.
CHAPTER_URLS: dict[str, str] = {f"ch{i:02d}": CHANNEL_URL for i in range(1, 31)}
CHAPTER_URLS["channel"] = CHANNEL_URL  # 부록 D 용 채널 메인 QR


def make_qr(url: str, out_path: Path, box_size: int = 10) -> None:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=box_size,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a0a0e", back_color="white")
    img.save(out_path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"== QR PNG 빌드 -> {OUT.relative_to(ROOT)}")
    for name, url in CHAPTER_URLS.items():
        out_path = OUT / f"{name}.png"
        make_qr(url, out_path)
        size_kb = out_path.stat().st_size / 1024
        print(f"   [OK] {out_path.name:<12} {size_kb:6.1f} KB  ->  {url}")
    print(f"\n== 완료. 총 {len(CHAPTER_URLS)} 개 PNG.")


if __name__ == "__main__":
    main()
