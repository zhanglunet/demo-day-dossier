# Demo-day-dossier · 中文 X thread 首跑

把 `dist-repo/docs/story.md`（438 行中文长文）改写成 10 条中文 X thread + 4 张 1200×675 中文配图。

## 发布记录

| 项 | 值 |
|---|---|
| 账号 | [@zhanglu](https://x.com/zhanglu) |
| 发布日期 | 2026-06-08 |
| Root URL | <https://x.com/zhanglu/status/2063789867855974665> |
| Thread 长度 | 10 条 |
| 配图 | 4 张（hook / pipeline / data / cta） |
| 发布路径 | **浏览器兜底**（post_thread_browser.py 流程） |
| API 路径状态 | ❌ 402 CreditsDepleted（dev portal 当前 enrolled account 无 credits） |

## 字数分布（X 中文加权计费，上限 280）

| Tweet | 角色 | 字符 | weighted | 图 |
|---|---|---|---|---|
| 1 | hook | 128 | 187 | 01-cover.png |
| 2 | pain | 86 | 128 | — |
| 3 | insight | 100 | 152 | — |
| 4 | what I had | 89 | 151 | — |
| 5 | pipeline | 160 | 206 | 02-pipeline.png |
| 6 | mechanism | 144 | 216 | — |
| 7 | counter-intuitive | 165 | 228 | — |
| 8 | data | 128 | 182 | 03-stat.png |
| 9 | meaning | 129 | 197 | — |
| 10 | CTA | 157 | 200 | 04-cta.png |

## 资产

```
examples/demo-day-dossier-2026-zh/
├── README.md           ← 本文件
├── thread.json         ← 10 条 thread 文本 + 图片映射
└── images/
    ├── 01-cover.png    (940 KB, "一晚 DD 完 56 个奇绩项目")
    ├── 02-pipeline.png (542 KB, "一条消息派 7 个 sub-agent")
    ├── 03-stat.png     (577 KB, 推荐度金字塔)
    └── 04-cta.png      (914 KB, GitHub + 线上链接 + 中文 quote)
```

中文模板源（next to English originals）：
```
templates/{cover,pipeline,stat,cta}-1200x675-zh.html.tmpl
```

## 复盘要点（写给下一次中文 X thread）

1. **X API Free tier 已废**（验证日 2026-06-08）：v1.1 `media/upload` 和 v2 `tweets` 都返回 402 CreditsDepleted。Basic tier $200/月起。Free 0 元用户**只能走浏览器路径**。
2. **加权计费**：中文字符各 2 单位，280 上限 → 实际 ~120-140 中文字一条。md2thread.py 校验的是 `len(text)`，对中文会**低估**，必须额外算 X-weighted。
3. **字体必须显式列中文 fallback**：headless Chrome 渲染 HTML 模板时，`-apple-system` 在 macOS 会回退到 PingFang SC；但稳妥写法是显式加 `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei"`，避免中文落到 Inter 变方框。
4. **letter-spacing 必须设 0**：英文模板里的负 letter-spacing 让中文字粘在一起，必须改 0 或正值。
5. **字号比英文要小 10-15%**：中文字符比拉丁字符占更多视觉权重，原 76px 在中文里嫌大。Cover 反而能放到 88px 因为字少；信息密集的 stat / pipeline 行高要更紧。
6. **粘贴可能要 Cmd+Shift+V**：X compose 偶尔对带 emoji 的 Unicode 剪贴板挑剔，普通 Cmd+V 不进字时切纯文本粘贴。
7. **图片附在 1, 5, 8, 10**：不要每条都附图，注意力会被稀释；中间条永远不放 URL（algo 降权）。

## 兜底流程的实际成本

- 文案改写：~10 分钟（手动结构化 + LLM 协助）
- 4 张图模板改造 + 渲染：~8 分钟
- 10 次手动 Cmd+V + 4 次拖图 + 最后 Post all：~5 分钟
- **总计：~25 分钟 / 0 元**（vs API 路径 $200/月 Basic tier）
