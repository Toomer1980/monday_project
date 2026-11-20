param([switch]$NoBrowser, [switch]$NoExplorer)
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$pubUrl = if (Test-Path "$ProjectDir\config\public_url.txt") { (Get-Content "$ProjectDir\config\public_url.txt" -Raw).Trim() } else { "http://127.0.0.1:8000" }
$tDir = "$ProjectDir\Content_Vault_4D_Thumbnails"
$fDir = "$ProjectDir\Content_Vault_4D_Full"
$sDir = "$ProjectDir\Content_Vault_4D_Shorts"
$tCnt = (Get-ChildItem $tDir -Filter "*_3D_Thumb.jpg" -ErrorAction SilentlyContinue).Count
$mCnt = (Get-ChildItem $tDir -Filter "*_3D_MovieThumb.mp4" -ErrorAction SilentlyContinue).Count
$fCnt = (Get-ChildItem $fDir -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count
$sCnt = (Get-ChildItem $sDir -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // LIVE VISUAL SHOWCASE" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  4D Live Storefront : $pubUrl/store" -ForegroundColor Green
Write-Host "  4D Member Portal   : $pubUrl/portal" -ForegroundColor Green
Write-Host "  Executive Matrix   : http://127.0.0.1:8000/dashboard" -ForegroundColor Green
Write-Host "  GitHub Repository  : https://github.com/Toomer1980/monday_project" -ForegroundColor Cyan
Write-Host "  3D Thumbnails      : $tCnt JPG + $mCnt MovieThumbs -> $tDir" -ForegroundColor Yellow
Write-Host "  4D Upgraded Vault  : $fCnt Full + $sCnt Shorts -> $fDir" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan

if (-not $NoBrowser) {
    Start-Process "$pubUrl/store"
    Start-Sleep -Milliseconds 700
    Start-Process "$pubUrl/portal"
    Start-Sleep -Milliseconds 700
    Start-Process "https://github.com/Toomer1980/monday_project"
}
if (-not $NoExplorer) {
    if (Test-Path $tDir) { Start-Process explorer.exe $tDir }
    if (Test-Path $sDir) { Start-Process explorer.exe $sDir }
}