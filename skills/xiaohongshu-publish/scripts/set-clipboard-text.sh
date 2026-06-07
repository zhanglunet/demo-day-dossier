#!/usr/bin/env bash
# 把一段文本（不含格式）放进 macOS 剪贴板，给小红书创作中心的标题 / 正文
# 单行输入框用。
#
# 为什么不直接 pbcopy？
#   pbcopy 也可以，但中文 + emoji + 换行有时会被 shell 截断。
#   这个脚本用 osascript 转一道，emoji 和换行都安全。
#
# 用法：
#   set-clipboard-text.sh "纯文本内容"
#   set-clipboard-text.sh "$(cat /tmp/post-body.txt)"
#   set-clipboard-text.sh "$(jq -r .body /tmp/xhs.json)"

set -euo pipefail

TEXT="${1:?用法: set-clipboard-text.sh <text>}"

# AppleScript 字符串转义：\ → \\，" → \"
ESCAPED=$(printf '%s' "$TEXT" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')

osascript -e "set the clipboard to \"$ESCAPED\"" 2>&1
CHARS=$(printf '%s' "$TEXT" | wc -c | tr -d ' ')
echo "✅ 剪贴板已设为纯文本（$CHARS 字节）"
