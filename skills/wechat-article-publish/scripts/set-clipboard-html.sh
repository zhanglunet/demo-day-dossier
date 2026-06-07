#!/usr/bin/env bash
# 把一个 HTML 文件作为 «class HTML» 富文本类型放到 macOS 剪贴板。
#
# 为什么不能用 pbcopy？
#   pbcopy 把内容当 text/plain。公众号编辑器粘贴时看到 plain 就当字符串处理，
#   会显示成裸的 <section><h1>... 标签字符串。
#   必须用 osascript 的 read POSIX file ... as «class HTML»，
#   公众号编辑器才会识别为富文本 HTML 并解析。
#
# 用法：
#   set-clipboard-html.sh <article.html>
#
# 之后验证：
#   osascript -e 'return (clipboard info)'
#   # 应该看到：«class HTML», <字节数>

set -euo pipefail

HTML="${1:?用法: set-clipboard-html.sh <article.html>}"
if [ ! -f "$HTML" ]; then
  echo "ERROR: 找不到 $HTML" >&2
  exit 1
fi

# 转绝对路径（osascript 需要）
ABS=$(cd "$(dirname "$HTML")" && pwd)/$(basename "$HTML")

osascript -e "set the clipboard to (read POSIX file \"$ABS\" as «class HTML»)"
INFO=$(osascript -e 'return (clipboard info)' 2>/dev/null | head -1)
echo "✅ 剪贴板已设为 HTML 富文本：$INFO"
echo "   下一步：到公众号编辑器正文区，Cmd+V 即可。"
