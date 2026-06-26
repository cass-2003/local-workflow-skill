#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阶段 6：给 winner 打 tier(通用/半通用) + 检测近义变体簇。标注只进 manifest/报告。"""
import csv, re, os
from collections import defaultdict

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAN = os.environ.get("PAW_MERGE_MANIFEST", os.path.join(REPO_ROOT, "skills", "_merge-manifest.csv"))

rows = list(csv.DictReader(open(MAN, encoding="utf-8-sig")))
wins = [r for r in rows if r["winner"] == "WIN"]

# --- tier 规则 ---
# Project-specific skills are excluded by gen_manifest.py before tiering. This
# repository keeps only portable skills: generic or vendor/product-specific.
SEMI_VENDOR_DOMAINS = {"payments-commerce","maps-location"}
SEMI_PREFIX = ("figma","notion","anna-","coff0xc-")
SEMI_SLUGS = {"vercel-deploy","netlify-deploy","cloudflare-deploy","render-deploy",
              "linear","sentry","chatgpt-apps","winui-app","aspnet-core"}

def tier(r):
    s, slug, dom = r["source"], r["slug"], r["proposed_domain"]
    if dom in SEMI_VENDOR_DOMAINS: return "半通用"
    if slug in SEMI_SLUGS: return "半通用"
    if slug.startswith(SEMI_PREFIX): return "半通用"
    if dom == "mobile-crossplatform" and re.search(r"miniprogram|harmonyos", slug): return "半通用"
    return "通用"

for r in wins:
    r["tier"] = tier(r)

# 写回 manifest（加 tier 列）
fields = list(rows[0].keys())
if "tier" not in fields: fields.append("tier")
for r in rows:
    r.setdefault("tier", "" if r["winner"]!="WIN" else r.get("tier",""))
with open(MAN, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for r in sorted(rows, key=lambda x:(x["proposed_domain"],x["source"],x["slug"])): w.writerow(r)

# --- 变体簇：剥 anna-/coff0xc- 前缀 + dev/development/engineering 后缀 后同 key 且 size>1 ---
def loose(slug):
    k = re.sub(r"^(anna-|coff0xc-)", "", slug.lower())
    k = re.sub(r"-(dev|development|engineering|reverse-engineering)$", "", k)
    return {"javascript-typescript":"ts","js-ts":"ts","typescript":"ts"}.get(k,k)
clusters = defaultdict(list)
for r in wins: clusters[loose(r["slug"])].append(r)
dup = {k:v for k,v in clusters.items() if len(v)>1}

# --- 报告 ---
from collections import Counter
print("=== tier 分布 ===")
for t,c in Counter(r["tier"] for r in wins).most_common(): print(f"  {t}: {c}")
print(f"\n=== 近义变体簇（{len(dup)} 簇，{sum(len(v) for v in dup.values())} 个技能）===")
for k in sorted(dup, key=lambda x:-len(dup[x])):
    items=[f"{r['slug']}[{r['source']}/{r['tier']}]" for r in dup[k]]
    print(f"  · {k} ({len(items)})：{'、'.join(items)}")
print(f"\nmanifest 已加 tier 列 -> {MAN}")
