# 能力库合并工具（一次性 · provenance 记录）

记录 `skills/` 从 42 → 435 技能是怎么合并出来的。**脚本内路径为生成时的本机绝对路径**，非通用工具；保留是为了**可复现与可审计**，再次运行需按本机环境改路径。

## 三步流水线

| 脚本 | 作用 |
|---|---|
| `gen_manifest.py` | 枚举三源（ours / `~/.codex/skills` / C_Skills）→ 归一化键去重（ours>codex>cskills）→ 领域归类 → 产出 `skills/_merge-manifest.csv` |
| `do_copy.py` | 按 manifest 把 winner 整目录复制到暂存 `skills/.merged/<大类>/<来源>/<slug>/`，展平 coff0xc 嵌套冗余 |
| `do_swap.py` | 删旧 7 类目录 → 把 `.merged/*` 上移为正式结构 → 清理 |

## 关键约定（与 `framework/core/03-routing.md`、`skills/README.md` 一致）

- **归一化键**：小写 + 剥 `-dev/-development/-engineering` 后缀 + 别名表（`js-ts`↔`javascript-typescript`）。不剥家族前缀（`anna-`/`coff0xc-`），故同语言的不同作者变体作为独立技能保留。
- **去重**：同键按 ours>codex>cskills 留一个赢家。
- **排除**：`.system`、`codex-windows-fast-patch` 等运行时内部项；`*.bak/.tmp`。
- **领域**：cskills 取 C_Skills README 的「分类」列；ours 取原目录；codex 用 `CODEX_EXACT` 精确映射 + 关键词规则。

## 复现

```bash
py -3 tools/skill-merge/gen_manifest.py   # 先看 _merge-manifest.csv
py -3 tools/skill-merge/do_copy.py        # 复制到 .merged 暂存
py -3 tools/skill-merge/do_swap.py        # 切换为正式结构
```

体检基线：435 赢家 · frontmatter 0 缺失 · 0 空目录 · 0 跨域重复 slug · README 计数 0 不符。
