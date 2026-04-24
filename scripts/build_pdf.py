#!/usr/bin/env python3
"""
build_pdf.py — Pandoc 없이 Chrome Headless 만으로 MD -> HTML -> PDF 생성

사용법:
    python3 scripts/build_pdf.py              # 본문만 PDF
    python3 scripts/build_pdf.py --with-cover # 표지 포함 PDF (유페이퍼용)

의존성:
    pip install markdown pygments pypdf
    Google Chrome (Windows/Mac/Linux 어디든)
"""
from __future__ import annotations
import os, re, sys, subprocess, shutil, argparse
from pathlib import Path
import markdown
from markdown.extensions.toc import TocExtension

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "draft"
EBOOK = ROOT / "ebook"
MD_OUT = EBOOK / "전체원고_v2.0.md"
HTML_OUT = EBOOK / "전체원고_v2.0.html"
PDF_BODY = EBOOK / "전체원고_v2.0.pdf"
PDF_FULL = EBOOK / "전체원고_v2.0_유페이퍼.pdf"
COVER_PNG = EBOOK / "cover" / "cover_A_red_column.png"

CSS = r"""
@page { size: A4; margin: 22mm 20mm 22mm 20mm;
  @bottom-center { content: counter(page); font-family: 'Pretendard','Apple SD Gothic Neo','Noto Sans KR',sans-serif; font-size: 10pt; color:#555; }
}
html { font-size: 11pt; }
body { font-family: 'Pretendard','Apple SD Gothic Neo','Noto Sans KR',sans-serif;
       line-height: 1.7; color:#1a1a1a; max-width: none; margin: 0; padding: 0;
       word-break: keep-all; overflow-wrap: break-word; }
h1, h2, h3, h4 { font-weight: 800; color:#0a0a0e; letter-spacing:-0.3px; margin-top: 1.8em; }
h1 { font-size: 24pt; page-break-before: always; border-bottom: 2px solid #E11D2E; padding-bottom: 6px; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 17pt; margin-top: 1.6em; }
h3 { font-size: 13pt; color:#E11D2E; }
h4 { font-size: 12pt; }
p { margin: 0.6em 0; text-align: justify; }
strong { color:#0a0a0e; }
em { color:#555; }
blockquote { border-left: 3px solid #E11D2E; margin: 1em 0; padding: 0.5em 1em; background:#fdf5f5;
             color:#333; border-radius: 0 4px 4px 0; }
code { font-family: 'D2Coding','Consolas','Source Code Pro',monospace; font-size: 0.9em;
       background:#f3f3f5; padding: 1px 4px; border-radius: 3px; }
pre { background:#0f1116; color:#f5f5f7; padding: 14px 16px; border-radius: 6px;
      overflow-x: auto; font-size: 0.85em; line-height: 1.5; page-break-inside: avoid; }
pre code { background: transparent; color: inherit; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.95em; }
th, td { border: 1px solid #ddd; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background:#fafafa; font-weight: 700; }
hr { border: 0; border-top: 1px dashed #ccc; margin: 2em 0; }
a { color:#E11D2E; text-decoration: none; }
ul, ol { margin: 0.5em 0; padding-left: 1.5em; }
li { margin: 0.3em 0; }
.toc { background:#fafafa; padding: 12px 20px; border-radius: 6px; margin: 1em 0 2em 0;
       font-size: 0.95em; page-break-after: always; }
.toc > ul { list-style: none; padding-left: 0; }
.toc li { margin: 4px 0; }
img { max-width: 100%; height: auto; }
"""

