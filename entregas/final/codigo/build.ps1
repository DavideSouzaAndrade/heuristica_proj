# Build pipeline: relatorio.md  ->  relatorio.html  ->  relatorio.pdf
#                 slides.md     ->  slides.html (reveal.js standalone)
#
# Requer:
#   * pypandoc-binary instalado via pip (provê pandoc embarcado em
#     %USERPROFILE%\AppData\Local\Programs\Python\Python313\Lib\site-packages\pypandoc\files\pandoc.exe)
#   * Microsoft Edge instalado (padrão em qualquer Windows)
#
# Uso:
#   cd entregas/final
#   .\build.ps1

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

# Localiza o pandoc embarcado no pypandoc
$pandoc = "$env:USERPROFILE\AppData\Local\Programs\Python\Python313\Lib\site-packages\pypandoc\files\pandoc.exe"
if (-not (Test-Path $pandoc)) {
    Write-Error "pandoc not found at $pandoc. Run: pip install pypandoc-binary"
}

# Localiza o Microsoft Edge
$edgeCandidates = @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)
$edge = $edgeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) {
    Write-Error "Microsoft Edge not found in standard install paths."
}

Write-Host "pandoc: $pandoc"
Write-Host "edge:   $edge"

# 1) Relatório: markdown -> HTML
Write-Host "--- generating relatorio.html ---"
& $pandoc relatorio.md `
    --citeproc `
    --bibliography=referencias.bib `
    --standalone `
    --embed-resources `
    --mathjax `
    --css=relatorio.css `
    --metadata=link-citations:true `
    --output=relatorio.html
if ($LASTEXITCODE -ne 0) { Write-Error "pandoc html failed" }

# 2) Relatório: HTML -> PDF via Edge headless
Write-Host "--- generating relatorio.pdf via Edge headless ---"
$htmlAbs = (Resolve-Path relatorio.html).Path
$pdfAbs = Join-Path $here "relatorio.pdf"
& $edge --headless --disable-gpu --no-pdf-header-footer `
    --print-to-pdf="$pdfAbs" "file:///$htmlAbs"
if ($LASTEXITCODE -ne 0) { Write-Error "edge pdf failed" }

# 3) Slides: markdown -> reveal.js HTML
Write-Host "--- generating slides.html (reveal.js) ---"
& $pandoc slides.md `
    --to=revealjs `
    --standalone `
    --embed-resources `
    --slide-level=2 `
    --metadata=revealjs-url:https://unpkg.com/reveal.js@4.6.1 `
    --output=slides.html
if ($LASTEXITCODE -ne 0) { Write-Error "pandoc slides failed" }

Write-Host ""
Write-Host "OK"
Write-Host "  relatorio.pdf  $((Get-Item relatorio.pdf).Length / 1KB) KB"
Write-Host "  relatorio.html $((Get-Item relatorio.html).Length / 1KB) KB"
Write-Host "  slides.html    $((Get-Item slides.html).Length / 1KB) KB"
