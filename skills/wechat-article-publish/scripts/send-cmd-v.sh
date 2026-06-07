#!/usr/bin/env bash
# 远程激活某个浏览器窗口并发送 Cmd+V 粘贴。
#
# 使用前提：
#   1. 剪贴板已经用 set-clipboard-html.sh 设成 «class HTML» 类型
#   2. 浏览器里你已经把光标定位到公众号编辑器的正文区
#
# 用法：
#   send-cmd-v.sh                          # 默认 Google Chrome
#   send-cmd-v.sh "Google Chrome"          # 你日常 Chrome（已登录）
#   send-cmd-v.sh "Google Chrome for Testing"  # Playwright 启动的 Chromium
#
# 注意：System Events 的 keystroke 需要 Mac 系统给 Terminal / iTerm /
# 你的 shell host 授予「辅助访问」权限（System Settings → Privacy &
# Security → Accessibility）。首次运行会弹权限提示，授权后再跑一次即可。

set -euo pipefail

APP="${1:-Google Chrome}"

osascript <<EOF
tell application "$APP" to activate
delay 0.6
tell application "System Events"
  keystroke "v" using {command down}
end tell
return "✅ Cmd+V 已发送到「$APP」"
EOF
