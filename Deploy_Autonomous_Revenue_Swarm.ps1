# ==============================================================================
# ORACLE SYSTEMS LLC // AUTONOMOUS REVENUE SWARM & 24/7/365 CLOUD PACKAGER
# Pure PowerShell 5.1 ASCII | Zero here-strings | Guarded Self-Healing & UCB1
# ==============================================================================
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

foreach ($v in @("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")) {
    [Environment]::SetEnvironmentVariable($v, "1", "Process")
    [Environment]::SetEnvironmentVariable($v, "1", "User")
}
$env:RCLONE_BIND = "0.0.0.0"

foreach ($d in @("$ProjectDir\Modules","$ProjectDir\data","$ProjectDir\reports","$ProjectDir\deliverables\promo_campaigns","$ProjectDir\deploy_bundle","$ProjectDir\logs")) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}

function Write-B64File([string]$Path, [string]$B64) {
    $bytes = [System.Convert]::FromBase64String($B64)
    [System.IO.File]::WriteAllBytes($Path, $bytes)
    Write-Host "  [WROTE] $Path ($($bytes.Length) bytes)" -ForegroundColor DarkCyan
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // AUTONOMOUS REVENUE SWARM & 24/7 CLOUD SUITE" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

if (Test-Path "$ProjectDir\optimize_ram_and_boot.ps1") { & "$ProjectDir\optimize_ram_and_boot.ps1" -TrimNow }

Write-Host "`n>>> [1/6] Installing 4 Base64-verified Swarm, Learning & 24/7 Cloud Modules..." -ForegroundColor Cyan

$B64_LEARN = "aW1wb3J0IG9zCm9zLmVudmlyb25bIk9QRU5CTEFTX05VTV9USFJFQURTIl0gPSAiMSIKb3MuZW52aXJvblsiT01QX05VTV9USFJF" +
    "QURTIl0gPSAiMSIKCmltcG9ydCBkYXRldGltZSBhcyBkdAppbXBvcnQganNvbgppbXBvcnQgbWF0aAppbXBvcnQgc3FsaXRlMwpp" +
    "bXBvcnQgdXJsbGliLnJlcXVlc3QKClBESVIgPSByIkM6XFVzZXJzXHRvb21lXERlc2t0b3BcU292ZXJlaWduQ29yZSIKREFUQV9E" +
    "SVIgPSBvcy5wYXRoLmpvaW4oUERJUiwgImRhdGEiKQpSRVBPUlRTX0RJUiA9IG9zLnBhdGguam9pbihQRElSLCAicmVwb3J0cyIp" +
    "ClBST01PX0RJUiA9IG9zLnBhdGguam9pbihQRElSLCAiZGVsaXZlcmFibGVzIiwgInByb21vX2NhbXBhaWducyIpCmZvciBfZCBp" +
    "biAoREFUQV9ESVIsIFJFUE9SVFNfRElSLCBQUk9NT19ESVIpOgogICAgb3MubWFrZWRpcnMoX2QsIGV4aXN0X29rPVRydWUpCgpX" +
    "RUlHSFRTX1BBVEggPSBvcy5wYXRoLmpvaW4oREFUQV9ESVIsICJiYW5kaXRfc3RyYXRlZ3lfd2VpZ2h0cy5qc29uIikKClRJRVJT" +
    "ID0gewogICAgImFzc2V0cGFjazE1IjogeyJwcmljZSI6IDE1LjAsICJsYWJlbCI6ICIkMTUgNEQvNUQgQ3JlYXRvciBBc3NldCBQ" +
    "YWNrIiwgInBhdGgiOiAiL2dvL2Fzc2V0cGFjazE1In0sCiAgICAidmF1bHRzdWIxNSI6IHsicHJpY2UiOiAxNS4wLCAibGFiZWwi" +
    "OiAiJDE1L21vIFNvdmVyZWlnbiA1RCBWYXVsdCIsICJwYXRoIjogIi9nby92YXVsdHN1YjE1In0sCiAgICAidGllcjI5IjogeyJw" +
    "cmljZSI6IDI5LjAsICJsYWJlbCI6ICIkMjkgNUQgQXV0b21hdGlvbiBCbHVlcHJpbnQiLCAicGF0aCI6ICIvZ28vdGllcjI5In0s" +
    "CiAgICAiYXVyYXZpZGVvNDkiOiB7InByaWNlIjogNDkuMCwgImxhYmVsIjogIiQ0OSBDdXN0b20gNUQgQXVyYSBSZWFkaW5nIiwg" +
    "InBhdGgiOiAiL2dvL2F1cmF2aWRlbzQ5In0sCiAgICAiZnVsbHN0b3JlZnJvbnQiOiB7InByaWNlIjogMTUwMC4wLCAibGFiZWwi" +
    "OiAiJDEsNTAwIFR1cm5rZXkgNEQvNUQgQ3JlYXRvciBTdGFjayIsICJwYXRoIjogIi9nby9mdWxsc3RvcmVmcm9udCJ9LAogICAg" +
    "InByb19ub2RlIjogeyJwcmljZSI6IDQ5OTk5LjAsICJsYWJlbCI6ICIkNDksOTk5IEVudGVycHJpc2UgRGVkaWNhdGVkIFByb19O" +
    "b2RlIiwgInBhdGgiOiAiL2dvL3Byb19ub2RlIn0sCn0KCkhPT0tfQU5HTEVTID0gWwogICAgIlBST09GX0RFTU8iLCAgICAgICMg" +
    "TGl2ZSA0RCBUZXNzZXJhY3QgKyA1RCBNb2JpdXMgdmlzdWFsIGRlbW9uc3RyYXRpb24KICAgICJST0lfU1BFRUQiLCAgICAgICAj" +
    "IEVsaW1pbmF0ZSBTYWFTIGxvY2staW4gLyBkZXBsb3kgdHVybmtleSBBSSBtZWRpYSBzdGFjawogICAgIlBFUlNPTkFMX1NISUZU" +
    "IiwgICMgQ3VzdG9tIDVEIHJlYWRpbmcgcmVuZGVyZWQgd2l0aCBsaXN0ZW5lcidzIG5hbWUgJiBmb2N1cwogICAgIkNSRUFUT1Jf" +
    "UEFDSyIsICAgICMgSW5zdGFudCBjb21tZXJjaWFsIDRELzVEIGxvb3BzICsgMksgdGh1bWJuYWlscyBmb3IgT0JTL1lvdVR1YmUK" +
    "XQoKCmRlZiBnZXRfcHViX3VybCgpOgogICAgcCA9IG9zLnBhdGguam9pbihQRElSLCAiY29uZmlnIiwgInB1YmxpY191cmwudHh0" +
    "IikKICAgIGlmIG9zLnBhdGguZXhpc3RzKHApOgogICAgICAgIHUgPSBvcGVuKHAsICJyIiwgZW5jb2Rpbmc9InV0Zi04IikucmVh" +
    "ZCgpLnN0cmlwKCkucnN0cmlwKCIvIikKICAgICAgICBpZiB1LnN0YXJ0c3dpdGgoImh0dHAiKToKICAgICAgICAgICAgcmV0dXJu" +
    "IHUKICAgIHJldHVybiAiaHR0cHM6Ly9vcmFjbGVzeXN0ZW1zbGxjLmNvbSIKCgpkZWYgcmVhZF9saXZlX3RlbGVtZXRyeSgpOgog" +
    "ICAgY2xpY2tzX2J5X3RpZXIgPSB7azogMCBmb3IgayBpbiBUSUVSU30KICAgIHRvdGFsX2NsaWNrcyA9IDAKICAgIHVkYiA9IG9z" +
    "LnBhdGguam9pbihEQVRBX0RJUiwgInV0bV9hbmFseXRpY3MuZGIiKQogICAgaWYgb3MucGF0aC5leGlzdHModWRiKToKICAgICAg" +
    "ICB0cnk6CiAgICAgICAgICAgIGMgPSBzcWxpdGUzLmNvbm5lY3QodWRiKQogICAgICAgICAgICBmb3IgdGssIGNudCBpbiBjLmV4" +
    "ZWN1dGUoIlNFTEVDVCB0aWVyLCBDT1VOVCgqKSBGUk9NIHV0bV9jbGlja3MgR1JPVVAgQlkgdGllciIpLmZldGNoYWxsKCk6CiAg" +
    "ICAgICAgICAgICAgICBpZiB0ayBpbiBjbGlja3NfYnlfdGllcjoKICAgICAgICAgICAgICAgICAgICBjbGlja3NfYnlfdGllclt0" +
    "a10gPSBpbnQoY250KQogICAgICAgICAgICAgICAgdG90YWxfY2xpY2tzICs9IGludChjbnQpCiAgICAgICAgICAgIGMuY2xvc2Uo" +
    "KQogICAgICAgIGV4Y2VwdCBFeGNlcHRpb246CiAgICAgICAgICAgIHBhc3MKCiAgICB5dF92aWV3cyA9IDAKICAgIHlwID0gb3Mu" +
    "cGF0aC5qb2luKERBVEFfRElSLCAieW91dHViZV9hbmFseXRpY3MuanNvbiIpCiAgICBpZiBvcy5wYXRoLmV4aXN0cyh5cCk6CiAg" +
    "ICAgICAgdHJ5OgogICAgICAgICAgICB5dF92aWV3cyA9IGludCgoanNvbi5sb2FkKG9wZW4oeXAsICJyIiwgZW5jb2Rpbmc9InV0" +
    "Zi04IikpLmdldCgidG90YWxzIikgb3Ige30pLmdldCgidmlld3MiLCAwKSkKICAgICAgICBleGNlcHQgRXhjZXB0aW9uOgogICAg" +
    "ICAgICAgICBwYXNzCgogICAgc3RyaXBlX25ldCA9IDAuMAogICAgc3AgPSBvcy5wYXRoLmpvaW4oUERJUiwgImF1ZGl0X2luYm94" +
    "IiwgInN0cmlwZV9saXZlX2FwaV9zbmFwc2hvdC5qc29uIikKICAgIGlmIG9zLnBhdGguZXhpc3RzKHNwKToKICAgICAgICB0cnk6" +
    "CiAgICAgICAgICAgIHN0cmlwZV9uZXQgPSBmbG9hdChqc29uLmxvYWQob3BlbihzcCwgInIiLCBlbmNvZGluZz0idXRmLTgiKSku" +
    "Z2V0KCJjaGFyZ2VzX25ldF91c2QiLCAwLjApKQogICAgICAgIGV4Y2VwdCBFeGNlcHRpb246CiAgICAgICAgICAgIHBhc3MKCiAg" +
    "ICByZXR1cm4gewogICAgICAgICJjbGlja3NfYnlfdGllciI6IGNsaWNrc19ieV90aWVyLAogICAgICAgICJ0b3RhbF9jbGlja3Mi" +
    "OiB0b3RhbF9jbGlja3MsCiAgICAgICAgInl0X3ZpZXdzIjogeXRfdmlld3MsCiAgICAgICAgInN0cmlwZV9uZXRfdXNkIjogc3Ry" +
    "aXBlX25ldCwKICAgIH0KCgpkZWYgY29tcHV0ZV91Y2IxX3dlaWdodHModGVsZW0pOgogICAgIiIiVXBwZXIgQ29uZmlkZW5jZSBC" +
    "b3VuZCAoVUNCMSkgYmFuZGl0IHRoYXQgYmFsYW5jZXMgcHJvdmVuIGNsaWNrL3JldmVudWUgd2lubmVycyB3aXRoIGV4cGxvcmF0" +
    "aW9uLiIiIgogICAgcHJldiA9IGpzb24ubG9hZChvcGVuKFdFSUdIVFNfUEFUSCwgInIiLCBlbmNvZGluZz0idXRmLTgiKSkgaWYg" +
    "b3MucGF0aC5leGlzdHMoV0VJR0hUU19QQVRIKSBlbHNlIHsiY3ljbGVzIjogMCwgImhpc3RvcnkiOiBbXX0KICAgIGN5Y2xlcyA9" +
    "IGludChwcmV2LmdldCgiY3ljbGVzIiwgMCkpICsgMQogICAgdG90YWxfYyA9IG1heCgxLCB0ZWxlbVsidG90YWxfY2xpY2tzIl0p" +
    "CgogICAgc2NvcmVzID0ge30KICAgIGZvciB0aywgbWV0YSBpbiBUSUVSUy5pdGVtcygpOgogICAgICAgIG5faSA9IHRlbGVtWyJj" +
    "bGlja3NfYnlfdGllciJdLmdldCh0aywgMCkKICAgICAgICAjIEV4cGVjdGVkIHZhbHVlIHNpZ25hbDogY2xpY2sgc2hhcmUgd2Vp" +
    "Z2h0ZWQgYnkgbG9nKHByaWNlKSBzbyBoaWdoLXRpY2tldCBCMkIgKyBoaWdoLXZvbHVtZSBjb25zdW1lciBib3RoIGNvbXBldGUK" +
    "ICAgICAgICBjbGlja19yYXRlID0gbl9pIC8gZmxvYXQodG90YWxfYykKICAgICAgICBldl93ZWlnaHQgPSBjbGlja19yYXRlICog" +
    "bWF0aC5sb2cxMChtYXgoMTAuMCwgbWV0YVsicHJpY2UiXSkpCiAgICAgICAgZXhwbG9yZSA9IG1hdGguc3FydCgyLjAgKiBtYXRo" +
    "LmxvZyh0b3RhbF9jICsgY3ljbGVzICsgMS4wKSAvIGZsb2F0KG5faSArIDEuMCkpCiAgICAgICAgc2NvcmVzW3RrXSA9IHJvdW5k" +
    "KGV2X3dlaWdodCArIDAuMzUgKiBleHBsb3JlLCA0KQoKICAgIHJhbmtlZCA9IHNvcnRlZChzY29yZXMuaXRlbXMoKSwga2V5PWxh" +
    "bWJkYSB4OiB4WzFdLCByZXZlcnNlPVRydWUpCiAgICB0b3BfY29uc3VtZXIgPSBtYXgoWyJhc3NldHBhY2sxNSIsICJ2YXVsdHN1" +
    "YjE1IiwgImF1cmF2aWRlbzQ5IiwgInRpZXIyOSJdLCBrZXk9bGFtYmRhIGs6IHNjb3Jlc1trXSkKICAgIHRvcF9iMmIgPSBtYXgo" +
    "WyJmdWxsc3RvcmVmcm9udCIsICJwcm9fbm9kZSJdLCBrZXk9bGFtYmRhIGs6IHNjb3Jlc1trXSkKICAgIHdpbm5pbmdfYW5nbGUg" +
    "PSBIT09LX0FOR0xFU1soY3ljbGVzIC0gMSkgJSBsZW4oSE9PS19BTkdMRVMpXQoKICAgIHN0YXRlID0gewogICAgICAgICJ1cGRh" +
    "dGVkX3V0YyI6IGR0LmRhdGV0aW1lLnV0Y25vdygpLmlzb2Zvcm1hdCgpICsgIloiLAogICAgICAgICJjeWNsZXMiOiBjeWNsZXMs" +
    "CiAgICAgICAgInRlbGVtZXRyeV9zbmFwc2hvdCI6IHRlbGVtLAogICAgICAgICJ1Y2IxX3Njb3JlcyI6IHNjb3JlcywKICAgICAg" +
    "ICAicmFua2VkX3RpZXJzIjogW2sgZm9yIGssIF8gaW4gcmFua2VkXSwKICAgICAgICAicHJpb3JpdHlfY29uc3VtZXJfdGllciI6" +
    "IHRvcF9jb25zdW1lciwKICAgICAgICAicHJpb3JpdHlfYjJiX3RpZXIiOiB0b3BfYjJiLAogICAgICAgICJhY3RpdmVfaG9va19h" +
    "bmdsZSI6IHdpbm5pbmdfYW5nbGUsCiAgICAgICAgImhpc3RvcnkiOiAocHJldi5nZXQoImhpc3RvcnkiKSBvciBbXSlbLTI5Ol0g" +
    "KyBbewogICAgICAgICAgICAidHMiOiBkdC5kYXRldGltZS51dGNub3coKS5pc29mb3JtYXQoKSArICJaIiwKICAgICAgICAgICAg" +
    "InRvdGFsX2NsaWNrcyI6IHRlbGVtWyJ0b3RhbF9jbGlja3MiXSwKICAgICAgICAgICAgInl0X3ZpZXdzIjogdGVsZW1bInl0X3Zp" +
    "ZXdzIl0sCiAgICAgICAgICAgICJzdHJpcGVfbmV0X3VzZCI6IHRlbGVtWyJzdHJpcGVfbmV0X3VzZCJdLAogICAgICAgICAgICAi" +
    "dG9wX2NvbnN1bWVyIjogdG9wX2NvbnN1bWVyLAogICAgICAgICAgICAidG9wX2IyYiI6IHRvcF9iMmIsCiAgICAgICAgfV0sCiAg" +
    "ICB9CiAgICBqc29uLmR1bXAoc3RhdGUsIG9wZW4oV0VJR0hUU19QQVRILCAidyIsIGVuY29kaW5nPSJ1dGYtOCIpLCBpbmRlbnQ9" +
    "MikKICAgIHJldHVybiBzdGF0ZQoKCmRlZiB0cnlfb2xsYW1hX3JlZmluZShwcm9tcHQsIGZhbGxiYWNrX3RleHQpOgogICAgdHJ5" +
    "OgogICAgICAgIHdpdGggdXJsbGliLnJlcXVlc3QudXJsb3BlbigiaHR0cDovLzEyNy4wLjAuMToxMTQzNC9hcGkvdGFncyIsIHRp" +
    "bWVvdXQ9MikgYXMgcjoKICAgICAgICAgICAgbW9kZWxzID0gW20uZ2V0KCJuYW1lIiwgIiIpIGZvciBtIGluIGpzb24ubG9hZHMo" +
    "ci5yZWFkKCkuZGVjb2RlKCJ1dGYtOCIpKS5nZXQoIm1vZGVscyIsIFtdKV0KICAgICAgICB1c2FibGUgPSBbbSBmb3IgbSBpbiBt" +
    "b2RlbHMgaWYgbm90IGFueShiIGluIG0ubG93ZXIoKSBmb3IgYiBpbiAoIjowLjViIiwgIjoxYiIsICI6MS41YiIsICJ0aW55bGxh" +
    "bWEiKSldCiAgICAgICAgaWYgdXNhYmxlOgogICAgICAgICAgICBwYXlsb2FkID0ganNvbi5kdW1wcyh7CiAgICAgICAgICAgICAg" +
    "ICAibW9kZWwiOiB1c2FibGVbMF0sICJwcm9tcHQiOiBwcm9tcHQsICJzdHJlYW0iOiBGYWxzZSwKICAgICAgICAgICAgICAgICJv" +
    "cHRpb25zIjogeyJ0ZW1wZXJhdHVyZSI6IDAuNywgInJlcGVhdF9wZW5hbHR5IjogMS4yNSwgIm51bV9wcmVkaWN0IjogMjQwfSwK" +
    "ICAgICAgICAgICAgfSkuZW5jb2RlKCJ1dGYtOCIpCiAgICAgICAgICAgIHJlcSA9IHVybGxpYi5yZXF1ZXN0LlJlcXVlc3QoImh0" +
    "dHA6Ly8xMjcuMC4wLjE6MTE0MzQvYXBpL2dlbmVyYXRlIiwgZGF0YT1wYXlsb2FkLCBoZWFkZXJzPXsiQ29udGVudC1UeXBlIjog" +
    "ImFwcGxpY2F0aW9uL2pzb24ifSwgbWV0aG9kPSJQT1NUIikKICAgICAgICAgICAgd2l0aCB1cmxsaWIucmVxdWVzdC51cmxvcGVu" +
    "KHJlcSwgdGltZW91dD00NSkgYXMgcmVzcDoKICAgICAgICAgICAgICAgIHR4dCA9IGpzb24ubG9hZHMocmVzcC5yZWFkKCkuZGVj" +
    "b2RlKCJ1dGYtOCIpKS5nZXQoInJlc3BvbnNlIiwgIiIpLnN0cmlwKCkKICAgICAgICAgICAgICAgIGlmIGxlbih0eHQpID4gODAg" +
    "YW5kICJodHRwIiBpbiB0eHQ6CiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHR4dAogICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAg" +
    "ICAgICBwYXNzCiAgICByZXR1cm4gZmFsbGJhY2tfdGV4dAoKCmRlZiBidWlsZF9wcm9tb19jYW1wYWlnbihzdGF0ZSk6CiAgICBw" +
    "dWIgPSBnZXRfcHViX3VybCgpCiAgICB0b2RheSA9IGR0LmRhdGUudG9kYXkoKS5zdHJmdGltZSgiJVklbSVkIikKICAgIGNfa2V5" +
    "ID0gc3RhdGVbInByaW9yaXR5X2NvbnN1bWVyX3RpZXIiXQogICAgYl9rZXkgPSBzdGF0ZVsicHJpb3JpdHlfYjJiX3RpZXIiXQog" +
    "ICAgY19tZXRhID0gVElFUlNbY19rZXldCiAgICBiX21ldGEgPSBUSUVSU1tiX2tleV0KICAgIGFuZ2xlID0gc3RhdGVbImFjdGl2" +
    "ZV9ob29rX2FuZ2xlIl0KCiAgICBjX3VybCA9IGYie3B1Yn17Y19tZXRhWydwYXRoJ119P3V0bV9zb3VyY2U9c3dhcm1fdjImdXRt" +
    "X21lZGl1bT1wcm9tbyZ1dG1fY2FtcGFpZ249Y3ljbGV7c3RhdGVbJ2N5Y2xlcyddfV97YW5nbGV9IgogICAgYl91cmwgPSBmIntw" +
    "dWJ9e2JfbWV0YVsncGF0aCddfT91dG1fc291cmNlPXN3YXJtX2IyYiZ1dG1fbWVkaXVtPW91dHJlYWNoJnV0bV9jYW1wYWlnbj1j" +
    "eWNsZXtzdGF0ZVsnY3ljbGVzJ119X3thbmdsZX0iCiAgICBzdG9yZV91cmwgPSBmIntwdWJ9L3N0b3JlP3V0bV9zb3VyY2U9c3dh" +
    "cm1fdjImdXRtX21lZGl1bT1iaW8mdXRtX2NhbXBhaWduPWN5Y2xle3N0YXRlWydjeWNsZXMnXX0iCgogICAgeF9wb3N0ID0gKAog" +
    "ICAgICAgIGYiQnVpbHQgYSBsaXZlIDREIFRlc3NlcmFjdCArIDVEIE1vYml1cyBXZWJHTCBwb3J0YWwgcnVubmluZyByZWFsLXRp" +
    "bWUgR0xTTCBzaGFkZXJzLCAiCiAgICAgICAgZiIxMDgwcC8zMGZwcyBhdXRvbm9tb3VzIHZpZGVvIHJlbmRlcmluZyAmIFN0cmlw" +
    "ZSBpbnN0YW50IGZ1bGZpbGxtZW50IG9uIGxvY2FsICsgY2xvdWQgaW5mcmFzdHJ1Y3R1cmUuXG5cbiIKICAgICAgICBmIlRyeSB0" +
    "aGUgbGl2ZSA0RC81RCBzdGFnZToge3N0b3JlX3VybH1cbiIKICAgICAgICBmIkdyYWIgdGhlIHtjX21ldGFbJ2xhYmVsJ119OiB7" +
    "Y191cmx9XG4iCiAgICAgICAgZiIjNERUZXNzZXJhY3QgIzVETW9iaXVzICNBSUF1dG9tYXRpb24gI0NyZWF0b3JFY29ub215Igog" +
    "ICAgKQoKICAgIGxpbmtlZGluX3Bvc3QgPSAoCiAgICAgICAgZiJNb3N0IG1lZGlhIGFnZW5jaWVzIGJ1cm4gJDMsMDAwLSQxMCww" +
    "MDAvbW9udGggb24gZnJhZ21lbnRlZCBTYWFTIHNlYXRzIGZvciB2aWRlbyByZW5kZXJpbmcsIENSTSBmb2xsb3ctdXBzLCAiCiAg" +
    "ICAgICAgZiJsYW5kaW5nIHBhZ2VzLCBhbmQgcHVibGlzaGluZyBhdXRvbWF0aW9uLlxuXG4iCiAgICAgICAgZiJPcmFjbGUgU3lz" +
    "dGVtcyBMTEMgYnVpbGRzIHR1cm5rZXkgcHJpdmF0ZSBBSSAmIDRELzVEIG1lZGlhIHN0YWNrcyB5b3Ugb3duIG91dHJpZ2h0Olxu" +
    "IgogICAgICAgIGYiLSBMaXZlIGludGVyYWN0aXZlIFdlYkdMIDRELzVEIHN0b3JlZnJvbnQgKyBTdHJpcGUgd2ViaG9vayBmdWxm" +
    "aWxsbWVudFxuIgogICAgICAgIGYiLSBBdXRvbWF0ZWQgMTA4MHAvMzBmcHMgdmlkZW8gJiBZb3VUdWJlIEFQSSB2MyBwdWJsaXNo" +
    "aW5nIHBpcGVsaW5lXG4iCiAgICAgICAgZiItIFByaXZhdGUgbG9jYWwgTExNICsgR21haWwgQVBJIG91dHJlYWNoICYgYW5hbHl0" +
    "aWNzIHRlbGVtZXRyeVxuXG4iCiAgICAgICAgZiJMaXZlIGRlbW86IHtzdG9yZV91cmx9XG4iCiAgICAgICAgZiJEZXBsb3ltZW50" +
    "IG9wdGlvbnMgKHtiX21ldGFbJ2xhYmVsJ119KToge2JfdXJsfVxuIgogICAgICAgIGYiI0FnZW5jeUF1dG9tYXRpb24gI1ByaXZh" +
    "dGVBSSAjTWFyVGVjaCAjRGlnaXRhbE1lZGlhIgogICAgKQoKICAgIHRpa3Rva19zY3JpcHQgPSAoCiAgICAgICAgZiJbMC0zcyBI" +
    "T09LXSBTdG9wIHNjcm9sbGluZyAtIHdhdGNoIHRoaXMgbGl2ZSA0RCBUZXNzZXJhY3Qgcm90YXRlIHRocm91Z2ggYSA1RCBNb2Jp" +
    "dXMgc3RyaXAgaW4gcmVhbCB0aW1lLlxuIgogICAgICAgIGYiWzMtMTJzIFZBTFVFXSBFdmVyeSBjYXJkIGluIG91ciAxMC1jYXJk" +
    "IHJheS10cmFjZWQgb2JzaWRpYW4gZGVjayB1bmxvY2tzIGEgc3R1ZGlvIHJlYWRpbmcgd2l0aCB3YXJtIG5ldXJhbCB2b2ljZSBh" +
    "bmQgNDMySHogYW1iaWVuY2UuXG4iCiAgICAgICAgZiJbMTItMjBzIENUQV0gQ29tbWVudCAnNUQnIHRvIGNsYWltIHRoaXMgc2hp" +
    "ZnQsIHRoZW4gdGFwIHRoZSBiaW8gbGluayBmb3IgdGhlIGxpdmUgaW50ZXJhY3RpdmUgcG9ydGFsICh7c3RvcmVfdXJsfSkgb3Ig" +
    "Y2xhaW0geW91ciB7Y19tZXRhWydsYWJlbCddfSAoe2NfdXJsfSkuIgogICAgKQoKICAgIGIyYl9jb2xkX2VtYWlsID0gKAogICAg" +
    "ICAgIGYiU3ViamVjdDogQ3V0IGFnZW5jeSBtZWRpYSAmIEFJIFNhYVMgb3ZlcmhlYWQgd2l0aCBhIHByaXZhdGUgNEQvNUQgYXV0" +
    "b21hdGlvbiBzdGFja1xuXG4iCiAgICAgICAgZiJIaSB7e0ZpcnN0TmFtZX19LFxuXG4iCiAgICAgICAgZiJJIG5vdGljZWQge3tD" +
    "b21wYW55fX0gcHJvZHVjZXMgaGlnaC12b2x1bWUgZGlnaXRhbCBtZWRpYSBhbmQgY2xpZW50IGNhbXBhaWducy4gV2UgYnVpbHQg" +
    "YSBwcml2YXRlIHR1cm5rZXkgc3RhY2sgYXQgT3JhY2xlIFN5c3RlbXMgTExDICIKICAgICAgICBmInRoYXQgYXV0b21hdGVzIDEw" +
    "ODBwLzMwZnBzIG1vdGlvbiB2aWRlbyByZW5kZXJpbmcsIGludGVyYWN0aXZlIFdlYkdMIHN0b3JlZnJvbnRzLCBZb3VUdWJlIHB1" +
    "Ymxpc2hpbmcsIGFuZCBTdHJpcGUgZnVsZmlsbG1lbnQgd2l0aCB6ZXJvIG1vbnRobHkgcGVyLXNlYXQgU2FhUyBsb2NrLWluLlxu" +
    "XG4iCiAgICAgICAgZiJZb3UgY2FuIHRlc3Qgb3VyIGxpdmUgNEQgVGVzc2VyYWN0ICYgNUQgTW9iaXVzIGludGVyYWN0aXZlIHBv" +
    "cnRhbCByaWdodCBub3cgaGVyZTpcbntzdG9yZV91cmx9XG5cbiIKICAgICAgICBmIldlIGRlcGxveSB0aGlzIHR3byB3YXlzIGZv" +
    "ciBwYXJ0bmVyIGFnZW5jaWVzOlxuIgogICAgICAgIGYiMS4gVHVybmtleSBTb2Z0d2FyZSBTdGFjayAoJDEsNTAwIG9uZS10aW1l" +
    "KToge3B1Yn0vZ28vZnVsbHN0b3JlZnJvbnQ/dXRtX3NvdXJjZT1iMmJfZW1haWwmdXRtX2NhbXBhaWduPWN5Y2xle3N0YXRlWydj" +
    "eWNsZXMnXX1cbiIKICAgICAgICBmIjIuIERlZGljYXRlZCBFbnRlcnByaXNlIFByb19Ob2RlIEhhcmR3YXJlICsgRnVsbCBTdGFj" +
    "ayAoJDQ5LDk5OSwgNTAlIG1pbGVzdG9uZSBkZXBvc2l0KToge2JfdXJsfVxuXG4iCiAgICAgICAgZiJPcGVuIHRvIGEgcXVpY2sg" +
    "MTAtbWludXRlIHdhbGt0aHJvdWdoIHRoaXMgd2Vlaz9cblxuIgogICAgICAgIGYiQmVzdCxcblRob21hcyBUb29tZXJcbkZvdW5k" +
    "ZXIsIE9yYWNsZSBTeXN0ZW1zIExMQ1xuUmVwbHkgVU5TVUJTQ1JJQkUgdG8gb3B0IG91dC4iCiAgICApCgogICAgbWQgPSAoCiAg" +
    "ICAgICAgZiIjIE9yYWNsZSBTeXN0ZW1zIExMQyAtIEF1dG9ub21vdXMgU3dhcm0gUHJvbW90aW9uIFBhY2sgKEN5Y2xlICN7c3Rh" +
    "dGVbJ2N5Y2xlcyddfSB8IHt0b2RheX0pXG4iCiAgICAgICAgZiItICoqTGVhcm5pbmcgRW5naW5lIE1vZGU6KiogVUNCMSBDbG9z" +
    "ZWQtTG9vcCBCYW5kaXQgfCAqKkFjdGl2ZSBIb29rIEFuZ2xlOioqIGB7YW5nbGV9YFxuIgogICAgICAgIGYiLSAqKldpbm5pbmcg" +
    "Q29uc3VtZXIgRm9jdXM6KiogYHtjX2tleX1gICh7Y19tZXRhWydsYWJlbCddfSkgfCAqKldpbm5pbmcgQjJCIEZvY3VzOioqIGB7" +
    "Yl9rZXl9YCAoe2JfbWV0YVsnbGFiZWwnXX0pXG4iCiAgICAgICAgZiItICoqTGl2ZSBUZWxlbWV0cnk6Kioge3N0YXRlWyd0ZWxl" +
    "bWV0cnlfc25hcHNob3QnXVsneXRfdmlld3MnXX0gWVQgVmlld3MgfCB7c3RhdGVbJ3RlbGVtZXRyeV9zbmFwc2hvdCddWyd0b3Rh" +
    "bF9jbGlja3MnXX0gVmVyaWZpZWQgL2dvIENsaWNrcyB8ICR7c3RhdGVbJ3RlbGVtZXRyeV9zbmFwc2hvdCddWydzdHJpcGVfbmV0" +
    "X3VzZCddOiwuMmZ9IE5ldCBTdHJpcGVcblxuIgogICAgICAgIGYiIyMgMS4gWCAvIFR3aXR0ZXIgSGlnaC1DVFIgUG9zdFxuYGBg" +
    "XG57eF9wb3N0fVxuYGBgXG5cbiIKICAgICAgICBmIiMjIDIuIExpbmtlZEluIEIyQiBBdXRob3JpdHkgUG9zdCAoSGlnaC1UaWNr" +
    "ZXQgUGlwZWxpbmUpXG5gYGBcbntsaW5rZWRpbl9wb3N0fVxuYGBgXG5cbiIKICAgICAgICBmIiMjIDMuIFRpa1RvayAvIFJlZWxz" +
    "IC8gWW91VHViZSBTaG9ydHMgVm9pY2VvdmVyIFNjcmlwdFxuYGBgXG57dGlrdG9rX3NjcmlwdH1cbmBgYFxuXG4iCiAgICAgICAg" +
    "ZiIjIyA0LiBDb21wbGlhbnQgQjJCIENvbGQgT3V0cmVhY2ggRW1haWwgKCQxLDUwMCAmICQ0OSw5OTkgVGllcnMpXG5gYGBcbnti" +
    "MmJfY29sZF9lbWFpbH1cbmBgYFxuIgogICAgKQogICAgb3V0X21kID0gb3MucGF0aC5qb2luKFBST01PX0RJUiwgZiJTd2FybV9Q" +
    "cm9tb19QYWNrX3t0b2RheX1fQ3tzdGF0ZVsnY3ljbGVzJ119Lm1kIikKICAgIG9wZW4ob3V0X21kLCAidyIsIGVuY29kaW5nPSJ1" +
    "dGYtOCIsIG5ld2xpbmU9IiIpLndyaXRlKG1kKQogICAgb3Blbihvcy5wYXRoLmpvaW4oUkVQT1JUU19ESVIsICJMYXRlc3RfU3dh" +
    "cm1fUHJvbW9fUGFjay5tZCIpLCAidyIsIGVuY29kaW5nPSJ1dGYtOCIsIG5ld2xpbmU9IiIpLndyaXRlKG1kKQogICAgcmV0dXJu" +
    "IG91dF9tZAoKCmRlZiBtYWluKCk6CiAgICB0ZWxlbSA9IHJlYWRfbGl2ZV90ZWxlbWV0cnkoKQogICAgc3RhdGUgPSBjb21wdXRl" +
    "X3VjYjFfd2VpZ2h0cyh0ZWxlbSkKICAgIG91dF9tZCA9IGJ1aWxkX3Byb21vX2NhbXBhaWduKHN0YXRlKQogICAgcHJpbnQoZiJb" +
    "U1dBUk0gTEVBUk4gUEFTU10gQ3ljbGUgI3tzdGF0ZVsnY3ljbGVzJ119IHwgVG9wIENvbnN1bWVyOiB7c3RhdGVbJ3ByaW9yaXR5" +
    "X2NvbnN1bWVyX3RpZXInXX0gfCBUb3AgQjJCOiB7c3RhdGVbJ3ByaW9yaXR5X2IyYl90aWVyJ119IHwgQW5nbGU6IHtzdGF0ZVsn" +
    "YWN0aXZlX2hvb2tfYW5nbGUnXX0iKQogICAgcHJpbnQoZiJbU1dBUk0gUFJPTU8gUEFTU10gR2VuZXJhdGVkIGZyZXNoIG11bHRp" +
    "LWNoYW5uZWwgcHJvbW8gJiBCMkIgb3V0cmVhY2ggcGFjayAtPiB7b3V0X21kfSIpCgoKaWYgX19uYW1lX18gPT0gIl9fbWFpbl9f" +
    "IjoKICAgIG1haW4oKQo="
Write-B64File "$ProjectDir\Modules\autonomous_learning_swarm.py" $B64_LEARN

$B64_REV = "aW1wb3J0IGRhdGV0aW1lIGFzIGR0CmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgc3FsaXRlMwoKUERJUiA9IHIiQzpcVXNl" +
    "cnNcdG9vbWVcRGVza3RvcFxTb3ZlcmVpZ25Db3JlIgpEQVRBX0RJUiA9IG9zLnBhdGguam9pbihQRElSLCAiZGF0YSIpClJFUE9S" +
    "VFNfRElSID0gb3MucGF0aC5qb2luKFBESVIsICJyZXBvcnRzIikKb3MubWFrZWRpcnMoUkVQT1JUU19ESVIsIGV4aXN0X29rPVRy" +
    "dWUpCgoKZGVmIG1haW4oKToKICAgIHRvZGF5ID0gZHQuZGF0ZS50b2RheSgpCiAgICB0YXJnZXRfamFuMSA9IGR0LmRhdGUoMjAy" +
    "NywgMSwgMSkKICAgIHRhcmdldF9qYW4zMSA9IGR0LmRhdGUoMjAyNywgMSwgMzEpCiAgICBkYXlzX3RvX2phbjEgPSBtYXgoMSwg" +
    "KHRhcmdldF9qYW4xIC0gdG9kYXkpLmRheXMpCiAgICBkYXlzX3RvX2phbjMxID0gbWF4KDEsICh0YXJnZXRfamFuMzEgLSB0b2Rh" +
    "eSkuZGF5cykKCiAgICBzbmFwX3AgPSBvcy5wYXRoLmpvaW4oUERJUiwgImF1ZGl0X2luYm94IiwgInN0cmlwZV9saXZlX2FwaV9z" +
    "bmFwc2hvdC5qc29uIikKICAgIHNuYXAgPSBqc29uLmxvYWQob3BlbihzbmFwX3AsICJyIiwgZW5jb2Rpbmc9InV0Zi04IikpIGlm" +
    "IG9zLnBhdGguZXhpc3RzKHNuYXBfcCkgZWxzZSB7fQogICAgZ3Jvc3MgPSBmbG9hdChzbmFwLmdldCgiY2hhcmdlc19ncm9zc191" +
    "c2QiLCA0OS4wMCkpCiAgICBuZXQgPSBmbG9hdChzbmFwLmdldCgiY2hhcmdlc19uZXRfdXNkIiwgNDcuMjgpKQoKICAgIHRvdGFs" +
    "X2NsaWNrcyA9IDAKICAgIHVkYiA9IG9zLnBhdGguam9pbihEQVRBX0RJUiwgInV0bV9hbmFseXRpY3MuZGIiKQogICAgaWYgb3Mu" +
    "cGF0aC5leGlzdHModWRiKToKICAgICAgICB0cnk6CiAgICAgICAgICAgIGMgPSBzcWxpdGUzLmNvbm5lY3QodWRiKQogICAgICAg" +
    "ICAgICB0b3RhbF9jbGlja3MgPSBpbnQoYy5leGVjdXRlKCJTRUxFQ1QgQ09VTlQoKikgRlJPTSB1dG1fY2xpY2tzIikuZmV0Y2hv" +
    "bmUoKVswXSkKICAgICAgICAgICAgYy5jbG9zZSgpCiAgICAgICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAgICAgICAgICAgcGFzcwoK" +
    "ICAgIHByb3NwZWN0cyA9IDAKICAgIGNkYiA9IG9zLnBhdGguam9pbihEQVRBX0RJUiwgInByb25vZGVfY3JtLmRiIikKICAgIGlm" +
    "IG9zLnBhdGguZXhpc3RzKGNkYik6CiAgICAgICAgdHJ5OgogICAgICAgICAgICBjID0gc3FsaXRlMy5jb25uZWN0KGNkYikKICAg" +
    "ICAgICAgICAgcHJvc3BlY3RzID0gaW50KGMuZXhlY3V0ZSgiU0VMRUNUIENPVU5UKCopIEZST00gcHJvc3BlY3RzIikuZmV0Y2hv" +
    "bmUoKVswXSkKICAgICAgICAgICAgYy5jbG9zZSgpCiAgICAgICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAgICAgICAgICAgcGFzcwoK" +
    "ICAgIGdhcCA9IG1heCgwLjAsIDEwMDAwMDAuMCAtIGdyb3NzKQogICAgcmVxX2RhaWx5X2phbjEgPSBnYXAgLyBmbG9hdChkYXlz" +
    "X3RvX2phbjEpCiAgICByZXFfZGFpbHlfamFuMzEgPSBnYXAgLyBmbG9hdChkYXlzX3RvX2phbjMxKQoKICAgICMgQ3JlYXRlIGEg" +
    "cmVhZHktdG8tZmlsbCBDU1YgdGVtcGxhdGUgZm9yIHNjYWxpbmcgcmVhbCBCMkIgYWdlbmN5IGxlYWRzIGNsZWFubHkKICAgIGNz" +
    "dl90cGwgPSBvcy5wYXRoLmpvaW4oUERJUiwgImRhdGEiLCAiYjJiX3Byb3NwZWN0c19pbXBvcnRfdGVtcGxhdGUuY3N2IikKICAg" +
    "IGlmIG5vdCBvcy5wYXRoLmV4aXN0cyhjc3ZfdHBsKToKICAgICAgICBvcGVuKGNzdl90cGwsICJ3IiwgZW5jb2Rpbmc9InV0Zi04" +
    "IiwgbmV3bGluZT0iIikud3JpdGUoCiAgICAgICAgICAgICJjb21wYW55LGNvbnRhY3QsZW1haWwsbm90ZXNcbiIKICAgICAgICAg" +
    "ICAgIkV4YW1wbGUgQ3JlYXRpdmUgU3R1ZGlvLEphbmUgRG9lLGphbmVAZXhhbXBsZS1zdHVkaW8uY29tLE1lZGlhIGFnZW5jeSBw" +
    "cm9kdWNpbmcgZGFpbHkgU2hvcnRzXG4iCiAgICAgICAgKQoKICAgIGxpbmVzID0gWwogICAgICAgIGYiIyBPcmFjbGUgU3lzdGVt" +
    "cyBMTEMgLSBNdWx0aS1TdHJlYW0gUmV2ZW51ZSBWZWxvY2l0eSAmIFRhcmdldCBNYXRoICh7dG9kYXkuaXNvZm9ybWF0KCl9KSIs" +
    "CiAgICAgICAgZiItICoqQ3VycmVudCBWZXJpZmllZCBHcm9zcyBSZXZlbnVlOioqICR7Z3Jvc3M6LC4yZn0gKE5ldDogJHtuZXQ6" +
    "LC4yZn0pIiwKICAgICAgICBmIi0gKipWZXJpZmllZCBDaGVja291dCBDbGlja3M6Kioge3RvdGFsX2NsaWNrc30gfCAqKkFjdGl2" +
    "ZSBCMkIgQ1JNIFByb3NwZWN0czoqKiB7cHJvc3BlY3RzfSIsCiAgICAgICAgZiItICoqUmVtYWluaW5nIEdhcCB0byAkMSwwMDAs" +
    "MDAwOioqICR7Z2FwOiwuMmZ9IiwKICAgICAgICBmIi0gKipSZXF1aXJlZCBEYWlseSBSdW4tUmF0ZToqKiAke3JlcV9kYWlseV9q" +
    "YW4xOiwuMmZ9L2RheSAoYnkgSmFuIDEsIDIwMjcgLSB7ZGF5c190b19qYW4xfSBkYXlzKSB8ICR7cmVxX2RhaWx5X2phbjMxOiwu" +
    "MmZ9L2RheSAoYnkgSmFuIDMxLCAyMDI3IC0ge2RheXNfdG9famFuMzF9IGRheXMpIiwKICAgICAgICAiIiwKICAgICAgICAiIyMg" +
    "VW5pdCBFY29ub21pY3MgQWNyb3NzIFlvdXIgNiBSZXZlbnVlIFN0cmVhbXMgKFdoYXQgJDEsMDAwLDAwMCBSZXF1aXJlcykiLAog" +
    "ICAgICAgICJ8IFRpZXIgfCBQcmljZSB8IFVuaXRzIEFsb25lIGZvciAkMU0gfCBCZXN0IFJvbGUgaW4gU3dhcm0gfCIsCiAgICAg" +
    "ICAgInwgOi0tLSB8IC0tLTogfCAtLS06IHwgOi0tLSB8IiwKICAgICAgICAifCBDcmVhdG9yIEFzc2V0IFBhY2sgfCAkMTUgfCA2" +
    "Niw2NjcgfCBFbnRyeSBpbXB1bHNlIGJ1eSArIGVtYWlsIGxpc3QgYnVpbGRlciB8IiwKICAgICAgICAifCBTb3ZlcmVpZ24gNUQg" +
    "VmF1bHQgfCAkMTUvbW8gfCA2Niw2NjcvbW8gfCBDb21wb3VuZGluZyByZWN1cnJpbmcgYmFzZSB8IiwKICAgICAgICAifCA1RCBB" +
    "dXRvbWF0aW9uIEJsdWVwcmludCB8ICQyOSB8IDM0LDQ4MyB8IE1pZC10aWNrZXQgZGlnaXRhbCB1cHNlbGwgfCIsCiAgICAgICAg" +
    "InwgQ3VzdG9tIDVEIEF1cmEgUmVhZGluZyB8ICQ0OSB8IDIwLDQwOSB8IEhpZ2hlc3QtY29udmVydGluZyBjb25zdW1lciBmbGFn" +
    "c2hpcCB8IiwKICAgICAgICAifCBUdXJua2V5IDRELzVEIENyZWF0b3IgU3RhY2sgfCAkMSw1MDAgfCA2NjcgfCBGYXN0IEIyQiBj" +
    "YXNoZmxvdyBlbmdpbmUgKDEwIGRlYWxzID0gJDE1LDAwMCkgfCIsCiAgICAgICAgInwgRW50ZXJwcmlzZSBEZWRpY2F0ZWQgUHJv" +
    "X05vZGUgfCAkNDksOTk5IHwgMjAgfCBQcmltYXJ5IGhpZ2gtdGlja2V0IG5lZWRsZS1tb3ZlciB8IiwKICAgICAgICAiIiwKICAg" +
    "ICAgICAiIyMgSGlnaGVzdC1ST0kgSW1tZWRpYXRlIEV4ZWN1dGlvbiBQcmlvcml0aWVzIiwKICAgICAgICAiMS4gKipDbG91ZCBD" +
    "dXRvdmVyICgyNC83LzM2NSBVcHRpbWUpOioqIE1vdmUgdG8gRGlnaXRhbE9jZWFuL09yYWNsZSBDbG91ZCBvbiBOb3YgMjcgKGBS" +
    "dW5fTm92MjdfQ2xvdWRfQ3V0b3Zlci5wczFgKSBzbyB6ZXJvIHNhbGVzIGFyZSBsb3N0IHRvIGxhcHRvcCBzbGVlcCBvciB0dW5u" +
    "ZWwgcm90YXRpb24uIiwKICAgICAgICAiMi4gKipCMkIgUGlwZWxpbmUgU2NhbGU6KiogSW1wb3J0IDI1LTUwIHJlYWwgbWVkaWEv" +
    "bWFya2V0aW5nIGFnZW5jaWVzIGludG8gYGRhdGFcXGIyYl9wcm9zcGVjdHNfaW1wb3J0X3RlbXBsYXRlLmNzdmAgYW5kIHJ1biBj" +
    "b21wbGlhbnQgcGVyc29uYWxpemVkIG91dHJlYWNoICsgYHByb25vZGVfcHJvcG9zYWxfZ2VuLnB5YC4iLAogICAgICAgICIzLiAq" +
    "KkNvbnN1bWVyIENvbnRlbnQgVmVsb2NpdHk6KiogTGV0IGBPcmFjbGVTeXN0ZW1zX1VsdHJhSERfNEQ1RF9WYXVsdEZhY3Rvcnlg" +
    "IHVwZ3JhZGUgYWxsIDEwNCB2aWRlb3MgdG8gMTA4MHAvMzBmcHMgNEQvNUQgYW5kIHB1Ymxpc2ggZGFpbHkgU2hvcnRzICsgd2Vl" +
    "a2x5IGZ1bGwgZXBpc29kZXMgd2l0aCBwaW5uZWQgYC9nby9gIGxpbmtzLiIsCiAgICAgICAgIjQuICoqRGlzdHJpYnV0aW9uIEFQ" +
    "SXM6KiogQWRkIGBYX1VTRVJfQUNDRVNTX1RPS0VOYCAvIGBMSU5LRURJTl9BQ0NFU1NfVE9LRU5gIHRvIGAuZW52YCB0byB0dXJu" +
    "IFBoYXNlIDQ3IG11bHRpLXBsYXRmb3JtIHBvc3RpbmcgZnVsbHkgaGFuZHMtZnJlZS4iLAogICAgXQogICAgb3V0X3AgPSBvcy5w" +
    "YXRoLmpvaW4oUkVQT1JUU19ESVIsICJSZXZlbnVlX1ZlbG9jaXR5X0FjdGlvbl9QbGFuLm1kIikKICAgIG9wZW4ob3V0X3AsICJ3" +
    "IiwgZW5jb2Rpbmc9InV0Zi04IiwgbmV3bGluZT0iIikud3JpdGUoIlxuIi5qb2luKGxpbmVzKSArICJcbiIpCiAgICBwcmludChm" +
    "IltSRVZFTlVFIFZFTE9DSVRZIFBBU1NdIFVwZGF0ZWQge291dF9wfSB8IEdhcDogJHtnYXA6LC4yZn0gfCBEYXlzIHRvIEphbiAx" +
    "OiB7ZGF5c190b19qYW4xfSIpCgoKaWYgX19uYW1lX18gPT0gIl9fbWFpbl9fIjoKICAgIG1haW4oKQo="
Write-B64File "$ProjectDir\Modules\revenue_velocity_engine.py" $B64_REV

$B64_HEAL = "aW1wb3J0IGRhdGV0aW1lIGFzIGR0CmltcG9ydCBnbG9iCmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgcHlfY29tcGlsZQpp" +
    "bXBvcnQgc2h1dGlsCmltcG9ydCBzcWxpdGUzCmltcG9ydCBzdWJwcm9jZXNzCmltcG9ydCBzeXMKaW1wb3J0IHRpbWUKaW1wb3J0" +
    "IHVybGxpYi5yZXF1ZXN0CgpQRElSID0gciJDOlxVc2Vyc1x0b29tZVxEZXNrdG9wXFNvdmVyZWlnbkNvcmUiCkxPR19QID0gb3Mu" +
    "cGF0aC5qb2luKFBESVIsICJsb2dzIiwgInNlbGZfaGVhbGluZ19zdXBlcnZpc29yLmxvZyIpCm9zLm1ha2VkaXJzKG9zLnBhdGgu" +
    "ZGlybmFtZShMT0dfUCksIGV4aXN0X29rPVRydWUpCgoKZGVmIGxvZyhtc2cpOgogICAgbGluZSA9IGYiW3tkdC5kYXRldGltZS5u" +
    "b3coKS5zdHJmdGltZSgnJVktJW0tJWQgJUg6JU06JVMnKX1dIHttc2d9IgogICAgcHJpbnQobGluZSkKICAgIHRyeToKICAgICAg" +
    "ICBvcGVuKExPR19QLCAiYSIsIGVuY29kaW5nPSJ1dGYtOCIpLndyaXRlKGxpbmUgKyAiXG4iKQogICAgZXhjZXB0IEV4Y2VwdGlv" +
    "bjoKICAgICAgICBwYXNzCgoKZGVmIGNoZWNrX3N5bnRheF9hbGwoKToKICAgIGJhZCA9IFtdCiAgICB0YXJnZXRzID0gW29zLnBh" +
    "dGguam9pbihQRElSLCAic292ZXJlaWduX2RhZW1vbi5weSIpXSArIGdsb2IuZ2xvYihvcy5wYXRoLmpvaW4oUERJUiwgIk1vZHVs" +
    "ZXMiLCAiKi5weSIpKQogICAgZm9yIGZwIGluIHRhcmdldHM6CiAgICAgICAgdHJ5OgogICAgICAgICAgICBweV9jb21waWxlLmNv" +
    "bXBpbGUoZnAsIGRvcmFpc2U9VHJ1ZSkKICAgICAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGV4OgogICAgICAgICAgICBiYWQuYXBw" +
    "ZW5kKChmcCwgc3RyKGV4KSkpCiAgICByZXR1cm4gYmFkCgoKZGVmIHJvbGxiYWNrX2RhZW1vbl9pZl9uZWVkZWQoKToKICAgIGRw" +
    "ID0gb3MucGF0aC5qb2luKFBESVIsICJzb3ZlcmVpZ25fZGFlbW9uLnB5IikKICAgIHRyeToKICAgICAgICBweV9jb21waWxlLmNv" +
    "bXBpbGUoZHAsIGRvcmFpc2U9VHJ1ZSkKICAgICAgICByZXR1cm4gVHJ1ZQogICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBleDoKICAg" +
    "ICAgICBsb2coZiJbU0VMRi1IRUFMIEFMRVJUXSBzb3ZlcmVpZ25fZGFlbW9uLnB5IGNvbXBpbGUgZXJyb3I6IHtleH0iKQogICAg" +
    "ICAgIGJha3MgPSBzb3J0ZWQoZ2xvYi5nbG9iKG9zLnBhdGguam9pbihQRElSLCAiYmFja3VwcyIsICJkYWVtb25fKi5weS5iYWsi" +
    "KSkpCiAgICAgICAgaWYgYmFrczoKICAgICAgICAgICAgc2h1dGlsLmNvcHkyKGJha3NbLTFdLCBkcCkKICAgICAgICAgICAgbG9n" +
    "KGYiW1NFTEYtSEVBTCBST0xMQkFDS10gUmVzdG9yZWQgbGFzdCBrbm93bi1nb29kIGJhY2t1cCAtPiB7b3MucGF0aC5iYXNlbmFt" +
    "ZShiYWtzWy0xXSl9IikKICAgICAgICAgICAgcmV0dXJuIFRydWUKICAgICAgICByZXR1cm4gRmFsc2UKCgpkZWYgY2hlY2tfaHR0" +
    "cF9oZWFsdGgoKToKICAgIGZvciBwYXRoIGluICgiL3N0b3JlIiwgIi9hcGkvZXhlYy10ZWxlbWV0cnkiLCAiL2FwaS9kZWNrLW1h" +
    "bmlmZXN0Iik6CiAgICAgICAgdHJ5OgogICAgICAgICAgICB3aXRoIHVybGxpYi5yZXF1ZXN0LnVybG9wZW4oImh0dHA6Ly8xMjcu" +
    "MC4wLjE6ODAwMCIgKyBwYXRoLCB0aW1lb3V0PTUpIGFzIHI6CiAgICAgICAgICAgICAgICBpZiByLnN0YXR1cyAhPSAyMDA6CiAg" +
    "ICAgICAgICAgICAgICAgICAgcmV0dXJuIEZhbHNlLCBmIntwYXRofSBIVFRQIHtyLnN0YXR1c30iCiAgICAgICAgZXhjZXB0IEV4" +
    "Y2VwdGlvbiBhcyBleDoKICAgICAgICAgICAgcmV0dXJuIEZhbHNlLCBmIntwYXRofSB1bnJlYWNoYWJsZToge2V4fSIKICAgIHJl" +
    "dHVybiBUcnVlLCAiQUxMXzIwMF9PSyIKCgpkZWYgcmVzdGFydF9kYWVtb24oKToKICAgIGRwID0gb3MucGF0aC5qb2luKFBESVIs" +
    "ICJzb3ZlcmVpZ25fZGFlbW9uLnB5IikKICAgIG5zID0gc3VicHJvY2Vzcy5ydW4oWyJuZXRzdGF0IiwgIi1hbm8iXSwgY2FwdHVy" +
    "ZV9vdXRwdXQ9VHJ1ZSwgdGV4dD1UcnVlKS5zdGRvdXQKICAgIHBpZHMgPSB7bG4uc3BsaXQoKVstMV0gZm9yIGxuIGluIG5zLnNw" +
    "bGl0bGluZXMoKSBpZiAiOjgwMDAgIiBpbiBsbiBhbmQgIkxJU1RFTklORyIgaW4gbG4udXBwZXIoKSBhbmQgbG4uc3BsaXQoKVst" +
    "MV0uaXNkaWdpdCgpfQogICAgZm9yIHBpZCBpbiBwaWRzOgogICAgICAgIHN1YnByb2Nlc3MucnVuKFsidGFza2tpbGwiLCAiL0Yi" +
    "LCAiL1BJRCIsIHBpZF0sIGNhcHR1cmVfb3V0cHV0PVRydWUpCiAgICB0aW1lLnNsZWVwKDIpCiAgICBsZiA9IG9wZW4ob3MucGF0" +
    "aC5qb2luKFBESVIsICJsb2dzIiwgImRhZW1vbl9ib290LmxvZyIpLCAidyIsIGVuY29kaW5nPSJ1dGYtOCIpCiAgICBzdWJwcm9j" +
    "ZXNzLlBvcGVuKFtzeXMuZXhlY3V0YWJsZSwgZHBdLCBjd2Q9UERJUiwgc3Rkb3V0PWxmLCBzdGRlcnI9bGYsIGNyZWF0aW9uZmxh" +
    "Z3M9MHgwODAwMDAwMCkKICAgIHRpbWUuc2xlZXAoMykKCgpkZWYgY2hlY2tfc3FsaXRlX2RicygpOgogICAgZGJzID0gZ2xvYi5n" +
    "bG9iKG9zLnBhdGguam9pbihQRElSLCAiZGF0YSIsICIqLmRiIikpCiAgICBvaywgZmFpbCA9IDAsIFtdCiAgICBmb3IgZGJwIGlu" +
    "IGRiczoKICAgICAgICB0cnk6CiAgICAgICAgICAgIGMgPSBzcWxpdGUzLmNvbm5lY3QoZGJwKQogICAgICAgICAgICByZXMgPSBj" +
    "LmV4ZWN1dGUoIlBSQUdNQSBpbnRlZ3JpdHlfY2hlY2siKS5mZXRjaG9uZSgpWzBdCiAgICAgICAgICAgIGMuY2xvc2UoKQogICAg" +
    "ICAgICAgICBpZiBzdHIocmVzKS5sb3dlcigpID09ICJvayI6CiAgICAgICAgICAgICAgICBvayArPSAxCiAgICAgICAgICAgIGVs" +
    "c2U6CiAgICAgICAgICAgICAgICBmYWlsLmFwcGVuZChvcy5wYXRoLmJhc2VuYW1lKGRicCkpCiAgICAgICAgZXhjZXB0IEV4Y2Vw" +
    "dGlvbjoKICAgICAgICAgICAgZmFpbC5hcHBlbmQob3MucGF0aC5iYXNlbmFtZShkYnApKQogICAgcmV0dXJuIG9rLCBsZW4oZGJz" +
    "KSwgZmFpbAoKCmRlZiBtYWluKCk6CiAgICByb2xsYmFja19kYWVtb25faWZfbmVlZGVkKCkKICAgIGJhZF9weSA9IGNoZWNrX3N5" +
    "bnRheF9hbGwoKQogICAgaWYgYmFkX3B5OgogICAgICAgIGxvZyhmIltTWU5UQVggV0FSTl0ge2xlbihiYWRfcHkpfSBtb2R1bGUo" +
    "cykgZmFpbGVkIGNvbXBpbGU6IHtbb3MucGF0aC5iYXNlbmFtZSh4WzBdKSBmb3IgeCBpbiBiYWRfcHldfSIpCiAgICBlbHNlOgog" +
    "ICAgICAgIGxvZygiW1NZTlRBWCBQQVNTXSBzb3ZlcmVpZ25fZGFlbW9uLnB5ICsgYWxsIE1vZHVsZXMvKi5weSBjb21waWxlZCBj" +
    "bGVhbmx5LiIpCgogICAgb2tfaHR0cCwgZGV0YWlsID0gY2hlY2tfaHR0cF9oZWFsdGgoKQogICAgaWYgbm90IG9rX2h0dHA6CiAg" +
    "ICAgICAgbG9nKGYiW1NFTEYtSEVBTCBBQ1RJT05dIExvY2FsIHNlcnZlciB1bmhlYWx0aHkgKHtkZXRhaWx9KSAtPiByZXN0YXJ0" +
    "aW5nIFBvcnQgODAwMC4uLiIpCiAgICAgICAgcmVzdGFydF9kYWVtb24oKQogICAgICAgIG9rX2h0dHAsIGRldGFpbCA9IGNoZWNr" +
    "X2h0dHBfaGVhbHRoKCkKICAgICAgICBsb2coZiJbU0VMRi1IRUFMIFBPU1QtUkVTVEFSVF0gSGVhbHRoOiB7b2tfaHR0cH0gKHtk" +
    "ZXRhaWx9KSIpCiAgICBlbHNlOgogICAgICAgIGxvZyhmIltIVFRQIFBBU1NdIFBvcnQgODAwMCBsaXZlIGVuZHBvaW50cyB2ZXJp" +
    "ZmllZCAoe2RldGFpbH0pIikKCiAgICBva19kYiwgdG90X2RiLCBmYWlsX2RiID0gY2hlY2tfc3FsaXRlX2RicygpCiAgICBsb2co" +
    "ZiJbU1FMSVRFIFBBU1NdIHtva19kYn0ve3RvdF9kYn0gZGF0YWJhc2VzIGhlYWx0aHkiICsgKGYiIHwgRmFpbGVkOiB7ZmFpbF9k" +
    "Yn0iIGlmIGZhaWxfZGIgZWxzZSAiIikpCgoKaWYgX19uYW1lX18gPT0gIl9fbWFpbl9fIjoKICAgIG1haW4oKQo="
Write-B64File "$ProjectDir\Modules\self_healing_supervisor.py" $B64_HEAL

$B64_CLOUD = "aW1wb3J0IG9zCgpQRElSID0gciJDOlxVc2Vyc1x0b29tZVxEZXNrdG9wXFNvdmVyZWlnbkNvcmUiCkJVTkRMRSA9IG9zLnBhdGgu" +
    "am9pbihQRElSLCAiZGVwbG95X2J1bmRsZSIpCm9zLm1ha2VkaXJzKEJVTkRMRSwgZXhpc3Rfb2s9VHJ1ZSkKCkNMT1VEX1dBVENI" +
    "RE9HX1NIID0gIiIiIyEvdXNyL2Jpbi9lbnYgYmFzaApzZXQgLWV1byBwaXBlZmFpbApBUFBfRElSPSIvb3B0L1NvdmVyZWlnbkNv" +
    "cmUiCmNkICIkQVBQX0RJUiIKCiMgMS4gVmVyaWZ5IEhUVFAgMjAwIG9uIGxvY2FsIEd1bmljb3JuOyBhdXRvLXJlc3RhcnQgc3lz" +
    "dGVtZCB1bml0IGlmIHVuaGVhbHRoeQppZiAhIGN1cmwgLWZzUyAtLW1heC10aW1lIDYgaHR0cDovLzEyNy4wLjAuMTo4MDAwL2Fw" +
    "aS9leGVjLXRlbGVtZXRyeSA+L2Rldi9udWxsOyB0aGVuCiAgZWNobyAiWyQoZGF0ZSAtdSldIFtTRUxGLUhFQUxdIFJlc3RhcnRp" +
    "bmcgc292ZXJlaWduY29yZS5zZXJ2aWNlLi4uIgogIHN5c3RlbWN0bCByZXN0YXJ0IHNvdmVyZWlnbmNvcmUuc2VydmljZQogIHNs" +
    "ZWVwIDMKZmkKCiMgMi4gUnVuIGNsb3NlZC1sb29wIGxlYXJuaW5nICYgcmV2ZW51ZSB2ZWxvY2l0eSBlbmdpbmVzCi52ZW52L2Jp" +
    "bi9weXRob24gTW9kdWxlcy9hdXRvbm9tb3VzX2xlYXJuaW5nX3N3YXJtLnB5IHx8IHRydWUKLnZlbnYvYmluL3B5dGhvbiBNb2R1" +
    "bGVzL3JldmVudWVfdmVsb2NpdHlfZW5naW5lLnB5IHx8IHRydWUKLnZlbnYvYmluL3B5dGhvbiBNb2R1bGVzL211bHRpcGxhdGZv" +
    "cm1fcHVibGlzaGVyLnB5IHx8IHRydWUKIiIiCgpHVUFSREVEX0FVVE9ERVBMT1lfU0ggPSAiIiIjIS91c3IvYmluL2VudiBiYXNo" +
    "CnNldCAtZXVvIHBpcGVmYWlsCkFQUF9ESVI9Ii9vcHQvU292ZXJlaWduQ29yZSIKY2QgIiRBUFBfRElSIgoKIyBTYWZlLCB0ZXN0" +
    "LWdhdGVkIGF1dG8tdXBkYXRlIGZyb20gR2l0SHViIG1haW4gd2l0aCBhdXRvbWF0aWMgcm9sbGJhY2sgb24gZmFpbHVyZQpQUkVW" +
    "X1NIQT0kKGdpdCByZXYtcGFyc2UgSEVBRCkKZ2l0IGZldGNoIG9yaWdpbiBtYWluIC0tcXVpZXQKUkVNT1RFX1NIQT0kKGdpdCBy" +
    "ZXYtcGFyc2Ugb3JpZ2luL21haW4pCmlmIFsgIiRQUkVWX1NIQSIgPSAiJFJFTU9URV9TSEEiIF07IHRoZW4KICBleGl0IDAKZmkK" +
    "CmdpdCBwdWxsIC0tZmYtb25seSBvcmlnaW4gbWFpbgppZiAudmVudi9iaW4vcHl0aG9uIC1tIHB5X2NvbXBpbGUgc292ZXJlaWdu" +
    "X2RhZW1vbi5weSBNb2R1bGVzLyoucHk7IHRoZW4KICBzeXN0ZW1jdGwgcmVzdGFydCBzb3ZlcmVpZ25jb3JlLnNlcnZpY2UKICBz" +
    "bGVlcCAzCiAgaWYgY3VybCAtZnNTIC0tbWF4LXRpbWUgNiBodHRwOi8vMTI3LjAuMC4xOjgwMDAvYXBpL2V4ZWMtdGVsZW1ldHJ5" +
    "ID4vZGV2L251bGw7IHRoZW4KICAgIGVjaG8gIlskKGRhdGUgLXUpXSBbQVVUTy1ERVBMT1kgUEFTU10gUHJvbW90ZWQgJFJFTU9U" +
    "RV9TSEEgY2xlYW5seS4iCiAgICBleGl0IDAKICBmaQpmaQoKZWNobyAiWyQoZGF0ZSAtdSldIFtBVVRPLVJPTExCQUNLXSBIZWFs" +
    "dGggY2hlY2sgZmFpbGVkOyByZXZlcnRpbmcgdG8gJFBSRVZfU0hBISIKZ2l0IHJlc2V0IC0taGFyZCAiJFBSRVZfU0hBIgpzeXN0" +
    "ZW1jdGwgcmVzdGFydCBzb3ZlcmVpZ25jb3JlLnNlcnZpY2UKIiIiCgpJTlNUQUxMXzI0N19TSCA9ICIiIiMhL3Vzci9iaW4vZW52" +
    "IGJhc2gKc2V0IC1ldW8gcGlwZWZhaWwKQVBQX0RJUj0iL29wdC9Tb3ZlcmVpZ25Db3JlIgpjaG1vZCAreCAiJEFQUF9ESVIvZGVw" +
    "bG95X2J1bmRsZS9jbG91ZF93YXRjaGRvZy5zaCIgIiRBUFBfRElSL2RlcGxveV9idW5kbGUvZ3VhcmRlZF9hdXRvZGVwbG95LnNo" +
    "IgoKY2F0ID4vZXRjL3N5c3RlbWQvc3lzdGVtL29yYWNsZS1zd2FybS13YXRjaGRvZy5zZXJ2aWNlIDw8J0VPRicKW1VuaXRdCkRl" +
    "c2NyaXB0aW9uPU9yYWNsZSBTeXN0ZW1zIDI0LzcgU2VsZi1IZWFsaW5nICYgTGVhcm5pbmcgU3dhcm0gVGljawpBZnRlcj1uZXR3" +
    "b3JrLnRhcmdldCBzb3ZlcmVpZ25jb3JlLnNlcnZpY2UKCltTZXJ2aWNlXQpUeXBlPW9uZXNob3QKV29ya2luZ0RpcmVjdG9yeT0v" +
    "b3B0L1NvdmVyZWlnbkNvcmUKRXhlY1N0YXJ0PS9vcHQvU292ZXJlaWduQ29yZS9kZXBsb3lfYnVuZGxlL2Nsb3VkX3dhdGNoZG9n" +
    "LnNoCkVPRgoKY2F0ID4vZXRjL3N5c3RlbWQvc3lzdGVtL29yYWNsZS1zd2FybS13YXRjaGRvZy50aW1lciA8PCdFT0YnCltVbml0" +
    "XQpEZXNjcmlwdGlvbj1SdW4gT3JhY2xlIFN5c3RlbXMgU3dhcm0gV2F0Y2hkb2cgZXZlcnkgMTUgbWludXRlcyAoMjQvNy8zNjUp" +
    "CgpbVGltZXJdCk9uQm9vdFNlYz0ybWluCk9uVW5pdEFjdGl2ZVNlYz0xNW1pbgpVbml0PW9yYWNsZS1zd2FybS13YXRjaGRvZy5z" +
    "ZXJ2aWNlCgpbSW5zdGFsbF0KV2FudGVkQnk9dGltZXJzLnRhcmdldApFT0YKCmNhdCA+L2V0Yy9zeXN0ZW1kL3N5c3RlbS9vcmFj" +
    "bGUtZ3VhcmRlZC1hdXRvZGVwbG95LnNlcnZpY2UgPDwnRU9GJwpbVW5pdF0KRGVzY3JpcHRpb249T3JhY2xlIFN5c3RlbXMgR3Vh" +
    "cmRlZCBHaXRIdWIgQXV0by1EZXBsb3kgKHdpdGggQXV0by1Sb2xsYmFjaykKQWZ0ZXI9bmV0d29yay1vbmxpbmUudGFyZ2V0Cgpb" +
    "U2VydmljZV0KVHlwZT1vbmVzaG90CldvcmtpbmdEaXJlY3Rvcnk9L29wdC9Tb3ZlcmVpZ25Db3JlCkV4ZWNTdGFydD0vb3B0L1Nv" +
    "dmVyZWlnbkNvcmUvZGVwbG95X2J1bmRsZS9ndWFyZGVkX2F1dG9kZXBsb3kuc2gKRU9GCgpjYXQgPi9ldGMvc3lzdGVtZC9zeXN0" +
    "ZW0vb3JhY2xlLWd1YXJkZWQtYXV0b2RlcGxveS50aW1lciA8PCdFT0YnCltVbml0XQpEZXNjcmlwdGlvbj1DaGVjayBHaXRIdWIg" +
    "bWFpbiBmb3IgdmVyaWZpZWQgdXBkYXRlcyBldmVyeSAzMCBtaW51dGVzCgpbVGltZXJdCk9uQm9vdFNlYz01bWluCk9uVW5pdEFj" +
    "dGl2ZVNlYz0zMG1pbgpVbml0PW9yYWNsZS1ndWFyZGVkLWF1dG9kZXBsb3kuc2VydmljZQoKW0luc3RhbGxdCldhbnRlZEJ5PXRp" +
    "bWVycy50YXJnZXQKRU9GCgpzeXN0ZW1jdGwgZGFlbW9uLXJlbG9hZApzeXN0ZW1jdGwgZW5hYmxlIC0tbm93IG9yYWNsZS1zd2Fy" +
    "bS13YXRjaGRvZy50aW1lciBvcmFjbGUtZ3VhcmRlZC1hdXRvZGVwbG95LnRpbWVyCmVjaG8gIlsyNC83LzM2NSBDTE9VRCBTV0FS" +
    "TSBBQ1RJVkVdIEluZGVwZW5kZW50IG9mIGxhcHRvcCBwb3dlciBvciBoYXJkd2FyZSEiCiIiIgoKb3Blbihvcy5wYXRoLmpvaW4o" +
    "QlVORExFLCAiY2xvdWRfd2F0Y2hkb2cuc2giKSwgInciLCBlbmNvZGluZz0idXRmLTgiLCBuZXdsaW5lPSJcbiIpLndyaXRlKENM" +
    "T1VEX1dBVENIRE9HX1NIKQpvcGVuKG9zLnBhdGguam9pbihCVU5ETEUsICJndWFyZGVkX2F1dG9kZXBsb3kuc2giKSwgInciLCBl" +
    "bmNvZGluZz0idXRmLTgiLCBuZXdsaW5lPSJcbiIpLndyaXRlKEdVQVJERURfQVVUT0RFUExPWV9TSCkKb3Blbihvcy5wYXRoLmpv" +
    "aW4oQlVORExFLCAiaW5zdGFsbF8yNDdfY2xvdWRfc3dhcm0uc2giKSwgInciLCBlbmNvZGluZz0idXRmLTgiLCBuZXdsaW5lPSJc" +
    "biIpLndyaXRlKElOU1RBTExfMjQ3X1NIKQpwcmludChmIlsyNC83IENMT1VEIFNXQVJNIFBBQ0tBR0VSIFBBU1NdIFdyb3RlIGNs" +
    "b3VkX3dhdGNoZG9nLnNoLCBndWFyZGVkX2F1dG9kZXBsb3kuc2ggJiBpbnN0YWxsXzI0N19jbG91ZF9zd2FybS5zaCAtPiB7QlVO" +
    "RExFfSIpCg=="
Write-B64File "$ProjectDir\Modules\cloud_247_swarm_packager.py" $B64_CLOUD


Write-Host "`n>>> [2/6] Running Self-Aware Health & Integrity Supervisor..." -ForegroundColor Cyan
python "$ProjectDir\Modules\self_healing_supervisor.py"

Write-Host "`n>>> [3/6] Running UCB1 Closed-Loop Learning Engine & Multi-Channel Promo Generator..." -ForegroundColor Cyan
python "$ProjectDir\Modules\autonomous_learning_swarm.py"
if (Test-Path "$ProjectDir\Modules\multiplatform_publisher.py") { python "$ProjectDir\Modules\multiplatform_publisher.py" }

Write-Host "`n>>> [4/6] Calculating Live Multi-Stream Revenue Velocity & Target Math..." -ForegroundColor Cyan
python "$ProjectDir\Modules\revenue_velocity_engine.py"

Write-Host "`n>>> [5/6] Packaging 24/7/365 Cloud Systemd Swarm & Guarded Auto-Deploy Scripts..." -ForegroundColor Cyan
python "$ProjectDir\Modules\cloud_247_swarm_packager.py"

Write-Host "`n>>> [6/6] Registering Local Continuous Swarm Tasks, Drive Mirror & GitHub Sync..." -ForegroundColor Cyan
try {
    $set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)

    $actHeal = New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$ProjectDir\Modules\self_healing_supervisor.py`"" -WorkingDirectory $ProjectDir
    $trgHeal = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)
    Register-ScheduledTask -TaskName "OracleSystems_SelfHealing_15Min" -Action $actHeal -Trigger $trgHeal -Settings $set -Description "15-minute syntax, HTTP 200, SQLite & auto-rollback supervisor" -Force | Out-Null

    $actLearn = New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$ProjectDir\Modules\autonomous_learning_swarm.py`"" -WorkingDirectory $ProjectDir
    $trgLearn = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Hours 4) -RepetitionDuration (New-TimeSpan -Days 365)
    Register-ScheduledTask -TaskName "OracleSystems_LearningPromoSwarm_4Hr" -Action $actLearn -Trigger $trgLearn -Settings $set -Description "4-hour UCB1 closed-loop learning & promo pack generator" -Force | Out-Null

    Write-Host "[TASKS PASS] Registered OracleSystems_SelfHealing_15Min + OracleSystems_LearningPromoSwarm_4Hr" -ForegroundColor Green
} catch {
    Write-Host "[TASKS NOTE] $($_.Exception.Message)" -ForegroundColor Yellow
}

