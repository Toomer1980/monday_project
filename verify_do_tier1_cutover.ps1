param(
    [string]$Domain = "oraclesystemsllc.com",
    [string]$ExpectedIP = "",
    [switch]$PromoteToProduction
)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$BaseUrl    = "https://$Domain"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  DIGITALOCEAN TIER 1 (`$34.80/mo) CUTOVER VERIFIER // $Domain" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

$passAll = $true

# 1. DNS A-Record Check
$ips = @()
try {
    $dns = Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop
    $ips = @($dns | Where-Object { $_.QueryType -eq "A" } | Select-Object -ExpandProperty IPAddress)
    $ipMatch = if ($ExpectedIP) { $ips -contains $ExpectedIP } else { $ips.Count -gt 0 }
    Write-Host ("[1/5] DNS A-Record       : {0} (Match Expected: {1})" -f ($ips -join ", "), $ipMatch) -ForegroundColor $(if ($ipMatch) { "Green" } else { "Yellow" })
    if (-not $ipMatch) { $passAll = $false }
} catch {
    Write-Host "[1/5] DNS A-Record       : NOT RESOLVED YET ($($_.Exception.Message))" -ForegroundColor Yellow
    $passAll = $false
}

# 2. TLS / SSL Certificate Check
try {
    $tcp = New-Object System.Net.Sockets.TcpClient($Domain, 443)
    $ssl = New-Object System.Net.Security.SslStream($tcp.GetStream(), $false, ({ $true }))
    $ssl.AuthenticateAsClient($Domain)
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($ssl.RemoteCertificate)
    $daysExp = ($cert.NotAfter - (Get-Date)).Days
    $ssl.Close(); $tcp.Close()
    Write-Host ("[2/5] HTTPS SSL Cert     : Valid until {0} ({1} days left) | Issuer: {2}" -f $cert.NotAfter.ToString("yyyy-MM-dd"), $daysExp, $cert.Issuer.Split(",")[0]) -ForegroundColor $(if ($daysExp -gt 7) { "Green" } else { "Yellow" })
} catch {
    Write-Host "[2/5] HTTPS SSL Cert     : FAILED ($($_.Exception.Message))" -ForegroundColor Red
    $passAll = $false
}

# 3. Live Endpoints (/store, /portal, /personalize) + Nginx Headers
foreach ($ep in @("/store","/portal","/personalize")) {
    try {
        $r = Invoke-WebRequest -Uri "$BaseUrl$ep" -UseBasicParsing -TimeoutSec 10
        $srv = $r.Headers["Server"]
        Write-Host ("[3/5] Endpoint {0,-12}: HTTP {1} | Server: {2}" -f $ep, $r.StatusCode, $(if ($srv) { $srv } else { "ok" })) -ForegroundColor Green
    } catch {
        Write-Host ("[3/5] Endpoint {0,-12}: FAILED ({1})" -f $ep, $_.Exception.Message) -ForegroundColor Red
        $passAll = $false
    }
}

# 4. Tracked /go/auravideo49 UTM Redirect Check
try {
    $req = [System.Net.HttpWebRequest]::Create("$BaseUrl/go/auravideo49?utm_source=cutover_check&utm_medium=do_tier1&utm_campaign=nov27")
    $req.AllowAutoRedirect = $false; $req.Timeout = 10000
    $resp = $req.GetResponse(); $code = [int]$resp.StatusCode; $loc = $resp.Headers["Location"]; $resp.Close()
    Write-Host "[4/5] UTM /go Redirect   : HTTP $code -> $loc" -ForegroundColor Green
} catch [System.Net.WebException] {
    if ($_.Exception.Response) {
        $r = $_.Exception.Response
        Write-Host "[4/5] UTM /go Redirect   : HTTP $([int]$r.StatusCode) -> $($r.Headers['Location'])" -ForegroundColor Green
    } else {
        Write-Host "[4/5] UTM /go Redirect   : FAILED ($($_.Exception.Message))" -ForegroundColor Red
        $passAll = $false
    }
}

# 5. Optional Production Cutover (Updates PUBLIC_BASE_URL + Rotates Live Stripe Webhook to Custom Domain)
if ($PromoteToProduction -and $passAll) {
    [IO.File]::WriteAllText("$ProjectDir\config\public_url.txt", $BaseUrl, $Utf8NoBom)
    $envTxt = [IO.File]::ReadAllText("$ProjectDir\.env")
    $envTxt = [regex]::Replace($envTxt, '(?m)^PUBLIC_BASE_URL=.*$', "PUBLIC_BASE_URL=$BaseUrl")
    [IO.File]::WriteAllText("$ProjectDir\.env", $envTxt, $Utf8NoBom)
    & "$ProjectDir\sync_stripe_webhook.ps1" -CreateIfMissing
    Write-Host "[5/5] PRODUCTION CUTOVER : COMPLETE! PUBLIC_BASE_URL & Live Stripe Webhook now point to $BaseUrl" -ForegroundColor Green
} elseif ($PromoteToProduction) {
    Write-Host "[5/5] PRODUCTION CUTOVER : HELD (fix failed gates above before promoting off Cloudflare tunnel)" -ForegroundColor Yellow
} else {
    Write-Host "[5/5] Cutover Ready      : Pass -PromoteToProduction once Droplet is live to switch Stripe webhook to $BaseUrl" -ForegroundColor Cyan
}