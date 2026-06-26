#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并 manifest 生成器：枚举三源 → 归一化去重(ours>codex>cskills) → 领域归类 → CSV。"""
import os, re, csv, sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(REPO_ROOT, ".."))

OURS = os.environ.get("PAW_OURS_SKILLS", os.path.join(REPO_ROOT, "skills"))
CODEX = os.environ.get("PAW_CODEX_SKILLS", os.path.expanduser("~/.codex/skills"))
CSK = os.environ.get("PAW_CSKILLS_DIR", os.path.join(WORKSPACE_ROOT, "C_Skills", "_unzipped", "all-skills"))
CSK_README = os.environ.get("PAW_CSKILLS_README", os.path.join(WORKSPACE_ROOT, "C_Skills", "README.md"))
OUT = os.environ.get("PAW_MERGE_MANIFEST", os.path.join(REPO_ROOT, "skills", "_merge-manifest.csv"))

JUNK_RE = re.compile(r'\.bak|backup|\.tmp', re.I)
EXCLUDE = {
    ".system",
    "codex-windows-fast-patch",
    # Runtime/project wrappers are intentionally excluded from this portable repo.
    "audit",
    "fix",
    "implement",
    "review",
    "status",
    "sprint",
    "sync-docs",
    "migrate-to-codex",
    "hatch-pet",
    "floatly-design-implementation",
    "floatly-ui-style",
}

# 2026-06-26: codex 源里部分 anna-/coff0xc- 技能在正式库中已去前缀；
# manifest 需要保留上游 relpath，同时输出正式采用的 slug。
CODEX_FINAL_SLUG = {
    "coff0xc-ai-agent-rag": "ai-agent-rag",
    "anna-api-design": "api-design-2",
    "anna-backend-engineering": "backend-engineering",
    "coff0xc-api-data-platform": "api-data-platform",
    "coff0xc-office-doc-tools": "office-doc-tools",
    "coff0xc-research-drawio-diagram": "research-drawio-diagram",
    "anna-db-design": "db-design",
    "anna-perf-engineering": "perf-engineering",
    "anna-shell-scripting": "shell-scripting-2",
    "coff0xc-software-engineering": "software-engineering",
    "anna-ui-design": "ui-design",
    "coff0xc-ui-doc-output": "ui-doc-output",
    "anna-apple-development": "apple-development",
    "anna-flutter-development": "flutter-development",
    "anna-uniapp-dev": "uniapp-dev",
    "anna-product-manager": "product-manager",
    "anna-go-dev": "go-dev-2",
    "anna-js-ts-dev": "js-ts-dev-2",
    "anna-python-dev": "python-dev-2",
    "anna-code-audit": "code-audit-2",
    "anna-git-workflow": "git-workflow-2",
    "anna-test-engineering": "test-engineering",
    "anna-reverse-engineering": "reverse-engineering-2",
    "coff0xc-authorized-assessment": "authorized-assessment",
    "coff0xc-binary-mobile-iot": "binary-mobile-iot",
    "coff0xc-blockchain-security": "blockchain-security-2",
    "coff0xc-cloud-devsecops": "cloud-devsecops",
    "coff0xc-compliance-architecture": "compliance-architecture",
    "coff0xc-detection-response": "detection-response",
    "coff0xc-identity-zero-trust": "identity-zero-trust",
    "anna-mobile-security": "mobile-security-2",
    "coff0xc-network-protocol-security": "network-protocol-security",
    "coff0xc-purple-deception": "purple-deception",
    "coff0xc-secure-code-appsec": "secure-code-appsec",
    "coff0xc-vulnerability-lifecycle": "vulnerability-lifecycle",
    "coff0xc-skill-router": "skill-router",
}

def norm_key(slug):
    k = slug.lower()
    k = re.sub(r'-(dev|development|engineering)$', '', k)
    alias = {"js-ts": "javascript-typescript"}
    return alias.get(k, k)

def is_skill_dir(path):
    return os.path.isfile(os.path.join(path, "SKILL.md"))

