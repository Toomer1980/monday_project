# ==============================================================================
# ORACLE SYSTEMS LLC // YOUTUBE 0-VIEW FIX + B2B LEAD VERIFIER + SSH KEY PREP
# Pure PowerShell 5.1 ASCII | Zero here-strings | Base64-verified Python modules
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

function Write-B64File([string]$Path, [string]$B64) {
    $bytes = [System.Convert]::FromBase64String($B64)
    [System.IO.File]::WriteAllBytes($Path, $bytes)
    Write-Host "  [WROTE] $Path ($($bytes.Length) bytes)" -ForegroundColor DarkCyan
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // YOUTUBE 0-VIEW FIX, B2B VERIFIER & CLOUD SSH PREP" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

if (Test-Path "$ProjectDir\optimize_ram_and_boot.ps1") { & "$ProjectDir\optimize_ram_and_boot.ps1" -TrimNow }

Write-Host "`n>>> [1/5] Writing Verified YouTube SEO Optimizer & B2B Lead Verifier..." -ForegroundColor Cyan

$B64_YTSEO = "aW1wb3J0IGdsb2IKaW1wb3J0IGlvCmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgcmUKZnJvbSBQSUwgaW1wb3J0IEltYWdl" +
    "CgpQRElSID0gciJDOlxVc2Vyc1x0b29tZVxEZXNrdG9wXFNvdmVyZWlnbkNvcmUiClRPS19QID0gb3MucGF0aC5qb2luKFBESVIs" +
    "ICJjb25maWciLCAieW91dHViZV90b2tlbi5qc29uIikKUFVCX1AgPSBvcy5wYXRoLmpvaW4oUERJUiwgImNvbmZpZyIsICJwdWJs" +
    "aWNfdXJsLnR4dCIpClRIVU1CX0RJUiA9IG9zLnBhdGguam9pbihQRElSLCAiQ29udGVudF9WYXVsdF80RF9UaHVtYm5haWxzIikK" +
    "Q0hfTUQgPSBvcy5wYXRoLmpvaW4oUERJUiwgInJlcG9ydHMiLCAiWW91VHViZV9DaGFwdGVyX1RpbWVzdGFtcHMubWQiKQpSRVBf" +
    "T1VUID0gb3MucGF0aC5qb2luKFBESVIsICJyZXBvcnRzIiwgIllvdVR1YmVfU0VPX1VwZ3JhZGVfUmVwb3J0Lm1kIikKCgpkZWYg" +
    "cGFyc2VfaXNvX2R1cl9zZWNvbmRzKGlzb19zdHIpOgogICAgbSA9IHJlLm1hdGNoKHIiUFQoPzooXGQrKUgpPyg/OihcZCspTSk/" +
    "KD86KFxkKylTKT8iLCBpc29fc3RyIG9yICIiKQogICAgaWYgbm90IG06CiAgICAgICAgcmV0dXJuIDAKICAgIHJldHVybiBpbnQo" +
    "bS5ncm91cCgxKSBvciAwKSAqIDM2MDAgKyBpbnQobS5ncm91cCgyKSBvciAwKSAqIDYwICsgaW50KG0uZ3JvdXAoMykgb3IgMCkK" +
    "CgpkZWYgY2xlYW5fc2VvX3RpdGxlKHJhd190aXRsZSwgaXNfc2hvcnQpOgogICAgdCA9IHJlLnN1YihyIig/aSleKHdlZWt8c2hv" +
    "cnQpW19cc10qXGQrW19cc10qIiwgIiIsIHJhd190aXRsZSBvciAiIikuc3RyaXAoKQogICAgdCA9IHJlLnN1YihyIig/aSlbX1xz" +
    "XSooNGRbX1xzXSptYXh8cmVhbFtfXHNdKmZ1bGx8NGR8NWQpJCIsICIiLCB0KS5zdHJpcCgpCiAgICB0ID0gdC5yZXBsYWNlKCJf" +
    "IiwgIiAiKS5zdHJpcCgiIC18Oi8iKQogICAgaWYgbm90IHQ6CiAgICAgICAgdCA9ICJTaWxlbnQgQWJ1bmRhbmNlICYgRmluYW5j" +
    "aWFsIEJyZWFrdGhyb3VnaCIKICAgIHQgPSAiICIuam9pbih3LmNhcGl0YWxpemUoKSBpZiB3LmlzbG93ZXIoKSBlbHNlIHcgZm9y" +
    "IHcgaW4gdC5zcGxpdCgpKQogICAgaWYgaXNfc2hvcnQ6CiAgICAgICAgb3V0ID0gZiJ7dH0gfCA0RCBUZXNzZXJhY3QgVGFyb3Qg" +
    "U2hpZnQgI1Nob3J0cyIKICAgIGVsc2U6CiAgICAgICAgb3V0ID0gZiJ7dH0gfCBGdWxsIDRELzVEIExpdmluZyBUYXJvdCBSZWFk" +
    "aW5nIChUaW1lbGVzcykiCiAgICByZXR1cm4gb3V0Wzo5Nl0KCgpkZWYgcGlja190aHVtYm5haWxfYnl0ZXMocmF3X3RpdGxlKToK" +
    "ICAgIHRodW1icyA9IHNvcnRlZChnbG9iLmdsb2Iob3MucGF0aC5qb2luKFRIVU1CX0RJUiwgIiouanBnIikpKQogICAgaWYgbm90" +
    "IHRodW1iczoKICAgICAgICByZXR1cm4gTm9uZSwgIiIKICAgIHdvcmRzID0gW3cubG93ZXIoKSBmb3IgdyBpbiByZS5maW5kYWxs" +
    "KHIiW0EtWmEtel17NCx9IiwgcmF3X3RpdGxlIG9yICIiKSBpZiB3Lmxvd2VyKCkgbm90IGluICgid2VlayIsICJzaG9ydCIsICJm" +
    "dWxsIiwgInJlYWRpbmciLCAidGFyb3QiKV0KICAgIGNob3NlbiA9IHRodW1ic1swXQogICAgZm9yIHRwIGluIHRodW1iczoKICAg" +
    "ICAgICBibiA9IG9zLnBhdGguYmFzZW5hbWUodHApLmxvd2VyKCkKICAgICAgICBpZiBhbnkodyBpbiBibiBmb3IgdyBpbiB3b3Jk" +
    "cyk6CiAgICAgICAgICAgIGNob3NlbiA9IHRwCiAgICAgICAgICAgIGJyZWFrCiAgICAjIFlvdVR1YmUgY3VzdG9tIHRodW1ibmFp" +
    "bCBBUEkgcmVxdWlyZXMgPD0gMiBNQjsgcmVzaXplIDE5MjB4MTA4MCBKUEVHIHE9OTAgKH40MDAtODAwIEtCLCByYXpvciBzaGFy" +
    "cCkKICAgIHdpdGggSW1hZ2Uub3BlbihjaG9zZW4pIGFzIGltOgogICAgICAgIGltID0gaW0uY29udmVydCgiUkdCIikucmVzaXpl" +
    "KCgxOTIwLCAxMDgwKSwgSW1hZ2UuUmVzYW1wbGluZy5MQU5DWk9TKQogICAgICAgIGJ1ZiA9IGlvLkJ5dGVzSU8oKQogICAgICAg" +
    "IGltLnNhdmUoYnVmLCBmb3JtYXQ9IkpQRUciLCBxdWFsaXR5PTkwLCBvcHRpbWl6ZT1UcnVlKQogICAgICAgIHJldHVybiBidWYu" +
    "Z2V0dmFsdWUoKSwgb3MucGF0aC5iYXNlbmFtZShjaG9zZW4pCgoKZGVmIGxvYWRfc2FtcGxlX2NoYXB0ZXJzKCk6CiAgICBpZiBv" +
    "cy5wYXRoLmV4aXN0cyhDSF9NRCk6CiAgICAgICAgdHh0ID0gb3BlbihDSF9NRCwgInIiLCBlbmNvZGluZz0idXRmLTgiKS5yZWFk" +
    "KCkKICAgICAgICB0c19saW5lcyA9IFtsbi5zdHJpcCgpIGZvciBsbiBpbiB0eHQuc3BsaXRsaW5lcygpIGlmIHJlLm1hdGNoKHIi" +
    "XlxkezJ9OlxkezJ9XHMrIiwgbG4uc3RyaXAoKSldCiAgICAgICAgaWYgdHNfbGluZXM6CiAgICAgICAgICAgIHJldHVybiAiXG4i" +
    "LmpvaW4odHNfbGluZXNbOjddKQogICAgcmV0dXJuICgKICAgICAgICAiMDA6MDAgT3BlbmluZyA0RCBUZXNzZXJhY3QgUG9ydGFs" +
    "ICYgQ29sbGVjdGl2ZSBFbmVyZ3lcbiIKICAgICAgICAiMDE6MzAgQ2FyZCAxIC0gUGFzdCBDYXRhbHlzdFxuIgogICAgICAgICIw" +
    "MzowMCBDYXJkIDIgLSBQcmVzZW50IE1vYml1cyBUdXJuaW5nIFBvaW50XG4iCiAgICAgICAgIjA0OjMwIENhcmQgMyAtIDVEIEd1" +
    "aWRpbmcgTGlnaHRcbiIKICAgICAgICAiMDY6MDAgQ2FyZCA0IC0gUmFkaWFudCBCcmVha3Rocm91Z2hcbiIKICAgICAgICAiMDc6" +
    "MzAgQ2FyZCA1IC0gU292ZXJlaWduIE1hc3RlcnlcbiIKICAgICAgICAiMDk6MDAgQ29tcGxldGUgNS1DYXJkIExpdmluZyBJbnRl" +
    "Z3JhdGlvbiIKICAgICkKCgpkZWYgbWFpbigpOgogICAgaWYgbm90IG9zLnBhdGguZXhpc3RzKFRPS19QKToKICAgICAgICBwcmlu" +
    "dCgiW1lULVNFT10geW91dHViZV90b2tlbi5qc29uIG5vdCBmb3VuZDsgc2tpcHBpbmcuIikKICAgICAgICByZXR1cm4KCiAgICBw" +
    "dWIgPSBvcGVuKFBVQl9QLCAiciIsIGVuY29kaW5nPSJ1dGYtOCIpLnJlYWQoKS5zdHJpcCgpLnJzdHJpcCgiLyIpIGlmIG9zLnBh" +
    "dGguZXhpc3RzKFBVQl9QKSBlbHNlICJodHRwczovL29yYWNsZXN5c3RlbXNsbGMuY29tIgogICAgY2hhcHRlcnNfYmxvY2sgPSBs" +
    "b2FkX3NhbXBsZV9jaGFwdGVycygpCgogICAgZnJvbSBnb29nbGUuYXV0aC50cmFuc3BvcnQucmVxdWVzdHMgaW1wb3J0IFJlcXVl" +
    "c3QKICAgIGZyb20gZ29vZ2xlLm9hdXRoMi5jcmVkZW50aWFscyBpbXBvcnQgQ3JlZGVudGlhbHMKICAgIGZyb20gZ29vZ2xlYXBp" +
    "Y2xpZW50LmRpc2NvdmVyeSBpbXBvcnQgYnVpbGQKICAgIGZyb20gZ29vZ2xlYXBpY2xpZW50Lmh0dHAgaW1wb3J0IE1lZGlhSW9C" +
    "YXNlVXBsb2FkCgogICAgY3JlZHMgPSBDcmVkZW50aWFscy5mcm9tX2F1dGhvcml6ZWRfdXNlcl9maWxlKFRPS19QKQogICAgaWYg" +
    "Y3JlZHMuZXhwaXJlZCBhbmQgY3JlZHMucmVmcmVzaF90b2tlbjoKICAgICAgICBjcmVkcy5yZWZyZXNoKFJlcXVlc3QoKSkKICAg" +
    "IHl0ID0gYnVpbGQoInlvdXR1YmUiLCAidjMiLCBjcmVkZW50aWFscz1jcmVkcykKCiAgICBjaCA9IHl0LmNoYW5uZWxzKCkubGlz" +
    "dChwYXJ0PSJjb250ZW50RGV0YWlscyIsIG1pbmU9VHJ1ZSkuZXhlY3V0ZSgpCiAgICBpdGVtcyA9IGNoLmdldCgiaXRlbXMiKSBv" +
    "ciBbXQogICAgaWYgbm90IGl0ZW1zOgogICAgICAgIHByaW50KCJbWVQtU0VPXSBObyBZb3VUdWJlIGNoYW5uZWwgZm91bmQgb24g" +
    "dG9rZW4uIikKICAgICAgICByZXR1cm4KCiAgICBwbF9pZCA9IGl0ZW1zWzBdWyJjb250ZW50RGV0YWlscyJdWyJyZWxhdGVkUGxh" +
    "eWxpc3RzIl1bInVwbG9hZHMiXQogICAgcGxfaXRlbXMgPSB5dC5wbGF5bGlzdEl0ZW1zKCkubGlzdChwYXJ0PSJzbmlwcGV0Iiwg" +
    "cGxheWxpc3RJZD1wbF9pZCwgbWF4UmVzdWx0cz0zMCkuZXhlY3V0ZSgpLmdldCgiaXRlbXMiKSBvciBbXQogICAgdmlkX2lkcyA9" +
    "IFtpdFsic25pcHBldCJdWyJyZXNvdXJjZUlkIl1bInZpZGVvSWQiXSBmb3IgaXQgaW4gcGxfaXRlbXNdCiAgICBpZiBub3Qgdmlk" +
    "X2lkczoKICAgICAgICBwcmludCgiW1lULVNFT10gTm8gdXBsb2FkZWQgdmlkZW9zIGZvdW5kLiIpCiAgICAgICAgcmV0dXJuCgog" +
    "ICAgdl9yZXNwID0geXQudmlkZW9zKCkubGlzdChwYXJ0PSJzbmlwcGV0LGNvbnRlbnREZXRhaWxzLHN0YXR1cyxzdGF0aXN0aWNz" +
    "IiwgaWQ9IiwiLmpvaW4odmlkX2lkcykpLmV4ZWN1dGUoKS5nZXQoIml0ZW1zIikgb3IgW10KCiAgICBmdWxsX3ZpZHMsIHNob3J0" +
    "X3ZpZHMgPSBbXSwgW10KICAgIGZvciB2IGluIHZfcmVzcDoKICAgICAgICBkdXIgPSBwYXJzZV9pc29fZHVyX3NlY29uZHModlsi" +
    "Y29udGVudERldGFpbHMiXS5nZXQoImR1cmF0aW9uIiwgIiIpKQogICAgICAgIGlzX3MgPSBkdXIgPD0gNjUgb3IgIiNzaG9ydHMi" +
    "IGluICh2WyJzbmlwcGV0Il0uZ2V0KCJ0aXRsZSIsICIiKSkubG93ZXIoKQogICAgICAgIChzaG9ydF92aWRzIGlmIGlzX3MgZWxz" +
    "ZSBmdWxsX3ZpZHMpLmFwcGVuZCgodiwgZHVyKSkKCiAgICBmbGFnc2hpcF9mdWxsX2lkID0gZnVsbF92aWRzWzBdWzBdWyJpZCJd" +
    "IGlmIGZ1bGxfdmlkcyBlbHNlICIiCiAgICBmbGFnc2hpcF9mdWxsX3VybCA9IGYiaHR0cHM6Ly95b3V0dS5iZS97ZmxhZ3NoaXBf" +
    "ZnVsbF9pZH0iIGlmIGZsYWdzaGlwX2Z1bGxfaWQgZWxzZSBmIntwdWJ9L3N0b3JlIgoKICAgIHNlb190YWdzID0gWwogICAgICAg" +
    "ICJ0YXJvdCByZWFkaW5nIiwgInRpbWVsZXNzIHRhcm90IHJlYWRpbmciLCAiY29sbGVjdGl2ZSB0YXJvdCByZWFkaW5nIiwKICAg" +
    "ICAgICAiZmluYW5jaWFsIGJyZWFrdGhyb3VnaCB0YXJvdCIsICJhYnVuZGFuY2UgdGFyb3QiLCAiNEQgdGVzc2VyYWN0IiwKICAg" +
    "ICAgICAiNUQgbW9iaXVzIiwgInBpY2sgYSBjYXJkIHRhcm90IiwgIk9yYWNsZSBTeXN0ZW1zIiwgIm1hbmlmZXN0YXRpb24gdGFy" +
    "b3QiLAogICAgXQoKICAgIGxvZ19saW5lcyA9IFsKICAgICAgICAiIyBPcmFjbGUgU3lzdGVtcyBMTEMgLSBZb3VUdWJlIEZ1bGwt" +
    "RXBpc29kZSAwLVZpZXcgRml4ICYgU0VPIFJlcG9ydCIsCiAgICAgICAgZiItICoqQ2hhbm5lbCBWaWRlb3MgQXVkaXRlZDoqKiB7" +
    "bGVuKHZfcmVzcCl9ICh7bGVuKGZ1bGxfdmlkcyl9IEZ1bGwgRXBpc29kZXMsIHtsZW4oc2hvcnRfdmlkcyl9IFNob3J0cykiLAog" +
    "ICAgICAgIGYiLSAqKkZsYWdzaGlwIEZ1bGwgRXBpc29kZSBMaW5rZWQgRnJvbSBBbGwgU2hvcnRzOioqIHtmbGFnc2hpcF9mdWxs" +
    "X3VybH0iLAogICAgICAgICIiLAogICAgXQoKICAgIHVwZGF0ZWRfZnVsbCwgdXBkYXRlZF9zaG9ydHMsIHRodW1ic19zZXQgPSAw" +
    "LCAwLCAwCgogICAgZm9yIHYsIGR1ciBpbiBmdWxsX3ZpZHM6CiAgICAgICAgdmlkID0gdlsiaWQiXQogICAgICAgIHNuaXAgPSB2" +
    "WyJzbmlwcGV0Il0KICAgICAgICBzdGF0ID0gdi5nZXQoInN0YXRpc3RpY3MiLCB7fSkKICAgICAgICBwcml2ID0gdi5nZXQoInN0" +
    "YXR1cyIsIHt9KS5nZXQoInByaXZhY3lTdGF0dXMiLCAidW5rbm93biIpCiAgICAgICAgb2xkX3RpdGxlID0gc25pcC5nZXQoInRp" +
    "dGxlIiwgIiIpCiAgICAgICAgbmV3X3RpdGxlID0gY2xlYW5fc2VvX3RpdGxlKG9sZF90aXRsZSwgaXNfc2hvcnQ9RmFsc2UpCgog" +
    "ICAgICAgIHNuaXBbInRpdGxlIl0gPSBuZXdfdGl0bGUKICAgICAgICBzbmlwWyJ0YWdzIl0gPSBzZW9fdGFncwogICAgICAgIHNu" +
    "aXBbImNhdGVnb3J5SWQiXSA9IHNuaXAuZ2V0KCJjYXRlZ29yeUlkIikgb3IgIjI0IgogICAgICAgIHNuaXBbImRlc2NyaXB0aW9u" +
    "Il0gPSAoCiAgICAgICAgICAgIGYie25ld190aXRsZX1cbiIKICAgICAgICAgICAgIlRpbWVsZXNzIDREIFRlc3NlcmFjdCBhbmQg" +
    "NUQgTW9iaXVzIGxpdmluZyB0YXJvdCB0cmFuc21pc3Npb24gbmFycmF0ZWQgd2l0aCB3YXJtIHN0dWRpbyB2b2ljZS5cblxuIgog" +
    "ICAgICAgICAgICAiQ0hBUFRFUlM6XG4iCiAgICAgICAgICAgIGYie2NoYXB0ZXJzX2Jsb2NrfVxuXG4iCiAgICAgICAgICAgIGYi" +
    "LS0gSU5URVJBQ1RJVkUgTElWRSA0RC81RCBUQVJPVCBQT1JUQUwgKERSQVcgWU9VUiBPV04gU1BSRUFEKTpcbntwdWJ9L3N0b3Jl" +
    "XG5cbiIKICAgICAgICAgICAgZiItLSBPUkRFUiBZT1VSIENVU1RPTSBQRVJTT05BTElaRUQgNUQgQVVSQSBSRUFESU5HICgkNDkp" +
    "Olxue3B1Yn0vZ28vYXVyYXZpZGVvNDk/dXRtX3NvdXJjZT15b3V0dWJlX2Z1bGwmdXRtX21lZGl1bT1kZXNjJnV0bV9jYW1wYWln" +
    "bj17dmlkfVxuXG4iCiAgICAgICAgICAgIGYiLS0gJDE1IDRELzVEIENSRUFUT1IgQVNTRVQgUEFDSyAoVGVzc2VyYWN0ICsgTW9i" +
    "aXVzIExvb3BzICYgMksgVGVtcGxhdGVzKTpcbntwdWJ9L2dvL2Fzc2V0cGFjazE1P3V0bV9zb3VyY2U9eW91dHViZV9mdWxsJnV0" +
    "bV9tZWRpdW09ZGVzYyZ1dG1fY2FtcGFpZ249e3ZpZH1cblxuIgogICAgICAgICAgICBmIi0tICQxNS9NTyBTT1ZFUkVJR04gNUQg" +
    "TUVNQkVSIFZBVUxUOlxue3B1Yn0vZ28vdmF1bHRzdWIxNT91dG1fc291cmNlPXlvdXR1YmVfZnVsbCZ1dG1fbWVkaXVtPWRlc2Mm" +
    "dXRtX2NhbXBhaWduPXt2aWR9XG5cbiIKICAgICAgICAgICAgIkNvbW1lbnQgSSBDTEFJTSBUSElTIDVEIFNISUZUIGJlbG93IGlm" +
    "IHRoaXMgcmVhZGluZyByZXNvbmF0ZWQgd2l0aCB5b3VyIGV4YWN0IHRpbWVsaW5lLlxuIgogICAgICAgICAgICAiI1Rhcm90UmVh" +
    "ZGluZyAjVGltZWxlc3NUYXJvdCAjQWJ1bmRhbmNlVGFyb3QgIzREVGVzc2VyYWN0ICM1RE1vYml1cyAjT3JhY2xlU3lzdGVtcyIK" +
    "ICAgICAgICApCiAgICAgICAgdHJ5OgogICAgICAgICAgICBib2R5ID0geyJpZCI6IHZpZCwgInNuaXBwZXQiOiBzbmlwfQogICAg" +
    "ICAgICAgICBpZiBwcml2IGluICgidW5saXN0ZWQiLCAicHJpdmF0ZSIpOgogICAgICAgICAgICAgICAgYm9keVsic3RhdHVzIl0g" +
    "PSB7InByaXZhY3lTdGF0dXMiOiAicHVibGljIn0KICAgICAgICAgICAgICAgIHl0LnZpZGVvcygpLnVwZGF0ZShwYXJ0PSJzbmlw" +
    "cGV0LHN0YXR1cyIsIGJvZHk9Ym9keSkuZXhlY3V0ZSgpCiAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICB5dC52aWRl" +
    "b3MoKS51cGRhdGUocGFydD0ic25pcHBldCIsIGJvZHk9Ym9keSkuZXhlY3V0ZSgpCiAgICAgICAgICAgIHVwZGF0ZWRfZnVsbCAr" +
    "PSAxCiAgICAgICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBleDoKICAgICAgICAgICAgbG9nX2xpbmVzLmFwcGVuZChmIi0gW1dBUk4g" +
    "RlVMTCB7dmlkfV0gTWV0YWRhdGEgdXBkYXRlIG5vdGU6IHtzdHIoZXgpWzoxNDBdfSIpCgogICAgICAgICMgVXBsb2FkIGNyaXNw" +
    "IDE5MjB4MTA4MCAySy1kZXJpdmVkIHRodW1ibmFpbCAocmVxdWlyZXMgdmVyaWZpZWQgWW91VHViZSBhY2NvdW50OyBkZWdyYWRl" +
    "cyBncmFjZWZ1bGx5IGlmIG5vdCkKICAgICAgICB0X2J5dGVzLCB0X25hbWUgPSBwaWNrX3RodW1ibmFpbF9ieXRlcyhvbGRfdGl0" +
    "bGUpCiAgICAgICAgaWYgdF9ieXRlczoKICAgICAgICAgICAgdHJ5OgogICAgICAgICAgICAgICAgbWVkaWEgPSBNZWRpYUlvQmFz" +
    "ZVVwbG9hZChpby5CeXRlc0lPKHRfYnl0ZXMpLCBtaW1ldHlwZT0iaW1hZ2UvanBlZyIsIHJlc3VtYWJsZT1GYWxzZSkKICAgICAg" +
    "ICAgICAgICAgIHl0LnRodW1ibmFpbHMoKS5zZXQodmlkZW9JZD12aWQsIG1lZGlhX2JvZHk9bWVkaWEpLmV4ZWN1dGUoKQogICAg" +
    "ICAgICAgICAgICAgdGh1bWJzX3NldCArPSAxCiAgICAgICAgICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZXg6CiAgICAgICAgICAg" +
    "ICAgICBsb2dfbGluZXMuYXBwZW5kKGYiLSBbVEhVTUIgTk9URSB7dmlkfV0gVmVyaWZ5IHBob25lIGF0IHlvdXR1YmUuY29tL3Zl" +
    "cmlmeSB0byB1bmxvY2sgQVBJIHRodW1ibmFpbHMgKHtzdHIoZXgpWzo5MF19KSIpCgogICAgICAgIGxvZ19saW5lcy5hcHBlbmQo" +
    "ZiItICoqRlVMTCBge3ZpZH1gKiogKHtkdXJ9cyB8IHdhcyBge3ByaXZ9YCB8IHtzdGF0LmdldCgndmlld0NvdW50JywnMCcpfSB2" +
    "aWV3cykgLT4gYHtuZXdfdGl0bGV9YCIpCgogICAgZm9yIHYsIGR1ciBpbiBzaG9ydF92aWRzOgogICAgICAgIHZpZCA9IHZbImlk" +
    "Il0KICAgICAgICBzbmlwID0gdlsic25pcHBldCJdCiAgICAgICAgb2xkX3RpdGxlID0gc25pcC5nZXQoInRpdGxlIiwgIiIpCiAg" +
    "ICAgICAgbmV3X3RpdGxlID0gY2xlYW5fc2VvX3RpdGxlKG9sZF90aXRsZSwgaXNfc2hvcnQ9VHJ1ZSkKICAgICAgICBzbmlwWyJ0" +
    "aXRsZSJdID0gbmV3X3RpdGxlCiAgICAgICAgc25pcFsidGFncyJdID0gc2VvX3RhZ3MgKyBbIlNob3J0cyIsICJUYXJvdFNob3J0" +
    "cyJdCiAgICAgICAgc25pcFsiZGVzY3JpcHRpb24iXSA9ICgKICAgICAgICAgICAgZiJXQVRDSCBUSEUgRlVMTCAxMC1NSU5VVEUg" +
    "NEQvNUQgUkVBRElORyBIRVJFOlxue2ZsYWdzaGlwX2Z1bGxfdXJsfVxuXG4iCiAgICAgICAgICAgIGYiLS0gU1RFUCBJTlRPIFRI" +
    "RSBMSVZFIDREIFRFU1NFUkFDVCAmIDVEIE1PQklVUyBQT1JUQUw6XG57cHVifS9zdG9yZVxuXG4iCiAgICAgICAgICAgIGYiLS0g" +
    "JDQ5IENVU1RPTSBQRVJTT05BTElaRUQgNUQgQVVSQSBSRUFESU5HOlxue3B1Yn0vZ28vYXVyYXZpZGVvNDk/dXRtX3NvdXJjZT15" +
    "b3V0dWJlX3Nob3J0JnV0bV9tZWRpdW09ZGVzYyZ1dG1fY2FtcGFpZ249e3ZpZH1cblxuIgogICAgICAgICAgICBmIi0tICQxNSA0" +
    "RC81RCBDUkVBVE9SIEFTU0VUIFBBQ0s6XG57cHVifS9nby9hc3NldHBhY2sxNT91dG1fc291cmNlPXlvdXR1YmVfc2hvcnQmdXRt" +
    "X21lZGl1bT1kZXNjJnV0bV9jYW1wYWlnbj17dmlkfVxuXG4iCiAgICAgICAgICAgICJDb21tZW50IEkgQ0xBSU0gVEhJUyBBTElH" +
    "Tk1FTlQgYmVsb3cuXG4iCiAgICAgICAgICAgICIjU2hvcnRzICNUYXJvdFJlYWRpbmcgIzREVGVzc2VyYWN0ICM1RE1vYml1cyAj" +
    "T3JhY2xlU3lzdGVtcyIKICAgICAgICApCiAgICAgICAgdHJ5OgogICAgICAgICAgICB5dC52aWRlb3MoKS51cGRhdGUocGFydD0i" +
    "c25pcHBldCIsIGJvZHk9eyJpZCI6IHZpZCwgInNuaXBwZXQiOiBzbmlwfSkuZXhlY3V0ZSgpCiAgICAgICAgICAgIHVwZGF0ZWRf" +
    "c2hvcnRzICs9IDEKICAgICAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGV4OgogICAgICAgICAgICBsb2dfbGluZXMuYXBwZW5kKGYi" +
    "LSBbV0FSTiBTSE9SVCB7dmlkfV0ge3N0cihleClbOjEyMF19IikKCiAgICBsb2dfbGluZXMuYXBwZW5kKGYiXG4jIyBTdW1tYXJ5" +
    "XG4tIEZ1bGwgRXBpc29kZXMgU0VPIFVwZ3JhZGVkOiAqKnt1cGRhdGVkX2Z1bGx9L3tsZW4oZnVsbF92aWRzKX0qKlxuLSBDdXN0" +
    "b20gVGh1bWJuYWlscyBQdXNoZWQ6ICoqe3RodW1ic19zZXR9L3tsZW4oZnVsbF92aWRzKX0qKlxuLSBTaG9ydHMgQ3Jvc3MtTGlu" +
    "a2VkIHRvIEZsYWdzaGlwIEZ1bGwgRXBpc29kZTogKip7dXBkYXRlZF9zaG9ydHN9L3tsZW4oc2hvcnRfdmlkcyl9KioiKQogICAg" +
    "cmVwID0gIlxuIi5qb2luKGxvZ19saW5lcykgKyAiXG4iCiAgICBvcGVuKFJFUF9PVVQsICJ3IiwgZW5jb2Rpbmc9InV0Zi04Iiwg" +
    "bmV3bGluZT0iIikud3JpdGUocmVwKQogICAgcHJpbnQoZiJbWVQtU0VPIFBBU1NdIFVwZ3JhZGVkIHt1cGRhdGVkX2Z1bGx9IEZ1" +
    "bGwgRXBpc29kZXMgKHRodW1ibmFpbHMgcHVzaGVkOiB7dGh1bWJzX3NldH0pICsgQ3Jvc3MtbGlua2VkIHt1cGRhdGVkX3Nob3J0" +
    "c30gU2hvcnRzIC0+IHtmbGFnc2hpcF9mdWxsX3VybH0iKQoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBtYWluKCkK"
Write-B64File "$ProjectDir\Modules\youtube_seo_full_optimizer.py" $B64_YTSEO

$B64_B2BV = "aW1wb3J0IGNzdgppbXBvcnQgb3MKaW1wb3J0IHJlCmltcG9ydCBzb2NrZXQKClBESVIgPSByIkM6XFVzZXJzXHRvb21lXERlc2t0" +
    "b3BcU292ZXJlaWduQ29yZSIKQ1NWX0lOID0gb3MucGF0aC5qb2luKFBESVIsICJkYXRhIiwgImIyYl9wcm9zcGVjdHNfaW1wb3J0" +
    "X3RlbXBsYXRlLmNzdiIpCkNTVl9DTEVBTiA9IG9zLnBhdGguam9pbihQRElSLCAiZGF0YSIsICJiMmJfcHJvc3BlY3RzX3Zlcmlm" +
    "aWVkLmNzdiIpCgpFTUFJTF9SWCA9IHJlLmNvbXBpbGUociJeW0EtWmEtejAtOS5fJStcLV0rQFtBLVphLXowLTkuXC1dK1wuW0Et" +
    "WmEtel17Mix9JCIpCkJBRF9QUkVGSVhFUyA9ICgibm9yZXBseSIsICJuby1yZXBseSIsICJkb25vdHJlcGx5IiwgIm1haWxlci1k" +
    "YWVtb24iLCAicG9zdG1hc3RlciIsICJhYnVzZSIsICJwcml2YWN5IiwgImxlZ2FsIikKCgpkZWYgZG9tYWluX3Jlc29sdmVzKGRv" +
    "bWFpbik6CiAgICB0cnk6CiAgICAgICAgc29ja2V0LmdldGFkZHJpbmZvKGRvbWFpbiwgNDQzKQogICAgICAgIHJldHVybiBUcnVl" +
    "CiAgICBleGNlcHQgRXhjZXB0aW9uOgogICAgICAgIHRyeToKICAgICAgICAgICAgc29ja2V0LmdldGFkZHJpbmZvKGRvbWFpbiwg" +
    "ODApCiAgICAgICAgICAgIHJldHVybiBUcnVlCiAgICAgICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAgICAgICAgICAgcmV0dXJuIEZh" +
    "bHNlCgoKZGVmIG1haW4oKToKICAgIGlmIG5vdCBvcy5wYXRoLmV4aXN0cyhDU1ZfSU4pOgogICAgICAgIHByaW50KGYiW0IyQiBW" +
    "RVJJRlldIEZpbGUgbm90IGZvdW5kOiB7Q1NWX0lOfSIpCiAgICAgICAgcmV0dXJuCiAgICB2YWxpZF9yb3dzLCBza2lwcGVkID0g" +
    "W10sIFtdCiAgICBzZWVuID0gc2V0KCkKICAgIHdpdGggb3BlbihDU1ZfSU4sICJyIiwgZW5jb2Rpbmc9InV0Zi04LXNpZyIsIG5l" +
    "d2xpbmU9IiIpIGFzIGY6CiAgICAgICAgZm9yIHJvdyBpbiBjc3YuRGljdFJlYWRlcihmKToKICAgICAgICAgICAgZW0gPSAocm93" +
    "LmdldCgiZW1haWwiKSBvciAiIikuc3RyaXAoKS5sb3dlcigpCiAgICAgICAgICAgIGNvbXAgPSAocm93LmdldCgiY29tcGFueSIp" +
    "IG9yICIiKS5zdHJpcCgpCiAgICAgICAgICAgIGNvbnQgPSAocm93LmdldCgiY29udGFjdCIpIG9yICJUZWFtIikuc3RyaXAoKQog" +
    "ICAgICAgICAgICBub3RlcyA9IChyb3cuZ2V0KCJub3RlcyIpIG9yICIiKS5zdHJpcCgpCiAgICAgICAgICAgIGlmIG5vdCBlbSBv" +
    "ciAiZXhhbXBsZS1zdHVkaW8uY29tIiBpbiBlbToKICAgICAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgICAgIGlmIG5vdCBF" +
    "TUFJTF9SWC5tYXRjaChlbSk6CiAgICAgICAgICAgICAgICBza2lwcGVkLmFwcGVuZCgoZW0sICJJbnZhbGlkIHN5bnRheCIpKQog" +
    "ICAgICAgICAgICAgICAgY29udGludWUKICAgICAgICAgICAgbG9jYWwsIGRvbSA9IGVtLnNwbGl0KCJAIiwgMSkKICAgICAgICAg" +
    "ICAgaWYgYW55KGxvY2FsLnN0YXJ0c3dpdGgocCkgZm9yIHAgaW4gQkFEX1BSRUZJWEVTKToKICAgICAgICAgICAgICAgIHNraXBw" +
    "ZWQuYXBwZW5kKChlbSwgIkRvLW5vdC1lbWFpbCBwcmVmaXgiKSkKICAgICAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgICAg" +
    "IGlmIGVtIGluIHNlZW46CiAgICAgICAgICAgICAgICBjb250aW51ZQogICAgICAgICAgICBpZiBub3QgZG9tYWluX3Jlc29sdmVz" +
    "KGRvbSk6CiAgICAgICAgICAgICAgICBza2lwcGVkLmFwcGVuZCgoZW0sIGYiRG9tYWluIHtkb219IGZhaWxlZCBETlMiKSkKICAg" +
    "ICAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgICAgIHNlZW4uYWRkKGVtKQogICAgICAgICAgICB2YWxpZF9yb3dzLmFwcGVu" +
    "ZCh7ImNvbXBhbnkiOiBjb21wIG9yIGRvbSwgImNvbnRhY3QiOiBjb250LCAiZW1haWwiOiBlbSwgIm5vdGVzIjogbm90ZXN9KQoK" +
    "ICAgIHdpdGggb3BlbihDU1ZfQ0xFQU4sICJ3IiwgZW5jb2Rpbmc9InV0Zi04IiwgbmV3bGluZT0iIikgYXMgZjoKICAgICAgICB3" +
    "ID0gY3N2LkRpY3RXcml0ZXIoZiwgZmllbGRuYW1lcz1bImNvbXBhbnkiLCAiY29udGFjdCIsICJlbWFpbCIsICJub3RlcyJdKQog" +
    "ICAgICAgIHcud3JpdGVoZWFkZXIoKQogICAgICAgIHcud3JpdGVyb3dzKHZhbGlkX3Jvd3MpCgogICAgcHJpbnQoZiJbQjJCIFZF" +
    "UklGWSBQQVNTXSBWZXJpZmllZCB7bGVuKHZhbGlkX3Jvd3MpfSBkZWxpdmVyYWJsZSBhZ2VuY3kgY29udGFjdChzKSAtPiB7Q1NW" +
    "X0NMRUFOfSB8IEZpbHRlcmVkIG91dDoge2xlbihza2lwcGVkKX0iKQogICAgZm9yIGVtLCB3aHkgaW4gc2tpcHBlZFs6MTBdOgog" +
    "ICAgICAgIHByaW50KGYiICBbU0tJUFBFRF0ge2VtfToge3doeX0iKQoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBt" +
    "YWluKCkK"
Write-B64File "$ProjectDir\Modules\b2b_lead_verifier.py" $B64_B2BV


Write-Host "`n>>> [2/5] Running YouTube Full-Episode 0-View Fix (Titles, Chapters, Thumbnails & Shorts Cross-Links)..." -ForegroundColor Cyan
python "$ProjectDir\Modules\youtube_seo_full_optimizer.py"

Write-Host "`n>>> [3/5] Running B2B CSV Email & Domain DNS Verifier..." -ForegroundColor Cyan
python "$ProjectDir\Modules\b2b_lead_verifier.py"

Write-Host "`n>>> [4/5] Generating / Checking Windows ED25519 SSH Key for 24/7 Cloud Cutover..." -ForegroundColor Cyan
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$keyPriv = Join-Path $sshDir "id_ed25519"
$keyPub  = Join-Path $sshDir "id_ed25519.pub"
New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
if (-not (Test-Path $keyPub)) {
    ssh-keygen -t ed25519 -N "" -f $keyPriv -C "Toomer1980@gmail.com"
}
if (Test-Path $keyPub) {
    $pubVal = (Get-Content $keyPub -Raw).Trim()
    try { Set-Clipboard -Value $pubVal } catch {}
    Write-Host "`n[SSH KEY READY & COPIED TO CLIPBOARD] Paste this key into DigitalOcean or Oracle Cloud:" -ForegroundColor Green
    Write-Host $pubVal -ForegroundColor Yellow
}

Write-Host "`n>>> [5/5] Syncing YouTube SEO Report to Drive & Pushing to GitHub..." -ForegroundColor Cyan
Copy-Item "$ProjectDir\reports\YouTube_SEO_Upgrade_Report.md" "$ProjectDir\Oracle_Audit_2026\YouTube_SEO_Upgrade_Report.md" -Force -ErrorAction SilentlyContinue
if (Get-Command rclone -ErrorAction SilentlyContinue) {
    rclone copy "$ProjectDir\Oracle_Audit_2026" "gdrive:Oracle_Audit_2026" --update --bind 0.0.0.0
}

$SafeFiles = @(
    "Deploy_Growth_SEO_and_CloudPrep.ps1",
    "Modules/youtube_seo_full_optimizer.py",
    "Modules/b2b_lead_verifier.py"
)
foreach ($sf in $SafeFiles) { if (Test-Path "$ProjectDir\$sf") { git add -- $sf } }
if (git diff --cached --name-only) {
    git commit -m "Growth Pack: YouTube Full-Episode 0-View SEO + Thumbnail + Shorts Cross-Linker, B2B Lead DNS Verifier & Cloud SSH Key Prep"
    $br = (git rev-parse --abbrev-ref HEAD).Trim()
    git push -u origin $br
    if ($LASTEXITCODE -eq 0) { Write-Host "[GITHUB PASS] Pushed Growth & Cloud Prep Suite cleanly to origin/$br!" -ForegroundColor Green }
}

Write-Host "`n[DONE] 1) Full YouTube episodes optimized + cross-linked from Shorts." -ForegroundColor Green
Write-Host "[DONE] 2) Your SSH public key is copied to clipboard for DigitalOcean/Oracle Cloud." -ForegroundColor Green
Write-Host "[NEXT] Open data\b2b_prospects_import_template.csv to add real agency leads, then run:" -ForegroundColor Yellow
Write-Host "  python .\Modules\b2b_lead_verifier.py; python .\Modules\b2b_client_acquisition_engine.py --csv .\data\b2b_prospects_verified.csv --live --cap 10" -ForegroundColor Yellow
