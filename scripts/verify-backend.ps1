[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$failures = [System.Collections.Generic.List[string]]::new()
$executed = [System.Collections.Generic.List[string]]::new()
$skipped = [System.Collections.Generic.List[string]]::new()

function Invoke-Check {
    param(
        [string]$Label,
        [string]$Command,
        [string[]]$Arguments
    )

    Write-Host "`n[$Label] $Command $($Arguments -join ' ')" -ForegroundColor Cyan
    & $Command @Arguments
    $exitCode = $LASTEXITCODE
    $script:executed.Add($Label)
    if ($exitCode -ne 0) {
        $script:failures.Add("$Label（退出码 $exitCode）")
    }
}

function Find-CommandOrNull {
    param([string[]]$Candidates)
    foreach ($candidate in $Candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($null -ne $command) { return $command.Source }
    }
    return $null
}

Push-Location $root
try {
    if (Test-Path -LiteralPath (Join-Path $root "pom.xml")) {
        $maven = if (Test-Path -LiteralPath (Join-Path $root "mvnw.cmd")) {
            Join-Path $root "mvnw.cmd"
        } elseif (Test-Path -LiteralPath (Join-Path $root "mvnw")) {
            Join-Path $root "mvnw"
        } else {
            Find-CommandOrNull @("mvn")
        }
        if (-not $maven) { $skipped.Add("Maven：未找到 wrapper 或 mvn") }
        else { Invoke-Check "Maven 验证" $maven @("verify") }
    } elseif ((Test-Path -LiteralPath (Join-Path $root "build.gradle")) -or (Test-Path -LiteralPath (Join-Path $root "build.gradle.kts"))) {
        $gradle = if (Test-Path -LiteralPath (Join-Path $root "gradlew.bat")) {
            Join-Path $root "gradlew.bat"
        } elseif (Test-Path -LiteralPath (Join-Path $root "gradlew")) {
            Join-Path $root "gradlew"
        } else {
            Find-CommandOrNull @("gradle")
        }
        if (-not $gradle) { $skipped.Add("Gradle：未找到 wrapper 或 gradle") }
        else { Invoke-Check "Gradle 构建与测试" $gradle @("build") }
    } elseif ((Test-Path -LiteralPath (Join-Path $root "pyproject.toml")) -or (Test-Path -LiteralPath (Join-Path $root "requirements.txt")) -or (Test-Path -LiteralPath (Join-Path $root "setup.py"))) {
        $python = Find-CommandOrNull @("python", "python3")
        if (-not $python) {
            $skipped.Add("Python：未找到 python 命令")
        } else {
            $pyprojectPath = Join-Path $root "pyproject.toml"
            $pyproject = if (Test-Path -LiteralPath $pyprojectPath) { Get-Content -Raw -LiteralPath $pyprojectPath } else { "" }
            if ($pyproject -match "(?m)^\[tool\.ruff" -or (Test-Path -LiteralPath (Join-Path $root "ruff.toml"))) {
                Invoke-Check "Ruff 静态检查" $python @("-m", "ruff", "check", ".")
            } else {
                $skipped.Add("Ruff：项目未声明配置")
            }
            if ($pyproject -match "(?m)^\[tool\.mypy" -or (Test-Path -LiteralPath (Join-Path $root "mypy.ini"))) {
                Invoke-Check "Mypy 类型检查" $python @("-m", "mypy", ".")
            } else {
                $skipped.Add("Mypy：项目未声明配置")
            }
            if ((Test-Path -LiteralPath (Join-Path $root "tests")) -or $pyproject -match "(?m)^\[tool\.pytest") {
                Invoke-Check "Pytest 测试" $python @("-m", "pytest")
            } else {
                $skipped.Add("Pytest：未发现 tests 或 pytest 配置")
            }
        }
    } elseif (Test-Path -LiteralPath (Join-Path $root "go.mod")) {
        $go = Find-CommandOrNull @("go")
        if (-not $go) { $skipped.Add("Go：未找到 go 命令") }
        else {
            Invoke-Check "Go Vet" $go @("vet", "./...")
            Invoke-Check "Go 测试" $go @("test", "./...")
            Invoke-Check "Go 构建" $go @("build", "./...")
        }
    } elseif (Test-Path -LiteralPath (Join-Path $root "Cargo.toml")) {
        $cargo = Find-CommandOrNull @("cargo")
        if (-not $cargo) { $skipped.Add("Rust：未找到 cargo 命令") }
        else {
            Invoke-Check "Rust 格式检查" $cargo @("fmt", "--", "--check")
            Invoke-Check "Rust Clippy" $cargo @("clippy", "--", "-D", "warnings")
            Invoke-Check "Rust 测试" $cargo @("test")
            Invoke-Check "Rust 构建" $cargo @("build")
        }
    } else {
        $solution = Get-ChildItem -LiteralPath $root -File -Filter "*.sln" | Select-Object -First 1
        $project = Get-ChildItem -LiteralPath $root -File -Filter "*.csproj" | Select-Object -First 1
        if ($solution -or $project) {
            $dotnet = Find-CommandOrNull @("dotnet")
            if (-not $dotnet) { $skipped.Add(".NET：未找到 dotnet 命令") }
            else {
                $target = if ($solution) { $solution.FullName } else { $project.FullName }
                Invoke-Check ".NET 格式检查" $dotnet @("format", $target, "--verify-no-changes")
                Invoke-Check ".NET 测试" $dotnet @("test", $target, "--no-restore")
                Invoke-Check ".NET 构建" $dotnet @("build", $target, "--no-restore")
            }
        } elseif (Test-Path -LiteralPath (Join-Path $root "package.json")) {
            $frontendVerifier = Join-Path $PSScriptRoot "verify-frontend.ps1"
            & $frontendVerifier -ProjectRoot $root
            $nodeExit = $LASTEXITCODE
            $executed.Add("Node.js 项目脚本验证")
            if ($nodeExit -ne 0) { $failures.Add("Node.js 项目脚本验证（退出码 $nodeExit）") }
        } else {
            $skipped.Add("未识别构建系统；请使用项目文档中的验证命令")
        }
    }
} finally {
    Pop-Location
}

Write-Host "`n验证摘要" -ForegroundColor Cyan
$executed | ForEach-Object { Write-Host "[已执行] $_" }
$skipped | ForEach-Object { Write-Host "[未运行] $_" -ForegroundColor Yellow }
$failures | ForEach-Object { Write-Host "[失败] $_" -ForegroundColor Red }

if ($failures.Count -gt 0) { exit 1 }
if ($executed.Count -eq 0) { exit 2 }
exit 0
