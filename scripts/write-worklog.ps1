[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [string]$Operation,

    [Parameter(Mandatory = $true)]
    [string]$Target,

    [Parameter(Mandatory = $true)]
    [string]$Reason,

    [Parameter(Mandatory = $true)]
    [string]$Result,

    [string]$Recovery = "回退本次对应差异；若存在外部状态变化，按项目恢复流程处理。",

    [string]$LogRelativePath = ".ai/operations.md"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $ProjectRoot).Path
$logFull = [System.IO.Path]::GetFullPath((Join-Path $root $LogRelativePath))

if (-not $logFull.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "日志路径逃出项目根目录：$logFull"
}

$dir = Split-Path -Parent $logFull
if (-not (Test-Path -LiteralPath $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

$nl = [Environment]::NewLine
$stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")

$entry = $nl + $nl + "## $stamp" + $nl + $nl +
    "- 操作：$Operation" + $nl +
    "- 目标：$Target" + $nl +
    "- 原因：$Reason" + $nl +
    "- 结果：$Result" + $nl +
    "- 恢复方式：$Recovery" + $nl

$enc = New-Object System.Text.UTF8Encoding($false)

if (-not (Test-Path -LiteralPath $logFull)) {
    $head = "# 操作日志" + $nl + $nl +
        "> 时间格式：``yyyy-MM-dd HH:mm:ss +08:00``" + $nl +
        "> 不记录令牌、密码、个人数据、完整环境变量。" + $nl
    [System.IO.File]::WriteAllText($logFull, $head, $enc)
}

[System.IO.File]::AppendAllText($logFull, $entry, $enc)

Write-Host "[+] 已追加到 $LogRelativePath" -ForegroundColor Green
Write-Host "    $stamp $Operation"