HTML_WRAP = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>테슬라처럼 만드는 비전 자율주행과 피지컬 AI</title>
<style>{css}</style>
</head><body>
{body}
</body></html>"""


def build_html() -> Path:
    if not MD_OUT.exists():
        print(f"! {MD_OUT} 가 없습니다. 먼저 build_manuscript.sh 를 실행하세요.")
        sys.exit(1)
    md_text = MD_OUT.read_text(encoding="utf-8")

    # TOC 마커 삽입 — 첫 `---` 바로 뒤에 목차
    md_with_toc = md_text.replace("---\n\n", "---\n\n[TOC]\n\n", 1)

    ext = [
        TocExtension(title="목차", toc_depth="1-2", permalink=False),
        "fenced_code", "tables", "codehilite", "admonition", "attr_list",
    ]
    html = markdown.markdown(md_with_toc, extensions=ext,
                             extension_configs={"codehilite": {"guess_lang": False, "noclasses": True}})
    HTML_OUT.write_text(HTML_WRAP.format(css=CSS, body=html), encoding="utf-8")
    return HTML_OUT


def find_chrome() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    for name in ("google-chrome", "chromium", "chrome"):
        w = shutil.which(name)
        if w:
            return w
    raise FileNotFoundError("Chrome 실행 파일을 찾을 수 없습니다.")


def html_to_pdf(html_path: Path, pdf_path: Path):
    chrome = find_chrome()
    url = "file:///" + str(html_path.resolve()).replace("\\", "/")
    out = str(pdf_path.resolve()).replace("\\", "/")
    cmd = [
        chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
        f"--print-to-pdf={out}", "--no-pdf-header-footer",
        "--print-to-pdf-no-header", "--virtual-time-budget=10000",
        url,
    ]
    print(f"  Chrome: {Path(chrome).name}")
    print(f"  HTML : {html_path.name}")
    print(f"  PDF  : {pdf_path.name}")
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if res.returncode != 0:
        print("! Chrome PDF 변환 실패:", res.stderr[-400:])
        sys.exit(1)


def make_cover_pdf() -> Path:
    cover_html = EBOOK / "cover" / "_cover_page.html"
    cover_pdf = EBOOK / "cover" / "_cover_page.pdf"
    cover_img_url = "file:///" + str(COVER_PNG.resolve()).replace("\\", "/")
    cover_html.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 0; }}
html,body {{ margin:0; padding:0; background:#fff; }}
body {{ width:100%; height:100vh; display:flex; align-items:center; justify-content:center; }}
img {{ max-width:100%; max-height:100vh; display:block; }}
</style></head><body><img src="{cover_img_url}"/></body></html>""", encoding="utf-8")
    html_to_pdf(cover_html, cover_pdf)
    return cover_pdf


def merge_cover_and_body(cover_pdf: Path, body_pdf: Path, out: Path):
    from pypdf import PdfWriter
    w = PdfWriter()
    w.append(str(cover_pdf))
    w.append(str(body_pdf))
    with open(out, "wb") as f:
        w.write(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-cover", action="store_true", help="표지 합본 PDF 추가 생성 (유페이퍼용)")
    args = ap.parse_args()

    print(f"== 1. HTML 빌드 -> {HTML_OUT.name}")
    build_html()
    html_size_kb = HTML_OUT.stat().st_size / 1024
    print(f"   [OK] {html_size_kb:.1f} KB")

    print(f"\n== 2. 본문 PDF 빌드 -> {PDF_BODY.name}")
    html_to_pdf(HTML_OUT, PDF_BODY)
    body_kb = PDF_BODY.stat().st_size / 1024
    print(f"   [OK] {body_kb:.1f} KB ({body_kb/1024:.2f} MB)")

    if args.with_cover:
        if not COVER_PNG.exists():
            print(f"! {COVER_PNG} 가 없습니다. 먼저 표지를 생성하세요.")
            sys.exit(1)
        print(f"\n== 3. 표지 페이지 PDF 생성")
        cover_pdf = make_cover_pdf()
        print(f"\n== 4. 표지 + 본문 합본 -> {PDF_FULL.name}")
        merge_cover_and_body(cover_pdf, PDF_BODY, PDF_FULL)
        full_kb = PDF_FULL.stat().st_size / 1024
        print(f"   [OK] {full_kb:.1f} KB ({full_kb/1024:.2f} MB)")
        # 임시 표지 PDF 제거
        cover_pdf.unlink(missing_ok=True)
        (EBOOK / "cover" / "_cover_page.html").unlink(missing_ok=True)

    print("\n== 완료. 산출물:")
    print(f"   - {PDF_BODY}   <- 부크크 업로드용")
    if args.with_cover:
        print(f"   - {PDF_FULL}   <- 유페이퍼 업로드용 (첫 장이 표지)")


if __name__ == "__main__":
    main()
