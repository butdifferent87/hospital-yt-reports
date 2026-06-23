# 병원 YouTube 월간 리포트

각 병원 채널의 월간 성과 리포트를 HTML로 만들어 GitHub Pages로 호스팅한다.
원장님에게는 링크만 전달하면 된다.

## 구조

```
hospital-yt-reports/
├── index.html              # 채널 목록 허브 (운영자용)
├── [채널슬러그]/
│   └── YYYY-MM.html        # 자체완결 월간 리포트 (CSS 내장)
└── README.md
```

## URL

- 허브: `https://butdifferent87.github.io/hospital-yt-reports/`
- 리포트: `https://butdifferent87.github.io/hospital-yt-reports/[채널슬러그]/YYYY-MM.html`

## 리포트 구성 (확정 템플릿)

1. **한 줄 평** — "이번 달 잘했나?"의 답. 5초 안에 보이게 (Trunk Test)
2. **성장 스냅샷** — 구독자 / 조회수 / 평균 조회율 / 시청시간 (전월 대비 ▲▼)
3. **이달의 영상** — 베스트 1편 + 왜 떴나
4. **다음 달 할 일 3개** — ★ = 원장님 결정 필요
5. **부록** — 전체 영상표 · 트래픽 · 시청자 (접힘, 참고용)

설계 원칙(Steve Krug): 원장은 읽지 않고 스캔한다 → 숫자 중복 제거, 원장 언어 라벨, 한 줄 평 강제.

## 매달 작업 흐름

1. YouTube Studio 개요 + 콘텐츠 탭 스샷/숫자 확보 (채널당 2~4장)
2. 새 `[채널]/YYYY-MM.html` 생성 (기존 파일 복사 후 숫자 교체)
3. `index.html` 허브에 링크 추가
4. commit + push → 1~2분 후 URL 라이브
5. 링크 복사해 원장님 전달

## 데이터 인테이크 (YouTube Studio → 리포트)

- **A. 채널 개요**: 구독자 / 조회수 / 시청시간 / 평균 조회율 / 노출·CTR → 개요 스샷 1장
- **B. 영상별 성과**: 제목별 조회수 / 평균조회율 / CTR → 콘텐츠 표 스샷 1장
- **C. 트래픽 소스**(선택): 탐색/검색/추천 비율 → 도달률 탭 스샷
- **D. 시청자**(분기 1회): 신규 vs 재방문, 연령·성별

최소 = A + B 스샷 2장이면 리포트 거의 다 채워진다.

## 주의

- GitHub Pages 무료 = 공개 URL (검색 노출은 `noindex`로 차단, 링크 아는 사람은 접근 가능).
  민감도 높으면 Notion 비공개 공유 / Vercel Pro 전환 검토.
