#!/bin/sh
# 자동 백업 (llm-wiki-starter): 스테이징→pre-commit 훅→커밋(형식 고정)→푸시→검증 한 줄.
# 사용: backup.sh "<작업 한 줄 요약>"   → 커밋 메시지 "wiki: <요약>" + Co-Authored-By 푸터
set -e
cd "$(dirname "$0")/../.."
[ -n "$1" ] || { echo "사용법: backup.sh \"<요약>\"" >&2; exit 2; }

if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "변경 없음 — 커밋 생략"; exit 0
fi
git add -A
git commit -m "wiki: $1"
git push
[ -z "$(git status --porcelain)" ] && echo "백업 완료 ✅ $(git log --oneline -1)" || { echo "⚠️ 워킹트리가 클린하지 않음" >&2; exit 1; }
