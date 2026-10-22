# Export the editable report through a Word-compatible COM interface without changing its content.
# No confidential documents are opened, and macro automation is disabled.
$ErrorActionPreference = 'Stop'
$veribrandRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$veribrandDocx = Join-Path $veribrandRoot 'docs/submission/VeriBrand_Round2_Update.docx'
$veribrandPdf = Join-Path $veribrandRoot 'docs/submission/VeriBrand_Round2_Update.pdf'
$veribrandStageDirectory = Join-Path $veribrandRoot '.verification/submission-qa'
New-Item -ItemType Directory -Force -Path $veribrandStageDirectory | Out-Null
$veribrandPdfStage = Join-Path $veribrandStageDirectory ('export-' + [guid]::NewGuid().ToString() + '.pdf')
$veribrandWord = $null
$veribrandDocument = $null
try {
    $veribrandWord = New-Object -ComObject Word.Application
    if ($veribrandWord.Documents.Count -ne 0) {
        throw 'The automation instance contains other documents; export stopped.'
    }
    $veribrandWord.Visible = $false
    $veribrandWord.DisplayAlerts = 0
    $veribrandWord.AutomationSecurity = 3
    Write-Output 'Exporting submission report through Word-compatible COM.'
    $veribrandDocument = $veribrandWord.Documents.Open($veribrandDocx, $false, $true)
    $veribrandDocument.Repaginate()
    # Some Word-compatible exporters fail when overwriting an existing PDF.
    # Export to a new path and replace the final file only after successful output.
    $veribrandDocument.ExportAsFixedFormat($veribrandPdfStage, 17)
    if (-not (Test-Path -LiteralPath $veribrandPdfStage)) { throw 'PDF export produced no output.' }
    Write-Output ('PDF exported: ' + $veribrandDocument.ComputeStatistics(2) + ' pages')
}
Copy-Item -LiteralPath $veribrandPdfStage -Destination $veribrandPdf -Force -ErrorAction Stop
Write-Output 'Final PDF replaced successfully.'
finally {
    # Word may close its automation server after the final document closes.
    # Cleanup must not mask either a successful export or an original exception.
    try { if ($null -ne $veribrandDocument) { $veribrandDocument.Close(0) } } catch { Write-Verbose 'Word document was already closed.' }
    try { if ($null -ne $veribrandWord -and $veribrandWord.Documents.Count -eq 0) { $veribrandWord.Quit() } } catch { Write-Verbose 'Word automation server had already exited.' }
    try { if ($null -ne $veribrandDocument) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($veribrandDocument) | Out-Null } } catch { Write-Verbose 'Document COM reference was already released.' }
    try { if ($null -ne $veribrandWord) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($veribrandWord) | Out-Null } } catch { Write-Verbose 'Word COM reference was already released.' }
}
