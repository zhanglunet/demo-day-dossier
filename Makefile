# dist-repo · 奇绩路演项目 / wiki 协作 Makefile

.PHONY: sync serve check clean help

help:
	@echo "Targets:"
	@echo "  sync   — projects.json → batch-4 → merge → render → embed (站点 + wiki 全量同步)"
	@echo "  serve  — 本地 :8888 起 CF Pages 模拟服务"
	@echo "  check  — 跑 sync 后 git diff, 不一致则 fail (CI 用)"
	@echo "  clean  — 删除 wiki 渲染产物 (保留 raw batches)"

sync:
	@python3 scripts/sync-wiki.py

serve:
	@cd output && python3 -m http.server 8888

check:
	@python3 scripts/sync-wiki.py > /dev/null
	@if [ -n "$$(git status --porcelain output/)" ]; then \
		echo "✗ output/ 与 projects.json 不同步, 请本地跑 \`make sync\` 后重新提交"; \
		git status --short output/; \
		exit 1; \
	else \
		echo "✓ output/ 与 projects.json 已同步"; \
	fi

clean:
	@rm -rf output/wiki/meetings output/wiki/people output/wiki/concepts output/wiki/entities
	@rm -f output/wiki/index.html output/wiki/data/extracted.json output/wiki/data/search-index.json
	@echo "✓ cleaned rendered wiki HTML (raw batches preserved)"
