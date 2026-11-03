[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Stop-MedVisionStartup {
    param([Parameter(Mandatory = $true)][string]$Message)

    Write-Error "MedVision startup failed: $Message"
    exit 1
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDirectory = Join-Path $projectRoot "AI_model"
$entryPoint = Join-Path $appDirectory "app.py"
$virtualEnvironment = Join-Path $appDirectory ".venv"
$pythonExecutable = Join-Path $virtualEnvironment "Scripts\python.exe"
$activateScript = Join-Path $virtualEnvironment "Scripts\Activate.ps1"
$hermesExecutable = Join-Path $projectRoot ".hermes-runtime\Scripts\hermes.exe"

$requiredFiles = @(
    @{ Path = $entryPoint; Label = "Streamlit entry point" },
    @{ Path = $pythonExecutable; Label = "Python virtual environment executable" },
    @{ Path = $activateScript; Label = "PowerShell virtual environment activation script" },
    @{ Path = (Join-Path $appDirectory "requirements.txt"); Label = "Python requirements file" },
    @{ Path = (Join-Path $appDirectory "model.pth"); Label = "Model checkpoint V1" },
    @{ Path = (Join-Path $appDirectory "models\model_v2_cbam.pth"); Label = "Model checkpoint V2" },
    @{ Path = (Join-Path $appDirectory "models\model_v3_transfer.pth"); Label = "Model checkpoint V3" },
    @{ Path = (Join-Path $appDirectory "models\model_v4_e0_control.pth"); Label = "Model checkpoint V4 E0" },
    @{ Path = (Join-Path $appDirectory "models\model_v4_e1_sqrt_weight.pth"); Label = "Model checkpoint V4 E1" },
    @{ Path = (Join-Path $appDirectory "models\model_v4_e2_beta099.pth"); Label = "Model checkpoint V4 E2" },
    @{ Path = (Join-Path $appDirectory "models\thresholds_v4.json"); Label = "V4 validation thresholds" },
    @{ Path = $hermesExecutable; Label = "Hermes executable" }
)

foreach ($requiredFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile.Path -PathType Leaf)) {
        Stop-MedVisionStartup "$($requiredFile.Label) was not found: $($requiredFile.Path)"
    }
}

try {
    . $activateScript
}
catch {
    Stop-MedVisionStartup "Could not activate virtual environment '$virtualEnvironment'. $($_.Exception.Message)"
}

$resolvedPython = (Resolve-Path -LiteralPath $pythonExecutable).Path
if (-not $env:VIRTUAL_ENV) {
    Stop-MedVisionStartup "The virtual environment was not activated."
}

Write-Host "Checking Python dependencies..." -ForegroundColor Cyan
$dependencyCheck = "import cv2, docx, numpy, pandas, pydicom, reportlab, streamlit, torch, torchvision; from PIL import Image"
$dependencyProcess = Start-Process `
    -FilePath $resolvedPython `
    -ArgumentList @("-c", "`"$dependencyCheck`"") `
    -WorkingDirectory $projectRoot `
    -Wait `
    -NoNewWindow `
    -PassThru
if ($dependencyProcess.ExitCode -ne 0) {
    Stop-MedVisionStartup "A Python dependency is missing or broken. Run: `"$resolvedPython`" -m pip install -r `"$appDirectory\requirements.txt`""
}

$existingListener = Get-NetTCPConnection -LocalAddress "127.0.0.1" -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
if ($existingListener) {
    Stop-MedVisionStartup "Port 127.0.0.1:8501 is already in use. Stop the existing process before retrying."
}

$env:PYTHONUTF8 = "1"
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"

Write-Host "Project root : $projectRoot" -ForegroundColor DarkGray
Write-Host "Python       : $resolvedPython" -ForegroundColor DarkGray
Write-Host "Hermes       : $hermesExecutable" -ForegroundColor DarkGray
Write-Host "MedVision    : http://127.0.0.1:8501" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow

Push-Location $projectRoot
$streamlitProcess = $null
try {
    $streamlitArguments = @(
        "-m",
        "streamlit",
        "run",
        "`"$entryPoint`"",
        "--server.address",
        "127.0.0.1",
        "--server.port",
        "8501",
        "--server.headless",
        "true"
    )
    $streamlitProcess = Start-Process `
        -FilePath $resolvedPython `
        -ArgumentList $streamlitArguments `
        -WorkingDirectory $projectRoot `
        -NoNewWindow `
        -PassThru
    $streamlitProcess.WaitForExit()

    if ($streamlitProcess.ExitCode -ne 0) {
        Stop-MedVisionStartup "Streamlit exited with code $($streamlitProcess.ExitCode)."
    }
}
finally {
    if ($null -ne $streamlitProcess -and -not $streamlitProcess.HasExited) {
        Stop-Process -Id $streamlitProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Pop-Location
}
