#!/usr/bin/env python3
"""index.md + 리프 WS 맵 파생 생성기 (machine-gates 스펙 #2).

원천 데이터 = 각 페이지 frontmatter(type·domains·summary·pinned) + Domain_Registry.
- 00. Core/index.md: 전체 재생성 (직접 수정 금지)
- 리프 WS 맵: frontmatter·타이틀·인트로는 보존, 타입 섹션(개념/사례·소스/방법론/관련 맵·쿼리)은 재생성,
  '열린 질문(RQ)'·'산출물' 섹션은 기존 내용 carry-over (수동 큐레이션 슬롯).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wikilib import VAULT, registry_domains, wiki_pages

pages = wiki_pages()
domains_map = registry_domains()
by_name = {f.stem: (f, fm) for f, _, fm in pages if fm}


def entry(name, fm):
    star = "⭐ " if fm.get("pinned") == "true" else ""
    return f"- {star}[[{name}]] — {fm.get('summary', '(summary 미표기)')}"


def sort_key(item):
    f, fm = item
    return (fm.get("pinned") != "true", fm.get("created", "9999"), f.stem)


def of_type(t, domain=None):
    out = []
    for f, _, fm in pages:
        if not fm or fm.get("type") != t:
            continue
        if domain and domain not in (fm.get("domains") or []):
            continue
        out.append((f, fm))
    return sorted(out, key=sort_key)


# ── index.md ──────────────────────────────────────────────
L = ["# 위키 목차 (index)", "",
     "> ⚙️ **이 파일은 `90. Settings/Scripts/build_index.py`가 자동 생성한다 — 직접 수정 금지.**",
     "> 원천: 각 페이지 frontmatter의 `summary`(120자 이내)·`type`·`domains`·`pinned`. 페이지를 고치면 스크립트를 다시 돌린다.", ""]

L += ["## 23. Sources — 소스 요약 (인제스트 1건당 1페이지)", ""]
L += [entry(f.stem, fm) for f, fm in of_type("source")] + [""]
L += ["## 21. Concepts — 개념", ""]
L += [entry(f.stem, fm) for f, fm in of_type("concept")] + [""]
L += ["## 22. Entities — 인물·도구·조직·채널", ""]
L += [entry(f.stem, fm) for f, fm in of_type("entity")] + [""]

L += ["## 25. Maps — 내비게이션 허브", "", "### WS 맵 트리 (도메인 워크스테이션 — 좌표 마스터: 90. Settings/Domain_Registry.md)", ""]
ws_order = ["WS — Home", "WS — Vision-Hub", "WS — Personal"] + [domains_map[v] for v in domains_map]
listed = set()
for name in ws_order:
    if name in by_name and name not in listed:
        L.append(entry(name, by_name[name][1]))
        listed.add(name)
L += ["", "### 주제 맵", ""]
L += [entry(f.stem, fm) for f, fm in of_type("map") if f.stem not in listed] + [""]

L += ["## 24. Guides — 방법론·절차", ""]
L += [entry(f.stem, fm) for f, fm in of_type("guide")] + [""]
L += ["## 30. Queries — 질의 답변 저장 (위키 밖 폴더)", ""]
L += [entry(f.stem, fm) for f, fm in of_type("query")] + [entry(f.stem, fm) for f, fm in of_type("synthesis")] + [""]
L += ["## 40. Paper Analyses — 논문 12단 분석 (Paper Mode, 허브만 등재)", ""]
L += [entry(f.stem, fm) for f, fm in of_type("paper-hub")] + [""]

(VAULT / "00. Core" / "index.md").write_text("\n".join(L), encoding="utf-8")
print(f"index.md 생성: 항목 {sum(1 for x in L if x.startswith('- '))}건")

# ── 리프 WS 맵 ─────────────────────────────────────────────
CARRY = ["## 열린 질문 (RQ)", "## 산출물로 나간 것 (70. Output)"]

for value, ws_name in domains_map.items():
    p = VAULT / "20. Wiki" / "25. Maps" / f"{ws_name}.md"
    old = p.read_text(encoding="utf-8")
    head_match = re.match(r"^(---\n.*?\n---\n.*?)(?=\n## )", old, re.S)
    if not head_match:
        print(f"⚠️ 머리부 파싱 실패, 건너뜀: {ws_name}")
        continue
    head = head_match.group(1)
    carry = {}
    for sec in CARRY:
        m = re.search(re.escape(sec) + r"\n(.*?)(?=\n## |\Z)", old, re.S)
        carry[sec] = m.group(1).strip() if m else "- (아직 없음)"

    def section(title, items):
        body = "\n".join(items) if items else "- (아직 없음)"
        return f"## {title}\n\n{body}\n"

    concepts = [entry(f.stem, fm) for f, fm in of_type("concept", value)]
    sources = [entry(f.stem, fm) + " (엔티티)" if fm.get("type") == "entity" else entry(f.stem, fm)
               for f, fm in sorted(of_type("source", value) + of_type("entity", value), key=sort_key)]
    hubs = [entry(f.stem, fm) + " (논문 허브)" for f, fm in of_type("paper-hub", value)]
    guides = [entry(f.stem, fm) for f, fm in of_type("guide", value)]
    related = [entry(f.stem, fm) for f, fm in of_type("map", value) if f.stem != ws_name]
    related += [entry(f.stem, fm) for f, fm in of_type("query", value) + of_type("synthesis", value)]

    parts = [head.rstrip(), "", section("핵심 개념 (Concepts)", concepts),
             section("사례·소스 (Sources)", sources + hubs), section("방법론 (Guides)", guides)]
    if related:
        parts.append(section("관련 맵·쿼리", related))
    parts.append(f"## 열린 질문 (RQ)\n\n{carry[CARRY[0]]}\n")
    parts.append(f"## 산출물로 나간 것 (70. Output)\n\n{carry[CARRY[1]]}\n")
    p.write_text("\n".join(parts), encoding="utf-8")
    print(f"WS 맵 재생성: {ws_name} (개념 {len(concepts)}·소스 {len(sources) + len(hubs)}·가이드 {len(guides)}·맵쿼리 {len(related)})")
