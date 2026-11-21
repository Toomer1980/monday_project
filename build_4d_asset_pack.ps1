$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$ZipOut     = "$ProjectDir\deliverables\Oracle_4D_Creator_Asset_Pack_15.zip"
$StageTmp   = "$ProjectDir\deliverables\_tmp_pack15"
$TiersJson  = "$ProjectDir\config\stripe_new_tiers.json"

New-Item -ItemType Directory -Path $StageTmp -Force | Out-Null
$readme = @"
ORACLE SYSTEMS LLC - 4D TESSERACT & MOBIUS CREATOR ASSET PACK
=============================================================
Commercial-use pack:
- Seamless 4D Tesseract & Mobius Fluid Portal Video Loops (16:9 + 9:16)
- High-Resolution 3D Pop-Out Thumbnail Templates (JPEG)
- Commercial License: Approved for unlimited YouTube, TikTok, Reels, OBS, and client projects.
"@
[IO.File]::WriteAllText("$StageTmp\LICENSE_AND_README.txt", $readme, $Utf8NoBom)

foreach ($lp in @("_master_4d_portal_1280x720.mp4","_master_4d_portal_1080x1920.mp4")) {
    $src = "$ProjectDir\Content_Vault_4D_Thumbnails\$lp"
    if (Test-Path $src) { Copy-Item $src $StageTmp -Force }
}
Get-ChildItem "$ProjectDir\Content_Vault_4D_Thumbnails" -Filter "*_3D_Thumb.jpg" -ErrorAction SilentlyContinue |
    Select-Object -First 6 | ForEach-Object { Copy-Item $_.FullName $StageTmp -Force }

if (Test-Path $ZipOut) { Remove-Item $ZipOut -Force }
Compress-Archive -Path "$StageTmp\*" -DestinationPath $ZipOut -CompressionLevel Optimal
Remove-Item $StageTmp -Recurse -Force -ErrorAction SilentlyContinue
$mb = [math]::Round((Get-Item $ZipOut).Length / 1MB, 2)
Write-Host "[PACK READY] $ZipOut ($mb MB)" -ForegroundColor Green

$tiers = @{ assetpack15 = ""; vaultsub15 = "" }
if (Test-Path $TiersJson) {
    try {
        $prev = Get-Content $TiersJson -Raw | ConvertFrom-Json
        if ($prev.assetpack15) { $tiers.assetpack15 = $prev.assetpack15 }
        if ($prev.vaultsub15)  { $tiers.vaultsub15  = $prev.vaultsub15 }
    } catch {}
}

$envTxt = if (Test-Path "$ProjectDir\.env") { [IO.File]::ReadAllText("$ProjectDir\.env") } else { "" }
$m = [regex]::Match($envTxt, '(?m)^STRIPE_SECRET_KEY\s*=\s*(.+)$')
if ($m.Success -and ($m.Groups[1].Value.Trim().Trim('"').Trim("'") -match '^(sk|rk)_live_[A-Za-z0-9]+$')) {
    $key = $m.Groups[1].Value.Trim().Trim('"').Trim("'")
    $hdr = @{ Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${key}:")))" }
    try {
        if (-not $tiers.assetpack15) {
            $p1  = Invoke-RestMethod -Uri "https://api.stripe.com/v1/products" -Headers $hdr -Method Post -ContentType "application/x-www-form-urlencoded" -Body "name=$([uri]::EscapeDataString('Oracle 4D Tesseract Creator Asset Pack'))&description=$([uri]::EscapeDataString('Seamless 4D Tesseract + Mobius video loops and 3D thumbnail templates'))"
            $pr1 = Invoke-RestMethod -Uri "https://api.stripe.com/v1/prices" -Headers $hdr -Method Post -ContentType "application/x-www-form-urlencoded" -Body "unit_amount=1500&currency=usd&product=$($p1.id)"
            $pl1 = Invoke-RestMethod -Uri "https://api.stripe.com/v1/payment_links" -Headers $hdr -Method Post -ContentType "application/x-www-form-urlencoded" -Body "line_items[0][price]=$($pr1.id)&line_items[0][quantity]=1"
            $tiers.assetpack15 = $pl1.url
            Write-Host "[STRIPE LIVE] Created `$15 Asset Pack Link -> $($pl1.url)" -ForegroundColor Green
        } else { Write-Host "[STRIPE LIVE] `$15 Asset Pack Link active -> $($tiers.assetpack15)" -ForegroundColor Green }

        if (-not $tiers.vaultsub15) {
            $p2  = Invoke-RestMethod -Uri "https://api.stripe.com/v1/products" -Headers $hdr -Method Post -ContentType "application/x-www-form-urlencoded" -Body "name=$([uri]::EscapeDataString('Oracle Sovereign 4D Member Vault (Monthly)'))&description=$([uri]::EscapeDataString('Monthly unlimited access to 30-min 4D transmissions and 432Hz downloads'))"
            $pr2 = Invoke-RestMethod -Uri "https://api.stripe.com/v1/prices" -Headers $hdr -Method Post -ContentType "application/x-www-form-urlencoded" -Body "unit_amount=1500&currency=usd&recurring[interval]=month&product=$($p2.id)"
            $pl2 = Invoke-RestMethod -Uri "https://api.stripe.com/v1/payment_links" -Headers $hdr -Method Post -ContentType "application/x-www-form-urlencoded" -Body "line_items[0][price]=$($pr2.id)&line_items[0][quantity]=1"
            $tiers.vaultsub15 = $pl2.url
            Write-Host "[STRIPE LIVE] Created `$15/mo Vault Subscription Link -> $($pl2.url)" -ForegroundColor Green
        } else { Write-Host "[STRIPE LIVE] `$15/mo Vault Subscription Link active -> $($tiers.vaultsub15)" -ForegroundColor Green }
    } catch { Write-Host "[WARN] Live Payment Link API note: $($_.Exception.Message)" -ForegroundColor Yellow }
}
[IO.File]::WriteAllText($TiersJson, ($tiers | ConvertTo-Json -Depth 3), $Utf8NoBom)