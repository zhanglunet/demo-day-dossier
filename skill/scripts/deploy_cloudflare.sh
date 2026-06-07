#!/usr/bin/env bash
# 为 demo-day-dossier 工作目录做幂等的 Cloudflare Pages 部署。
#
# 用法：
#   deploy_cloudflare.sh <workdir> <project-name> [commit-msg]
#
# 注意：
#   - 调用前需先完成 `npx wrangler login`。
#   - 只推送 index.html + dd.html，不推送 JSON / docx / md 源文件。

set -euo pipefail

WORKDIR="${1:?Usage: deploy_cloudflare.sh <workdir> <project-name> [commit-msg]}"
PROJECT="${2:?Need a Cloudflare Pages project slug}"
COMMIT="${3:-Demo-day dossier update}"

if [ ! -d "$WORKDIR/output" ]; then
  echo "ERROR: 找不到 $WORKDIR/output/" >&2
  exit 1
fi

# 准备部署目录（只放对外公开安全的文件）
DEPLOY_DIR="$WORKDIR/output/_deploy"
mkdir -p "$DEPLOY_DIR"
for f in index.html dd.html; do
  if [ -f "$WORKDIR/output/$f" ]; then
    cp "$WORKDIR/output/$f" "$DEPLOY_DIR/"
  fi
done

echo "=== 待部署文件 ==="
ls -lh "$DEPLOY_DIR"
echo "==================="

# 鉴权检查
if ! npx wrangler whoami 2>&1 | grep -q "You are logged in"; then
  echo "ERROR: 尚未登录，请先在终端执行：! npx wrangler login" >&2
  exit 1
fi

# 创建 Pages 项目（幂等 — 已存在则忽略）
npx wrangler pages project create "$PROJECT" --production-branch=main 2>&1 || true

# 部署
npx wrangler pages deploy "$DEPLOY_DIR" \
  --project-name="$PROJECT" \
  --branch=main \
  --commit-message="$COMMIT"

echo ""
echo "=== 线上验收 ==="
curl -s -o /dev/null -w "Home  HTTP %{http_code}  %{size_download}B\n" "https://${PROJECT}.pages.dev/" || true
curl -s -o /dev/null -w "DD    HTTP %{http_code}  %{size_download}B\n" -L "https://${PROJECT}.pages.dev/dd" || true
echo ""
echo "🌐 全景页：https://${PROJECT}.pages.dev/"
echo "🌐 DD 表：https://${PROJECT}.pages.dev/dd"
