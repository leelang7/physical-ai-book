# SVG 표지 → PNG 내보내기 가이드

부크크·유페이퍼 업로드용 최종 PNG 를 만드는 방법 네 가지입니다. 가장 위 방식이 가장 쉽습니다.

---

## 방법 1 · VSCode + Chrome (가장 쉬움, 권장)

1. VSCode 에서 `ebook/cover/cover_A_red_column.svg` 열기
2. 우클릭 → **Open with Live Server** (Live Server 확장 필요) 또는 **Open in Browser**
3. 브라우저 주소창의 파일을 그대로 두고, 개발자 도구 → Device Mode → 1600×2400 설정
4. 우클릭 → **Capture full size screenshot** (Chrome)
5. 저장된 파일을 `cover/cover_A_red_column.png` 로 옮기기

## 방법 2 · Inkscape (무료, 자동화 가능)

```bash
# Ubuntu/Mac
inkscape ebook/cover/cover_A_red_column.svg \
    --export-type=png \
    --export-width=1600 \
    --export-filename=ebook/cover/cover_A_red_column.png
```

## 방법 3 · ImageMagick (명령줄)

```bash
# 의존성: ImageMagick + librsvg
magick -density 300 ebook/cover/cover_A_red_column.svg \
    -resize 1600x2400 \
    ebook/cover/cover_A_red_column.png
```

주의 : ImageMagick 기본 렌더러는 텍스트 품질이 떨어질 수 있어, `librsvg2-bin` 을 함께 설치하면 결과가 훨씬 깔끔합니다.

## 방법 4 · Chrome Headless (완전 자동)

```bash
google-chrome --headless --disable-gpu \
    --screenshot=ebook/cover/cover_A_red_column.png \
    --window-size=1600,2400 \
    --default-background-color=0 \
    file://$PWD/ebook/cover/cover_A_red_column.svg
```

---

## 한글 폰트 확인

세 SVG 모두 `Pretendard → Apple SD Gothic Neo → Noto Sans KR` fallback 을 걸어 두었으므로 **Windows·macOS·Ubuntu** 중 하나는 갖고 있습니다. 그래도 불안하면 **Pretendard** 를 먼저 설치해 두세요: https://cactus.tistory.com/306

## 최종 체크

PNG 내보내기 직후 **썸네일 크기(256×384px) 로 축소해 보고**, 제목과 저자명이 여전히 읽히면 합격입니다. 읽히지 않으면 글자 크기를 15% 정도 키워 다시 내보내세요.
