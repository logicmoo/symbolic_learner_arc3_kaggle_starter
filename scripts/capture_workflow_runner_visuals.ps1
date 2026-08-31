param(
    [string]$BaseUrl = "http://127.0.0.1:5173",
    [string]$Workspace = "shared",
    [string]$RunId = "",
    [string]$OutputDirectory = "workbench/docs/todo/assets/actual"
)

$ErrorActionPreference = "Stop"
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$outputRoot = Join-Path $repositoryRoot $OutputDirectory
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null

$browserCandidates = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)
$browser = $browserCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $browser) {
    throw "Chrome or Edge is required to capture workflow-runner visuals."
}

$temporaryProfile = Join-Path ([System.IO.Path]::GetTempPath()) "metta-workbench-visual-$PID"
New-Item -ItemType Directory -Path $temporaryProfile -Force | Out-Null
try {
    if (-not $RunId) {
        $runRegistry = Invoke-RestMethod "$BaseUrl/workbench/engine/runs?limit=1"
        $RunId = [string]$runRegistry.runs[0].id
    }
    if (-not $RunId) {
        throw "No durable workflow run exists. Run a workflow before capturing visual acceptance images."
    }
    $encodedWorkspace = [uri]::EscapeDataString($Workspace)
    $encodedRun = [uri]::EscapeDataString($RunId)
    $captures = @(
        @{ Name = "workflow-runs-topology.png"; Url = "$BaseUrl/?workspace=$encodedWorkspace&view=workflowRuns&run=$encodedRun" },
        @{ Name = "workflow-runs-chronology.png"; Url = "$BaseUrl/?workspace=$encodedWorkspace&view=workflowRuns&run=$encodedRun&runView=chronology" }
    )
    foreach ($capture in $captures) {
        $target = Join-Path $outputRoot $capture.Name
        & $browser --headless=new --disable-gpu --hide-scrollbars --window-size=1920,1080 `
            --force-device-scale-factor=1 --virtual-time-budget=10000 --run-all-compositor-stages-before-draw `
            --user-data-dir=$temporaryProfile --screenshot=$target $capture.Url | Out-Null
        if (-not (Test-Path -LiteralPath $target)) {
            throw "Browser did not create $target"
        }
        Write-Host "Captured $target"
    }
}
finally {
    $resolvedTemp = [System.IO.Path]::GetFullPath($temporaryProfile)
    $systemTemp = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
    if ($resolvedTemp.StartsWith($systemTemp, [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $resolvedTemp)) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
    }
}
