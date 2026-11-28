param(
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Archive,
    [Parameter(Mandatory=$true)][string]$Signature,
    [Parameter(Mandatory=$true)][string]$InstallRoot,
    [Parameter(Mandatory=$true)][string]$PublisherFile,
    [Parameter(Mandatory=$true)][string]$ExpectedPublisherFingerprint
)
$ErrorActionPreference = 'Stop'
& $Python -I -B (Join-Path $PSScriptRoot 'bootstrap_individual.py') --archive $Archive --signature $Signature --root $InstallRoot --python $Python --publisher-file $PublisherFile --expected-publisher-fingerprint $ExpectedPublisherFingerprint
if ($LASTEXITCODE -ne 0) { throw 'La instalación verificada ha sido rechazada.' }
