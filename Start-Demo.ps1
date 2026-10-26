$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$workspacePython = Join-Path $PSScriptRoot '..\..\work\venv\Scripts\python.exe'
if (Test-Path -LiteralPath $projectPython) {
    $demoPython = $projectPython
} elseif (Test-Path -LiteralPath $workspacePython) {
    $demoPython = $workspacePython
} else {
    Write-Host 'Install Python 3.12 and follow the README setup steps first.'
    exit 1
}
& $demoPython -m streamlit run app/dashboard.py --server.address 127.0.0.1 --browser.gatherUsageStats false
