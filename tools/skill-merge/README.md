# 能力库合并工具（一次性 · provenance 记录）

记录 `skills/` 从 42 → 409 → 439 → 517 → 523 → 557 → 565 技能是怎么合并和扩容出来的。脚本默认使用仓库相对路径和 `~/.codex/skills`，也可以通过环境变量改写来源位置，保留是为了**可复现与可审计**。

## 三步流水线

| 脚本 | 作用 |
|---|---|
| `gen_manifest.py` | 枚举来源层（ours / codex / community，可选第三方授权包归入 community）→ 归一化键去重（ours>codex>community）→ 领域归类 → 产出 `skills/_merge-manifest.csv` |
| `do_copy.py` | 按 manifest 把 winner 整目录复制到暂存 `skills/.merged/<大类>/<来源>/<slug>/`，展平 coff0xc 嵌套冗余 |
| `do_swap.py` | 删旧 7 类目录 → 把 `.merged/*` 上移为正式结构 → 清理 |

## 关键约定（与 `framework/core/03-routing.md`、`skills/README.md` 一致）

- **归一化键**：小写 + 剥 `-dev/-development/-engineering` 后缀 + 别名表（`js-ts`↔`javascript-typescript`）。不剥家族前缀（`anna-`/`coff0xc-`），故同语言的不同作者变体作为独立技能保留。
- **去重**：同键按 ours>codex>community 留一个赢家。
- **排除**：`.system`、`codex-windows-fast-patch`、运行时命令封装、项目/产品定制样本等非通用项；`*.bak/.tmp`。
- **领域**：正式仓库结构优先取目录领域；可选第三方授权包可通过 README 分类映射；codex 原始导入可用 `CODEX_EXACT` 精确映射 + 关键词规则。

## 复现

```bash
# 可选：按你的机器位置覆盖来源
# export PAW_CODEX_SKILLS="$HOME/.codex/skills"
# export PAW_EXTERNAL_SKILLS_DIR="/path/to/authorized-skills"
# export PAW_EXTERNAL_SKILLS_README="/path/to/authorized-skills/README.md"

py -3 tools/skill-merge/gen_manifest.py   # 先看 _merge-manifest.csv
py -3 tools/skill-merge/do_copy.py        # 复制到 .merged 暂存
py -3 tools/skill-merge/do_swap.py        # 切换为正式结构
```

> 注意：第三方授权包是可选导入源；正式仓库中统一落到 `community/` 来源层，不在公开索引里单独拆来源。

体检基线：565 赢家 · frontmatter 0 缺失 · 0 空目录 · 0 跨域重复 slug · README 计数 0 不符。
