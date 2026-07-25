# 20. Wiki/ — AI가 컴파일하는 지식층

이 폴더가 위키의 본체다. 루트 `CLAUDE.md`의 위키 헌법(카파시 규칙 10 + 추가 원칙)을 그대로 따른다.

## 하위 폴더와 페이지 타입

| 폴더 | 타입 | 내용 |
|---|---|---|
| `21. Concepts/` | concept | 개념 페이지. **해석·연결은 여기서** |
| `22. Entities/` | entity | 인물·도구·조직·채널 |
| `23. Sources/` | source | 인제스트 1건당 1페이지. **사실만** — 핵심 주장·엔티티·개념 (해석 금지, 규칙 7). 출처 사슬의 허리 |
| `24. Guides/` | guide | 시스템급 방법론·절차 — 재사용 가능한 how-to |
| `25. Maps/` | map | 여러 페이지를 잇는 내비게이션 허브 + **WS 맵 트리**(도메인 워크스테이션 — 루트 CLAUDE.md 도메인 좌표 원칙) |
| `26. Questions/` | research-question | 반복 등장·산출물로 이어질 **열린 질문**을 1급 카드로 추적 (`RQ-{slug}.md`) — 필요해질 때 개설 |

> 질의 답변의 재저장은 이 폴더가 아니라 `30. Queries/`에 한다.

## 작업 규칙 (요약)

- 페이지 생성/삭제 → `00. Core/index.md` 갱신 (규칙 2), 모든 작업 → `00. Core/log.md` 기록 (규칙 3)
- 내부 참조는 `[[wikilink]]` (규칙 4), 모든 페이지에 YAML frontmatter (규칙 5 — 스키마는 루트 CLAUDE.md, `domains` 좌표 필수)
- 모순 발견 시 양쪽 소스 모두 인용 (규칙 6)
- **새 페이지보다 기존 페이지 업데이트 우선** (규칙 9)
- 컴파일 시 1차 해석 렌즈는 루트 CLAUDE.md §3의 렌즈 문장을 따른다. `Who am I` 문서의 용어·원칙과 공명하면 링크한다.
- 타입 판단 기준: 사실 요약=source / 해석·연결=concept / 사람·도구=entity / 절차·방법론=guide / 허브·목차=map
- (탐색 게이트 모듈 활성 시) AI가 컴파일한 concept·entity·guide·map은 `explored: false`로 태어난다 → 사용자 검토 후 `true` 승격. `confidence: high` 단정에는 `> [!warning] 편향 점검` 콜아웃 필수.

> 원류: 이현석(비전허브) LLM Wiki v1.14 — llm-wiki-starter로 배포