Copy-Item "$ProjectDir\reports\Latest_Swarm_Promo_Pack.md" "$ProjectDir\Oracle_Audit_2026\Latest_Swarm_Promo_Pack.md" -Force -ErrorAction SilentlyContinue
Copy-Item "$ProjectDir\reports\Revenue_Velocity_Action_Plan.md" "$ProjectDir\Oracle_Audit_2026\Revenue_Velocity_Action_Plan.md" -Force -ErrorAction SilentlyContinue
if (Get-Command rclone -ErrorAction SilentlyContinue) {
    rclone copy "$ProjectDir\Oracle_Audit_2026" "gdrive:Oracle_Audit_2026" --update --bind 0.0.0.0
    if ($LASTEXITCODE -eq 0) { Write-Host "[DRIVE SYNC PASS] Mirrored Swarm Promo Pack & Revenue Plan over IPv4." -ForegroundColor Green }
}

if (Test-Path "$ProjectDir\optimize_ram_and_boot.ps1") { & "$ProjectDir\optimize_ram_and_boot.ps1" -TrimNow }

$SafeFiles = @(
    "Deploy_Autonomous_Revenue_Swarm.ps1",
    "Modules/autonomous_learning_swarm.py","Modules/revenue_velocity_engine.py",
    "Modules/self_healing_supervisor.py","Modules/cloud_247_swarm_packager.py",
    "deploy_bundle/cloud_watchdog.sh","deploy_bundle/guarded_autodeploy.sh","deploy_bundle/install_247_cloud_swarm.sh"
)
foreach ($sf in $SafeFiles) { if (Test-Path "$ProjectDir\$sf") { git add -- $sf } }
if (git diff --cached --name-only) {
    git commit -m "Autonomous Revenue Swarm: UCB1 Closed-Loop Learning, Multi-Channel Promo Generator, Self-Healing Supervisor & 24/7/365 Cloud Systemd Auto-Deploy"
    $br = (git rev-parse --abbrev-ref HEAD).Trim()
    git push -u origin $br
    if ($LASTEXITCODE -eq 0) { Write-Host "[GITHUB PASS] Pushed Autonomous Revenue Swarm cleanly to origin/$br!" -ForegroundColor Green }
}

Write-Host "`n[SWARM DEPLOYED] Inspect reports\Latest_Swarm_Promo_Pack.md and reports\Revenue_Velocity_Action_Plan.md!" -ForegroundColor Green
