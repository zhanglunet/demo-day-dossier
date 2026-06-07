#!/usr/bin/env bash
# 用 Chrome headless 把一份本地 HTML 渲染成 @2x Retina PNG。
#
# 用法：
#   render-image.sh <input.html> <output.png> <width> <height>
#
# 示例：
#   render-image.sh templates/cover-1200x675.html.tmpl  out/cover.png  1200 675
#   render-image.sh templates/pipeline-1200x600.html.tmpl out/pipeline.png 1200 600
#
# 也可以截线上 URL：
#   render-image.sh "https://example.com/" out/example.png 1280 800

set -euo pipefail

INPUT="${1:?用法: render-image.sh <input.html|URL> <output.png> <width> <height>}"
OUTPUT="${2:?需要输出 PNG 路径}"
W="${3:?需要宽度（px）}"
H="${4:?需要高度（px）}"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ ! -x "$CHROME" ]; then
  echo "ERROR: 找不到 Chrome，请装 Google Chrome 或改 CHROME 路径" >&2
  exit 1
fi

# 本地 HTML → file:// URL；URL 直接用
if [[ "$INPUT" == http*://* ]]; then
  URL="$INPUT"
else
  if [ ! -f "$INPUT" ]; then
    echo "ERROR: 找不到 $INPUT" >&2
    exit 1
  fi
  URL="file://$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
fi

mkdir -p "$(dirname "$OUTPUT")"

"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --window-size="$W,$H" --force-device-scale-factor=2 \
  --screenshot="$OUTPUT" --virtual-time-budget=4000 \
  "$URL" 2>&1 | grep -iE "error|fail" | grep -vi "task_policy" || true

if [ ! -f "$OUTPUT" ]; then
  echo "❌ 渲染失败：$OUTPUT 没有生成" >&2
  exit 1
fi

SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)
KB=$((SIZE / 1024))
echo "✅ $OUTPUT  (${W}×${H} @2x, ${KB} KB)"
