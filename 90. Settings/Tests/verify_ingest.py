#!/usr/bin/env python3
"""인제스트 회귀 검증 (machine-gates 스펙 #6) — ingest-fixture.md 처리 결과를 기계 검사."""
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "Scripts"
sys.path.insert(0, str(SCRIPTS))
from wikilib import VAULT, parse_frontmatter, registry_domains, wikilinks

FIXTURE_URL = "https://example.com/llm-wiki-fixture"
fails = []


def check(cond, ok_msg, fail_msg):
    print(("✅ " + ok_msg) if cond else ("❌ " + fail_msg))
    if not cond:
        fails.append(fail_msg)
    return cond


# 1. Raw 파일
raw_file, raw_fm = None, None
for f in (VAULT / "10. Raw Sources" / "11. Articles").glob("*.md"):
    fm = parse_frontmatter(f.read_text(encoding="utf-8"))
    if fm and fm.get("origin_url") == FIXTURE_URL:
        raw_file, raw_fm = f, fm
        break
if check(raw_file is not None, f"Raw 존재: {raw_file.name if raw_file else ''}", "Raw 파일 없음 (11. Articles에 origin_url 매칭 실패)"):
    for k in ("title", "collected", "why_collected"):
        check(k in raw_fm, f"Raw frontmatter `{k}` 있음", f"Raw frontmatter `{k}` 누락")
    check(raw_fm.get("type") == "raw", "Raw type: raw", f"Raw type 오류: {raw_fm.get('type')}")

# 2. Sources 페이지
src_file, src_fm = None, None
if raw_file:
    raw_rel = raw_file.relative_to(VAULT).as_posix()
    for f in (VAULT / "20. Wiki" / "23. Sources").glob("*.md"):
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm and fm.get("source_raw") == raw_rel:
            src_file, src_fm = f, fm
            break
if check(src_file is not None, f"Sources 페이지 존재: {src_file.name if src_file else ''}", "source_raw로 Raw를 가리키는 Sources 페이지 없음"):
    reg = registry_domains()
    doms = src_fm.get("domains") or []
    check(bool(doms) and all(d in reg for d in doms), f"domains 유효: {doms}", f"domains 없음/레지스트리 밖: {doms}")
    check(0 < len(src_fm.get("summary", "")) <= 120, "summary 120자 이내", f"summary 없음/초과: {len(src_fm.get('summary', ''))}자")

# 3. 장부
ledger = (VAULT / "00. Core" / "ingest-ledger.md")
check(ledger.exists() and FIXTURE_URL in ledger.read_text(encoding="utf-8"), "장부 행 존재", "ingest-ledger에 픽스처 행 없음")

# 4~5. index·WS 맵 등재
if src_file:
    idx_links = wikilinks((VAULT / "00. Core" / "index.md").read_text(encoding="utf-8"))
    check(src_file.stem in idx_links, "index 등재", "index 미등재 — build_index.py 실행 여부 확인")
    reg = registry_domains()
    for d in (src_fm.get("domains") or []):
        ws = VAULT / "20. Wiki" / "25. Maps" / f"{reg[d]}.md"
        check(src_file.stem in wikilinks(ws.read_text(encoding="utf-8")), f"WS 맵 등재({reg[d]})", f"WS 맵 미등재({reg[d]})")

# 6. 기계 린트
r = subprocess.run([sys.executable, str(SCRIPTS / "lint.py")], capture_output=True, text=True)
check(r.returncode == 0, "lint.py 종료 코드 0", "lint.py 🔴 존재")

print("\n" + ("회귀 검증 ALL PASS ✅" if not fails else f"회귀 검증 실패 {len(fails)}건 ❌"))
sys.exit(1 if fails else 0)
