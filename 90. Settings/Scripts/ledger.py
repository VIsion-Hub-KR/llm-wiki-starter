#!/usr/bin/env python3
"""인제스트 장부 기계 관리 (machine-gates v2 #2) — 표 파손·중복·갱신 누락 방지.

사용:
  ledger.py check <식별키>                  # 있으면 행 출력·exit 0, 없으면 NOT_FOUND·exit 1
  ledger.py add --key K --title T --edited E --raw R --status S [--date YYYY-MM-DD]
                                           # 행 추가 (동일 키 있으면 교체 — 갱신 인제스트)
  ledger.py touch-scan <ISO8601>           # last_scan 갱신 (전용 라인 관리)
  ledger.py set-db "<이름>=collection://<id>"  # DB ID 등록 (화이트리스트 resolve)
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[2] / "00. Core" / "ingest-ledger.md"


HEADER = ["# 인제스트 장부", "", "> /ingest 스킬 전용. 수동 편집 금지(ledger.py로만). 식별키: 외부 도서관=page_id · 웹=origin_url.",
          "> DB IDs: (외부 도서관 스캔 도입 시 set-db로 등록)", "",
          "| 식별키(page_id\\|origin_url) | 제목 | last_edited | raw 경로 | 인제스트일 | 상태 |", "|---|---|---|---|---|---|"]


def load():
    if not LEDGER.exists():
        LEDGER.write_text("\n".join(HEADER) + "\n", encoding="utf-8")
    return LEDGER.read_text(encoding="utf-8").splitlines()


def save(lines):
    LEDGER.write_text("\n".join(lines) + "\n", encoding="utf-8")


def rows(lines):
    out = []
    for i, l in enumerate(lines):
        if l.startswith("|") and not l.startswith("|---") and "식별키" not in l:
            cells = [c.strip() for c in l.strip("|").split("|")]
            out.append((i, cells))
    return out


def cmd_check(key):
    for _, cells in rows(load()):
        if cells and cells[0] == key:
            print("FOUND\t" + "\t".join(cells))
            return 0
    print("NOT_FOUND")
    return 1


def cmd_add(a):
    esc = lambda s: s.replace("|", "\\|")
    date = a.date or datetime.date.today().isoformat()
    row = f"| {esc(a.key)} | {esc(a.title)} | {esc(a.edited)} | {esc(a.raw)} | {date} | {esc(a.status)} |"
    lines = load()
    for i, cells in rows(lines):
        if cells and cells[0] == a.key:
            lines[i] = row
            save(lines)
            print(f"REPLACED: {a.key}")
            return 0
    lines.append(row)
    save(lines)
    print(f"ADDED: {a.key}")
    return 0


def cmd_touch_scan(iso):
    lines = load()
    for i, l in enumerate(lines):
        if re.match(r"^> last_scan:\s", l):
            lines[i] = f"> last_scan: {iso}"
            save(lines)
            print(f"last_scan = {iso}")
            return 0
    lines.insert(2, f"> last_scan: {iso}")
    save(lines)
    print(f"last_scan(신설) = {iso}")
    return 0


def cmd_set_db(pair):
    name, _, cid = pair.partition("=")
    lines = load()
    for i, l in enumerate(lines):
        if l.startswith("> DB IDs:"):
            if name in l:
                print(f"이미 등록됨: {name}")
                return 0
            lines[i] = l + f" · {name}={cid}"
            save(lines)
            print(f"DB 등록: {name}")
            return 0
    print("DB IDs 헤더 없음")
    return 1


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").add_argument("key")
    a = sub.add_parser("add")
    for f in ("--key", "--title", "--edited", "--raw", "--status"):
        a.add_argument(f, required=True)
    a.add_argument("--date")
    sub.add_parser("touch-scan").add_argument("iso")
    sub.add_parser("set-db").add_argument("pair")
    args = p.parse_args()
    if args.cmd == "check":
        sys.exit(cmd_check(args.key))
    if args.cmd == "add":
        sys.exit(cmd_add(args))
    if args.cmd == "touch-scan":
        sys.exit(cmd_touch_scan(args.iso))
    if args.cmd == "set-db":
        sys.exit(cmd_set_db(args.pair))
