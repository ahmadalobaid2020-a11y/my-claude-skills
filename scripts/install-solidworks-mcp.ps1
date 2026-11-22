<#
.SYNOPSIS
  Installs two SOLIDWORKS MCP servers on Windows and registers them with Claude Code (user scope).

.DESCRIPTION
  solidworks     soheil-mp/solidworks-mcp           C# / .NET 10, 161 tools (sw_*, doc_*, sketch_*, feature_*, ...)
  solidworks-py  HarrierPigeon/Solidworks-MCP-Server Python, tools prefixed solidworks_*

  Both upstream installers register themselves as "solidworks"; here the Python server gets the name
  "solidworks-py" so the two can sit side by side. They drive the same running SOLIDWORKS, so let an
  agent use one of them at a time.

  Needs Windows, SOLIDWORKS and git. The C# server also needs the .NET 10 SDK (installed with winget
  when missing); uv is installed for the Python server when missing. Re-running updates both.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\install-solidworks-mcp.ps1
  powershell -ExecutionPolicy Bypass -File scripts\install-solidworks-mcp.ps1 -Only DotNet
  powershell -ExecutionPolicy Bypass -File scripts\install-solidworks-mcp.ps1 -Desktop
#>
param(
    [ValidateSet('Both', 'DotNet', 'Python')]
    [string]$Only = 'Both',
    # Also add both servers to Claude Desktop's claude_desktop_config.json (a backup is written first).
    [switch]$Desktop
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'SOLIDWORKS only runs on Windows; run this script there.' }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git is required: https://git-scm.com/downloads/win' }

$servers = [ordered]@{}   # name -> command array, for the Claude Desktop config
$failed = @()

function Sync-Repo($url, $dir) {
    if (Test-Path (Join-Path $dir '.git')) {
        & git -C $dir pull -q --ff-only
    } else {
        New-Item -ItemType Directory -Force (Split-Path -Parent $dir) | Out-Null
        & git clone -q --depth 1 $url $dir
    }
    if ($LASTEXITCODE -ne 0) { throw "git could not fetch $url" }
}

function Register-ClaudeCode($name, $command) {
    if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
        Write-Warning "Claude Code CLI not found; register manually: claude mcp add --scope user $name -- $($command -join ' ')"
        return
    }
    # Windows PowerShell turns redirected stderr into errors; a missing registration is fine here.
    $ErrorActionPreference = 'Continue'
    & claude mcp remove $name -s user *> $null
    $ErrorActionPreference = 'Stop'
    & claude mcp add --scope user $name -- @command
    if ($LASTEXITCODE -ne 0) { throw "claude mcp add failed for '$name'." }
    Write-Host "Registered '$name' with Claude Code (user scope)."
}

# --- solidworks: soheil-mp/solidworks-mcp (C#) -------------------------------------------------
if ($Only -in 'Both', 'DotNet') {
    try {
        Write-Host '==> solidworks (soheil-mp/solidworks-mcp)' -ForegroundColor Cyan
        $hasSdk = (Get-Command dotnet -ErrorAction SilentlyContinue) -and (((& dotnet --list-sdks) -join "`n") -match '(?m)^10\.')
        if (-not $hasSdk) {
            Write-Host 'Installing the .NET 10 SDK with winget...'
            & winget install --id Microsoft.DotNet.SDK.10 -e --silent --accept-source-agreements --accept-package-agreements
            $env:Path = "$env:ProgramFiles\dotnet;$env:Path"
            if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
                throw 'The .NET 10 SDK is required: https://dotnet.microsoft.com/download'
            }
        }
        $src = Join-Path $env:LOCALAPPDATA 'solidworks-mcp\src'
        Sync-Repo 'https://github.com/soheil-mp/solidworks-mcp.git' $src
        # Upstream installer: publishes to %LOCALAPPDATA%\solidworks-mcp\bin\<version>-<timestamp> and
        # registers it; it falls back to the dotnet host when Smart App Control blocks the unsigned exe.
        & powershell -ExecutionPolicy Bypass -File (Join-Path $src 'tools\install.ps1') -Name solidworks
        if ($LASTEXITCODE -ne 0) { throw 'tools\install.ps1 failed.' }

        $bin = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'solidworks-mcp\bin') -Directory |
            Sort-Object LastWriteTime | Select-Object -Last 1
        $servers['solidworks'] = @((Join-Path $bin.FullName 'solidworks-mcp.exe'))

        # The skill that teaches the agent how to use this server's tools.
        $skill = Join-Path $env:USERPROFILE '.claude\skills\solidworks-mcp'
        if (Test-Path $skill) { Remove-Item $skill -Recurse -Force }
        New-Item -ItemType Directory -Force (Split-Path -Parent $skill) | Out-Null
        Copy-Item (Join-Path $src 'skills\solidworks-mcp') $skill -Recurse
        Write-Host "Installed the solidworks-mcp skill to $skill"
    } catch {
        Write-Warning "solidworks: $($_.Exception.Message)"
        $failed += 'solidworks'
    }
}

