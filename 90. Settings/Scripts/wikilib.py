"""LLM Wiki 기계 게이트 공용 라이브러리 — frontmatter 파싱·페이지 수집·레지스트리 로드."""
import re
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]

WIKI_DIRS = ["20. Wiki/21. Concepts", "20. Wiki/22. Entities", "20. Wiki/23. Sources",
             "20. Wiki/24. Guides", "20. Wiki/25. Maps", "20. Wiki/26. Questions"]
TYPE_DIR = {"concept": "21. Concepts", "entity": "22. Entities", "source": "23. Sources",
            "guide": "24. Guides", "map": "25. Maps", "research-question": "26. Questions"}
ALLOWED_TYPES = {"source", "concept", "entity", "guide", "map", "query", "synthesis",
                 "research-question", "paper-hub", "paper-analysis", "raw"}


def parse_frontmatter(text):
    """평탄 키 전용 미니 파서. dict 반환 (frontmatter 없으면 None). 값은 문자열, 리스트는 [a, b] 형태만."""
    if not text.startswith("---"):
        return None
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if not line or line.startswith("#") or line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.split("  #")[0].strip().strip('"')
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key.strip()] = [v.strip().strip('"') for v in inner.split(",") if v.strip()] if inner else []
        else:
            fm[key.strip()] = val
    return fm


def fm_body(text):
    m = re.match(r"^---\n.*?\n---\n?", text, re.S)
    return text[m.end():] if m else text


def wiki_pages():
    """검사 대상 페이지 (path, text, fm) 목록 — 20. Wiki 전 타입 + 30. Queries + 40 허브 + 00. Core/WS — Home."""
    pages = []
    for d in WIKI_DIRS:
        p = VAULT / d
        if p.exists():
            for f in sorted(p.glob("*.md")):
                if f.name == "CLAUDE.md":
                    continue
                t = f.read_text(encoding="utf-8")
                pages.append((f, t, parse_frontmatter(t)))
    q = VAULT / "30. Queries"
    for f in sorted(q.glob("*.md")):
        if f.name == "CLAUDE.md":
            continue
        t = f.read_text(encoding="utf-8")
        pages.append((f, t, parse_frontmatter(t)))
    pa = VAULT / "40. Paper Analyses"
    if pa.exists():
        for f in sorted(pa.glob("*/*.md")):
            t = f.read_text(encoding="utf-8")
            fm = parse_frontmatter(t)
            if fm and fm.get("type") == "paper-hub":  # 원자는 면제 — 허브만
                pages.append((f, t, fm))
    home = VAULT / "00. Core" / "WS — Home.md"
    if home.exists():
        t = home.read_text(encoding="utf-8")
        pages.append((home, t, parse_frontmatter(t)))
    return pages


def all_md_names():
    """wikilink 해소용 — 볼트 전체 .md basename 집합 (숨김·superpowers 제외)."""
    names = set()
    for f in VAULT.rglob("*.md"):
        rel = f.relative_to(VAULT).as_posix()
        if rel.startswith(".") or "/." in rel:
            continue
        names.add(f.stem)
    return names


def registry_domains():
    """Domain_Registry.md에서 값→WS 맵 이름 매핑 로드."""
    reg = VAULT / "90. Settings" / "Domain_Registry.md"
    mapping = {}
    if not reg.exists():
        return mapping
    for line in reg.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*`([a-z_]+)`\s*\|.*?\[\[(WS — [^\]]+)\]\]", line)
        if m:
            mapping[m.group(1)] = m.group(2)
    return mapping


def wikilinks(text):
    """본문의 [[링크]] 목록 (별칭·헤딩 제거)."""
    return [l.split("|")[0].split("#")[0].strip() for l in re.findall(r"\[\[([^\]]+)\]\]", text)]
