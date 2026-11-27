param(
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$InstallRoot,
    [ValidateSet('activate','serve','rollback')][string]$Action = 'serve',
    [string]$Version
)
$ErrorActionPreference = 'Stop'
$Arguments = @('-I','-B',(Join-Path $PSScriptRoot 'bootstrap_individual.py'),'--action',$Action,'--root',$InstallRoot)
if ($Action -ne 'serve') {
    if (-not $Version) { throw 'Es necesaria la versión instalada exacta.' }
    $Arguments += @('--version',$Version)
}
& $Python @Arguments
if ($LASTEXITCODE -ne 0) { throw 'La operación verificada ha sido rechazada.' }
