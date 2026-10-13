# Build the LaTeX reports (English and Vietnamese) with pdflatex + bibtex.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts/build_reports.ps1
param([string[]]$Lang = @("en", "vi"))

$ErrorActionPreference = "Stop"
$reportRoot = Join-Path $PSScriptRoot "..\report"

foreach ($d in $Lang) {
    $dir = Join-Path $reportRoot $d
    Write-Host "=== Building $d ==="
    Push-Location $dir
    try {
        pdflatex -interaction=nonstopmode main.tex | Out-Null
        bibtex main | Out-Null
        pdflatex -interaction=nonstopmode main.tex | Out-Null
        pdflatex -interaction=nonstopmode main.tex | Out-Null
    }
    finally {
        Pop-Location
    }
    Write-Host "  -> report/$d/main.pdf"
}
