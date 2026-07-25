# CHANGELOG

## 0.1.0 (2026-07-25)

- 최초 릴리스 — 파이프라인 스켈레톤(01→10→20→30→70→80→90) + 위키 헌법 10 + Gold In Gold Out
- `/setup` 5단계 설치 인터뷰: 정체성 → **좌표(2티어: 기존 시스템 판독/역할 질문)** → 용도 → 소스 → 운영·모듈
- 도메인 렌즈: Domain Registry + WS 맵 트리 — 사용자별 계층 구조 커스터마이즈
- 운영 스킬 4종 동봉: ingest · query · lint · inbox

## 0.1.1 (2026-07-26)

- 세 줄 온보딩 — README를 "clone 한 줄(목적지 경로 포함) → claude → 설치해줘" 패턴으로 개편
- 랜딩 페이지 공개 (gh-pages): https://vision-hub-kr.github.io/llm-wiki-starter/

## 0.1.2 (2026-07-26)

- 랜딩 페이지 v2 (AKM submit 페이지 디자인 시스템 이식: 스티키 헤더·테마 토글·스텝 서클·프라미스 박스) — Vercel 배포로 전환: https://llm-wiki-starter.vercel.app (GitHub Pages 서빙 중단, gh-pages 브랜치는 랜딩 소스 보관)

## 0.1.3 (2026-07-26)

- 랜딩 v3 — 비전허브 공식 브랜드 디자인 시스템(Noda Report) 적용: 남색 다크(#0a0e1c) + 브랜드 오렌지(#f4a36c) 액센트, Pretendard Variable + JetBrains Mono, 섹션 타이틀 컬러 변형(orange/green/cool), 다크 고정(테마 토글 제거)

## 0.2.0 (2026-07-26)

- **기계 게이트 이식** (디렉터 볼트 v1.15 검증분) — "정답이 하나인 검사는 코드, 판단은 LLM"
  - `90. Settings/Scripts/`: lint.py(기계 린터+Raw 해시 불변 검증), build_index.py(index·WS 맵 파생 생성), ledger.py(장부 관리), notion_scan.py(외부 도서관 스캔), backup.sh, precommit_guard.sh(시크릿·대용량 차단), wikilib.py
  - `90. Settings/Tests/`: 인제스트 회귀 픽스처 + verify_ingest.py
  - frontmatter `summary` 키 신설 — index는 파생물(직접 수정 금지), 헌법 규칙 2·10 개정
  - /setup: build_index 실행·시크릿 훅 설치 단계 추가 · /ingest·/lint: 스크립트 우선 2단 구조
  - 미설치 상태에서 lint.py 실행 시 /setup 안내 가드

## 0.2.1 (2026-07-26)

- **브랜드명 확정: Bespoke LLM Wiki** — 저장소 bespoke-llm-wiki-starter로 개명(구 URL 자동 리다이렉트), 기본 클론 폴더 "Bespoke LLM Wiki", 랜딩 https://bespoke-llm-wiki.vercel.app (구 Vercel 프로젝트 제거)
