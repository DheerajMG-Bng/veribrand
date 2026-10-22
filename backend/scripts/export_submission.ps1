# Export the editable report through a Word-compatible COM interface without changing its content.
# No confidential documents are opened, and macro automation is disabled.
$veribrandRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$veribrandDocx = Join-Path $veribrandRoot 'docs/submission/VeriBrand_Round2_Update.docx'
$veribrandPdf = Join-Path $veribrandRoot 'docs/submission/VeriBrand_Round2_Update.pdf'
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
    $veribrandDocument.ExportAsFixedFormat($veribrandPdf, 17)
    Write-Output ('PDF exported: ' + $veribrandDocument.ComputeStatistics(2) + ' pages')
}
finally {
    # Word may close its automation server after the final document closes.
    # Cleanup must not mask either a successful export or an original exception.
    try { if ($null -ne $veribrandDocument) { $veribrandDocument.Close(0) } } catch { Write-Verbose 'Word document was already closed.' }
    try { if ($null -ne $veribrandWord -and $veribrandWord.Documents.Count -eq 0) { $veribrandWord.Quit() } } catch { Write-Verbose 'Word automation server had already exited.' }
    try { if ($null -ne $veribrandDocument) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($veribrandDocument) | Out-Null } } catch { Write-Verbose 'Document COM reference was already released.' }
    try { if ($null -ne $veribrandWord) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($veribrandWord) | Out-Null } } catch { Write-Verbose 'Word COM reference was already released.' }
}