# ---------- enumerate sources ----------
def list_ours():
    out = []  # (slug, src, domain_hint, multifile, relpath)
    for domain in sorted(os.listdir(OURS)):
        domainp = os.path.join(OURS, domain)
        if not os.path.isdir(domainp) or domain.startswith("_"):
            continue
        oursp = os.path.join(domainp, "ours")
        if not os.path.isdir(oursp):
            continue
        for slug in sorted(os.listdir(oursp)):
            sp = os.path.join(oursp, slug)
            if is_skill_dir(sp):
                nfiles = sum(1 for _, _, fs in os.walk(sp) for _ in fs)
                out.append((slug, "ours", domain, nfiles > 1, f"{domain}/ours/{slug}"))
    return out

def list_codex():
    out = []
    for slug in sorted(os.listdir(CODEX)):
        sp = os.path.join(CODEX, slug)
        if not os.path.isdir(sp) or JUNK_RE.search(slug) or slug in EXCLUDE:
            continue
        if not is_skill_dir(sp):
            # some like orchestration have SKILL.md nested deeper
            has = any(f == "SKILL.md" for _,_,fs in os.walk(sp) for f in fs)
            if not has:
                continue
        nfiles = sum(1 for _,_,fs in os.walk(sp) for _ in fs)
        out.append((slug, "codex", None, nfiles > 1, slug))
    return out

def parse_csk_categories():
    m = {}
    with open(CSK_README, encoding="utf-8") as f:
        for line in f:
            mt = re.match(r'^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|', line)
            if mt:
                m[mt.group(1)] = mt.group(2).strip()
    return m

def list_csk(cats):
    out = []
    for slug in sorted(os.listdir(CSK)):
        sp = os.path.join(CSK, slug)
        if is_skill_dir(sp):
            out.append((slug, "cskills", cats.get(slug), False, slug))
    return out

