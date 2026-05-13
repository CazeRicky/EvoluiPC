#!/bin/sh

set -eu

DJANGO_URL="${DJANGO_URL:-http://django:8000}"
ENGINE_URL="${ENGINE_URL:-http://engine:8002}"

pass_count=0
fail_count=0

check_endpoint() {
  name="$1"
  method="$2"
  url="$3"
  expected="$4"
  body="${5:-}"

  if [ "$method" = "POST" ]; then
    code="$(curl -s -o /tmp/evoluipc_test_body -w '%{http_code}' -X POST "$url" -H 'Content-Type: application/json' -d "$body" || true)"
  else
    code="$(curl -s -o /tmp/evoluipc_test_body -w '%{http_code}' -X GET "$url" || true)"
  fi

  case "$expected" in
    *"$code"*)
      pass_count=$((pass_count + 1))
      ;;
    *)
      fail_count=$((fail_count + 1))
      return 1
      ;;
  esac
}

check_connection() {
  name="$1"
  host="$2"
  port="$3"

  if nc -z "$host" "$port" >/dev/null 2>&1; then
    pass_count=$((pass_count + 1))
  else
    fail_count=$((fail_count + 1))
    return 1
  fi
}

check_connection Neo4j neo4j 7687 || true
check_connection Engine engine 8002 || true
check_connection Django django 8000 || true

check_endpoint "Django auth me" GET "$DJANGO_URL/api/auth/me" "401" 
check_endpoint "Django register" POST "$DJANGO_URL/api/auth/register" "400|201" '{"username":"testuser","email":"test@example.com","password":"testpass123"}' || true
check_endpoint "Django login" POST "$DJANGO_URL/api/auth/login" "400|401" '{"username":"invalid","password":"invalid"}' || true
check_endpoint "Engine recommendations" GET "$ENGINE_URL/api/recommendations/me" "400|401" 

if [ "$fail_count" -eq 0 ]; then
  echo "PASS"
  exit 0
fi

echo "FAIL"
exit 1
