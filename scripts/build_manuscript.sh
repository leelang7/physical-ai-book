#!/usr/bin/env bash
# build_manuscript.sh — draft/ 원고 전체를 단일 Markdown·PDF·EPUB 으로 빌드
# 사용법:
#   bash scripts/build_manuscript.sh           # MD 만 재컴파일
#   bash scripts/build_manuscript.sh --pdf     # MD + PDF (pandoc 필요)
#   bash scripts/build_manuscript.sh --epub    # MD + EPUB (pandoc 필요)
#   bash scripts/build_manuscript.sh --all     # MD + PDF + EPUB
#
# 의존성:
#   pandoc >= 3.1       (brew install pandoc / apt install pandoc)
#   xelatex             (PDF 생성용, MacTeX / TeX Live 설치)
#   Pretendard 폰트     (한글 본문 폰트, https://cactus.tistory.com/306)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRAFT="$ROOT/draft"
OUT_DIR="$ROOT/ebook"
VER="v2.0"
MD_OUT="$OUT_DIR/전체원고_${VER}.md"
PDF_OUT="$OUT_DIR/전체원고_${VER}.pdf"
EPUB_OUT="$OUT_DIR/전체원고_${VER}.epub"
COVER_PNG="$OUT_DIR/cover/cover_A_red_column.png"

BUILD_PDF=0
BUILD_EPUB=0
for a in "$@"; do
  case "$a" in
    --pdf)  BUILD_PDF=1 ;;
    --epub) BUILD_EPUB=1 ;;
    --all)  BUILD_PDF=1; BUILD_EPUB=1 ;;
  esac
done

echo "==> 1. 원고 컴파일 → $MD_OUT"
{
  cat "$DRAFT/00_서문.md"; printf "\n\n---\n\n"
  cat "$DRAFT/00_이책의_사용법.md"; printf "\n\n---\n\n"
  cat "$DRAFT/01_목차.md"; printf "\n\n---\n\n"
  printf "# 1부. 자율주행의 패러다임 전환\n\n"
  for i in 01 02 03; do cat "$DRAFT/ch${i}_"*.md; printf "\n\n---\n\n"; done
  printf "# 2부. 비전 기반 인식\n\n"
  for i in 04 05 06 07 08; do cat "$DRAFT/ch${i}_"*.md; printf "\n\n---\n\n"; done
  printf "# 3부. 예측 · 계획 · 제어\n\n"
  for i in 09 10 11; do cat "$DRAFT/ch${i}_"*.md; printf "\n\n---\n\n"; done
  printf "# 4부. 데이터 엔진\n\n"
  for i in 12 13 14; do cat "$DRAFT/ch${i}_"*.md; printf "\n\n---\n\n"; done
  printf "# 5부. 학습 인프라와 MLOps\n\n"
  for i in 15 16 17; do cat "$DRAFT/ch${i}_"*.md; printf "\n\n---\n\n"; done
  printf "# 6부. 피지컬 AI로의 확장\n\n"
  for i in 18 19 20 21 22; do cat "$DRAFT/ch${i}_"*.md; printf "\n\n---\n\n"; done
  printf "# 7부. 실습 프로젝트\n\n"
  for i in 23 24 25 26 27; do cat "$DRAFT/ch${i}_"*.md; printf "\n\n---\n\n"; done
  printf "# 8부. 미래와 윤리, 그리고 현장\n\n"
  for i in 28 29 30; do cat "$DRAFT/ch${i}_"*.md; printf "\n\n---\n\n"; done
  printf "# 부록\n\n"
  cat "$DRAFT/appA_"*.md; printf "\n\n---\n\n"
  cat "$DRAFT/appB_"*.md; printf "\n\n---\n\n"
  cat "$DRAFT/appC_"*.md; printf "\n\n---\n\n"
  cat "$DRAFT/appD_"*.md
} > "$MD_OUT"

CHARS=$(wc -m < "$MD_OUT" | tr -d ' ')
LINES=$(wc -l < "$MD_OUT" | tr -d ' ')
echo "    ✓ ${LINES} lines, ${CHARS} chars"

if [[ $BUILD_PDF -eq 1 ]]; then
  echo "==> 2. PDF 빌드 → $PDF_OUT"
  if ! command -v pandoc >/dev/null 2>&1; then
    echo "    ✗ pandoc 설치 필요: apt install pandoc / brew install pandoc"
    exit 1
  fi
  pandoc "$MD_OUT" -o "$PDF_OUT" \
    --pdf-engine=xelatex \
    -V mainfont="Pretendard" \
    -V monofont="D2Coding" \
    -V geometry:margin=25mm \
    -V fontsize=11pt \
    -V documentclass=book \
    -V lang=ko-KR \
    --toc --toc-depth=2 \
    --number-sections
  echo "    ✓ PDF 생성 완료"
fi

if [[ $BUILD_EPUB -eq 1 ]]; then
  echo "==> 3. EPUB 빌드 → $EPUB_OUT"
  if ! command -v pandoc >/dev/null 2>&1; then
    echo "    ✗ pandoc 설치 필요"
    exit 1
  fi
  EPUB_ARGS=(
    "$MD_OUT" -o "$EPUB_OUT"
    --metadata=title:"테슬라처럼 만드는 비전 자율주행과 피지컬 AI"
    --metadata=author:"이석창"
    --metadata=lang:ko-KR
    --metadata=publisher:"All That AI"
    --metadata=rights:"© 2026 Seokchang Lee"
    --toc --toc-depth=2
  )
  if [[ -f "$COVER_PNG" ]]; then
    EPUB_ARGS+=(--epub-cover-image="$COVER_PNG")
  fi
  pandoc "${EPUB_ARGS[@]}"
  echo "    ✓ EPUB 생성 완료"
fi

echo ""
echo "==> 완료. 산출물:"
echo "    - $MD_OUT"
[[ $BUILD_PDF  -eq 1 ]] && echo "    - $PDF_OUT"
[[ $BUILD_EPUB -eq 1 ]] && echo "    - $EPUB_OUT"