# ---------- domain classification ----------
# C_Skills 分类 → 统一大类
CSK_MAP = {
    "reverse-engineering":"reverse-engineering","programming-languages":"programming-languages",
    "payments-commerce":"payments-commerce","mobile-crossplatform":"mobile-crossplatform",
    "maps-location":"maps-location","quality-delivery":"quality-delivery","cloud-infra":"cloud-infra",
    "ai-automation":"ai-automation","frontend-ui":"frontend-ui","product-growth":"product-growth",
    "hardware-systems":"hardware-systems","backend-api":"backend-api","security-engineering":"security-engineering",
    "research-knowledge":"research-knowledge","data-analysis":"data-analysis","content-authoring":"content-authoring",
    "engineering":"engineering-core",
}
# codex 精确映射（最高优先，处理歧义 slug）
CODEX_EXACT = {
 "dev":"workflow-orchestration","spec":"workflow-orchestration","spec-check":"workflow-orchestration",
 "spec-do":"workflow-orchestration","orchestration":"workflow-orchestration",
 "memory":"workflow-orchestration","agent-briefing":"workflow-orchestration",
 "skill-creator":"workflow-orchestration","mcp-builder":"workflow-orchestration","deep-thinking":"workflow-orchestration",
 "coff0xc-skill-router":"workflow-orchestration",
 "commit":"quality-delivery","yeet":"quality-delivery","tools":"quality-delivery","cli-creator":"quality-delivery",
 "qa":"quality-delivery","testing":"quality-delivery","refactor":"quality-delivery","code-audit":"quality-delivery",
 "code-simplifier":"quality-delivery","code-migration":"quality-delivery","git-workflow":"quality-delivery",
 "gh-fix-ci":"quality-delivery","gh-address-comments":"quality-delivery","devex-tooling":"quality-delivery",
 "prompt-engineering":"ai-automation","ai-orchestrator":"ai-automation","ai-agent-dev":"ai-automation","mlops":"ai-automation",
 "domains":"engineering-core","linear":"product-growth","sentry":"product-growth",
 "i18n-l10n":"frontend-ui","cms-headless":"backend-api","graphics-rendering":"frontend-ui",
 "fingerprint-engine":"security-engineering","proxy-pool-manager":"security-engineering",
 "anna-db-design":"data-analysis","anna-perf-engineering":"engineering-core","system-design":"engineering-core",
 "web-fetch":"research-knowledge","context7":"research-knowledge","game-dev":"research-knowledge",
 "coff0xc-api-data-platform":"backend-api","coff0xc-authorized-assessment":"security-engineering",
 "coff0xc-binary-mobile-iot":"security-engineering","coff0xc-office-doc-tools":"content-authoring",
 "coff0xc-secure-code-appsec":"security-engineering","coff0xc-software-engineering":"engineering-core",
 "coff0xc-ai-agent-rag":"ai-automation","coff0xc-blockchain-security":"security-engineering",
 "coff0xc-cloud-devsecops":"security-engineering","coff0xc-compliance-architecture":"security-engineering",
 "coff0xc-detection-response":"security-engineering","coff0xc-identity-zero-trust":"security-engineering",
 "coff0xc-network-protocol-security":"security-engineering","coff0xc-purple-deception":"security-engineering",
 "coff0xc-research-drawio-diagram":"content-authoring","coff0xc-ui-doc-output":"frontend-ui",
 "coff0xc-vulnerability-lifecycle":"security-engineering",
}
# codex 关键词分类（顺序敏感，先匹配先得；裸 "dev" 已移除，语言由 programming 段精确捕获）
CODEX_RULES = [
 ("workflow-orchestration", ["orchestrat","skill-router","agent-briefing"]),
 ("reverse-engineering", ["revers","-reversing","dotnet-reversing","android-reversing","binary-exploit"]),
 ("security-engineering", ["pentest","redteam","red-team","threat","vuln","exploit","malware","forensic","incident","attack","credential","privilege","lateral","post-exploit","evasion","c2","phishing","osint","recon","honeypot","detection","soc","edr","siem","yara","sigma","wireless","ics-scada","iot-security","kernel-security","crypto-security","email-security","oauth-security","api-security","graphql-pentest","spa-pentest","web-pentest","cdn-bypass","data-exfil","backdoor","supply-chain","secrets-manage","security","zero-trust","identity-security","purple","compliance","privacy","quantum","bug-bounty","blockchain-security","ad-pentest","network-protocol","network-monitoring","ctf","mobile-security","browser-security","container-security","cloud-security","linux-hardening","windows-hardening","devsecops","iac-devops","data-security","vulnerability","full-pentest","pentest-report","red-team-poc","security-tool-dev","security-best","security-ownership","security-threat","serverless-security"]),
 ("payments-commerce", ["pay","stripe","paypal","adyen","square","checkout","wallet","alipay","wechat-pay","fintech"]),
 ("maps-location", ["map","gis","arcgis","leaflet","openstreetmap","openlayers","amap","gaode","tianditu"]),
 ("mobile-crossplatform", ["android","ios","apple","flutter","react-native","electron","harmonyos","uniapp","kotlin","swift","miniprogram","tauri"]),
 ("ai-automation", ["ai-agent","ai-orch","ai-engineer","rag","llm","prompt","agent","mcp","browser-automation","autojs","playwright","computer-use","speech","transcribe","ai-content","ai-image"]),
 ("frontend-ui", ["uidesign","ui-design","ui-doc","react","vue","svelte","angular","nextjs","next-dev","css","figma","accessibility","screenshot","frontend","preact","panel-ui","winui","chatgpt-apps"]),
 ("backend-api", ["api-design","api-discovery","graphql","grpc","backend","fastapi","django","nestjs","spring","laravel","rails","aspnet","microservice","event-driven","realtime","service-mesh","websocket","rate-limit"]),
 ("programming-languages", ["python-dev","go-dev","rust-dev","java-dev","js-ts","csharp","-cpp","c-cpp","php-dev","ruby-dev","dotnet-dev","scala","r-dev","lua","elixir","typescript-dev"]),
 ("cloud-infra", ["docker","k8s","kubernetes","cloud-native","terraform","iac","finops","deploy","vercel","netlify","cloudflare","render","platform-eng","sre","serverless","edge-comput","disaster","chaos","monitoring","observability","container-sec"]),
 ("data-analysis", ["data-eng","data-visual","database","sql","spreadsheet","data-secur"]),
 ("hardware-systems", ["embedded","firmware","fpga","driver","stm32","hardware","linux-driver","windows-driver","uefi","wasm"]),
 ("quality-delivery", ["test","qa","code-audit","git-workflow","git-","gh-","refactor","code-simplif","code-migration","verify","release","performance-test","devex","low-code","quality"]),
 ("content-authoring", ["doc-office","pdf","presentation","document","technical-writing","notion","speech","translate","jupyter","quick-translate","research-paper","academic"]),
 ("product-growth", ["product-manager","product-market","marketing","promo","social-media","linear","sentry","domains","sdk-integration"]),
 ("research-knowledge", ["research","context7","web-fetch","search-engine","web3","game-dev","graphics","game"]),
 ("engineering-core", ["api-versioning","idempotency","pagination","concurrency","dependency","error-handling","feature-flag","graceful","http-caching","memory-leak","monorepo","regex","string-encoding","structured-logging","datetime","environment-config","migration-zero","system-design","api-engineering","architecture","shell-scripting"]),
]
def classify_codex(slug):
    s = slug.lower()
    if s in CODEX_EXACT:
        return CODEX_EXACT[s], "exact"
    for dom, kws in CODEX_RULES:
        for kw in kws:
            if kw in s:
                return dom, ("kw:"+kw)
    return "UNCLASSIFIED", "?"

