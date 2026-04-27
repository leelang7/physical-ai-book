# 장별 QR 코드 — 독자 안내

이 디렉토리에는 책 *"테슬라처럼 만드는 비전 자율주행과 피지컬 AI"* (이석창 지음, All That AI Vol.01) 의 **장별 QR 코드 31개** 가 PNG 로 들어 있습니다.

## 사용법

각 PNG 파일명은 본문의 장 번호와 1:1 로 대응합니다.

| 파일 | 연결 대상 | 본문 위치 |
|---|---|---|
| `ch01.png` ~ `ch30.png` | YouTube "All That AI" 채널 (해당 장 해설 영상) | 각 장 끝 *"더 읽을 거리"* 섹션 |
| `channel.png` | YouTube 채널 메인 | 부록 D — 저자 연계 안내 |

스마트폰 카메라로 PNG 를 비추면 YouTube 가 열립니다.

## v1.0 시점의 안내

초판(2026 출간) 시점에는 **모든 QR 이 채널 메인** 으로 동일하게 연결됩니다. 이유는 단순합니다 — 각 장 해설 영상이 아직 녹화 전이기 때문입니다. 영상이 녹화·발행되는 대로 GitHub 저장소의 본 디렉토리가 갱신됩니다. 같은 PNG 파일명이 그때마다 새 영상의 플레이리스트로 자동 연결되도록 운영하지 않습니다 — QR 자체는 채널 URL 을 가리키므로 영구히 유효합니다. 다만 채널 안에서 "Tesla Book Ch.XX" 라는 일관된 제목 규칙으로 영상이 누적되므로, 독자가 채널 내 검색만 하시면 해당 장의 영상을 바로 찾으실 수 있습니다.

## 영상 발행 일정

| 시점 | 예상 발행 |
|---|---|
| 출간 직후 | 런칭 영상 1편 + 쇼츠 5편 |
| 출간 후 4주 (M1) | ch01~ch05 해설 (주 1회) |
| 출간 후 8주 (M2) | ch06~ch11 해설 |
| 출간 후 12주 (M3) | ch15~ch22 해설 |
| 출간 후 16주 (M4) | ch24~ch27 해설 |
| 출간 후 20주 (M5) | ch28~ch30 + Optimus·VLA 특집 |

자세한 일정은 저장소 루트의 [code/README.md](../../code/README.md) 의 M1~M5 로드맵과 동일합니다.

## 빌드 재현

```bash
pip install --user qrcode[pil]
python scripts/build_qr.py
```

스크립트 ([scripts/build_qr.py](../../scripts/build_qr.py)) 안의 `CHAPTER_URLS` 딕셔너리가 단일 진실원입니다. 영상 누적 후 플레이리스트 URL 로 교체하고 다시 실행하면 31개 PNG 가 일괄 갱신됩니다.

## 라이선스

QR 코드 PNG : MIT (자유 재배포 가능)
연결 대상 콘텐츠 : YouTube "All That AI" — 저자 권리 보유

## 문의

- 영상 요청·요약 의견 : [Issues](https://github.com/leelang7/physical-ai-book/issues)
- 저자 이메일 : leescvsir@gmail.com
