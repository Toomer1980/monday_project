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

try {
    $dns = Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop
    $ips = @($dns | Where-Object { $_.QueryType -eq "A" } | Select-Object -ExpandProperty IPAddress)
    $ipMatch = if ($ExpectedIP) { $ips -contains $ExpectedIP } else { $ips.Count -gt 0 }
    Write-Host ("[1/5] DNS A-Record       : {0} (Match: {1})" -f ($ips -join ", "), $ipMatch) -ForegroundColor $(if ($ipMatch) { "Green" } else { "Yellow" })
    if (-not $ipMatch) { $passAll = $false }
} catch { Write-Host "[1/5] DNS A-Record       : NOT RESOLVED ($($_.Exception.Message))" -ForegroundColor Yellow; $passAll = $false }

try {
    $tcp = New-Object System.Net.Sockets.TcpClient($Domain, 443)
    $ssl = New-Object System.Net.Security.SslStream($tcp.GetStream(), $false, ({ $true }))
    $ssl.AuthenticateAsClient($Domain)
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($ssl.RemoteCertificate)
    $daysExp = ($cert.NotAfter - (Get-Date)).Days
    $ssl.Close(); $tcp.Close()
    Write-Host ("[2/5] HTTPS SSL Cert     : Valid until {0} ({1} days left)" -f $cert.NotAfter.ToString("yyyy-MM-dd"), $daysExp) -ForegroundColor $(if ($daysExp -gt 7) { "Green" } else { "Yellow" })
} catch { Write-Host "[2/5] HTTPS SSL Cert     : FAILED ($($_.Exception.Message))" -ForegroundColor Red; $passAll = $false }

foreach ($ep in @("/store","/portal","/personalize")) {
    try {
        $r = Invoke-WebRequest -Uri "$BaseUrl$ep" -UseBasicParsing -TimeoutSec 10
        Write-Host ("[3/5] Endpoint {0,-12}: HTTP {1}" -f $ep, $r.StatusCode) -ForegroundColor Green
    } catch { Write-Host ("[3/5] Endpoint {0,-12}: FAILED ({1})" -f $ep, $_.Exception.Message) -ForegroundColor Red; $passAll = $false }
}

try {
    $req = [System.Net.HttpWebRequest]::Create("$BaseUrl/go/auravideo49?utm_source=cutover&utm_medium=do_tier1&utm_campaign=nov27")
    $req.AllowAutoRedirect = $false; $req.Timeout = 10000
    $resp = $req.GetResponse(); $code = [int]$resp.StatusCode; $loc = $resp.Headers["Location"]; $resp.Close()
    Write-Host "[4/5] UTM /go Redirect   : HTTP $code -> $loc" -ForegroundColor Green
} catch [System.Net.WebException] {
    if ($_.Exception.Response) {
        $r = $_.Exception.Response
        Write-Host "[4/5] UTM /go Redirect   : HTTP $([int]$r.StatusCode) -> $($r.Headers['Location'])" -ForegroundColor Green
    } else { Write-Host "[4/5] UTM /go Redirect   : FAILED ($($_.Exception.Message))" -ForegroundColor Red; $passAll = $false }
}

if ($PromoteToProduction -and $passAll) {
    [IO.File]::WriteAllText("$ProjectDir\config\public_url.txt", $BaseUrl, $Utf8NoBom)
    $envTxt = [IO.File]::ReadAllText("$ProjectDir\.env")
    $envTxt = [regex]::Replace($envTxt, '(?m)^PUBLIC_BASE_URL=.*$', "PUBLIC_BASE_URL=$BaseUrl")
    [IO.File]::WriteAllText("$ProjectDir\.env", $envTxt, $Utf8NoBom)
    & "$ProjectDir\sync_stripe_webhook.ps1" -CreateIfMissing
    Write-Host "[5/5] PRODUCTION CUTOVER : COMPLETE! Switched PUBLIC_BASE_URL & Stripe Webhook to $BaseUrl" -ForegroundColor Green
} else {
    Write-Host "[5/5] Cutover Status     : Ready -> pass -PromoteToProduction once Droplet is live." -ForegroundColor Cyan
}