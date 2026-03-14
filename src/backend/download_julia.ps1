$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$resDir = Join-Path $root "resources"
if (-not (Test-Path $resDir)) { New-Item -ItemType Directory -Path $resDir | Out-Null }

$zipPath = Join-Path $resDir "julia.zip"
$url = "https://julialang-s3.julialang.org/bin/winnt/x64/1.10/julia-1.10.0-win64.zip"

if (-not (Test-Path $zipPath)) {
    Write-Host "Downloading Julia from $url..."
    Invoke-WebRequest -Uri $url -OutFile $zipPath
} else {
    Write-Host "Julia zip already exists."
}

Write-Host "Extracting..."
Expand-Archive -Path $zipPath -DestinationPath $resDir -Force

# Find extracted folder (usually julia-1.10.0)
$extracted = Get-ChildItem -Path $resDir -Directory | Where-Object { $_.Name -like "julia-*" }
if ($extracted) {
    $target = Join-Path $resDir "julia"
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Rename-Item -Path $extracted.FullName -NewName "julia"
    Write-Host "renamed $($extracted.Name) to julia"
} else {
    Write-Error "Could not find extracted julia folder"
}

if (Test-Path $zipPath) { Remove-Item $zipPath }
Write-Host "Julia setup complete."
