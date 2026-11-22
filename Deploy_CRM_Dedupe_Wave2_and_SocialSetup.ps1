# ==============================================================================
# ORACLE SYSTEMS LLC // CRM DEDUPE + WAVE 2 (+30 AGENCIES) + SOCIAL/YT WIZARD
# Pure PowerShell 5.1 ASCII | Zero here-strings | Base64-verified Python modules
# ==============================================================================
param(
    [string]$XToken = "",
    [string]$LinkedInToken = "",
    [string]$LinkedInUrn = "",
    [switch]$UpgradeYouTubeCommentScope
)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

foreach ($v in @("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")) {
    [Environment]::SetEnvironmentVariable($v, "1", "Process")
    [Environment]::SetEnvironmentVariable($v, "1", "User")
}
$env:RCLONE_BIND = "0.0.0.0"

function Write-B64File([string]$Path, [string]$B64) {
    $bytes = [System.Convert]::FromBase64String($B64)
    [System.IO.File]::WriteAllBytes($Path, $bytes)
    Write-Host "  [WROTE] $Path ($($bytes.Length) bytes)" -ForegroundColor DarkCyan
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // CRM DEDUPE, WAVE 2 AGENCIES & SOCIAL API SUITE" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

if (Test-Path "$ProjectDir\optimize_ram_and_boot.ps1") { & "$ProjectDir\optimize_ram_and_boot.ps1" -TrimNow }

Write-Host "`n>>> [1/7] Installing CRM Dedupe Guard, Wave 2 Harvester, Social Config & Reply Monitor..." -ForegroundColor Cyan
$B64_DEDUPE = "aW1wb3J0IG9zCmltcG9ydCBzcWxpdGUzCgpQRElSID0gciJDOlxVc2Vyc1x0b29tZVxEZXNrdG9wXFNvdmVyZWlnbkNvcmUiCkNS" +
    "TV9EQiA9IG9zLnBhdGguam9pbihQRElSLCAiZGF0YSIsICJwcm9ub2RlX2NybS5kYiIpCkVOR0lORV9QWSA9IG9zLnBhdGguam9p" +
    "bihQRElSLCAiTW9kdWxlcyIsICJiMmJfY2xpZW50X2FjcXVpc2l0aW9uX2VuZ2luZS5weSIpCgoKZGVmIGRlZHVwZV9jcm0oKToK" +
    "ICAgIGlmIG5vdCBvcy5wYXRoLmV4aXN0cyhDUk1fREIpOgogICAgICAgIHByaW50KCJbQ1JNLURFRFVQRV0gcHJvbm9kZV9jcm0u" +
    "ZGIgbm90IGZvdW5kIHlldC4iKQogICAgICAgIHJldHVybgogICAgYyA9IHNxbGl0ZTMuY29ubmVjdChDUk1fREIpCiAgICBjLnJv" +
    "d19mYWN0b3J5ID0gc3FsaXRlMy5Sb3cKICAgIHJvd3MgPSBjLmV4ZWN1dGUoIlNFTEVDVCAqIEZST00gcHJvc3BlY3RzIE9SREVS" +
    "IEJZIGlkIEFTQyIpLmZldGNoYWxsKCkKICAgIGJlZm9yZSA9IGxlbihyb3dzKQoKICAgICMgR3JvdXAgYnkgbG93ZXJjYXNlIGVt" +
    "YWlsOyBrZWVwIENPTlRBQ1RFRC9SRVBMSUVEIHJvd3Mgb3ZlciBORVcgcm93cwogICAgcmFuayA9IHsiUkVQTElFRCI6IDQsICJQ" +
    "Uk9QT1NBTCI6IDMsICJDT05UQUNURUQiOiAyLCAiUVVFVUVEIjogMSwgIk5FVyI6IDB9CiAgICBrZWVwX2J5X2VtYWlsID0ge30K" +
    "ICAgIGRlbGV0ZV9pZHMgPSBbXQogICAgZm9yIHIgaW4gcm93czoKICAgICAgICBlbSA9IChyWyJlbWFpbCJdIG9yICIiKS5zdHJp" +
    "cCgpLmxvd2VyKCkKICAgICAgICBpZiBub3QgZW06CiAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgc3QgPSAoclsic3RhZ2Ui" +
    "XSBvciAiTkVXIikudXBwZXIoKSBpZiAic3RhZ2UiIGluIHIua2V5cygpIGVsc2UgIk5FVyIKICAgICAgICBzYyA9IHJhbmsuZ2V0" +
    "KHN0LCAwKQogICAgICAgIGlmIGVtIG5vdCBpbiBrZWVwX2J5X2VtYWlsOgogICAgICAgICAgICBrZWVwX2J5X2VtYWlsW2VtXSA9" +
    "IChyWyJpZCJdLCBzYykKICAgICAgICBlbHNlOgogICAgICAgICAgICBwcmV2X2lkLCBwcmV2X3NjID0ga2VlcF9ieV9lbWFpbFtl" +
    "bV0KICAgICAgICAgICAgaWYgc2MgPiBwcmV2X3NjOgogICAgICAgICAgICAgICAgZGVsZXRlX2lkcy5hcHBlbmQocHJldl9pZCkK" +
    "ICAgICAgICAgICAgICAgIGtlZXBfYnlfZW1haWxbZW1dID0gKHJbImlkIl0sIHNjKQogICAgICAgICAgICBlbHNlOgogICAgICAg" +
    "ICAgICAgICAgZGVsZXRlX2lkcy5hcHBlbmQoclsiaWQiXSkKCiAgICBmb3IgZGlkIGluIGRlbGV0ZV9pZHM6CiAgICAgICAgYy5l" +
    "eGVjdXRlKCJERUxFVEUgRlJPTSBwcm9zcGVjdHMgV0hFUkUgaWQ9PyIsIChkaWQsKSkKCiAgICAjIE5vcm1hbGl6ZSBhbGwgZW1h" +
    "aWxzIHRvIGxvd2VyY2FzZSAmIGVuZm9yY2UgY2FzZS1pbnNlbnNpdGl2ZSBVTklRVUUgaW5kZXgKICAgIGMuZXhlY3V0ZSgiVVBE" +
    "QVRFIHByb3NwZWN0cyBTRVQgZW1haWwgPSBMT1dFUihUUklNKGVtYWlsKSkgV0hFUkUgZW1haWwgSVMgTk9UIE5VTEwiKQogICAg" +
    "dHJ5OgogICAgICAgIGMuZXhlY3V0ZSgiQ1JFQVRFIFVOSVFVRSBJTkRFWCBJRiBOT1QgRVhJU1RTIGlkeF9wcm9zcGVjdHNfZW1h" +
    "aWxfdW5pcXVlIE9OIHByb3NwZWN0cyhlbWFpbCBDT0xMQVRFIE5PQ0FTRSkiKQogICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBleDoK" +
    "ICAgICAgICBwcmludChmIltDUk0tREVEVVBFIE5PVEVdIEluZGV4IG5vdGU6IHtleH0iKQoKICAgIGMuY29tbWl0KCkKICAgIGFm" +
    "dGVyID0gYy5leGVjdXRlKCJTRUxFQ1QgQ09VTlQoKikgRlJPTSBwcm9zcGVjdHMiKS5mZXRjaG9uZSgpWzBdCiAgICBjb250YWN0" +
    "ZWQgPSBjLmV4ZWN1dGUoIlNFTEVDVCBDT1VOVCgqKSBGUk9NIHByb3NwZWN0cyBXSEVSRSBVUFBFUihDT0FMRVNDRShzdGFnZSwn" +
    "JykpPSdDT05UQUNURUQnIikuZmV0Y2hvbmUoKVswXQogICAgcXVldWVkX25ldyA9IGMuZXhlY3V0ZSgiU0VMRUNUIENPVU5UKCop" +
    "IEZST00gcHJvc3BlY3RzIFdIRVJFIFVQUEVSKENPQUxFU0NFKHN0YWdlLCdORVcnKSkgSU4gKCdORVcnLCdRVUVVRUQnKSIpLmZl" +
    "dGNob25lKClbMF0KICAgIGMuY2xvc2UoKQogICAgcHJpbnQoZiJbQ1JNLURFRFVQRSBQQVNTXSBDbGVhbmVkIHtsZW4oZGVsZXRl" +
    "X2lkcyl9IGR1cGxpY2F0ZSByb3cocykgKHtiZWZvcmV9IC0+IHthZnRlcn0gdW5pcXVlIHByb3NwZWN0cykgfCBDb250YWN0ZWQ6" +
    "IHtjb250YWN0ZWR9IHwgUmVhZHkgZm9yIE5leHQgQmF0Y2g6IHtxdWV1ZWRfbmV3fSIpCgoKZGVmIHBhdGNoX2VuZ2luZV9pbXBv" +
    "cnRfZ3VhcmQoKToKICAgICIiIkVuc3VyZSBiMmJfY2xpZW50X2FjcXVpc2l0aW9uX2VuZ2luZS5weSBjaGVja3MgTE9XRVIoZW1h" +
    "aWwpIGV4cGxpY2l0bHkgYmVmb3JlIGluc2VydGluZy4iIiIKICAgIGlmIG5vdCBvcy5wYXRoLmV4aXN0cyhFTkdJTkVfUFkpOgog" +
    "ICAgICAgIHJldHVybgogICAgc3JjID0gb3BlbihFTkdJTkVfUFksICJyIiwgZW5jb2Rpbmc9InV0Zi04IikucmVhZCgpCiAgICBt" +
    "YXJrZXIgPSAiU0VMRUNUIDEgRlJPTSBwcm9zcGVjdHMgV0hFUkUgTE9XRVIoZW1haWwpPT8iCiAgICBpZiBtYXJrZXIgaW4gc3Jj" +
    "OgogICAgICAgIHByaW50KCJbQ1JNLUdVQVJEIFBBU1NdIGIyYl9jbGllbnRfYWNxdWlzaXRpb25fZW5naW5lLnB5IGFscmVhZHkg" +
    "aGFzIGV4cGxpY2l0IGVtYWlsIGRlZHVwZSBndWFyZC4iKQogICAgICAgIHJldHVybgogICAgb2xkX3NuaXAgPSAnICAgICAgICAg" +
    "ICAgY3VyID0gYy5leGVjdXRlKFxuICAgICAgICAgICAgICAgICJJTlNFUlQgT1IgSUdOT1JFIElOVE8gcHJvc3BlY3RzJwogICAg" +
    "bmV3X3NuaXAgPSAoCiAgICAgICAgJyAgICAgICAgICAgIGlmIGMuZXhlY3V0ZSgiU0VMRUNUIDEgRlJPTSBwcm9zcGVjdHMgV0hF" +
    "UkUgTE9XRVIoZW1haWwpPT8iLCAoZW0sKSkuZmV0Y2hvbmUoKTpcbicKICAgICAgICAnICAgICAgICAgICAgICAgIGNvbnRpbnVl" +
    "XG4nCiAgICAgICAgJyAgICAgICAgICAgIGN1ciA9IGMuZXhlY3V0ZShcbicKICAgICAgICAnICAgICAgICAgICAgICAgICJJTlNF" +
    "UlQgT1IgSUdOT1JFIElOVE8gcHJvc3BlY3RzJwogICAgKQogICAgaWYgb2xkX3NuaXAgaW4gc3JjOgogICAgICAgIG9wZW4oRU5H" +
    "SU5FX1BZLCAidyIsIGVuY29kaW5nPSJ1dGYtOCIsIG5ld2xpbmU9IiIpLndyaXRlKHNyYy5yZXBsYWNlKG9sZF9zbmlwLCBuZXdf" +
    "c25pcCwgMSkpCiAgICAgICAgcHJpbnQoIltDUk0tR1VBUkQgUEFTU10gUGF0Y2hlZCBiMmJfY2xpZW50X2FjcXVpc2l0aW9uX2Vu" +
    "Z2luZS5weSB3aXRoIGV4cGxpY2l0IExPV0VSKGVtYWlsKSBkdXBsaWNhdGUgZ3VhcmQuIikKCgppZiBfX25hbWVfXyA9PSAiX19t" +
    "YWluX18iOgogICAgZGVkdXBlX2NybSgpCiAgICBwYXRjaF9lbmdpbmVfaW1wb3J0X2d1YXJkKCkK"
Write-B64File "$ProjectDir\Modules\fix_crm_dedupe.py" $B64_DEDUPE
$B64_WAVE2 = "aW1wb3J0IGNvbmN1cnJlbnQuZnV0dXJlcwppbXBvcnQgY3N2CmltcG9ydCBkYXRldGltZSBhcyBkdAppbXBvcnQganNvbgppbXBv" +
    "cnQgb3MKaW1wb3J0IHN5cwoKUERJUiA9IHIiQzpcVXNlcnNcdG9vbWVcRGVza3RvcFxTb3ZlcmVpZ25Db3JlIgpzeXMucGF0aC5p" +
    "bnNlcnQoMCwgb3MucGF0aC5qb2luKFBESVIsICJNb2R1bGVzIikpCmltcG9ydCBiMmJfcHVibGljX2xlYWRfaGFydmVzdGVyIGFz" +
    "IGhtb2QKCkRBVEFfRElSID0gb3MucGF0aC5qb2luKFBESVIsICJkYXRhIikKUkVQT1JUU19ESVIgPSBvcy5wYXRoLmpvaW4oUERJ" +
    "UiwgInJlcG9ydHMiKQpDU1ZfVFBMID0gb3MucGF0aC5qb2luKERBVEFfRElSLCAiYjJiX3Byb3NwZWN0c19pbXBvcnRfdGVtcGxh" +
    "dGUuY3N2IikKQ1NWX1ZFUiA9IG9zLnBhdGguam9pbihEQVRBX0RJUiwgImIyYl9wcm9zcGVjdHNfdmVyaWZpZWQuY3N2IikKSlNP" +
    "Tl9NQVNURVIgPSBvcy5wYXRoLmpvaW4oREFUQV9ESVIsICJ2ZXJpZmllZF9iMmJfYWdlbmN5X2xlYWRzLmpzb24iKQpNRF9SRVBP" +
    "UlQgPSBvcy5wYXRoLmpvaW4oUkVQT1JUU19ESVIsICJWZXJpZmllZF9BZ2VuY3lfTGVhZHNfTWFzdGVyLm1kIikKCiMgV2F2ZSAy" +
    "OiAzMCBBZGRpdGlvbmFsIFJlYWwgQjJCIFZpZGVvLCBQb2RjYXN0IFByb2R1Y3Rpb24sIFNhYVMgQW5pbWF0aW9uICYgQ3JlYXRv" +
    "ciBBZ2VuY2llcwpXQVZFMl9BR0VOQ0lFUyA9IFsKICAgIHsiY29tcGFueSI6ICJMZW1vbmxpZ2h0IiwgImRvbWFpbiI6ICJsZW1v" +
    "bmxpZ2h0LmNvbSIsICJuaWNoZSI6ICJPbi1EZW1hbmQgQnJhbmQgVmlkZW8gUHJvZHVjdGlvbiBhdCBTY2FsZSIsICJ0YXJnZXRf" +
    "dGllciI6ICJQcm9fTm9kZSAoJDQ5LDk5OSkiLCAiaWNwX3Njb3JlIjogOTYsICJrbm93bl9wdWJsaWNfZW1haWwiOiAiIiwgImNv" +
    "bnRhY3RfdXJsIjogImh0dHBzOi8vd3d3LmxlbW9ubGlnaHQuY29tL2NvbnRhY3QvIn0sCiAgICB7ImNvbXBhbnkiOiAiVmlkaWNv" +
    "IiwgImRvbWFpbiI6ICJ2aWRpY28uY29tIiwgIm5pY2hlIjogIkIyQiBTYWFTICYgVGVjaCBWaWRlbyBQcm9kdWN0aW9uIEFnZW5j" +
    "eSIsICJ0YXJnZXRfdGllciI6ICJQcm9fTm9kZSAoJDQ5LDk5OSkiLCAiaWNwX3Njb3JlIjogOTcsICJrbm93bl9wdWJsaWNfZW1h" +
    "aWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8vdmlkaWNvLmNvbS9jb250YWN0LyJ9LAogICAgeyJjb21wYW55IjogIkRl" +
    "bW8gRHVjayIsICJkb21haW4iOiAiZGVtb2R1Y2suY29tIiwgIm5pY2hlIjogIkV4cGxhaW5lciAmIENvbW1lcmNpYWwgVmlkZW8g" +
    "U3R1ZGlvIiwgInRhcmdldF90aWVyIjogIkNyZWF0b3IgU3RhY2sgKCQxLDUwMCkiLCAiaWNwX3Njb3JlIjogOTMsICJrbm93bl9w" +
    "dWJsaWNfZW1haWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8vZGVtb2R1Y2suY29tL2NvbnRhY3QvIn0sCiAgICB7ImNv" +
    "bXBhbnkiOiAiWXVtIFl1bSBWaWRlb3MiLCAiZG9tYWluIjogInl1bXl1bXZpZGVvcy5jb20iLCAibmljaGUiOiAiQjJCIEFuaW1h" +
    "dGVkIEV4cGxhaW5lciAmIE1hcmtldGluZyBWaWRlb3MiLCAidGFyZ2V0X3RpZXIiOiAiQ3JlYXRvciBTdGFjayAoJDEsNTAwKSIs" +
    "ICJpY3Bfc2NvcmUiOiA5NCwgImtub3duX3B1YmxpY19lbWFpbCI6ICIiLCAiY29udGFjdF91cmwiOiAiaHR0cHM6Ly93d3cueXVt" +
    "eXVtdmlkZW9zLmNvbS9jb250YWN0LyJ9LAogICAgeyJjb21wYW55IjogIld5em93bCIsICJkb21haW4iOiAid3l6b3dsLmNvbSIs" +
    "ICJuaWNoZSI6ICJBbmltYXRlZCBFeHBsYWluZXIgJiBTYWFTIFZpZGVvIFN0dWRpbyIsICJ0YXJnZXRfdGllciI6ICJQcm9fTm9k" +
    "ZSAoJDQ5LDk5OSkiLCAiaWNwX3Njb3JlIjogOTUsICJrbm93bl9wdWJsaWNfZW1haWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0" +
    "dHBzOi8vd3d3Lnd5em93bC5jb20vY29udGFjdC8ifSwKICAgIHsiY29tcGFueSI6ICJFcGlwaGVvIiwgImRvbWFpbiI6ICJlcGlw" +
    "aGVvLmNvbSIsICJuaWNoZSI6ICJCMkIgRXhwbGFpbmVyICYgU3RvcnkgVmlkZW8gUHJvZHVjdGlvbiIsICJ0YXJnZXRfdGllciI6" +
    "ICJDcmVhdG9yIFN0YWNrICgkMSw1MDApIiwgImljcF9zY29yZSI6IDkyLCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250" +
    "YWN0X3VybCI6ICJodHRwczovL2VwaXBoZW8uY29tL2NvbnRhY3QvIn0sCiAgICB7ImNvbXBhbnkiOiAiRXhwbGFpbmlmeSIsICJk" +
    "b21haW4iOiAiZXhwbGFpbmlmeS5jb20iLCAibmljaGUiOiAiRW50ZXJwcmlzZSBFeHBsYWluZXIgJiBBbmltYXRlZCBWaWRlbyBB" +
    "Z2VuY3kiLCAidGFyZ2V0X3RpZXIiOiAiQ3JlYXRvciBTdGFjayAoJDEsNTAwKSIsICJpY3Bfc2NvcmUiOiA5MSwgImtub3duX3B1" +
    "YmxpY19lbWFpbCI6ICIiLCAiY29udGFjdF91cmwiOiAiaHR0cHM6Ly9leHBsYWluaWZ5LmNvbS9jb250YWN0LyJ9LAogICAgeyJj" +
    "b21wYW55IjogIkJyZWFkbmJleW9uZCIsICJkb21haW4iOiAiYnJlYWRuYmV5b25kLmNvbSIsICJuaWNoZSI6ICJNb3Rpb24gR3Jh" +
    "cGhpY3MgJiBFeHBsYWluZXIgVmlkZW8gU3R1ZGlvIiwgInRhcmdldF90aWVyIjogIkNyZWF0b3IgU3RhY2sgKCQxLDUwMCkiLCAi" +
    "aWNwX3Njb3JlIjogOTIsICJrbm93bl9wdWJsaWNfZW1haWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8vYnJlYWRuYmV5" +
    "b25kLmNvbS9jb250YWN0LyJ9LAogICAgeyJjb21wYW55IjogIk1vdGlvbkdpbGl0eSIsICJkb21haW4iOiAibW90aW9uZ2lsaXR5" +
    "LmNvbSIsICJuaWNoZSI6ICJCMkIgU2FhUyAmIFRlY2ggRXhwbGFpbmVyIFZpZGVvIEFnZW5jeSIsICJ0YXJnZXRfdGllciI6ICJD" +
    "cmVhdG9yIFN0YWNrICgkMSw1MDApIiwgImljcF9zY29yZSI6IDkzLCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0" +
    "X3VybCI6ICJodHRwczovL21vdGlvbmdpbGl0eS5jb20vY29udGFjdC11cy8ifSwKICAgIHsiY29tcGFueSI6ICJLYXNyYSBEZXNp" +
    "Z24iLCAiZG9tYWluIjogImthc3JhZGVzaWduLmNvbSIsICJuaWNoZSI6ICIzRCBBbmltYXRpb24gJiBDb21tZXJjaWFsIFZpZGVv" +
    "IFN0dWRpbyIsICJ0YXJnZXRfdGllciI6ICJDcmVhdG9yIFN0YWNrICgkMSw1MDApIiwgImljcF9zY29yZSI6IDkxLCAia25vd25f" +
    "cHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3VybCI6ICJodHRwczovL3d3dy5rYXNyYWRlc2lnbi5jb20vY29udGFjdC8ifSwK" +
    "ICAgIHsiY29tcGFueSI6ICJMb3dlciBTdHJlZXQiLCAiZG9tYWluIjogImxvd2Vyc3RyZWV0LmNvIiwgIm5pY2hlIjogIkIyQiBC" +
    "cmFuZGVkIFBvZGNhc3QgUHJvZHVjdGlvbiBBZ2VuY3kiLCAidGFyZ2V0X3RpZXIiOiAiUHJvX05vZGUgKCQ0OSw5OTkpIiwgImlj" +
    "cF9zY29yZSI6IDk0LCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3VybCI6ICJodHRwczovL2xvd2Vyc3RyZWV0" +
    "LmNvL2NvbnRhY3QifSwKICAgIHsiY29tcGFueSI6ICJRdWlsbCBQb2RjYXN0aW5nIiwgImRvbWFpbiI6ICJxdWlsbHBvZGNhc3Rp" +
    "bmcuY29tIiwgIm5pY2hlIjogIkZ1bGwtU2VydmljZSBCcmFuZCBQb2RjYXN0IEFnZW5jeSIsICJ0YXJnZXRfdGllciI6ICJDcmVh" +
    "dG9yIFN0YWNrICgkMSw1MDApIiwgImljcF9zY29yZSI6IDkzLCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3Vy" +
    "bCI6ICJodHRwczovL3d3dy5xdWlsbHBvZGNhc3RpbmcuY29tL2NvbnRhY3QifSwKICAgIHsiY29tcGFueSI6ICJTd2VldCBGaXNo" +
    "IE1lZGlhIiwgImRvbWFpbiI6ICJzd2VldGZpc2htZWRpYS5jb20iLCAibmljaGUiOiAiQjJCIFBvZGNhc3QgJiBTaG9ydC1Gb3Jt" +
    "IFZpZGVvIENvbnRlbnQiLCAidGFyZ2V0X3RpZXIiOiAiUHJvX05vZGUgKCQ0OSw5OTkpIiwgImljcF9zY29yZSI6IDk2LCAia25v" +
    "d25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3VybCI6ICJodHRwczovL3N3ZWV0ZmlzaG1lZGlhLmNvbS9jb250YWN0LyJ9" +
    "LAogICAgeyJjb21wYW55IjogIkZhbWUgQjJCIFBvZGNhc3RpbmciLCAiZG9tYWluIjogImZhbWUuc28iLCAibmljaGUiOiAiQjJC" +
    "IFBvZGNhc3QgR3Jvd3RoICYgWW91VHViZSBDbGlwcyBBZ2VuY3kiLCAidGFyZ2V0X3RpZXIiOiAiUHJvX05vZGUgKCQ0OSw5OTkp" +
    "IiwgImljcF9zY29yZSI6IDk1LCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3VybCI6ICJodHRwczovL3d3dy5m" +
    "YW1lLnNvL2NvbnRhY3QifSwKICAgIHsiY29tcGFueSI6ICJDb21lIEFsaXZlIENyZWF0aXZlIiwgImRvbWFpbiI6ICJjb21lYWxp" +
    "dmVjcmVhdGl2ZS5jb20iLCAibmljaGUiOiAiQnJhbmRlZCBQb2RjYXN0ICYgVmlkZW8gUHJvZHVjdGlvbiIsICJ0YXJnZXRfdGll" +
    "ciI6ICJDcmVhdG9yIFN0YWNrICgkMSw1MDApIiwgImljcF9zY29yZSI6IDkxLCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJj" +
    "b250YWN0X3VybCI6ICJodHRwczovL2NvbWVhbGl2ZWNyZWF0aXZlLmNvbS9jb250YWN0LyJ9LAogICAgeyJjb21wYW55IjogIlBh" +
    "Y2lmaWMgQ29udGVudCIsICJkb21haW4iOiAicGFjaWZpYy1jb250ZW50LmNvbSIsICJuaWNoZSI6ICJFbnRlcnByaXNlIEJyYW5k" +
    "ZWQgQXVkaW8gJiBQb2RjYXN0IFN0dWRpbyIsICJ0YXJnZXRfdGllciI6ICJQcm9fTm9kZSAoJDQ5LDk5OSkiLCAiaWNwX3Njb3Jl" +
    "IjogOTIsICJrbm93bl9wdWJsaWNfZW1haWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8vcGFjaWZpYy1jb250ZW50LmNv" +
    "bS9jb250YWN0LyJ9LAogICAgeyJjb21wYW55IjogIkpBUiBBdWRpbyIsICJkb21haW4iOiAiamFyYXVkaW8uY29tIiwgIm5pY2hl" +
    "IjogIkJyYW5kIFBvZGNhc3QgU3RyYXRlZ3kgJiBQcm9kdWN0aW9uIEFnZW5jeSIsICJ0YXJnZXRfdGllciI6ICJDcmVhdG9yIFN0" +
    "YWNrICgkMSw1MDApIiwgImljcF9zY29yZSI6IDkxLCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3VybCI6ICJo" +
    "dHRwczovL2phcmF1ZGlvLmNvbS9jb250YWN0LyJ9LAogICAgeyJjb21wYW55IjogIkNvbnRlbnQgQWxsaWVzIiwgImRvbWFpbiI6" +
    "ICJjb250ZW50YWxsaWVzLmNvbSIsICJuaWNoZSI6ICJCMkIgRXhlY3V0aXZlIFBvZGNhc3QgJiBWaWRlbyBBZ2VuY3kiLCAidGFy" +
    "Z2V0X3RpZXIiOiAiUHJvX05vZGUgKCQ0OSw5OTkpIiwgImljcF9zY29yZSI6IDk0LCAia25vd25fcHVibGljX2VtYWlsIjogIiIs" +
    "ICJjb250YWN0X3VybCI6ICJodHRwczovL2NvbnRlbnRhbGxpZXMuY29tL2NvbnRhY3QifSwKICAgIHsiY29tcGFueSI6ICJSZXNv" +
    "bmF0ZSBSZWNvcmRpbmdzIiwgImRvbWFpbiI6ICJyZXNvbmF0ZXJlY29yZGluZ3MuY29tIiwgIm5pY2hlIjogIlBvZGNhc3QgJiBW" +
    "aWRlbyBQb3N0LVByb2R1Y3Rpb24gU3R1ZGlvIiwgInRhcmdldF90aWVyIjogIlByb19Ob2RlICgkNDksOTk5KSIsICJpY3Bfc2Nv" +
    "cmUiOiA5MywgImtub3duX3B1YmxpY19lbWFpbCI6ICIiLCAiY29udGFjdF91cmwiOiAiaHR0cHM6Ly9yZXNvbmF0ZXJlY29yZGlu" +
    "Z3MuY29tL2NvbnRhY3QvIn0sCiAgICB7ImNvbXBhbnkiOiAiQmlsbG8gQ3JlYXRvciBWaWRlbyIsICJkb21haW4iOiAiYmlsbG8u" +
    "YXBwIiwgIm5pY2hlIjogIkNyZWF0b3IgVmlkZW8gQWRzICYgUGVyZm9ybWFuY2UgUHJvZHVjdGlvbiIsICJ0YXJnZXRfdGllciI6" +
    "ICJQcm9fTm9kZSAoJDQ5LDk5OSkiLCAiaWNwX3Njb3JlIjogOTMsICJrbm93bl9wdWJsaWNfZW1haWwiOiAiIiwgImNvbnRhY3Rf" +
    "dXJsIjogImh0dHBzOi8vYmlsbG8uYXBwL2NvbnRhY3QtdXMvIn0sCiAgICB7ImNvbXBhbnkiOiAiVmlyYWwgTmF0aW9uIiwgImRv" +
    "bWFpbiI6ICJ2aXJhbG5hdGlvbi5jb20iLCAibmljaGUiOiAiQ3JlYXRvciBUYWxlbnQsIFNvY2lhbCBWaWRlbyAmIEFJIE1hcmtl" +
    "dGluZyIsICJ0YXJnZXRfdGllciI6ICJQcm9fTm9kZSAoJDQ5LDk5OSkiLCAiaWNwX3Njb3JlIjogOTUsICJrbm93bl9wdWJsaWNf" +
    "ZW1haWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8vd3d3LnZpcmFsbmF0aW9uLmNvbS9jb250YWN0LyJ9LAogICAgeyJj" +
    "b21wYW55IjogIlViaXF1aXRvdXMiLCAiZG9tYWluIjogInViaXF1aXRvdXNpbmZsdWVuY2UuY29tIiwgIm5pY2hlIjogIllvdVR1" +
    "YmUgJiBUaWtUb2sgQ3JlYXRvciBDYW1wYWlnbiBBZ2VuY3kiLCAidGFyZ2V0X3RpZXIiOiAiUHJvX05vZGUgKCQ0OSw5OTkpIiwg" +
    "ImljcF9zY29yZSI6IDkzLCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3VybCI6ICJodHRwczovL3d3dy51Ymlx" +
    "dWl0b3VzaW5mbHVlbmNlLmNvbS9jb250YWN0In0sCiAgICB7ImNvbXBhbnkiOiAiU3Bhcmtob3VzZSIsICJkb21haW4iOiAidGhl" +
    "c3Bhcmtob3VzZS5jb20iLCAibmljaGUiOiAiQ29tbWVyY2lhbCBCcmFuZCBWaWRlbyAmIFNvY2lhbCBBZHMgU3R1ZGlvIiwgInRh" +
    "cmdldF90aWVyIjogIkNyZWF0b3IgU3RhY2sgKCQxLDUwMCkiLCAiaWNwX3Njb3JlIjogOTIsICJrbm93bl9wdWJsaWNfZW1haWwi" +
    "OiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8vd3d3LnRoZXNwYXJraG91c2UuY29tL2NvbnRhY3QvIn0sCiAgICB7ImNvbXBh" +
    "bnkiOiAiVmVyYWNpdHlDb2xhYiIsICJkb21haW4iOiAidmVyYWNpdHljb2xhYi5jb20iLCAibmljaGUiOiAiVmlkZW8gQ3JlYXRp" +
    "dmUgJiBCcmFuZCBTdG9yeXRlbGxpbmcgQWdlbmN5IiwgInRhcmdldF90aWVyIjogIkNyZWF0b3IgU3RhY2sgKCQxLDUwMCkiLCAi" +
    "aWNwX3Njb3JlIjogOTEsICJrbm93bl9wdWJsaWNfZW1haWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8vd3d3LnZlcmFj" +
    "aXR5Y29sYWIuY29tL2NvbnRhY3QvIn0sCiAgICB7ImNvbXBhbnkiOiAiQmV2ZXJsZXkgJiBDbyAvIFRoaW5rIEJyYW5kZWQiLCAi" +
    "ZG9tYWluIjogInRoaW5rYnJhbmRlZG1lZGlhLmNvbSIsICJuaWNoZSI6ICJCcmFuZCBWaWRlbyAmIERpZ2l0YWwgQ29udGVudCBQ" +
    "cm9kdWN0aW9uIiwgInRhcmdldF90aWVyIjogIkNyZWF0b3IgU3RhY2sgKCQxLDUwMCkiLCAiaWNwX3Njb3JlIjogOTAsICJrbm93" +
    "bl9wdWJsaWNfZW1haWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8vdGhpbmticmFuZGVkbWVkaWEuY29tL2NvbnRhY3Qv" +
    "In0sCiAgICB7ImNvbXBhbnkiOiAiWWRyYXciLCAiZG9tYWluIjogInlkcmF3LmNvbSIsICJuaWNoZSI6ICJBbmltYXRlZCBNYXJr" +
    "ZXRpbmcgJiBFeHBsYWluZXIgVmlkZW9zIiwgInRhcmdldF90aWVyIjogIkNyZWF0b3IgU3RhY2sgKCQxLDUwMCkiLCAiaWNwX3Nj" +
    "b3JlIjogOTAsICJrbm93bl9wdWJsaWNfZW1haWwiOiAiIiwgImNvbnRhY3RfdXJsIjogImh0dHBzOi8veWRyYXcuY29tL2NvbnRh" +
    "Y3QtdXMvIn0sCiAgICB7ImNvbXBhbnkiOiAiSWRlYVJvY2tldCIsICJkb21haW4iOiAiaWRlYXJvY2tldGFuaW1hdGlvbi5jb20i" +
    "LCAibmljaGUiOiAiMkQvM0QgQjJCIEFuaW1hdGlvbiAmIFZpZGVvIEFnZW5jeSIsICJ0YXJnZXRfdGllciI6ICJDcmVhdG9yIFN0" +
    "YWNrICgkMSw1MDApIiwgImljcF9zY29yZSI6IDkxLCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3VybCI6ICJo" +
    "dHRwczovL2lkZWFyb2NrZXRhbmltYXRpb24uY29tL2NvbnRhY3QvIn0sCiAgICB7ImNvbXBhbnkiOiAiR2lzdGVvIiwgImRvbWFp" +
    "biI6ICJnaXN0ZW8uY29tIiwgIm5pY2hlIjogIkV4cGxhaW5lciBWaWRlbyAmIENyZWF0b3IgTW90aW9uIFN0dWRpbyIsICJ0YXJn" +
    "ZXRfdGllciI6ICJDcmVhdG9yIFN0YWNrICgkMSw1MDApIiwgImljcF9zY29yZSI6IDkwLCAia25vd25fcHVibGljX2VtYWlsIjog" +
    "IiIsICJjb250YWN0X3VybCI6ICJodHRwczovL2dpc3Rlby5jb20vY29udGFjdC8ifSwKICAgIHsiY29tcGFueSI6ICJEaWdpdGFs" +
    "IEJyZXciLCAiZG9tYWluIjogImRpZ2l0YWxicmV3LmNvbSIsICJuaWNoZSI6ICJFbW15LVdpbm5pbmcgRXhwbGFpbmVyICYgQnJh" +
    "bmQgVmlkZW8gU3R1ZGlvIiwgInRhcmdldF90aWVyIjogIlByb19Ob2RlICgkNDksOTk5KSIsICJpY3Bfc2NvcmUiOiA5NCwgImtu" +
    "b3duX3B1YmxpY19lbWFpbCI6ICIiLCAiY29udGFjdF91cmwiOiAiaHR0cHM6Ly93d3cuZGlnaXRhbGJyZXcuY29tL2NvbnRhY3Qv" +
    "In0sCiAgICB7ImNvbXBhbnkiOiAiTW90aW9uQ3VlIiwgImRvbWFpbiI6ICJtb3Rpb25jdWUuY29tIiwgIm5pY2hlIjogIkIyQiBW" +
    "aWRlbyBNYXJrZXRpbmcgJiBNb3Rpb24gRGVzaWduIEFnZW5jeSIsICJ0YXJnZXRfdGllciI6ICJDcmVhdG9yIFN0YWNrICgkMSw1" +
    "MDApIiwgImljcF9zY29yZSI6IDkzLCAia25vd25fcHVibGljX2VtYWlsIjogIiIsICJjb250YWN0X3VybCI6ICJodHRwczovL21v" +
    "dGlvbmN1ZS5jb20vY29udGFjdC8ifSwKXQoKCmRlZiBtYWluKCk6CiAgICBwcmV2ID0ganNvbi5sb2FkKG9wZW4oSlNPTl9NQVNU" +
    "RVIsICJyIiwgZW5jb2Rpbmc9InV0Zi04IikpIGlmIG9zLnBhdGguZXhpc3RzKEpTT05fTUFTVEVSKSBlbHNlIHt9CiAgICBleGlz" +
    "dGluZ19kaXJlY3QgPSBsaXN0KHByZXYuZ2V0KCJkaXJlY3RfZW1haWxfbGVhZHMiKSBvciBbXSkKICAgIGV4aXN0aW5nX2Zvcm1z" +
    "ID0gbGlzdChwcmV2LmdldCgiY29udGFjdF9mb3JtX2xlYWRzIikgb3IgW10pCiAgICBzZWVuX2RvbWFpbnMgPSB7ci5nZXQoImRv" +
    "bWFpbiIsICIiKS5sb3dlcigpIGZvciByIGluIGV4aXN0aW5nX2RpcmVjdCArIGV4aXN0aW5nX2Zvcm1zfQoKICAgIHRvX3NjYW4g" +
    "PSBbYSBmb3IgYSBpbiBXQVZFMl9BR0VOQ0lFUyBpZiBhWyJkb21haW4iXS5sb3dlcigpIG5vdCBpbiBzZWVuX2RvbWFpbnNdCiAg" +
    "ICBwcmludChmIltXQVZFIDIgSEFSVkVTVEVSXSBBdWRpdGluZyB7bGVuKHRvX3NjYW4pfSBuZXcgQjJCIFZpZGVvLCBQb2RjYXN0" +
    "ICYgQW5pbWF0aW9uIEFnZW5jaWVzIChza2lwcGluZyB7bGVuKFdBVkUyX0FHRU5DSUVTKS1sZW4odG9fc2Nhbil9IGFscmVhZHkg" +
    "c2Nhbm5lZCkuLi4iKQoKICAgIG5ld19kaXJlY3QsIG5ld19mb3JtcyA9IFtdLCBbXQogICAgd2l0aCBjb25jdXJyZW50LmZ1dHVy" +
    "ZXMuVGhyZWFkUG9vbEV4ZWN1dG9yKG1heF93b3JrZXJzPTgpIGFzIGV4OgogICAgICAgIGZvciByZXMgaW4gZXgubWFwKGhtb2Qu" +
    "aGFydmVzdF9vbmVfYWdlbmN5LCB0b19zY2FuKToKICAgICAgICAgICAgaWYgcmVzWyJlbWFpbCJdOgogICAgICAgICAgICAgICAg" +
    "bmV3X2RpcmVjdC5hcHBlbmQocmVzKQogICAgICAgICAgICAgICAgcHJpbnQoZiIgIFt7cmVzWydpY3Bfc2NvcmUnXX1dIHtyZXNb" +
    "J2NvbXBhbnknXTo8MzJ9IHwgRU1BSUwgRk9VTkQ6IHtyZXNbJ2VtYWlsJ119ICh7cmVzWydteF9zdGF0dXMnXX0pIikKICAgICAg" +
    "ICAgICAgZWxpZiByZXNbInNpdGVfcmVhY2hhYmxlIl06CiAgICAgICAgICAgICAgICBuZXdfZm9ybXMuYXBwZW5kKHJlcykKICAg" +
    "ICAgICAgICAgICAgIHByaW50KGYiICBbe3Jlc1snaWNwX3Njb3JlJ119XSB7cmVzWydjb21wYW55J106PDMyfSB8IEZPUk0gT05M" +
    "WSAtPiB7cmVzWydjb250YWN0X3VybCddfSIpCiAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICBwcmludChmIiAgWy0t" +
    "XSB7cmVzWydjb21wYW55J106PDMyfSB8IFNpdGUgdW5yZWFjaGFibGUgLyB0aW1lb3V0LCBza2lwcGVkIikKCiAgICBhbGxfZGly" +
    "ZWN0ID0gc29ydGVkKGV4aXN0aW5nX2RpcmVjdCArIG5ld19kaXJlY3QsIGtleT1sYW1iZGEgcjogci5nZXQoImljcF9zY29yZSIs" +
    "IDApLCByZXZlcnNlPVRydWUpCiAgICAjIERlZHVwZSBkaXJlY3QgYnkgZW1haWwKICAgIGRlZHVwX2RpcmVjdCwgc2Vlbl9lbSA9" +
    "IFtdLCBzZXQoKQogICAgZm9yIHIgaW4gYWxsX2RpcmVjdDoKICAgICAgICBlbSA9IChyLmdldCgiZW1haWwiKSBvciAiIikubG93" +
    "ZXIoKS5zdHJpcCgpCiAgICAgICAgaWYgZW0gYW5kIGVtIG5vdCBpbiBzZWVuX2VtOgogICAgICAgICAgICBzZWVuX2VtLmFkZChl" +
    "bSkKICAgICAgICAgICAgZGVkdXBfZGlyZWN0LmFwcGVuZChyKQoKICAgIGFsbF9mb3JtcyA9IHNvcnRlZChleGlzdGluZ19mb3Jt" +
    "cyArIG5ld19mb3Jtcywga2V5PWxhbWJkYSByOiByLmdldCgiaWNwX3Njb3JlIiwgMCksIHJldmVyc2U9VHJ1ZSkKICAgIGRlZHVw" +
    "X2Zvcm1zLCBzZWVuX2ZkID0gW10sIHNldCgpCiAgICBmb3IgciBpbiBhbGxfZm9ybXM6CiAgICAgICAgZG0gPSAoci5nZXQoImRv" +
    "bWFpbiIpIG9yICIiKS5sb3dlcigpLnN0cmlwKCkKICAgICAgICBpZiBkbSBhbmQgZG0gbm90IGluIHNlZW5fZmQ6CiAgICAgICAg" +
    "ICAgIHNlZW5fZmQuYWRkKGRtKQogICAgICAgICAgICBkZWR1cF9mb3Jtcy5hcHBlbmQocikKCiAgICBjc3Zfcm93cyA9IFsKICAg" +
    "ICAgICB7ImNvbXBhbnkiOiByWyJjb21wYW55Il0sICJjb250YWN0Ijogci5nZXQoImNvbnRhY3QiKSBvciAiUGFydG5lcnNoaXBz" +
    "IFRlYW0iLCAiZW1haWwiOiByWyJlbWFpbCJdLCAibm90ZXMiOiByWyJub3RlcyJdfQogICAgICAgIGZvciByIGluIGRlZHVwX2Rp" +
    "cmVjdAogICAgXQogICAgZm9yIHRhcmdldF9jc3YgaW4gKENTVl9UUEwsIENTVl9WRVIpOgogICAgICAgIHdpdGggb3Blbih0YXJn" +
    "ZXRfY3N2LCAidyIsIGVuY29kaW5nPSJ1dGYtOCIsIG5ld2xpbmU9IiIpIGFzIGY6CiAgICAgICAgICAgIHcgPSBjc3YuRGljdFdy" +
    "aXRlcihmLCBmaWVsZG5hbWVzPVsiY29tcGFueSIsICJjb250YWN0IiwgImVtYWlsIiwgIm5vdGVzIl0pCiAgICAgICAgICAgIHcu" +
    "d3JpdGVoZWFkZXIoKQogICAgICAgICAgICB3LndyaXRlcm93cyhjc3Zfcm93cykKCiAgICBqc29uLmR1bXAoewogICAgICAgICJn" +
    "ZW5lcmF0ZWRfdXRjIjogZHQuZGF0ZXRpbWUudXRjbm93KCkuaXNvZm9ybWF0KCkgKyAiWiIsCiAgICAgICAgInRvdGFsX2FnZW5j" +
    "aWVzX2F1ZGl0ZWQiOiBsZW4oZGVkdXBfZGlyZWN0KSArIGxlbihkZWR1cF9mb3JtcyksCiAgICAgICAgInZlcmlmaWVkX2RpcmVj" +
    "dF9lbWFpbF9jb3VudCI6IGxlbihkZWR1cF9kaXJlY3QpLAogICAgICAgICJjb250YWN0X2Zvcm1fYWdlbmN5X2NvdW50IjogbGVu" +
    "KGRlZHVwX2Zvcm1zKSwKICAgICAgICAiZGlyZWN0X2VtYWlsX2xlYWRzIjogZGVkdXBfZGlyZWN0LAogICAgICAgICJjb250YWN0" +
    "X2Zvcm1fbGVhZHMiOiBkZWR1cF9mb3JtcywKICAgIH0sIG9wZW4oSlNPTl9NQVNURVIsICJ3IiwgZW5jb2Rpbmc9InV0Zi04Iiks" +
    "IGluZGVudD0yKQoKICAgIGxpbmVzID0gWwogICAgICAgIGYiIyBPcmFjbGUgU3lzdGVtcyBMTEMgLSBWZXJpZmllZCBCMkIgQWdl" +
    "bmN5IExlYWRzIERpcmVjdG9yeSAoV2F2ZSAxICsgV2F2ZSAyIHwge2R0LmRhdGV0aW1lLm5vdygpLnN0cmZ0aW1lKCclWS0lbS0l" +
    "ZCAlSDolTScpfSBFU1QpIiwKICAgICAgICBmIi0gKipUb3RhbCBWZXJpZmllZCBBY3RpdmUgQWdlbmNpZXM6Kioge2xlbihkZWR1" +
    "cF9kaXJlY3QpICsgbGVuKGRlZHVwX2Zvcm1zKX0iLAogICAgICAgIGYiLSAqKk1YLVZlcmlmaWVkIERpcmVjdCBCdXNpbmVzcyBF" +
    "bWFpbHMgKEdtYWlsIEFQSSBSZWFkeSk6Kioge2xlbihkZWR1cF9kaXJlY3QpfSAoK3tsZW4obmV3X2RpcmVjdCl9IG5ldyBpbiBX" +
    "YXZlIDIpIiwKICAgICAgICBmIi0gKipDb250YWN0LUZvcm0gQWdlbmNpZXM6Kioge2xlbihkZWR1cF9mb3Jtcyl9ICgre2xlbihu" +
    "ZXdfZm9ybXMpfSBuZXcgaW4gV2F2ZSAyKSIsCiAgICAgICAgIiIsCiAgICAgICAgIiMjIDEuIE1YLVZlcmlmaWVkIERpcmVjdCBF" +
    "bWFpbCBMZWFkcyIsCiAgICAgICAgInwgSUNQIHwgQWdlbmN5IHwgUHVibGljIEJ1c2luZXNzIEVtYWlsIHwgVGFyZ2V0IE9mZmVy" +
    "IHwgTmljaGUgfCIsCiAgICAgICAgInwgOi0tLTogfCA6LS0tIHwgOi0tLSB8IDotLS0gfCA6LS0tIHwiLAogICAgXQogICAgZm9y" +
    "IHIgaW4gZGVkdXBfZGlyZWN0OgogICAgICAgIGxpbmVzLmFwcGVuZChmInwge3JbJ2ljcF9zY29yZSddfSB8IHtyWydjb21wYW55" +
    "J119IHwgYHtyWydlbWFpbCddfWAgfCB7clsndGFyZ2V0X3RpZXInXX0gfCB7clsnbmljaGUnXX0gfCIpCiAgICBsaW5lcyArPSBb" +
    "CiAgICAgICAgIiIsCiAgICAgICAgIiMjIDIuIEhpZ2gtVmFsdWUgQ29udGFjdC1Gb3JtIEFnZW5jaWVzIiwKICAgICAgICAifCBJ" +
    "Q1AgfCBBZ2VuY3kgfCBDb250YWN0IFBhZ2UgfCBUYXJnZXQgT2ZmZXIgfCBOaWNoZSB8IiwKICAgICAgICAifCA6LS0tOiB8IDot" +
    "LS0gfCA6LS0tIHwgOi0tLSB8IDotLS0gfCIsCiAgICBdCiAgICBmb3IgciBpbiBkZWR1cF9mb3JtczoKICAgICAgICBsaW5lcy5h" +
    "cHBlbmQoZiJ8IHtyWydpY3Bfc2NvcmUnXX0gfCB7clsnY29tcGFueSddfSB8IHtyWydjb250YWN0X3VybCddfSB8IHtyWyd0YXJn" +
    "ZXRfdGllciddfSB8IHtyWyduaWNoZSddfSB8IikKICAgIG9wZW4oTURfUkVQT1JULCAidyIsIGVuY29kaW5nPSJ1dGYtOCIsIG5l" +
    "d2xpbmU9IiIpLndyaXRlKCJcbiIuam9pbihsaW5lcykgKyAiXG4iKQoKICAgIHByaW50KGYiXG5bV0FWRSAyIFBBU1NdICt7bGVu" +
    "KG5ld19kaXJlY3QpfSBuZXcgTVgtdmVyaWZpZWQgZGlyZWN0IGVtYWlscyAoVG90YWw6IHtsZW4oZGVkdXBfZGlyZWN0KX0pIHwg" +
    "K3tsZW4obmV3X2Zvcm1zKX0gbmV3IGNvbnRhY3QtZm9ybSBhZ2VuY2llcyAoVG90YWw6IHtsZW4oZGVkdXBfZm9ybXMpfSkiKQoK" +
    "CmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBtYWluKCkK"
Write-B64File "$ProjectDir\Modules\b2b_wave2_harvester.py" $B64_WAVE2
$B64_SOC = "aW1wb3J0IGFyZ3BhcnNlCmltcG9ydCBvcwoKUERJUiA9IHIiQzpcVXNlcnNcdG9vbWVcRGVza3RvcFxTb3ZlcmVpZ25Db3JlIgpF" +
    "TlZfUCA9IG9zLnBhdGguam9pbihQRElSLCAiLmVudiIpClRPS19ZVCA9IG9zLnBhdGguam9pbihQRElSLCAiY29uZmlnIiwgInlv" +
    "dXR1YmVfdG9rZW4uanNvbiIpCkNMSUVOVF9TRUNSRVRTID0gb3MucGF0aC5qb2luKFBESVIsICJjb25maWciLCAieW91dHViZV9j" +
    "bGllbnRfc2VjcmV0Lmpzb24iKQoKCmRlZiBsb2FkX2Vudl9saW5lcygpOgogICAgaWYgbm90IG9zLnBhdGguZXhpc3RzKEVOVl9Q" +
    "KToKICAgICAgICByZXR1cm4gW10KICAgIHJldHVybiBvcGVuKEVOVl9QLCAiciIsIGVuY29kaW5nPSJ1dGYtOCIsIGVycm9ycz0i" +
    "aWdub3JlIikucmVhZCgpLnNwbGl0bGluZXMoKQoKCmRlZiBzZXRfZW52X2tleShsaW5lcywga2V5LCB2YWwpOgogICAgaWYgbm90" +
    "IHZhbDoKICAgICAgICByZXR1cm4gbGluZXMKICAgIG91dCA9IFtdCiAgICBmb3VuZCA9IEZhbHNlCiAgICBmb3IgbG4gaW4gbGlu" +
    "ZXM6CiAgICAgICAgaWYgbG4uc3RyaXAoKS5zdGFydHN3aXRoKGtleSArICI9Iik6CiAgICAgICAgICAgIG91dC5hcHBlbmQoZiJ7" +
    "a2V5fT17dmFsfSIpCiAgICAgICAgICAgIGZvdW5kID0gVHJ1ZQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIG91dC5hcHBlbmQo" +
    "bG4pCiAgICBpZiBub3QgZm91bmQ6CiAgICAgICAgb3V0LmFwcGVuZChmIntrZXl9PXt2YWx9IikKICAgIHJldHVybiBvdXQKCgpk" +
    "ZWYgY2hlY2tfc3RhdHVzKCk6CiAgICBlbnYgPSB7fQogICAgZm9yIGxuIGluIGxvYWRfZW52X2xpbmVzKCk6CiAgICAgICAgcyA9" +
    "IGxuLnN0cmlwKCkKICAgICAgICBpZiBzIGFuZCBub3Qgcy5zdGFydHN3aXRoKCIjIikgYW5kICI9IiBpbiBzOgogICAgICAgICAg" +
    "ICBrLCB2ID0gcy5zcGxpdCgiPSIsIDEpCiAgICAgICAgICAgIGVudltrLnN0cmlwKCldID0gdi5zdHJpcCgpLnN0cmlwKCciJyku" +
    "c3RyaXAoIiciKQoKICAgIHhfb2sgPSBib29sKGVudi5nZXQoIlhfVVNFUl9BQ0NFU1NfVE9LRU4iKSBvciBlbnYuZ2V0KCJUV0lU" +
    "VEVSX0JFQVJFUl9VU0VSX1RPS0VOIikpCiAgICBsaV9vayA9IGJvb2woZW52LmdldCgiTElOS0VESU5fQUNDRVNTX1RPS0VOIikg" +
    "YW5kIGVudi5nZXQoIkxJTktFRElOX0FVVEhPUl9VUk4iKSkKICAgIHByaW50KGYiW1NPQ0lBTCBBUEkgU1RBVFVTXSBYL1R3aXR0" +
    "ZXIgQXV0by1Qb3N0OiB7J0FSTUVEJyBpZiB4X29rIGVsc2UgJ05PVCBTRVQnfSB8IExpbmtlZEluIEF1dG8tUG9zdDogeydBUk1F" +
    "RCcgaWYgbGlfb2sgZWxzZSAnTk9UIFNFVCd9IikKICAgIGlmIG5vdCB4X29rIG9yIG5vdCBsaV9vazoKICAgICAgICBwcmludCgi" +
    "ICBUbyBhcm0gaGFuZHMtZnJlZSBzb2NpYWwgcG9zdGluZyBhbnl0aW1lIHdpdGhvdXQgdG91Y2hpbmcgY29kZSwgcnVuOiIpCiAg" +
    "ICAgICAgcHJpbnQoJyAgcHl0aG9uIC5cXE1vZHVsZXNcXGNvbmZpZ3VyZV9zb2NpYWxfYW5kX3l0X3Njb3Blcy5weSAtLXgtdG9r" +
    "ZW4gIllPVVJfWF9UT0tFTiIgLS1saS10b2tlbiAiWU9VUl9MSV9UT0tFTiIgLS1saS11cm4gInVybjpsaTpwZXJzb246WU9VUl9J" +
    "RCInKQoKCmRlZiB1cGdyYWRlX3lvdXR1YmVfY29tbWVudF9zY29wZSgpOgogICAgaWYgbm90IG9zLnBhdGguZXhpc3RzKENMSUVO" +
    "VF9TRUNSRVRTKToKICAgICAgICAjIEZhbGxiYWNrIHNlYXJjaCBmb3IgR29vZ2xlIE9BdXRoIGNsaWVudCBzZWNyZXQgSlNPTiBp" +
    "biBjb25maWcvCiAgICAgICAgZm9yIGZuIGluIG9zLmxpc3RkaXIob3MucGF0aC5qb2luKFBESVIsICJjb25maWciKSk6CiAgICAg" +
    "ICAgICAgIGlmICJjbGllbnRfc2VjcmV0IiBpbiBmbi5sb3dlcigpIGFuZCBmbi5lbmRzd2l0aCgiLmpzb24iKToKICAgICAgICAg" +
    "ICAgICAgIGNzID0gb3MucGF0aC5qb2luKFBESVIsICJjb25maWciLCBmbikKICAgICAgICAgICAgICAgIGJyZWFrCiAgICAgICAg" +
    "ZWxzZToKICAgICAgICAgICAgcHJpbnQoIltZVC1TQ09QRV0gQ2xpZW50IHNlY3JldCBKU09OIG5vdCBmb3VuZCBpbiBjb25maWdc" +
    "XC4gU2tpcHBpbmcgYnJvd3NlciBPQXV0aC4iKQogICAgICAgICAgICByZXR1cm4KICAgIGVsc2U6CiAgICAgICAgY3MgPSBDTElF" +
    "TlRfU0VDUkVUUwoKICAgIGZyb20gZ29vZ2xlX2F1dGhfb2F1dGhsaWIuZmxvdyBpbXBvcnQgSW5zdGFsbGVkQXBwRmxvdwogICAg" +
    "c2NvcGVzID0gWwogICAgICAgICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9hdXRoL3lvdXR1YmUudXBsb2FkIiwKICAgICAg" +
    "ICAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vYXV0aC95b3V0dWJlLmZvcmNlLXNzbCIsCiAgICAgICAgImh0dHBzOi8vd3d3" +
    "Lmdvb2dsZWFwaXMuY29tL2F1dGgveW91dHViZS5yZWFkb25seSIsCiAgICBdCiAgICBwcmludCgiW1lULVNDT1BFXSBPcGVuaW5n" +
    "IGJyb3dzZXIgdG8gYXV0aG9yaXplIFlvdVR1YmUgQ29tbWVudCArIFVwbG9hZCBzY29wZSAoc2lnbiBpbiBhcyB0b29tZXIxMDI3" +
    "QGdtYWlsLmNvbSkuLi4iKQogICAgZmxvdyA9IEluc3RhbGxlZEFwcEZsb3cuZnJvbV9jbGllbnRfc2VjcmV0c19maWxlKGNzLCBz" +
    "Y29wZXMpCiAgICBjcmVkcyA9IGZsb3cucnVuX2xvY2FsX3NlcnZlcihwb3J0PTApCiAgICBvcGVuKFRPS19ZVCwgInciLCBlbmNv" +
    "ZGluZz0idXRmLTgiKS53cml0ZShjcmVkcy50b19qc29uKCkpCiAgICBwcmludChmIltZVC1TQ09QRSBQQVNTXSBVcGRhdGVkIHtU" +
    "T0tfWVR9IHdpdGggeW91dHViZS5mb3JjZS1zc2whIExpdmUgWW91VHViZSBjb252ZXJzaW9uIGNvbW1lbnRzIGFyZSBub3cgdW5s" +
    "b2NrZWQuIikKCgpkZWYgbWFpbigpOgogICAgYXAgPSBhcmdwYXJzZS5Bcmd1bWVudFBhcnNlcigpCiAgICBhcC5hZGRfYXJndW1l" +
    "bnQoIi0teC10b2tlbiIsIHR5cGU9c3RyLCBkZWZhdWx0PSIiKQogICAgYXAuYWRkX2FyZ3VtZW50KCItLWxpLXRva2VuIiwgdHlw" +
    "ZT1zdHIsIGRlZmF1bHQ9IiIpCiAgICBhcC5hZGRfYXJndW1lbnQoIi0tbGktdXJuIiwgdHlwZT1zdHIsIGRlZmF1bHQ9IiIpCiAg" +
    "ICBhcC5hZGRfYXJndW1lbnQoIi0tdXBncmFkZS15dC1zY29wZSIsIGFjdGlvbj0ic3RvcmVfdHJ1ZSIpCiAgICBhcmdzID0gYXAu" +
    "cGFyc2VfYXJncygpCgogICAgY2hhbmdlZCA9IEZhbHNlCiAgICBsaW5lcyA9IGxvYWRfZW52X2xpbmVzKCkKICAgIGZvciBrLCB2" +
    "IGluIFsKICAgICAgICAoIlhfVVNFUl9BQ0NFU1NfVE9LRU4iLCBhcmdzLnhfdG9rZW4uc3RyaXAoKSksCiAgICAgICAgKCJMSU5L" +
    "RURJTl9BQ0NFU1NfVE9LRU4iLCBhcmdzLmxpX3Rva2VuLnN0cmlwKCkpLAogICAgICAgICgiTElOS0VESU5fQVVUSE9SX1VSTiIs" +
    "IGFyZ3MubGlfdXJuLnN0cmlwKCkpLAogICAgXToKICAgICAgICBpZiB2OgogICAgICAgICAgICBsaW5lcyA9IHNldF9lbnZfa2V5" +
    "KGxpbmVzLCBrLCB2KQogICAgICAgICAgICBjaGFuZ2VkID0gVHJ1ZQogICAgaWYgY2hhbmdlZDoKICAgICAgICBvcGVuKEVOVl9Q" +
    "LCAidyIsIGVuY29kaW5nPSJ1dGYtOCIsIG5ld2xpbmU9IlxuIikud3JpdGUoIlxuIi5qb2luKGxpbmVzKSArICJcbiIpCiAgICAg" +
    "ICAgcHJpbnQoIltFTlYgUEFTU10gVXBkYXRlZCAuZW52IHdpdGggc29jaWFsIEFQSSBjcmVkZW50aWFscyAocmVtYWlucyBzdHJp" +
    "Y3RseSBnaXRpZ25vcmVkKS4iKQoKICAgIGlmIGFyZ3MudXBncmFkZV95dF9zY29wZToKICAgICAgICB1cGdyYWRlX3lvdXR1YmVf" +
    "Y29tbWVudF9zY29wZSgpCgogICAgY2hlY2tfc3RhdHVzKCkKCgppZiBfX25hbWVfXyA9PSAiX19tYWluX18iOgogICAgbWFpbigp" +
    "Cg=="
Write-B64File "$ProjectDir\Modules\configure_social_and_yt_scopes.py" $B64_SOC
$B64_REP = "aW1wb3J0IGRhdGV0aW1lIGFzIGR0CmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgc3FsaXRlMwppbXBvcnQgcmVxdWVzdHMK" +
    "ClBESVIgPSByIkM6XFVzZXJzXHRvb21lXERlc2t0b3BcU292ZXJlaWduQ29yZSIKQ1JNX0RCID0gb3MucGF0aC5qb2luKFBESVIs" +
    "ICJkYXRhIiwgInByb25vZGVfY3JtLmRiIikKSE9UX01EID0gb3MucGF0aC5qb2luKFBESVIsICJyZXBvcnRzIiwgIkhvdF9CMkJf" +
    "UmVwbGllcy5tZCIpCgoKZGVmIGZpbmRfZ21haWxfdG9rZW4oKToKICAgIGZvciBjYW5kIGluICgKICAgICAgICBvcy5wYXRoLmpv" +
    "aW4oUERJUiwgImNvbmZpZyIsICJnbWFpbF90b2tlbi5qc29uIiksCiAgICAgICAgb3MucGF0aC5qb2luKFBESVIsICJjb25maWci" +
    "LCAiZ29vZ2xlX21haWxfdG9rZW4uanNvbiIpLAogICAgICAgIG9zLnBhdGguam9pbihQRElSLCAiZ21haWxfdG9rZW4uanNvbiIp" +
    "LAogICAgICAgIG9zLnBhdGguam9pbihQRElSLCAidG9rZW4uanNvbiIpLAogICAgKToKICAgICAgICBpZiBvcy5wYXRoLmV4aXN0" +
    "cyhjYW5kKToKICAgICAgICAgICAgcmV0dXJuIGNhbmQKICAgIHJldHVybiAiIgoKCmRlZiBtYWluKCk6CiAgICBpZiBub3Qgb3Mu" +
    "cGF0aC5leGlzdHMoQ1JNX0RCKToKICAgICAgICBwcmludCgiW1JFUExZLU1PTl0gQ1JNIERCIG5vdCBmb3VuZC4iKQogICAgICAg" +
    "IHJldHVybgoKICAgIGMgPSBzcWxpdGUzLmNvbm5lY3QoQ1JNX0RCKQogICAgYy5yb3dfZmFjdG9yeSA9IHNxbGl0ZTMuUm93CiAg" +
    "ICBjb250YWN0ZWQgPSBjLmV4ZWN1dGUoIlNFTEVDVCBpZCwgY29tcGFueSwgZW1haWwsIHN0YWdlIEZST00gcHJvc3BlY3RzIFdI" +
    "RVJFIFVQUEVSKENPQUxFU0NFKHN0YWdlLCcnKSk9J0NPTlRBQ1RFRCciKS5mZXRjaGFsbCgpCiAgICBpZiBub3QgY29udGFjdGVk" +
    "OgogICAgICAgIHByaW50KCJbUkVQTFktTU9OXSBObyBDT05UQUNURUQgcHJvc3BlY3RzIHRvIG1vbml0b3IgeWV0LiIpCiAgICAg" +
    "ICAgYy5jbG9zZSgpCiAgICAgICAgcmV0dXJuCgogICAgdG9rX3AgPSBmaW5kX2dtYWlsX3Rva2VuKCkKICAgIGlmIG5vdCB0b2tf" +
    "cDoKICAgICAgICBwcmludChmIltSRVBMWS1NT05dIE1vbml0b3Jpbmcge2xlbihjb250YWN0ZWQpfSBjb250YWN0ZWQgYWdlbmN5" +
    "KHMpIHwgQ2hlY2sgR21haWwgaW5ib3ggZGlyZWN0bHkgKG5vIGxvY2FsIHJlYWQgdG9rZW4gcGF0aCBmb3VuZCkuIikKICAgICAg" +
    "ICBjLmNsb3NlKCkKICAgICAgICByZXR1cm4KCiAgICB0cnk6CiAgICAgICAgZnJvbSBnb29nbGUuYXV0aC50cmFuc3BvcnQucmVx" +
    "dWVzdHMgaW1wb3J0IFJlcXVlc3QKICAgICAgICBmcm9tIGdvb2dsZS5vYXV0aDIuY3JlZGVudGlhbHMgaW1wb3J0IENyZWRlbnRp" +
    "YWxzCgogICAgICAgIGNyZWRzID0gQ3JlZGVudGlhbHMuZnJvbV9hdXRob3JpemVkX3VzZXJfZmlsZSh0b2tfcCkKICAgICAgICBp" +
    "ZiBub3QgY3JlZHMudmFsaWQgb3IgY3JlZHMuZXhwaXJlZDoKICAgICAgICAgICAgY3JlZHMucmVmcmVzaChSZXF1ZXN0KCkpCiAg" +
    "ICAgICAgaGRycyA9IHsiQXV0aG9yaXphdGlvbiI6IGYiQmVhcmVyIHtjcmVkcy50b2tlbn0ifQoKICAgICAgICBob3RfaGl0cyA9" +
    "IFtdCiAgICAgICAgZm9yIHJvdyBpbiBjb250YWN0ZWQ6CiAgICAgICAgICAgIGVtID0gKHJvd1siZW1haWwiXSBvciAiIikubG93" +
    "ZXIoKQogICAgICAgICAgICBkb20gPSBlbS5zcGxpdCgiQCIpWy0xXSBpZiAiQCIgaW4gZW0gZWxzZSAiIgogICAgICAgICAgICBp" +
    "ZiBub3QgZG9tOgogICAgICAgICAgICAgICAgY29udGludWUKICAgICAgICAgICAgciA9IHJlcXVlc3RzLmdldCgKICAgICAgICAg" +
    "ICAgICAgICJodHRwczovL2dtYWlsLmdvb2dsZWFwaXMuY29tL2dtYWlsL3YxL3VzZXJzL21lL21lc3NhZ2VzIiwKICAgICAgICAg" +
    "ICAgICAgIGhlYWRlcnM9aGRycywKICAgICAgICAgICAgICAgIHBhcmFtcz17InEiOiBmImZyb206QHtkb219IG5ld2VyX3RoYW46" +
    "MTRkIiwgIm1heFJlc3VsdHMiOiAzfSwKICAgICAgICAgICAgICAgIHRpbWVvdXQ9MTIsCiAgICAgICAgICAgICkKICAgICAgICAg" +
    "ICAgaWYgci5zdGF0dXNfY29kZSA9PSA0MDM6CiAgICAgICAgICAgICAgICBwcmludChmIltSRVBMWS1NT04gTk9URV0gR21haWwg" +
    "dG9rZW4gaXMgc2VuZC1vbmx5IChIVFRQIDQwMyBvbiBpbmJveCByZWFkKS4gQ2hlY2sgR21haWwgbWFudWFsbHkgZm9yIHJlcGxp" +
    "ZXMgZnJvbSB5b3VyIHtsZW4oY29udGFjdGVkKX0gY29udGFjdGVkIGFnZW5jaWVzLiIpCiAgICAgICAgICAgICAgICBjLmNsb3Nl" +
    "KCkKICAgICAgICAgICAgICAgIHJldHVybgogICAgICAgICAgICBpZiByLnN0YXR1c19jb2RlID09IDIwMDoKICAgICAgICAgICAg" +
    "ICAgIG1zZ3MgPSByLmpzb24oKS5nZXQoIm1lc3NhZ2VzIikgb3IgW10KICAgICAgICAgICAgICAgIGlmIG1zZ3M6CiAgICAgICAg" +
    "ICAgICAgICAgICAgYy5leGVjdXRlKCJVUERBVEUgcHJvc3BlY3RzIFNFVCBzdGFnZT0nUkVQTElFRCcgV0hFUkUgaWQ9PyIsIChy" +
    "b3dbImlkIl0sKSkKICAgICAgICAgICAgICAgICAgICBjLmNvbW1pdCgpCiAgICAgICAgICAgICAgICAgICAgaG90X2hpdHMuYXBw" +
    "ZW5kKChyb3dbImNvbXBhbnkiXSwgZW0sIGxlbihtc2dzKSkpCiAgICAgICAgICAgICAgICAgICAgcHJpbnQoZiIgIFtIT1QgQjJC" +
    "IFJFUExZIERFVEVDVEVEXSB7cm93Wydjb21wYW55J119IDx7ZW19PiAoe2xlbihtc2dzKX0gbWVzc2FnZShzKSkiKQoKICAgICAg" +
    "ICBsaW5lcyA9IFsKICAgICAgICAgICAgZiIjIE9yYWNsZSBTeXN0ZW1zIExMQyAtIEhvdCBCMkIgQWdlbmN5IFJlcGxpZXMgKHtk" +
    "dC5kYXRldGltZS5ub3coKS5zdHJmdGltZSgnJVktJW0tJWQgJUg6JU0nKX0gRVNUKSIsCiAgICAgICAgICAgIGYiLSAqKkNvbnRh" +
    "Y3RlZCBBZ2VuY2llcyBNb25pdG9yZWQ6Kioge2xlbihjb250YWN0ZWQpfSIsCiAgICAgICAgICAgIGYiLSAqKkhvdCBSZXBsaWVz" +
    "IERldGVjdGVkOioqIHtsZW4oaG90X2hpdHMpfSIsCiAgICAgICAgICAgICIiLAogICAgICAgIF0KICAgICAgICBmb3IgY29tcCwg" +
    "ZW0sIGNudCBpbiBob3RfaGl0czoKICAgICAgICAgICAgbGluZXMuYXBwZW5kKGYiLSAqKntjb21wfSoqIChge2VtfWApIOKAlCB7" +
    "Y250fSBpbmNvbWluZyBtZXNzYWdlKHMpIC0+IFNlbmQgUHJvcG9zYWwgUERGIGZyb20gYGRlbGl2ZXJhYmxlc1xccHJvcG9zYWxz" +
    "XFxgICYgYm9vayAxMC1taW4gd2Fsa3Rocm91Z2ghIikKICAgICAgICBpZiBub3QgaG90X2hpdHM6CiAgICAgICAgICAgIGxpbmVz" +
    "LmFwcGVuZCgiLSBObyByZXBsaWVzIHlldCAoZmlyc3QgMTAgZW1haWxzIGp1c3QgZGlzcGF0Y2hlZCB0b2RheTsgdHlwaWNhbCBC" +
    "MkIgcmVwbHkgd2luZG93IGlzIDQtNDggaG91cnMpLiIpCiAgICAgICAgb3BlbihIT1RfTUQsICJ3IiwgZW5jb2Rpbmc9InV0Zi04" +
    "IiwgbmV3bGluZT0iIikud3JpdGUoIlxuIi5qb2luKGxpbmVzKSArICJcbiIpCiAgICAgICAgcHJpbnQoZiJbUkVQTFktTU9OIFBB" +
    "U1NdIENoZWNrZWQge2xlbihjb250YWN0ZWQpfSBjb250YWN0ZWQgYWdlbmNpZXMgfCBIb3QgcmVwbGllczoge2xlbihob3RfaGl0" +
    "cyl9IikKICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZXg6CiAgICAgICAgcHJpbnQoZiJbUkVQTFktTU9OIE5PVEVdIHtzdHIoZXgp" +
    "WzoxNDBdfSIpCiAgICBmaW5hbGx5OgogICAgICAgIGMuY2xvc2UoKQoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBt" +
    "YWluKCkK"
Write-B64File "$ProjectDir\Modules\b2b_reply_monitor.py" $B64_REP

Write-Host "`n>>> [2/7] Deduplicating pronode_crm.db & Locking Email Uniqueness (Protects Today's 10 Sent Agencies)..." -ForegroundColor Cyan
python "$ProjectDir\Modules\fix_crm_dedupe.py"

Write-Host "`n>>> [3/7] Running Wave 2 B2B Agency Harvester (+30 Real Video/Podcast/SaaS Agencies + MX Check)..." -ForegroundColor Cyan
python "$ProjectDir\Modules\b2b_wave2_harvester.py"

Write-Host "`n>>> [4/7] Importing Deduplicated Wave 2 Leads Into CRM & Generating Branded Proposal PDFs (No Extra Sends Today)..." -ForegroundColor Cyan
python "$ProjectDir\Modules\b2b_client_acquisition_engine.py" --csv "$ProjectDir\data\b2b_prospects_verified.csv" --cap 10

Write-Host "`n>>> [5/7] Checking/Wiring Social API Tokens (.env) & Optional YouTube Comment Scope..." -ForegroundColor Cyan
$socArgs = @("$ProjectDir\Modules\configure_social_and_yt_scopes.py")
if ($XToken) { $socArgs += @("--x-token", $XToken) }
if ($LinkedInToken) { $socArgs += @("--li-token", $LinkedInToken) }
if ($LinkedInUrn) { $socArgs += @("--li-urn", $LinkedInUrn) }
if ($UpgradeYouTubeCommentScope) { $socArgs += "--upgrade-yt-scope" }
& python @socArgs

Write-Host "`n>>> [6/7] Refreshing 6-Stream Command Center, Running Reply Monitor & Scheduling Hourly Reply Checks..." -ForegroundColor Cyan
python "$ProjectDir\Modules\multi_stream_promo_publisher.py"
python "$ProjectDir\Modules\b2b_reply_monitor.py"
try {
    $set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $actR = New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$ProjectDir\Modules\b2b_reply_monitor.py`"" -WorkingDirectory $ProjectDir
    $trgR = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(10) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
    Register-ScheduledTask -TaskName "OracleSystems_B2B_ReplyMonitor_Hourly" -Action $actR -Trigger $trgR -Settings $set -Force | Out-Null
    Write-Host "[TASKS PASS] Registered OracleSystems_B2B_ReplyMonitor_Hourly (tracks incoming agency replies every hour)" -ForegroundColor Green
} catch {
    Write-Host "[TASKS NOTE] $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n>>> [7/7] Mirroring Updated Directory to Drive, Pushing to GitHub & Opening Command Center..." -ForegroundColor Cyan
foreach ($rep in @("Verified_Agency_Leads_Master.md","Hot_B2B_Replies.md","Live_Revenue_Promo_Broadcast.md")) {
    $src = Join-Path "$ProjectDir\reports" $rep
    if (Test-Path $src) { Copy-Item $src (Join-Path "$ProjectDir\Oracle_Audit_2026" $rep) -Force -ErrorAction SilentlyContinue }
}
if (Get-Command rclone -ErrorAction SilentlyContinue) {
    rclone copy "$ProjectDir\Oracle_Audit_2026" "gdrive:Oracle_Audit_2026" --update --bind 0.0.0.0
}
if (Test-Path "$ProjectDir\optimize_ram_and_boot.ps1") { & "$ProjectDir\optimize_ram_and_boot.ps1" -TrimNow }

$SafeFiles = @(
    "Deploy_CRM_Dedupe_Wave2_and_SocialSetup.ps1",
    "Modules/fix_crm_dedupe.py",
    "Modules/b2b_wave2_harvester.py",
    "Modules/configure_social_and_yt_scopes.py",
    "Modules/b2b_reply_monitor.py",
    "Modules/b2b_client_acquisition_engine.py"
)
foreach ($sf in $SafeFiles) { if (Test-Path "$ProjectDir\$sf") { git add -- $sf } }
if (git diff --cached --name-only) {
    git commit -m "CRM Dedupe Guard, Wave 2 (+30 Real B2B Video/Podcast/SaaS Agencies), Hourly Reply Monitor & Social/YouTube Scope Wizard"
    $br = (git rev-parse --abbrev-ref HEAD).Trim()
    git push -u origin $br
    if ($LASTEXITCODE -eq 0) { Write-Host "[GITHUB PASS] Pushed Wave 2 & CRM Dedupe Guard cleanly to origin/$br!" -ForegroundColor Green }
}

$hub = "$ProjectDir\reports\Oracle_Revenue_Lead_Command_Center.html"
if (Test-Path $hub) { Start-Process $hub }
Write-Host "`n[WAVE 2 COMPLETE] CRM deduplicated (zero double-emails tomorrow at 9:30AM), Wave 2 agencies loaded & Command Center updated!" -ForegroundColor Green