# ---------- build ----------
cats = parse_csk_categories()
rows = []
for slug, src, hint, mf, rel in list_ours():
    rows.append([src, slug, norm_key(slug), hint, "rule:ours-path", "yes" if mf else "no", rel])
for slug, src, hint, mf, rel in list_codex():
    dom, why = classify_codex(slug)
    rows.append([src, CODEX_FINAL_SLUG.get(slug, slug), norm_key(slug), dom, why, "yes" if mf else "no", rel])
for slug, src, hint, mf, rel in list_csk(cats):
    rows.append([src, slug, norm_key(slug), CSK_MAP.get(hint, hint or "UNCLASSIFIED"), "rule:csk-readme", "no", rel])

# dedup: ours>codex>cskills by norm_key
prio = {"ours":0, "codex":1, "cskills":2}
best = {}
for r in rows:
    k = r[2]
    if k not in best or prio[r[0]] < prio[best[k][0]]:
        best[k] = r
winners = set(id(v) for v in best.values())
for r in rows:
    r.append("WIN" if id(r) in winners else "dup")

# write CSV
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["source","slug","normalized_key","proposed_domain","domain_reason","multifile","relpath","winner"])
    for r in sorted(rows, key=lambda x:(x[3], x[0], x[1])):
        w.writerow(r)

# summary
from collections import Counter
win_rows = [r for r in rows if r[-1]=="WIN"]
print(f"total skills enumerated: {len(rows)}  (ours/codex/cskills = "
      f"{sum(1 for r in rows if r[0]=='ours')}/{sum(1 for r in rows if r[0]=='codex')}/{sum(1 for r in rows if r[0]=='cskills')})")
print(f"winners (deduped): {len(win_rows)}   dropped dups: {len(rows)-len(win_rows)}")
print("\n=== winners by domain ===")
for dom,c in sorted(Counter(r[3] for r in win_rows).items(), key=lambda x:-x[1]):
    print(f"  {dom:24} {c}")
unc = [r for r in win_rows if r[3]=="UNCLASSIFIED"]
print(f"\n=== UNCLASSIFIED winners ({len(unc)}) — need manual domain ===")
for r in unc:
    print(f"  {r[0]:7} {r[1]}")
print("\n=== cross-source dedup drops (same capability, lower-priority dropped) ===")
drops = [r for r in rows if r[-1]=="dup"]
for r in sorted(drops, key=lambda x:x[2]):
    print(f"  drop {r[0]:7} {r[1]:34} (key={r[2]})")
print(f"\nmanifest -> {OUT}")
