#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 .merged 双层结构切换为 skills/ 正式结构：删旧 7 类目录 → 上移 .merged/* → 清理。"""
import os, shutil, time

SKILLS = r"J:\07-Codex与AI工具\05-工作区与技能\skills-workspace\local-skills-workspace\skills"
MERGED = os.path.join(SKILLS, ".merged")
OLD_CATS = ["backend-infra","data-sync-validation","engineering-core",
            "frontend-extension","language-runtime","source-commands","workflow-core"]

def robust_rmtree(p):
    for _ in range(12):
        try:
            shutil.rmtree(p); return True
        except (PermissionError, OSError):
            time.sleep(0.8)
    return not os.path.exists(p)

# 1. 删旧 7 类
for c in OLD_CATS:
    p = os.path.join(SKILLS, c)
    if os.path.isdir(p):
        ok = robust_rmtree(p)
        print(f"removed old {c}: {ok}")

# 2. 上移 .merged/* → skills/
for dom in sorted(os.listdir(MERGED)):
    src = os.path.join(MERGED, dom)
    dst = os.path.join(SKILLS, dom)
    if os.path.exists(dst):
        robust_rmtree(dst)
    shutil.move(src, dst)
print(f"moved {len(os.listdir(SKILLS))} entries up")

# 3. 清理 .merged
robust_rmtree(MERGED)
print(f".merged gone: {not os.path.exists(MERGED)}")

# 4. report
doms = [d for d in sorted(os.listdir(SKILLS)) if os.path.isdir(os.path.join(SKILLS,d)) and not d.startswith('.')]
print("final domains:", doms)
