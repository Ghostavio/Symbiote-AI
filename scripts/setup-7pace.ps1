# =============================================================
# setup-7pace.ps1 — Configura SEVENPACE_API_TOKEN e SEVENPACE_BASE_URL
# armazenando o token em $HOME\.7pace.ps1 (fora do $PROFILE).
#
# Equivalente Windows do setup-7pace.sh. Mesmos princípios:
#   - Token nunca passa pela conversa com AI
#   - Mantido em arquivo dedicado fora do $PROFILE pra não ser
#     lido caso o $PROFILE seja aberto em IDE com AI
#
# Como rodar:
#   .\scripts\setup-7pace.ps1
#
# Em PowerShell 5.1+ ou 7.x. Funciona em Windows nativo, não em WSL
# (use o setup-7pace.sh dentro do WSL).
# =============================================================

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$secretFile = Join-Path $HOME '.7pace.ps1'
$baseUrlDefault = 'https://<SEVENPACE_ORG>.timehub.7pace.com'

# --- Localizar $PROFILE ---
$profilePath = $PROFILE.CurrentUserCurrentHost
$profileDir = Split-Path -Parent $profilePath
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}
if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}

Write-Host '🔑 Setup 7pace Timetracker (Windows)' -ForegroundColor Cyan
Write-Host ''
Write-Host "  OS:          $([System.Environment]::OSVersion.VersionString)"
Write-Host "  PowerShell:  $($PSVersionTable.PSVersion)"
Write-Host "  `$PROFILE:    $profilePath"
Write-Host "  Token será gravado em: $secretFile (ACL restrita ao seu usuário)"
Write-Host ''
Write-Host 'Por que um arquivo separado? Se você abrir o $PROFILE em uma IDE'
Write-Host "com AI, ela passa a ler o conteúdo. Mantendo o token em .7pace.ps1"
Write-Host '(que você nunca abre), a chave fica fora desse contexto.'
Write-Host ''

# --- Pedir token (SecureString → texto, sem ficar no histórico) ---
$secureToken = Read-Host -AsSecureString -Prompt 'Cole seu token do 7pace (input oculto)'
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
$token = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)

if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host '✗ Token vazio — abortando.' -ForegroundColor Red
    exit 1
}

$baseUrl = Read-Host -Prompt "Base URL [$baseUrlDefault]"
if ([string]::IsNullOrWhiteSpace($baseUrl)) { $baseUrl = $baseUrlDefault }

# --- Gravar $HOME\.7pace.ps1 ---
# Escapar aspas simples para literal PowerShell
$tokenEscaped = $token -replace "'", "''"
$baseUrlEscaped = $baseUrl -replace "'", "''"

$secretContent = @"
# 7pace Timetracker — gerado por scripts/setup-7pace.ps1
# NÃO commitar. NÃO compartilhar. NÃO abrir em IDE com AI.
`$env:SEVENPACE_API_TOKEN = '$tokenEscaped'
`$env:SEVENPACE_BASE_URL = '$baseUrlEscaped'
"@

Set-Content -Path $secretFile -Value $secretContent -Encoding UTF8 -NoNewline:$false

# --- ACL restritiva (só o usuário atual lê/escreve) ---
try {
    $acl = Get-Acl $secretFile
    $acl.SetAccessRuleProtection($true, $false)  # remove herança
    $userId = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $userId,
        'FullControl',
        'Allow')
    $acl.AddAccessRule($rule)
    Set-Acl -Path $secretFile -AclObject $acl
    Write-Host "✓ Token gravado em $secretFile (ACL restrita a $userId)" -ForegroundColor Green
} catch {
    Write-Host "✓ Token gravado em $secretFile" -ForegroundColor Green
    Write-Host "⚠ Não foi possível restringir ACL: $_" -ForegroundColor Yellow
}

# --- Adicionar dot-source ao $PROFILE (idempotente) ---
$sourceLine = '. $HOME\.7pace.ps1'
$profileContent = Get-Content -Path $profilePath -Raw -ErrorAction SilentlyContinue

if ($profileContent -and $profileContent -match '\.7pace\.ps1') {
    Write-Host "✓ `$PROFILE já dá source no $secretFile — não duplicado" -ForegroundColor Green
} else {
    Add-Content -Path $profilePath -Value ''
    Add-Content -Path $profilePath -Value '# 7pace Timetracker — configurado por setup-7pace.ps1'
    Add-Content -Path $profilePath -Value $sourceLine
    Write-Host "✓ Adicionada linha '$sourceLine' em $profilePath" -ForegroundColor Green
}

# --- Limpar token da memória ---
$token = $null
$tokenEscaped = $null
[System.GC]::Collect()

Write-Host ''
Write-Host '─────────────────────────────────────────────'
Write-Host 'Para ativar nesta sessão:'
Write-Host "  . `$PROFILE"
Write-Host ''
Write-Host 'Ou abra um novo PowerShell. Depois valide:'
Write-Host "  if (`$env:SEVENPACE_API_TOKEN) { 'OK' }"
Write-Host '─────────────────────────────────────────────'
