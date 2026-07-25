---
name: ingest
description: LLM Wiki로 소스를 인제스트합니다 — 출처를 감지해 10. Raw Sources/에 1차 정리 사본을 만들고 20. Wiki/에 컴파일하는 한 흐름. "수집해", "인제스트", "이 링크 위키에 넣어", "긁어와" 등에 반응. 외부 도서관(노션 등) 출처는 정리된 것으로 직행, 웹 출처(01. Inbox/·URL)는 검색 보강으로 1차 정리 후 합류. 장부(ledger)로 중복 자동 스킵.
---

# /ingest — LLM Wiki 인제스트

## 전제

- 이 스킬은 `/setup` 완료 후에만 쓴다. 루트 `CLAUDE.md`의 위키 헌법을 항상 따른다. 호칭·언어는 루트 CLAUDE.md §4를 따른다.
- **외부 도서관(노션 등) 원본은 절대 건드리지 않는다** (읽기 전용 — 삭제·아카이브·수정 금지).
- **출처 감지**: 입력이 외부 도서관(노션 등 — CLAUDE.md에 도서관 설정이 있을 때) 페이지면 **도서관 레인**(이미 정리됨 → 직행), `01. Inbox/`의 파일이나 일반 웹 URL이면 **웹 레인**(검색으로 보강해 1차 정리 후 Raw로 승격).
- `10. Raw Sources/`에 이미 저장된 파일은 절대 수정하지 않는다. 원본이 갱신된 경우에만 사본을 **새로 써서 교체**하고 장부·log에 기록한다.
- 루트 CLAUDE.md에 정확히 `paper-mode: 활성` 문구가 있는 경우에만 논문(DOI·arXiv·Abstract+References PDF) 감지 시 12단 분석 모드로 전환한다. **`예약(미활성)` 표기는 활성이 아니다** — v0.1 킷에는 12단 모드가 미동봉이므로, 활성 문구가 없으면 논문도 표준 인제스트로 처리한다.

## 공통 절차 (페이지 1건 처리)

1. **장부 대조** — `00. Core/ingest-ledger.md`에서 식별키(`origin_url` 또는 도서관 페이지 id) 검색 (파일이 없으면 첫 인제스트 때 생성):
   - 없음 → 신규 인제스트 / 있고 원본 변경 없음 → **스킵** (보고에만 표시) / 원본이 더 최신 → **갱신** (Raw 교체 + wiki 갱신)
2. **가져오기** — 원문을 읽는다. 불완전하면(저자·출처 누락 등) 검색으로 보강해 **온전한 형태**로 만든다 (= 1차 정리).
3. **Raw 사본 저장** — `10. Raw Sources/<슬롯 폴더>/YYYY-MM-DD_슬러그.md`:
   - 분류는 `10. Raw Sources/CLAUDE.md`의 표준 슬롯 표를 따른다. 해당 슬롯 폴더가 없으면 번호 유지하며 개설.
   - frontmatter 필수: `title` · `type: raw` · `collected` · `origin_url` · `why_collected`
   - 본문은 원문 그대로 (요약·수정 금지 — 소화는 wiki에서)
4. **why_collected 채우기 (Gold In Gold Out)**: 요청 문장에 목적이 있으면 그것을 쓴다. 불명이면 사용자에게 묻는다 — "왜 수집하셨어요? 지금 하는 일과 어떻게 연결돼요?" **답 없이 컴파일하지 않는다.**
5. **위키 컴파일** — `20. Wiki/`:
   - `23. Sources/`에 소스 요약 1건 (사실만 — 규칙 7). 관련 `21. Concepts/`·`22. Entities/` 생성·갱신 (**기존 페이지 우선** — 규칙 9). 방법론이면 `24. Guides/`, 여러 페이지 관통 허브면 `25. Maps/` 갱신.
   - 1차 해석 렌즈: 루트 CLAUDE.md §3의 렌즈 문장.
   - frontmatter는 루트 CLAUDE.md §7 스키마.
   - **도메인 좌표**: why_collected 답에서 `domains` 값을 확정한다 — `90. Settings/Domain_Registry.md` 등재 값만, 다중 허용, 판단 안 서면 사용자에게 질문. frontmatter 기입 + 해당 `WS — {Domain}` 맵의 타입별 섹션(concept→핵심 개념, source·entity→사례·소스, guide→방법론)에 wikilink 등재까지가 컴파일 완료 조건.
   - (탐색 게이트 모듈 활성 시) 새 concept·entity·guide·map은 `explored: false`로 생성, `confidence: high` 단정에는 편향 점검 콜아웃.
6. **기록** — `00. Core/index.md` 갱신(페이지당 한 줄, 120자), `00. Core/log.md` append, 장부 갱신. Inbox에서 온 항목이면 제거.
7. **백업** — 루트 CLAUDE.md §4의 백업 설정을 따른다 (git 사용 시 commit, 자동 푸시 여부는 설정대로).

## 보고 형식

**신규 n건 / 갱신 n건 / 스킵 n건** + 각 건의 Raw 경로와 생성·갱신된 wiki 페이지 wikilink 목록.

## 금지 사항

- why_collected 없는 컴파일 · Raw in-place 수정 · 외부 도서관 원본 수정·삭제 · 외부 도서관 무차별 수집(사용자가 지목한 것만)

> 원류: 이현석(비전허브) LLM Wiki v1.14 /ingest — 범용화 배포판
