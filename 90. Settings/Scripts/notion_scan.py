#!/usr/bin/env python3
"""노션 화이트리스트 동기화 스캔 (machine-gates v2 #1) — /ingest 모드 C의 수집 단계를 기계화.

장부 헤더의 DB IDs에 등록된 데이터소스에서 last_scan 이후 생성·수정된 페이지 목록만 뽑아
표로 출력한다 (장부 기등재 여부 표시). 인제스트 여부 판단은 AI·디렉터의 몫.

요구: NOTION_TOKEN 환경변수. 없으면 안내 후 종료(스킬이 MCP 경로로 폴백).
사용: notion_scan.py [--since ISO8601] [--limit N]
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[2] / "00. Core" / "ingest-ledger.md"
TOKEN = os.environ.get("NOTION_TOKEN", "")


def api(path, payload, version):
    req = urllib.request.Request(
        f"https://api.notion.com/v1/{path}", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Notion-Version": version,
                 "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def query_ds(ds_id, since, limit):
    payload = {"page_size": min(limit, 100),
               "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}]}
    if since:
        payload["filter"] = {"timestamp": "last_edited_time", "last_edited_time": {"after": since}}
    try:
        return api(f"data_sources/{ds_id}/query", payload, "2025-09-03")["results"]
    except Exception:
        return api(f"databases/{ds_id}/query", payload, "2022-06-28")["results"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since")
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()

    if not TOKEN:
        print("NOTION_TOKEN 없음 — MCP 경로(notion-search/query)로 폴백하세요.")
        sys.exit(2)

    text = LEDGER.read_text(encoding="utf-8")
    since = args.since
    if not since:
        m = re.search(r"^> last_scan:\s*(\S+)", text, re.M)
        since = m.group(1) if m and m.group(1).startswith("2") else None
    dbs = dict(re.findall(r"([\w가-힣 .'&-]+)=collection://([0-9a-f-]+)", text))
    known = set(re.findall(r"^\| ([^|]+?) \|", text, re.M))

    print(f"스캔 기준: since={since or '(전체)'} · DB {len(dbs)}개\n")
    total = 0
    for name, ds_id in dbs.items():
        try:
            results = query_ds(ds_id, since, args.limit)
        except Exception as e:
            print(f"⚠️ {name}: 조회 실패 — {e}")
            continue
        fresh = []
        for pg in results:
            pid = pg["id"].replace("-", "")
            pid_dash = pg["id"]
            title = ""
            for prop in pg.get("properties", {}).values():
                if prop.get("type") == "title" and prop["title"]:
                    title = "".join(t.get("plain_text", "") for t in prop["title"])
            mark = "기등재" if (pid_dash in known or pid in known) else "신규"
            fresh.append((pid_dash, title[:50], pg.get("last_edited_time", ""), mark))
        total += len(fresh)
        print(f"== {name} ({len(fresh)}건)")
        for pid, title, edited, mark in fresh:
            print(f"  [{mark}] {title} | {edited} | {pid}")
    print(f"\n총 {total}건. 인제스트할 항목을 골라 /ingest 공통 절차로 처리한 뒤 `ledger.py touch-scan <ISO>`.")


if __name__ == "__main__":
    main()
