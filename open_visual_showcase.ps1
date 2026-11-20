param(
    [switch]$NoBrowser,
    [switch]$NoExplorer
)
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$pubUrl = if (Test-Path "$ProjectDir\config\public_url.txt") { (Get-Content "$ProjectDir\config\public_url.txt" -Raw).Trim() } else { "http://127.0.0.1:8000" }

$thumbDir = "$ProjectDir\Content_Vault_4D_Thumbnails"
$fullDir  = "$ProjectDir\Content_Vault_4D_Full"
$shortDir = "$ProjectDir\Content_Vault_4D_Shorts"
$tCnt = (Get-ChildItem $thumbDir -Filter "*_3D_Thumb.jpg" -ErrorAction SilentlyContinue).Count
$mCnt = (Get-ChildItem $thumbDir -Filter "*_3D_MovieThumb.mp4" -ErrorAction SilentlyContinue).Count
$fCnt = (Get-ChildItem $fullDir  -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count
$sCnt = (Get-ChildItem $shortDir -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // LIVE VISUAL SHOWCASE" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  Public Storefront : $pubUrl/store" -ForegroundColor Green
Write-Host "  Member Portal     : $pubUrl/portal  (includes `$1,500 + `$49,999 Upsell Bar)" -ForegroundColor Green
Write-Host "  Executive Matrix  : http://127.0.0.1:8000/dashboard" -ForegroundColor Green
Write-Host "  GitHub Repository : https://github.com/Toomer1980/monday_project" -ForegroundColor Cyan
Write-Host "  3D Thumbnails     : $tCnt JPG + $mCnt Animated MovieThumbs -> $thumbDir" -ForegroundColor Yellow
Write-Host "  4D Upgraded Vault : $fCnt Full + $sCnt Shorts -> $fullDir" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan

if (-not $NoBrowser) {
    Start-Process "$pubUrl/store"
    Start-Sleep -Milliseconds 600
    Start-Process "$pubUrl/portal"
    Start-Sleep -Milliseconds 600
    Start-Process "https://github.com/Toomer1980/monday_project"
}
if (-not $NoExplorer) {
    if (Test-Path $thumbDir) { Start-Process explorer.exe $thumbDir }
    if (Test-Path $fullDir)  { Start-Process explorer.exe $fullDir }
}