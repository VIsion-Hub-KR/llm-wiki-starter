#!/usr/bin/env python3
"""LLM Wiki 기계 린터 (machine-gates 스펙 #1·#3).

검사: ① frontmatter 필수 키 ② type 스키마 ③ domains 레지스트리 대조 ④ source_raw 실존
⑤ 깨진 wikilink ⑥ index 정합(누락·유령·요약 120자) ⑦ WS 맵 등재 ⑧ Raw sha256 불변 ⑨ summary 키.
출력: 🔴(위반)/🟡(판단 필요) 목록 + 요약. 🔴 있으면 exit 1.

사용: python3 lint.py            # 검사
      python3 lint.py --json    # 결과 JSON (스킬 연동용)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wikilib import VAULT, ALLOWED_TYPES, all_md_names, fm_body, registry_domains, wiki_pages, wikilinks

RED, YEL = [], []
HASH_MANIFEST = Path(__file__).parent / "raw_hashes.json"


def check_pages(pages, domains_map):
    for f, text, fm in pages:
        rel = f.relative_to(VAULT).as_posix()
        if fm is None:
            RED.append(f"frontmatter 없음: {rel}")
            continue
        for key in ("title", "type", "created", "updated"):
            if key not in fm:
                RED.append(f"필수 키 `{key}` 누락: {rel}")
        t = fm.get("type", "")
        if t and t not in ALLOWED_TYPES:
            RED.append(f"type 값이 스키마 밖(`{t}`): {rel}")
        if "domains" not in fm:
            YEL.append(f"domains 미표기: {rel}")
        else:
            for d in fm["domains"]:
                if d not in domains_map:
                    RED.append(f"레지스트리 밖 domains 값 `{d}`: {rel}")
        if "summary" not in fm and t not in ("paper-hub",):
            YEL.append(f"summary 미표기(자동 생성 원천 없음): {rel}")
        if t == "source":
            sr = fm.get("source_raw", "")
            if not sr:
                RED.append(f"source 타입인데 source_raw 없음: {rel}")
            elif not (VAULT / sr).exists():
                RED.append(f"source_raw 경로 실존 안 함({sr}): {rel}")


def check_wikilinks(pages, names):
    for f, text, fm in pages:
        rel = f.relative_to(VAULT).as_posix()
        for link in set(wikilinks(fm_body(text))):
            if link and link not in names:
                YEL.append(f"미해소 wikilink [[{link}]]: {rel} (의도적 미래 링크인지 확인)")


def check_ws_maps(pages, domains_map):
    map_texts = {}
    for value, ws_name in domains_map.items():
        p = VAULT / "20. Wiki" / "25. Maps" / f"{ws_name}.md"
        if not p.exists():
            RED.append(f"레지스트리의 WS 맵 파일 없음: {ws_name}.md (값 `{value}`)")
            continue
        map_texts[value] = set(wikilinks(p.read_text(encoding="utf-8")))
    for f, text, fm in pages:
        if not fm or fm.get("type") == "map":
            continue
        for d in fm.get("domains", []) or []:
            if d in map_texts and f.stem not in map_texts[d]:
                YEL.append(f"WS 맵 미등재: [[{f.stem}]] → WS — 맵(값 `{d}`) — build_index.py 재실행 필요")


def check_index(pages, names):
    idx = VAULT / "00. Core" / "index.md"
    text = idx.read_text(encoding="utf-8")
    listed = set(wikilinks(text))
    expected = {f.stem for f, _, fm in pages if fm}
    for p in sorted(expected - listed):
        RED.append(f"index 누락: [[{p}]]")
    for p in sorted(listed - {n for n in names}):
        RED.append(f"index 유령 항목(파일 없음): [[{p}]]")
    for line in text.splitlines():
        m = re.match(r"- (?:⭐ )?\[\[[^\]]+\]\] — (.+)$", line)
        if m and len(m.group(1)) > 120:
            YEL.append(f"index 요약 120자 초과({len(m.group(1))}자): {line[:50]}…")


def check_raw_hashes():
    raw = VAULT / "10. Raw Sources"
    manifest = json.loads(HASH_MANIFEST.read_text()) if HASH_MANIFEST.exists() else {}
    current, new = {}, []
    for f in sorted(raw.rglob("*")):
        if not f.is_file() or f.name in ("CLAUDE.md", ".gitkeep", ".DS_Store"):
            continue
        rel = f.relative_to(VAULT).as_posix()
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        current[rel] = h
        if rel not in manifest:
            new.append(rel)
        elif manifest[rel] != h:
            RED.append(f"Raw 불변 위반(해시 변경): {rel} — 헌법 규칙 1. 의도된 교체면 매니페스트 갱신 후 log 기록")
    for rel in manifest:
        if rel not in current:
            YEL.append(f"Raw 파일 소실(매니페스트에 있으나 없음): {rel}")
    if not any(m.startswith("Raw 불변") for m in RED):
        HASH_MANIFEST.write_text(json.dumps(current, ensure_ascii=False, indent=1))
        for rel in new:
            print(f"ℹ️  Raw 해시 신규 등록: {rel}")


def check_gates_and_refs(pages):
    """탐색 게이트·살아있는 참조·샤딩 (machine-gates v2 #3 — 기존 AI 판단 항목의 기계화)."""
    import datetime
    gate_on = "탐색 게이트 (활성)" in (VAULT / "CLAUDE.md").read_text(encoding="utf-8")
    backlog = [f.stem for f, _, fm in pages if fm and fm.get("explored") == "false"] if gate_on else []
    if backlog:
        print(f"ℹ️  탐색 게이트 백로그: explored: false {len(backlog)}장 (디렉터 검토 승격 대기)")
    for f, text, fm in pages:
        if gate_on and fm and fm.get("confidence") == "high" and "편향 점검" not in text:
            YEL.append(f"confidence: high인데 편향 점검 콜아웃 없음: {f.relative_to(VAULT).as_posix()}")
    who = VAULT / "00. Core" / "Who am I.md"
    if who.exists():
        age = (datetime.date.today() - datetime.date.fromtimestamp(who.stat().st_mtime)).days
        if age > 30:
            YEL.append(f"살아있는 참조: Who am I.md 최종 수정 {age}일 경과 — 갱신 검토 (디렉터 유지 문서)")
    q_count = len(list((VAULT / "30. Queries").glob("*.md"))) - 1  # CLAUDE.md 제외
    if q_count > 100:
        YEL.append(f"30. Queries {q_count}개 — 연도 폴더 샤딩 시점 (30. Queries/CLAUDE.md 전환 규칙)")


def check_orphans(pages):
    """고아 검출 — index·WS 맵(생성물) 밖에서 들어오는 링크가 0인 페이지 (연결 제안은 AI 몫)."""
    incoming = {f.stem: 0 for f, _, fm in pages if fm}
    for f, text, fm in pages:
        if not fm or fm.get("type") == "map":
            continue
        for link in set(wikilinks(fm_body(text))):
            if link in incoming and link != f.stem:
                incoming[link] += 1
    orphans = [n for n, (f, _, fm) in ((f.stem, (f, t, fm)) for f, t, fm in pages)
               if fm and fm.get("type") not in ("map",) and incoming.get(n, 0) == 0]
    if orphans:
        YEL.append(f"고아 페이지 {len(orphans)}장 (콘텐츠 페이지에서 미링크 — 연결 제안 필요): "
                   + " · ".join(f"[[{n}]]" for n in orphans[:8]) + (" …" if len(orphans) > 8 else ""))


def main():
    if not (VAULT / "90. Settings" / "Domain_Registry.md").exists():
        print("Domain_Registry.md 없음 — 아직 미설치 상태입니다. 먼저 /setup을 실행하세요.")
        sys.exit(2)
    domains_map = registry_domains()
    pages = wiki_pages()
    names = all_md_names()
    check_pages(pages, domains_map)
    check_wikilinks(pages, names)
    check_ws_maps(pages, domains_map)
    check_index(pages, names)
    check_raw_hashes()
    check_gates_and_refs(pages)
    check_orphans(pages)
    if "--json" in sys.argv:
        print(json.dumps({"red": RED, "yellow": YEL}, ensure_ascii=False, indent=1))
    else:
        for m in RED:
            print(f"🔴 {m}")
        for m in YEL:
            print(f"🟡 {m}")
        print(f"\n기계 린트: 페이지 {len(pages)}장 — 🔴 {len(RED)} · 🟡 {len(YEL)}"
              + (" — ALL PASS ✅" if not RED and not YEL else ""))
    sys.exit(1 if RED else 0)


if __name__ == "__main__":
    main()
