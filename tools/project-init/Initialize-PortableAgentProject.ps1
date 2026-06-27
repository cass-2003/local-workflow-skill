param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath,

    [string]$ProjectName,

    [string]$Idea = "",

    [string]$RepoRoot,

    [switch]$Force,

    [switch]$RefreshAgentEntries,

    [switch]$EnsureIndexes,

    [switch]$AgentEntriesOnly,

    [switch]$NoGit,

    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
}

$TemplateRoot = Join-Path $RepoRoot "skills\workflow-orchestration\ours\project-inception-docs\assets\templates\startup-docs"

function Write-Step($Message) {
    Write-Host "[portable-agent-init] $Message"
}

function Ensure-Directory($Path) {
    if (Test-Path -LiteralPath $Path) { return }
    Write-Step "create directory: $Path"
    if (-not $WhatIf) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
}

function Copy-IfMissing($Source, $Destination) {
    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        Write-Step "keep existing: $Destination"
        return
    }
    Ensure-Directory (Split-Path -Parent $Destination)
    $verb = if (Test-Path -LiteralPath $Destination) { "overwrite" } else { "copy" }
    Write-Step "$verb`: $Destination"
    if (-not $WhatIf) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
    }
}

function Copy-ManagedAgentEntry($Source, $Destination) {
    Ensure-Directory (Split-Path -Parent $Destination)
    Write-Step "refresh managed workflow block: $Destination"
    if ($WhatIf) { return }

    $sourceText = Get-Content -LiteralPath $Source -Raw -Encoding UTF8
    if (-not (Test-Path -LiteralPath $Destination)) {
        Set-Content -LiteralPath $Destination -Encoding UTF8 -Value $sourceText
        return
    }

    $destText = Get-Content -LiteralPath $Destination -Raw -Encoding UTF8
    $begin = "<!-- BEGIN PORTABLE AGENT WORKFLOW -->"
    $end = "<!-- END PORTABLE AGENT WORKFLOW -->"
    $sourceMatch = [regex]::Match($sourceText, "(?s)$([regex]::Escape($begin)).*?$([regex]::Escape($end))")
    if (-not $sourceMatch.Success) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        return
    }

    $destPattern = "(?s)$([regex]::Escape($begin)).*?$([regex]::Escape($end))"
    if ([regex]::IsMatch($destText, $destPattern)) {
        $newText = [regex]::Replace(
            $destText,
            $destPattern,
            [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $sourceMatch.Value },
            1
        )
    }
    else {
        $lines = $destText -split "`r?`n", 2
        if ($lines.Count -eq 2 -and $lines[0] -match '^#\s+') {
            $newText = $lines[0].TrimEnd() + "`r`n`r`n" + $sourceMatch.Value.Trim() + "`r`n`r`n" + $lines[1].TrimStart()
        }
        else {
            $newText = $sourceMatch.Value.Trim() + "`r`n`r`n" + $destText.TrimStart()
        }
    }

    # Remove older generic workflow blocks that predate managed markers, while
    # preserving project-specific sections that follow them.
    $legacyPattern = "(?s)(<!-- END PORTABLE AGENT WORKFLOW -->\s*)\r?\n## Project Workflow\r?\n.*?\r?\n## State System\r?\n.*?\r?\n## Documentation Entry\r?\n(?:\r?\n- [^\r\n]*){1,8}\r?\n"
    $newText = [regex]::Replace($newText, $legacyPattern, '$1' + "`r`n", 1)
    Set-Content -LiteralPath $Destination -Encoding UTF8 -Value $newText
}

function Write-IfMissing($Destination, $Content) {
    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        Write-Step "keep existing: $Destination"
        return
    }
    Ensure-Directory (Split-Path -Parent $Destination)
    $verb = if (Test-Path -LiteralPath $Destination) { "overwrite" } else { "write" }
    Write-Step "$verb`: $Destination"
    if (-not $WhatIf) {
        Set-Content -LiteralPath $Destination -Encoding UTF8 -Value $Content
    }
}

function Test-InsideGitWorktree($Path) {
    $original = Get-Location
    try {
        Set-Location -LiteralPath $Path
        $oldPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        git rev-parse --is-inside-work-tree 2>$null | Out-Null
        $ErrorActionPreference = $oldPreference
        return ($LASTEXITCODE -eq 0)
    }
    finally {
        $ErrorActionPreference = "Stop"
        Set-Location $original
    }
}