# --- solidworks-py: HarrierPigeon/Solidworks-MCP-Server (Python) -------------------------------
if ($Only -in 'Both', 'Python') {
    try {
        Write-Host '==> solidworks-py (HarrierPigeon/Solidworks-MCP-Server)' -ForegroundColor Cyan
        $uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
        if (-not $uv) {
            Write-Host 'Installing uv with winget...'
            & winget install --id=astral-sh.uv -e --silent --accept-source-agreements --accept-package-agreements
            foreach ($c in (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links\uv.exe'), (Join-Path $env:USERPROFILE '.local\bin\uv.exe')) {
                if (-not $uv -and (Test-Path $c)) { $uv = $c }
            }
            if (-not $uv) { throw 'uv is required: https://docs.astral.sh/uv/' }
        }
        $root = Join-Path $env:LOCALAPPDATA 'SolidWorksMCP'
        $app = Join-Path $root 'app'
        $venv = Join-Path $root 'venv'
        # An install made by the upstream script is a plain folder, not a clone: move it aside once.
        if ((Test-Path $app) -and -not (Test-Path (Join-Path $app '.git'))) {
            Move-Item $app "$app.old-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        }
        Sync-Repo 'https://github.com/HarrierPigeon/Solidworks-MCP-Server.git' $app
        if (Test-Path $venv) { Remove-Item $venv -Recurse -Force }
        & $uv venv $venv --python 3.12
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
        $python = Join-Path $venv 'Scripts\python.exe'
        & $uv pip install --python $python -r (Join-Path $app 'requirements.txt')
        if ($LASTEXITCODE -ne 0) { throw 'Could not install the Python dependencies.' }
        & $python -c 'import win32com.client, mcp, PIL'
        if ($LASTEXITCODE -ne 0) { throw 'pywin32, mcp or Pillow did not import.' }

        $command = @($python, (Join-Path $app 'server.py'))
        Register-ClaudeCode 'solidworks-py' $command
        $servers['solidworks-py'] = $command
    } catch {
        Write-Warning "solidworks-py: $($_.Exception.Message)"
        $failed += 'solidworks-py'
    }
}

# --- Claude Desktop (optional) -----------------------------------------------------------------
if ($Desktop -and $servers.Count) {
    $cfgDir = Join-Path $env:APPDATA 'Claude'
    $store = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'Packages') -Directory -Filter 'Claude*' -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not (Test-Path $cfgDir) -and $store) { $cfgDir = Join-Path $store.FullName 'LocalCache\Roaming\Claude' }
    New-Item -ItemType Directory -Force $cfgDir | Out-Null
    $cfgPath = Join-Path $cfgDir 'claude_desktop_config.json'
    $config = $null
    if (Test-Path $cfgPath) {
        Copy-Item $cfgPath "$cfgPath.backup" -Force
        $raw = Get-Content $cfgPath -Raw
        if ($raw -and $raw.Trim()) { $config = $raw | ConvertFrom-Json }
    }
    if (-not $config) { $config = [pscustomobject]@{} }
    if (-not $config.PSObject.Properties['mcpServers'] -or -not $config.mcpServers) {
        $config | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{}) -Force
    }
    foreach ($name in $servers.Keys) {
        $command = $servers[$name]
        $entry = [ordered]@{ command = $command[0] }
        if ($command.Count -gt 1) { $entry.args = @($command | Select-Object -Skip 1) }
        $config.mcpServers | Add-Member -NotePropertyName $name -NotePropertyValue ([pscustomobject]$entry) -Force
    }
    # UTF-8 without a BOM: Windows PowerShell's -Encoding utf8 writes one, which some JSON parsers reject.
    [IO.File]::WriteAllText($cfgPath, ($config | ConvertTo-Json -Depth 20), (New-Object System.Text.UTF8Encoding $false))
    Write-Host "Updated $cfgPath (restart Claude Desktop completely)."
}

Write-Host ''
if ($failed.Count) { Write-Warning "Not installed: $($failed -join ', ')"; exit 1 }
Write-Host "Done: $($servers.Keys -join ', '). Start SOLIDWORKS, restart Claude Code, then ask: 'Check the SOLIDWORKS status'."
