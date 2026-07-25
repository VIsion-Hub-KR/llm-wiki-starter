#!/bin/sh
# 시크릿·대용량 커밋 차단 게이트 (machine-gates 스펙 #5) — .git/hooks/pre-commit에서 호출
# 검사 대상: staged 변경분만. 위반 시 커밋 중단(exit 1).

fail=0

# 1) 시크릿 패턴 (staged diff의 추가 줄만)
PATTERNS='sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|xox[bpa]-[A-Za-z0-9-]{10,}|ntn_[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
hits=$(git diff --cached --diff-filter=ACM -U0 | grep -E '^\+' | grep -EI "$PATTERNS" | head -5)
if [ -n "$hits" ]; then
  echo "🔴 pre-commit 차단: 시크릿 패턴이 staged 변경에 있습니다:" >&2
  echo "$hits" | sed 's/\(.\{60\}\).*/\1.../' >&2
  fail=1
fi

# 2) .env류 파일
envfiles=$(git diff --cached --name-only --diff-filter=ACM | grep -E '(^|/)\.env(\.|$)' )
if [ -n "$envfiles" ]; then
  echo "🔴 pre-commit 차단: .env 파일이 staged 되어 있습니다: $envfiles" >&2
  fail=1
fi

# 3) 5MB 초과 파일 (바이너리 정책 — 스펙 #4)
for f in $(git diff --cached --name-only --diff-filter=ACM); do
  [ -f "$f" ] || continue
  size=$(wc -c < "$f" | tr -d ' ')
  if [ "$size" -gt 5242880 ]; then
    echo "🔴 pre-commit 차단: 5MB 초과 파일 ($f, ${size}B) — 바이너리 정책 위반. 원본은 노션·드라이브에, 위키엔 링크만." >&2
    fail=1
  fi
done

exit $fail