Ensure-Directory $ProjectPath
$ProjectPath = (Resolve-Path -LiteralPath $ProjectPath).Path

if (-not $ProjectName) {
    $ProjectName = Split-Path -Leaf $ProjectPath
    if (-not $ProjectName) { $ProjectName = "New Project" }
}

if (-not (Test-Path -LiteralPath $TemplateRoot)) {
    throw "Template root not found: $TemplateRoot"
}

Write-Step "project: $ProjectPath"
Write-Step "name: $ProjectName"
Write-Step "template: $TemplateRoot"

if ((-not $NoGit) -and (-not $AgentEntriesOnly) -and (-not $WhatIf)) {
    $gitDir = Join-Path $ProjectPath ".git"
    $insideGit = Test-InsideGitWorktree $ProjectPath
    if (-not (Test-Path -LiteralPath $gitDir) -and -not $insideGit) {
        Write-Step "git init"
        git -C $ProjectPath init | Out-Null
    }
    else {
        Write-Step "git already available; skip init"
    }
}
elseif ($WhatIf -and -not $NoGit -and -not $AgentEntriesOnly) {
    Write-Step "would inspect Git and initialize when needed"
}

$topLevelFiles = if ($AgentEntriesOnly) { @("AGENTS.md", "CLAUDE.md") } else { @(".gitignore", "AGENTS.md", "CLAUDE.md") }
foreach ($name in $topLevelFiles) {
    $src = Join-Path $TemplateRoot $name
    $dst = Join-Path $ProjectPath $name
    if (($RefreshAgentEntries -or $AgentEntriesOnly) -and ($name -in @("AGENTS.md", "CLAUDE.md"))) {
        Copy-ManagedAgentEntry $src $dst
    }
    else {
        Copy-IfMissing $src $dst
    }
}

if ($AgentEntriesOnly) {
    Write-Step "agent entries refreshed only; skip README/docs/state"
    Write-Step "done"
    return
}

$readmePath = Join-Path $ProjectPath "README.md"
if ((Test-Path -LiteralPath $readmePath) -and -not $Force) {
    Write-Step "keep existing: $readmePath"
}
else {
    $readme = Get-Content -LiteralPath (Join-Path $TemplateRoot "README.md") -Raw -Encoding UTF8
    $readme = $readme.Replace("<项目名称>", $ProjectName)
    if ($Idea) {
        $readme = $readme.Replace("<这个项目为谁解决什么问题，第一版交付什么结果。>", $Idea)
    }
    Write-IfMissing $readmePath $readme
}

foreach ($dir in @("docs", "state")) {
    $srcDir = Join-Path $TemplateRoot $dir
    if (Test-Path -LiteralPath $srcDir) {
        Get-ChildItem -LiteralPath $srcDir -Recurse -File | ForEach-Object {
            $rel = $_.FullName.Substring($srcDir.Length).TrimStart("\", "/")
            $dst = Join-Path (Join-Path $ProjectPath $dir) $rel
            if ($EnsureIndexes -and ($rel -in @("INDEX.md", "audit\INDEX.md", "audit\TEMPLATE-GLOBAL-AUDIT.md", "planning\下一步工作包.md"))) {
                Copy-IfMissing $_.FullName $dst
                return
            }
            Copy-IfMissing $_.FullName $dst
        }
    }
}

$logPath = Join-Path $ProjectPath "state\LOG.md"
if ((Test-Path -LiteralPath $logPath) -and -not $RefreshAgentEntries -and -not $EnsureIndexes) {
    $entry = @"

## $(Get-Date -Format "yyyy-MM-dd")

- `init` 初始化 Portable Agent Workflow 项目地基。
  - 项目：$ProjectName
  - 想法：$(if ($Idea) { $Idea } else { "待确认" })
  - 地基：Git / .gitignore / AGENTS.md / CLAUDE.md / docs / state
"@
    Write-Step "append init log: $logPath"
    if (-not $WhatIf) {
        Add-Content -LiteralPath $logPath -Encoding UTF8 -Value $entry
    }
}

Write-Step "done"
Write-Step "next: review README.md, docs/INDEX.md, and state/*.md; then run validation and create the first atomic commit when ready."
