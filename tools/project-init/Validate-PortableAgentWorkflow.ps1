param(
    [string]$RepoRoot,
    [switch]$SkipSmoke
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
}

$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure($Message) {
    $script:failures.Add($Message) | Out-Null
}

function Assert-FileContains($Path, [string[]]$Patterns) {
    if (-not (Test-Path -LiteralPath $Path)) {
        Add-Failure "missing file: $Path"
        return
    }
    $text = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    foreach ($pattern in $Patterns) {
        if ($text -notmatch [regex]::Escape($pattern)) {
            Add-Failure "missing pattern '$pattern' in $Path"
        }
    }
}

function Assert-NoRegex($Path, $Pattern, $Description) {
    if (-not (Test-Path -LiteralPath $Path)) {
        Add-Failure "missing file: $Path"
        return
    }
    $matches = Select-String -LiteralPath $Path -Pattern $Pattern -Encoding UTF8
    foreach ($match in $matches) {
        Add-Failure "$Description in ${Path}:$($match.LineNumber): $($match.Line.Trim())"
    }
}

$startup = Join-Path $RepoRoot "skills\workflow-orchestration\ours\project-inception-docs\assets\templates\startup-docs"
$core = Join-Path $RepoRoot "framework\core"
$tool = Join-Path $RepoRoot "tools\project-init\Initialize-PortableAgentProject.ps1"

Assert-FileContains (Join-Path $startup "AGENTS.md") @(
    "<!-- BEGIN PORTABLE AGENT WORKFLOW -->",
    "<!-- END PORTABLE AGENT WORKFLOW -->",
    "State Restore",
    "Loop Record"
)
Assert-FileContains (Join-Path $startup "CLAUDE.md") @(
    "<!-- BEGIN PORTABLE AGENT WORKFLOW -->",
    "<!-- END PORTABLE AGENT WORKFLOW -->",
    "State Restore",
    "Loop Record"
)
Assert-FileContains (Join-Path $core "02-state-systems.md") @("State Restore Gate", "Loop Record")
Assert-FileContains (Join-Path $core "08-autonomous-project-loop.md") @("Active Goal", "Loop Record")
Assert-FileContains $tool @("AgentEntriesOnly", "RefreshAgentEntries", "EnsureIndexes")

$stateTemplates = @("LOG.md", "MEMORY.md", "PROGRESS.md", "REQUIREMENTS.md")
foreach ($name in $stateTemplates) {
    $path = Join-Path (Join-Path $startup "state") $name
    Assert-NoRegex $path "<[^>]+>" "state template placeholder residue"
}

if (-not $SkipSmoke) {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("paw-validate-" + [Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmp | Out-Null
    try {
        Set-Content -LiteralPath (Join-Path $tmp "AGENTS.md") -Encoding UTF8 -Value "# AGENTS.md`r`n`r`n## Project Specific`r`n`r`n- keep me`r`n"
        & $tool -ProjectPath $tmp -AgentEntriesOnly | Out-Null

        $agentText = Get-Content -LiteralPath (Join-Path $tmp "AGENTS.md") -Raw -Encoding UTF8
        if ($agentText -notmatch "BEGIN PORTABLE AGENT WORKFLOW") { Add-Failure "smoke: managed block was not inserted" }
        if ($agentText -notmatch "Loop Record") { Add-Failure "smoke: Loop Record missing from refreshed AGENTS.md" }
        if ($agentText -notmatch "keep me") { Add-Failure "smoke: project-specific section was not preserved" }
        if (Test-Path -LiteralPath (Join-Path $tmp ".git")) { Add-Failure "smoke: AgentEntriesOnly unexpectedly initialized Git" }
        if (Test-Path -LiteralPath (Join-Path $tmp ".gitignore")) { Add-Failure "smoke: AgentEntriesOnly unexpectedly copied .gitignore" }
    }
    finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

if ($failures.Count -gt 0) {
    Write-Host "Portable Agent Workflow validation failed:" -ForegroundColor Red
    foreach ($failure in $failures) {
        Write-Host " - $failure" -ForegroundColor Red
    }
    exit 1
}

Write-Host "Portable Agent Workflow validation passed." -ForegroundColor Green
