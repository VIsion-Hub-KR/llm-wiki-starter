# 인제스트 회귀 픽스처 (machine-gates 스펙 #6)

> **용도**: /ingest 스킬·볼트 구조를 개정한 뒤, 인제스트 1건이 처음부터 끝까지 규격대로 흘러가는지 검증하는 고정 표본.
> **절차**: ① 아래 "표본 소스" 블록을 `01. Inbox/픽스처-테스트.md`로 복사 ② `/ingest`로 처리 (why 맥락 포함되어 있음) ③ `python3 "90. Settings/Tests/verify_ingest.py"` 실행 → ALL PASS 확인 ④ 생성물 삭제(Raw·Sources 페이지·장부 행) + `build_index.py` 재실행으로 원상 복구.
> 상시 CI가 아니라 **개정 때 돌리는 수동 게이트**다.

---

## 표본 소스 (이 블록을 Inbox로 복사)

```markdown
- [ ] https://example.com/llm-wiki-fixture — 왜: 인제스트 파이프라인 회귀 테스트용 고정 표본 (용도: 당신의 좌표계에서 알맞은 도메인 하나)

### 픽스처 아티클: 지식 시스템의 세 가지 층

지식 시스템은 수집층, 소화층, 산출층의 세 층으로 나뉜다. 수집층은 원료를 모으고,
소화층은 재사용 가능한 단위로 컴파일하며, 산출층은 발행물로 꺼낸다.
이 문서는 회귀 테스트용 고정 표본이며 사실적 주장을 담지 않는다. (저자: 픽스처 봇, 2026-01-01)
```

## 기대 결과 (verify_ingest.py가 검사)

1. `10. Raw Sources/11. Articles/`에 `origin_url: https://example.com/llm-wiki-fixture`인 Raw 파일 존재 (frontmatter: title·type: raw·collected·why_collected)
2. `20. Wiki/23. Sources/`에 해당 Raw를 `source_raw`로 가리키는 source 페이지 존재 (domains ⊆ 레지스트리, summary 120자 이내)
3. `00. Core/ingest-ledger.md`에 origin_url 행 존재
4. index.md에 페이지 등재 (build_index.py 산출)
5. 해당 도메인 WS 맵에 등재
6. `lint.py` 종료 코드 0 (🔴 없음)
