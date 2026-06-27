#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 manifest 把 winner 整目录复制到 skills/.merged/<domain>/<source>/<slug>/。"""
import os, csv, shutil

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(REPO_ROOT, ".."))

SKILLS = os.environ.get("PAW_SKILLS_DIR", os.path.join(REPO_ROOT, "skills"))
OURS = os.environ.get("PAW_OURS_SKILLS", SKILLS)
CODEX = os.environ.get("PAW_CODEX_SKILLS", os.path.expanduser("~/.codex/skills"))
CSK = os.environ.get("PAW_CSKILLS_DIR", os.path.join(WORKSPACE_ROOT, "C_Skills", "_unzipped", "all-skills"))
MANIFEST = os.path.join(SKILLS, "_merge-manifest.csv")
MERGED = os.path.join(SKILLS, ".merged")

SRC_BASE = {"ours": OURS, "community": OURS, "codex": CODEX, "cskills": CSK}

if os.path.exists(MERGED):
    shutil.rmtree(MERGED)

rows = [r for r in csv.DictReader(open(MANIFEST, encoding="utf-8-sig")) if r["winner"] == "WIN"]
copied = 0
errors = []
for r in rows:
    src_root = SRC_BASE[r["source"]]
    src = os.path.join(src_root, r["relpath"].replace("/", os.sep))
    if not os.path.isdir(src):
        errors.append(f"MISSING SRC: {r['source']} {r['relpath']}")
        continue
    dst = os.path.join(MERGED, r["proposed_domain"], r["source"], r["slug"])
    shutil.copytree(src, dst, dirs_exist_ok=True)
    # prune coff0xc 嵌套同名冗余子目录
    nested = os.path.join(dst, r["slug"])
    if os.path.isdir(nested) and os.path.isfile(os.path.join(nested, "SKILL.md")):
        shutil.rmtree(nested)
    copied += 1

print(f"copied: {copied} / {len(rows)} winners")
if errors:
    print("ERRORS:")
    for e in errors:
        print("  " + e)

# verify counts
total_skillmd = sum(1 for _,_,fs in os.walk(MERGED) for f in fs if f == "SKILL.md")
top_skillmd = 0
for dom in os.listdir(MERGED):
    for src in os.listdir(os.path.join(MERGED, dom)):
        for slug in os.listdir(os.path.join(MERGED, dom, src)):
            if os.path.isfile(os.path.join(MERGED, dom, src, slug, "SKILL.md")):
                top_skillmd += 1
print(f"top-level skill dirs with SKILL.md: {top_skillmd}")
print(f"total SKILL.md (incl nested sub-skills like orchestration/tools): {total_skillmd}")
print(f"domains created: {len(os.listdir(MERGED))}")
