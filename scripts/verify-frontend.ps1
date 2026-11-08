[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [string]$PackageJson,

    [switch]$AllowMutatingChecks
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-PackageJson {
    param([string]$Root, [string]$ExplicitPath)

    if ($ExplicitPath) {
        return (Resolve-Path -LiteralPath $ExplicitPath).Path
    }

    $rootPackage = Join-Path $Root "package.json"
    if (Test-Path -LiteralPath $rootPackage) {
        return (Resolve-Path -LiteralPath $rootPackage).Path
    }

    $candidates = @(
        Get-ChildItem -LiteralPath $Root -Filter "package.json" -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch "[\\/](node_modules|dist|build|coverage)[\\/]" }
    )

    if ($candidates.Count -eq 0) {
        throw "未找到 package.json。请将 -ProjectRoot 指向前端根目录，或使用 -PackageJson 指定文件。"
    }
    if ($candidates.Count -gt 1) {
        $paths = ($candidates.FullName | ForEach-Object { "- $_" }) -join "`n"
        throw "找到多个 package.json，请使用 -PackageJson 明确指定：`n$paths"
    }

    return $candidates[0].FullName
}

function Get-ScriptValue {
    param([object]$Scripts, [string]$Name)
    $property = $Scripts.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return [string]$property.Value
}

function Select-Script {
    param([object]$Scripts, [string[]]$Candidates)
    foreach ($candidate in $Candidates) {
        if ($null -ne $Scripts.PSObject.Properties[$candidate]) {
            return $candidate
        }
    }
    return $null
}

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$packagePath = Resolve-PackageJson -Root $root -ExplicitPath $PackageJson
$packageRoot = Split-Path -Parent $packagePath
$package = Get-Content -Raw -LiteralPath $packagePath | ConvertFrom-Json

if ($null -eq $package.scripts) {
    Write-Warning "package.json 没有 scripts，无法自动验证。"
    exit 2
}

$manager = "npm"
if (Test-Path -LiteralPath (Join-Path $packageRoot "pnpm-lock.yaml")) {
    $manager = "pnpm"
} elseif ((Test-Path -LiteralPath (Join-Path $packageRoot "yarn.lock"))) {
    $manager = "yarn"
} elseif ((Test-Path -LiteralPath (Join-Path $packageRoot "bun.lock")) -or (Test-Path -LiteralPath (Join-Path $packageRoot "bun.lockb"))) {
    $manager = "bun"
}

if ($null -eq (Get-Command $manager -ErrorAction SilentlyContinue)) {
    Write-Error "项目使用 $manager，但当前环境未找到该命令。脚本不会自动安装工具。"
    exit 2
}

$groups = @(
    [PSCustomObject]@{ Label = "格式检查"; Candidates = @("format:check", "format-check", "check:format", "prettier:check") },
    [PSCustomObject]@{ Label = "Lint"; Candidates = @("lint") },
    [PSCustomObject]@{ Label = "类型检查"; Candidates = @("typecheck", "type-check", "check:types", "types:check") },
    [PSCustomObject]@{ Label = "测试"; Candidates = @("test:run", "test:unit", "test") },
    [PSCustomObject]@{ Label = "构建"; Candidates = @("build") }
)

$failures = [System.Collections.Generic.List[string]]::new()
$executed = [System.Collections.Generic.List[string]]::new()
$skipped = [System.Collections.Generic.List[string]]::new()
$previousCi = $env:CI
$env:CI = "true"

Push-Location $packageRoot
try {
    foreach ($group in $groups) {
        $scriptName = Select-Script -Scripts $package.scripts -Candidates $group.Candidates
        if (-not $scriptName) {
            $skipped.Add("$($group.Label)：未定义可识别脚本")
            continue
        }

        $scriptValue = Get-ScriptValue -Scripts $package.scripts -Name $scriptName
        if (-not $AllowMutatingChecks -and $scriptValue -match "(^|\s)--fix(\s|$)") {
            $skipped.Add("$($group.Label)：$scriptName 包含 --fix；使用 -AllowMutatingChecks 才会执行")
            continue
        }

        Write-Host "`n[$($group.Label)] $manager run $scriptName" -ForegroundColor Cyan
        & $manager "run" $scriptName
        $exitCode = $LASTEXITCODE
        $executed.Add("$($group.Label)：$scriptName")
        if ($exitCode -ne 0) {
            $failures.Add("$($group.Label)：$scriptName（退出码 $exitCode）")
        }
    }
} finally {
    Pop-Location
    $env:CI = $previousCi
}

Write-Host "`n验证摘要" -ForegroundColor Cyan
$executed | ForEach-Object { Write-Host "[已执行] $_" }
$skipped | ForEach-Object { Write-Host "[未运行] $_" -ForegroundColor Yellow }
$failures | ForEach-Object { Write-Host "[失败] $_" -ForegroundColor Red }

if ($failures.Count -gt 0) { exit 1 }
if ($executed.Count -eq 0) { exit 2 }
exit 0
