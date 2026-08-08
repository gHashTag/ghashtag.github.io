#!/usr/bin/env bash
# Check that what is committed here is what t27.ai actually serves.
#
# Written because three separate checks returned a confident green on something
# broken: a build script that skips the typechecker, an asset-hash pattern that
# missed the underscore in Vite hashes and so compared an empty string against
# an empty string, and a redirect stub that looked right in a browser while
# every crawler received the homepage.
#
# Every check here fails loudly on an empty value rather than treating it as a
# pass. That is the whole point.
#
#   ./verify-site.sh          check the live site
#   ./verify-site.sh --local  check only what is on disk (no network)

set -uo pipefail
cd "$(dirname "$0")"

SITE="https://t27.ai"
PAGES="gft verification proof ip course cases about"
fails=0

red()  { printf '  \033[31m✗\033[0m %s\n' "$1"; fails=$((fails + 1)); }
green(){ printf '  \033[32m✓\033[0m %s\n' "$1"; }

echo
echo "── on disk ──"

# The domain lives or dies by this file; a deploy that drops it takes the site
# off its own name.
if [ "$(cat CNAME 2>/dev/null)" = "t27.ai" ]; then
  green "CNAME is t27.ai"
else
  red "CNAME missing or wrong: '$(cat CNAME 2>/dev/null)'"
fi

LOCAL_JS=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' index.html 2>/dev/null | head -1)
if [ -n "$LOCAL_JS" ]; then
  green "index.html references $LOCAL_JS"
else
  red "no bundle reference found in index.html — the pattern or the file is wrong"
fi

missing=0
for f in $(grep -o 'assets/[A-Za-z0-9._-]*' index.html 2>/dev/null | sort -u); do
  [ -f "$f" ] || { red "index.html references a missing file: $f"; missing=1; }
done
[ "$missing" = 0 ] && green "every referenced asset exists on disk"

# A landing page that redirects into a fragment URL cannot be indexed: the
# crawler discards the fragment and files the page under the homepage.
for p in $PAGES; do
  f="$p/index.html"
  if [ ! -f "$f" ]; then
    red "$p/ is missing"
    continue
  fi
  words=$(sed -e 's/<[^>]*>/ /g' "$f" | wc -w | tr -d ' ')
  if grep -q 'location.replace\|http-equiv="refresh"' "$f"; then
    red "$p/ still auto-redirects — it will not be indexed"
  elif [ "$words" -lt 150 ]; then
    red "$p/ has only $words words — too thin to index"
  else
    green "$p/ is a real page ($words words)"
  fi
  for tag in 'og:title' 'og:description' 'og:image' 'rel="canonical"'; do
    grep -q "$tag" "$f" || red "$p/ is missing $tag"
  done
done

grep -q "Sitemap: $SITE/sitemap.xml" robots.txt 2>/dev/null \
  && green "robots.txt points at the sitemap" \
  || red "robots.txt missing or does not reference the sitemap"

for p in $PAGES; do
  grep -q "<loc>$SITE/$p/</loc>" sitemap.xml 2>/dev/null || red "sitemap.xml does not list /$p/"
done
grep -q "<loc>$SITE/</loc>" sitemap.xml 2>/dev/null \
  && green "sitemap.xml lists the homepage and $(grep -c '<loc>' sitemap.xml) URLs in total" \
  || red "sitemap.xml missing or does not list the homepage"

if [ "${1:-}" = "--local" ]; then
  echo
  [ "$fails" = 0 ] && echo "on-disk checks passed" || echo "$fails problem(s) on disk"
  exit $((fails > 0))
fi

echo
echo "── live ──"

LIVE_JS=$(curl -fsS "$SITE/index.html?cb=$RANDOM" 2>/dev/null | grep -o 'assets/index-[A-Za-z0-9_-]*\.js' | head -1)
if [ -z "$LIVE_JS" ]; then
  red "could not read a bundle reference from the live homepage"
elif [ "$LIVE_JS" = "$LOCAL_JS" ]; then
  green "live bundle matches what is committed ($LIVE_JS)"
else
  red "live is serving $LIVE_JS but this checkout has $LOCAL_JS — not published yet, or not published at all"
fi

for p in "" $PAGES; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -L "$SITE/$p")
  [ "$code" = "200" ] && green "/$p → 200" || red "/$p → $code"
done

for f in robots.txt sitemap.xml cv.pdf; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$SITE/$f")
  [ "$code" = "200" ] && green "/$f → 200" || red "/$f → $code"
done

# Preview images are the difference between a link that sells and a link that
# looks like spam, and they break silently.
for p in $PAGES; do
  img=$(curl -fsS "$SITE/$p/" 2>/dev/null | grep -o 'og:image" content="[^"]*"' | sed 's/.*content="//;s/"$//')
  if [ -z "$img" ]; then
    red "/$p/ serves no og:image"
    continue
  fi
  code=$(curl -s -o /dev/null -w '%{http_code}' "$img")
  [ "$code" = "200" ] && green "/$p/ preview image → 200" || red "/$p/ preview image $img → $code"
done

echo
if [ "$fails" = 0 ]; then
  echo "all checks passed"
else
  echo "$fails check(s) failed"
fi
exit $((fails > 0))
