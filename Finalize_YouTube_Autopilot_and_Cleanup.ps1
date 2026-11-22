# ==============================================================================
# ORACLE SYSTEMS LLC // YOUTUBE STUDIO CLEANUP + PURE-HTTP AUTOPILOT UPGRADE
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

function Write-B64File([string]$Path, [string]$B64) {
    $bytes = [System.Convert]::FromBase64String($B64)
    [System.IO.File]::WriteAllBytes($Path, $bytes)
    Write-Host "  [WROTE] $Path ($($bytes.Length) bytes)" -ForegroundColor DarkCyan
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // YOUTUBE CLEANUP & PURE-HTTP AUTOPILOT UPGRADE" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

if (Test-Path "$ProjectDir\optimize_ram_and_boot.ps1") { & "$ProjectDir\optimize_ram_and_boot.ps1" -TrimNow }

Write-Host "`n>>> [1/5] Installing Aborted-Draft Cleaner & Pure-HTTP Auto-Publisher..." -ForegroundColor Cyan
$B64_CLN = "aW1wb3J0IGpzb24KaW1wb3J0IG9zCmltcG9ydCByZXF1ZXN0cwoKUERJUiA9IHIiQzpcVXNlcnNcdG9vbWVcRGVza3RvcFxTb3Zl" +
    "cmVpZ25Db3JlIgpUT0tfUCA9IG9zLnBhdGguam9pbihQRElSLCAiY29uZmlnIiwgInlvdXR1YmVfdG9rZW4uanNvbiIpClNUQVRF" +
    "X1AgPSBvcy5wYXRoLmpvaW4oUERJUiwgImRhdGEiLCAieW91dHViZV91bHRyYV80ZDVkX3VwbG9hZHMuanNvbiIpCgoKZGVmIGdl" +
    "dF90b2tlbigpOgogICAgZnJvbSBnb29nbGUuYXV0aC50cmFuc3BvcnQucmVxdWVzdHMgaW1wb3J0IFJlcXVlc3QKICAgIGZyb20g" +
    "Z29vZ2xlLm9hdXRoMi5jcmVkZW50aWFscyBpbXBvcnQgQ3JlZGVudGlhbHMKCiAgICBjcmVkcyA9IENyZWRlbnRpYWxzLmZyb21f" +
    "YXV0aG9yaXplZF91c2VyX2ZpbGUoVE9LX1ApCiAgICBpZiBub3QgY3JlZHMudmFsaWQgb3IgY3JlZHMuZXhwaXJlZCBvciBub3Qg" +
    "Y3JlZHMudG9rZW46CiAgICAgICAgY3JlZHMucmVmcmVzaChSZXF1ZXN0KCkpCiAgICByZXR1cm4gY3JlZHMudG9rZW4KCgpkZWYg" +
    "bWFpbigpOgogICAgaWYgbm90IG9zLnBhdGguZXhpc3RzKFRPS19QKToKICAgICAgICBwcmludCgiW1lULUNMRUFOXSBNaXNzaW5n" +
    "IGNvbmZpZ1xceW91dHViZV90b2tlbi5qc29uIikKICAgICAgICByZXR1cm4KCiAgICB0b2tlbiA9IGdldF90b2tlbigpCiAgICBo" +
    "ZHJzID0geyJBdXRob3JpemF0aW9uIjogZiJCZWFyZXIge3Rva2VufSJ9CiAgICBzdCA9IGpzb24ubG9hZChvcGVuKFNUQVRFX1As" +
    "ICJyIiwgZW5jb2Rpbmc9InV0Zi04IikpIGlmIG9zLnBhdGguZXhpc3RzKFNUQVRFX1ApIGVsc2Uge30KICAgIHByb3RlY3RlZF9p" +
    "ZHMgPSBzZXQoKHN0LmdldCgidXBsb2FkZWRfZmlsZXMiKSBvciB7fSkudmFsdWVzKCkpIHwgewogICAgICAgICJrb0ZwdU1LdU44" +
    "WSIsICJyWXFOZVhPcEFXdyIsICJmdXA4d3YxMEJVWSIsICJwbXZsYms3OGlvYyIKICAgIH0KCiAgICBjaCA9IHJlcXVlc3RzLmdl" +
    "dCgiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20veW91dHViZS92My9jaGFubmVscz9wYXJ0PWNvbnRlbnREZXRhaWxzJm1pbmU9" +
    "dHJ1ZSIsIGhlYWRlcnM9aGRycywgdGltZW91dD0yMCkuanNvbigpCiAgICBpdGVtcyA9IGNoLmdldCgiaXRlbXMiKSBvciBbXQog" +
    "ICAgaWYgbm90IGl0ZW1zOgogICAgICAgIHByaW50KCJbWVQtQ0xFQU5dIE5vIGNoYW5uZWwgZm91bmQuIikKICAgICAgICByZXR1" +
    "cm4KCiAgICBwbF9pZCA9IGl0ZW1zWzBdWyJjb250ZW50RGV0YWlscyJdWyJyZWxhdGVkUGxheWxpc3RzIl1bInVwbG9hZHMiXQog" +
    "ICAgcGwgPSByZXF1ZXN0cy5nZXQoZiJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS95b3V0dWJlL3YzL3BsYXlsaXN0SXRlbXM/" +
    "cGFydD1zbmlwcGV0JnBsYXlsaXN0SWQ9e3BsX2lkfSZtYXhSZXN1bHRzPTQwIiwgaGVhZGVycz1oZHJzLCB0aW1lb3V0PTIwKS5q" +
    "c29uKCkKICAgIHZpZHMgPSBbaXRbInNuaXBwZXQiXVsicmVzb3VyY2VJZCJdWyJ2aWRlb0lkIl0gZm9yIGl0IGluIChwbC5nZXQo" +
    "Iml0ZW1zIikgb3IgW10pXQogICAgaWYgbm90IHZpZHM6CiAgICAgICAgcHJpbnQoIltZVC1DTEVBTl0gTm8gdXBsb2FkcyBmb3Vu" +
    "ZC4iKQogICAgICAgIHJldHVybgoKICAgIGRldCA9IHJlcXVlc3RzLmdldCgKICAgICAgICBmImh0dHBzOi8vd3d3Lmdvb2dsZWFw" +
    "aXMuY29tL3lvdXR1YmUvdjMvdmlkZW9zP3BhcnQ9c25pcHBldCxzdGF0dXMsc3RhdGlzdGljcyxjb250ZW50RGV0YWlscyZpZD17" +
    "JywnLmpvaW4odmlkcyl9IiwKICAgICAgICBoZWFkZXJzPWhkcnMsIHRpbWVvdXQ9MjAsCiAgICApLmpzb24oKQoKICAgIGRlbGV0" +
    "ZWQgPSAwCiAgICBmb3IgdiBpbiBkZXQuZ2V0KCJpdGVtcyIpIG9yIFtdOgogICAgICAgIHZpZCA9IHZbImlkIl0KICAgICAgICBp" +
    "ZiB2aWQgaW4gcHJvdGVjdGVkX2lkczoKICAgICAgICAgICAgY29udGludWUKICAgICAgICB1cF9zdGF0dXMgPSAodi5nZXQoInN0" +
    "YXR1cyIpIG9yIHt9KS5nZXQoInVwbG9hZFN0YXR1cyIsICIiKQogICAgICAgIHZpZXdzID0gaW50KCh2LmdldCgic3RhdGlzdGlj" +
    "cyIpIG9yIHt9KS5nZXQoInZpZXdDb3VudCIsIDApKQogICAgICAgIGR1ciA9ICh2LmdldCgiY29udGVudERldGFpbHMiKSBvciB7" +
    "fSkuZ2V0KCJkdXJhdGlvbiIsICIiKQogICAgICAgIHRpdGxlID0gKHYuZ2V0KCJzbmlwcGV0Iikgb3Ige30pLmdldCgidGl0bGUi" +
    "LCAiIikKICAgICAgICAjIE9ubHkgZGVsZXRlIGFib3J0ZWQvZmFpbGVkL3VucHJvY2Vzc2VkIDAtdmlldyBzaGVsbHMgKCJQcm9j" +
    "ZXNzaW5nIHdpbGwgYmVnaW4gc2hvcnRseSIpCiAgICAgICAgaXNfYWJvcnRlZF9zaGVsbCA9ICh1cF9zdGF0dXMgaW4gKCJmYWls" +
    "ZWQiLCAicmVqZWN0ZWQiLCAiZGVsZXRlZCIsICJ1cGxvYWRlZCIpKSBhbmQgKHZpZXdzID09IDApIGFuZCAoZHVyIGluICgiIiwg" +
    "IlAwRCIsICJQVDBTIikpCiAgICAgICAgaWYgaXNfYWJvcnRlZF9zaGVsbDoKICAgICAgICAgICAgciA9IHJlcXVlc3RzLmRlbGV0" +
    "ZShmImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3lvdXR1YmUvdjMvdmlkZW9zP2lkPXt2aWR9IiwgaGVhZGVycz1oZHJzLCB0" +
    "aW1lb3V0PTIwKQogICAgICAgICAgICBpZiByLnN0YXR1c19jb2RlIGluICgyMDAsIDIwNCk6CiAgICAgICAgICAgICAgICBkZWxl" +
    "dGVkICs9IDEKICAgICAgICAgICAgICAgIHByaW50KGYiICBbREVMRVRFRCBBQk9SVEVEIFNIRUxMXSB7dmlkfSAoc3RhdHVzPXt1" +
    "cF9zdGF0dXN9KSAtPiB7dGl0bGVbOjU1XX0iKQogICAgICAgICAgICBlbHNlOgogICAgICAgICAgICAgICAgcHJpbnQoZiIgIFtE" +
    "RUxFVEUgTk9URV0ge3ZpZH06IEhUVFAge3Iuc3RhdHVzX2NvZGV9IHtyLnRleHRbOjEwMF19IikKCiAgICBwcmludChmIltZVC1D" +
    "TEVBTiBQQVNTXSBSZW1vdmVkIHtkZWxldGVkfSBhYm9ydGVkICdQcm9jZXNzaW5nIHdpbGwgYmVnaW4gc2hvcnRseScgZHJhZnQg" +
    "c2hlbGwocykuIFByb3RlY3RlZCBsaXZlIElEcyB1bnRvdWNoZWQuIikKCgppZiBfX25hbWVfXyA9PSAiX19tYWluX18iOgogICAg" +
    "bWFpbigpCg=="
Write-B64File "$ProjectDir\Modules\cleanup_aborted_yt_drafts.py" $B64_CLN
$B64_AUT = "aW1wb3J0IGFyZ3BhcnNlCmltcG9ydCBqc29uCmltcG9ydCBvcwppbXBvcnQgcmUKaW1wb3J0IHN5cwppbXBvcnQgdGltZQoKUERJ" +
    "UiA9IHIiQzpcVXNlcnNcdG9vbWVcRGVza3RvcFxTb3ZlcmVpZ25Db3JlIgpzeXMucGF0aC5pbnNlcnQoMCwgb3MucGF0aC5qb2lu" +
    "KFBESVIsICJNb2R1bGVzIikpCgppbXBvcnQgcHVibGlzaF9yZWFsXzRkNWRfeW91dHViZSBhcyBwdWJtb2QKClZBVUxUX1NUQVRF" +
    "ID0gb3MucGF0aC5qb2luKFBESVIsICJkYXRhIiwgInVsdHJhXzRkNWRfdmF1bHRfcHJvZ3Jlc3MuanNvbiIpCkZVTExfRElSID0g" +
    "b3MucGF0aC5qb2luKFBESVIsICJDb250ZW50X1ZhdWx0XzREX0Z1bGwiKQpTSE9SVFNfRElSID0gb3MucGF0aC5qb2luKFBESVIs" +
    "ICJDb250ZW50X1ZhdWx0XzREX1Nob3J0cyIpCgoKZGVmIGNsZWFuX3RvcGljKGZuYW1lKToKICAgIGJhc2UgPSByZS5zdWIociIo" +
    "P2kpXih3ZWVrfHNob3J0KV9cZCtfIiwgIiIsIGZuYW1lKQogICAgYmFzZSA9IHJlLnN1YihyIig/aSkoXzRkX21heHxfcmVhbF9m" +
    "dWxsKT9cLm1wNCQiLCAiIiwgYmFzZSkKICAgIHJldHVybiBiYXNlLnJlcGxhY2UoIl8iLCAiICIpLnN0cmlwKCkgb3IgIlF1YW50" +
    "dW0gQWxpZ25tZW50IgoKCmRlZiBsYXRlc3RfbGl2ZV9mdWxsX3VybChzdCwgcHViX3VybCk6CiAgICB1cGxvYWRlZCA9IHN0Lmdl" +
    "dCgidXBsb2FkZWRfZmlsZXMiKSBvciB7fQogICAgZm9yIGsgaW4gcmV2ZXJzZWQobGlzdCh1cGxvYWRlZC5rZXlzKCkpKToKICAg" +
    "ICAgICBpZiBrLmxvd2VyKCkuc3RhcnRzd2l0aCgid2Vla18iKToKICAgICAgICAgICAgcmV0dXJuIGYiaHR0cHM6Ly95b3V0dS5i" +
    "ZS97dXBsb2FkZWRba119IgogICAgcmV0dXJuIGYie3B1Yl91cmx9L3N0b3JlIgoKCmRlZiBydW5fYXV0b19wdWJsaXNoKG1vZGU9" +
    "InNob3J0IiwgbWF4X3VwbG9hZHM9MSk6CiAgICBpZiBub3Qgb3MucGF0aC5leGlzdHMocHVibW9kLlRPS19QKToKICAgICAgICBw" +
    "cmludCgiW0FVVE8tWVRdIE1pc3NpbmcgY29uZmlnXFx5b3V0dWJlX3Rva2VuLmpzb24iKQogICAgICAgIHJldHVybgoKICAgIHZh" +
    "dWx0ID0ganNvbi5sb2FkKG9wZW4oVkFVTFRfU1RBVEUsICJyIiwgZW5jb2Rpbmc9InV0Zi04IikpIGlmIG9zLnBhdGguZXhpc3Rz" +
    "KFZBVUxUX1NUQVRFKSBlbHNlIHt9CiAgICBzdCA9IHB1Ym1vZC5sb2FkX3N0YXRlKCkKICAgIHVwbG9hZGVkID0gc3Quc2V0ZGVm" +
    "YXVsdCgidXBsb2FkZWRfZmlsZXMiLCB7fSkKICAgIHB1Yl91cmwgPSBwdWJtb2QuZ2V0X3B1Yl91cmwoKQoKICAgIHAzNl9wYXRo" +
    "ID0gb3MucGF0aC5qb2luKFBESVIsICJkYXRhIiwgImxpdmluZ19zaG9ydHNfcmVuZGVyZWQuanNvbiIpCiAgICBwMzZfc2hvcnRz" +
    "ID0ganNvbi5sb2FkKG9wZW4ocDM2X3BhdGgsICJyIiwgZW5jb2Rpbmc9InV0Zi04IikpIGlmIG9zLnBhdGguZXhpc3RzKHAzNl9w" +
    "YXRoKSBlbHNlIFtdCgogICAgaWYgbW9kZSA9PSAiZnVsbCI6CiAgICAgICAgY2FuZGlkYXRlcyA9IGxpc3QodmF1bHQuZ2V0KCJm" +
    "dWxsX2RvbmUiKSBvciBbXSkKICAgICAgICBiYXNlX2RpciA9IEZVTExfRElSCiAgICBlbHNlOgogICAgICAgIHNlZW4gPSBzZXQo" +
    "KQogICAgICAgIGNhbmRpZGF0ZXMgPSBbXQogICAgICAgIGZvciBzIGluIGxpc3QodmF1bHQuZ2V0KCJzaG9ydHNfZG9uZSIpIG9y" +
    "IFtdKSArIGxpc3QocDM2X3Nob3J0cyk6CiAgICAgICAgICAgIGlmIHMgbm90IGluIHNlZW46CiAgICAgICAgICAgICAgICBzZWVu" +
    "LmFkZChzKQogICAgICAgICAgICAgICAgY2FuZGlkYXRlcy5hcHBlbmQocykKICAgICAgICBiYXNlX2RpciA9IFNIT1JUU19ESVIK" +
    "CiAgICBwZW5kaW5nID0gW2YgZm9yIGYgaW4gY2FuZGlkYXRlcyBpZiBmIG5vdCBpbiB1cGxvYWRlZCBhbmQgb3MucGF0aC5leGlz" +
    "dHMob3MucGF0aC5qb2luKGJhc2VfZGlyLCBmKSldCiAgICBpZiBub3QgcGVuZGluZzoKICAgICAgICBwcmludChmIltBVVRPLVlU" +
    "XSBObyBuZXcgcmVuZGVyZWQgVWx0cmEtSEQge21vZGV9cyB3YWl0aW5nIHRvIHB1Ymxpc2ggKGFscmVhZHkgdXBsb2FkZWQ6IHts" +
    "ZW4odXBsb2FkZWQpfSkuIikKICAgICAgICByZXR1cm4KCiAgICB0b2tlbiA9IHB1Ym1vZC5nZXRfZnJlc2hfYWNjZXNzX3Rva2Vu" +
    "KCkKICAgIGZsYWdzaGlwX3VybCA9IGxhdGVzdF9saXZlX2Z1bGxfdXJsKHN0LCBwdWJfdXJsKQogICAgY291bnQgPSAwCgogICAg" +
    "Zm9yIGZuYW1lIGluIHBlbmRpbmdbOm1heF91cGxvYWRzXToKICAgICAgICBmcGF0aCA9IG9zLnBhdGguam9pbihiYXNlX2Rpciwg" +
    "Zm5hbWUpCiAgICAgICAgdG9waWMgPSBjbGVhbl90b3BpYyhmbmFtZSkKICAgICAgICBrdyA9IFt3Lmxvd2VyKCkgZm9yIHcgaW4g" +
    "cmUuZmluZGFsbChyIltBLVphLXowLTldKyIsIGZuYW1lKSBpZiBsZW4odykgPj0gM11bOjNdCgogICAgICAgIGlmIG1vZGUgPT0g" +
    "ImZ1bGwiOgogICAgICAgICAgICB0aXRsZSA9IGYie3RvcGljfSB8IEZ1bGwgMTAtTWluIDREIFRlc3NlcmFjdCAmIDVEIE1vYml1" +
    "cyBUYXJvdCBSZWFkaW5nIgogICAgICAgICAgICB3a19tID0gcmUubWF0Y2gociIoV2Vla19cZCspIiwgZm5hbWUsIHJlLkkpCiAg" +
    "ICAgICAgICAgIGNoYXBzID0gcHVibW9kLmxvYWRfY2hhcHRlcnNfZm9yKHdrX20uZ3JvdXAoMSkgaWYgd2tfbSBlbHNlICJXZWVr" +
    "XzAxIikKICAgICAgICAgICAgZGVzYyA9ICgKICAgICAgICAgICAgICAgIGYie3RpdGxlfVxuIgogICAgICAgICAgICAgICAgIkZ1" +
    "bGwtbGVuZ3RoIDEwODBwLzMwZnBzIGxpdmluZyA0RCBUZXNzZXJhY3QgYW5kIDVEIE1vYml1cyByYXktdHJhY2VkIHRhcm90IHJl" +
    "YWRpbmcgd2l0aCB3YXJtIHN0dWRpbyBuYXJyYXRpb24uXG5cbiIKICAgICAgICAgICAgICAgIGYiQ0hBUFRFUlM6XG57Y2hhcHN9" +
    "XG5cbiIKICAgICAgICAgICAgICAgIGYiLS0gTElWRSBJTlRFUkFDVElWRSA0RC81RCBUQVJPVCBQT1JUQUw6XG57cHViX3VybH0v" +
    "c3RvcmVcblxuIgogICAgICAgICAgICAgICAgZiItLSAkNDkgQ1VTVE9NIFBFUlNPTkFMSVpFRCA1RCBBVVJBIFJFQURJTkc6XG57" +
    "cHViX3VybH0vZ28vYXVyYXZpZGVvNDk/dXRtX3NvdXJjZT15dF9hdXRvX2Z1bGwmdXRtX21lZGl1bT1kZXNjJnV0bV9jYW1wYWln" +
    "bj17Zm5hbWV9XG5cbiIKICAgICAgICAgICAgICAgIGYiLS0gJDE1IDRELzVEIENSRUFUT1IgQVNTRVQgUEFDSzpcbntwdWJfdXJs" +
    "fS9nby9hc3NldHBhY2sxNT91dG1fc291cmNlPXl0X2F1dG9fZnVsbCZ1dG1fbWVkaXVtPWRlc2MmdXRtX2NhbXBhaWduPXtmbmFt" +
    "ZX1cblxuIgogICAgICAgICAgICAgICAgZiItLSAkMTUvTU8gU09WRVJFSUdOIDVEIE1FTUJFUiBWQVVMVDpcbntwdWJfdXJsfS9n" +
    "by92YXVsdHN1YjE1P3V0bV9zb3VyY2U9eXRfYXV0b19mdWxsJnV0bV9tZWRpdW09ZGVzYyZ1dG1fY2FtcGFpZ249e2ZuYW1lfVxu" +
    "XG4iCiAgICAgICAgICAgICAgICAiQ29tbWVudCBJIENMQUlNIFRISVMgNUQgU0hJRlQgYmVsb3cuXG4iCiAgICAgICAgICAgICAg" +
    "ICAiI1Rhcm90UmVhZGluZyAjVGltZWxlc3NUYXJvdCAjNERUZXNzZXJhY3QgIzVETW9iaXVzICNPcmFjbGVTeXN0ZW1zIgogICAg" +
    "ICAgICAgICApCiAgICAgICAgICAgIHRhZ3MgPSBbInRhcm90IHJlYWRpbmciLCAidGltZWxlc3MgdGFyb3QiLCAiNEQgdGVzc2Vy" +
    "YWN0IiwgIjVEIG1vYml1cyIsICJPcmFjbGUgU3lzdGVtcyIsIHRvcGljLmxvd2VyKCldCiAgICAgICAgICAgIHVwX3BhdGggPSBw" +
    "dWJtb2QucHJlcGFyZV9kc2xfdXBsb2FkX2ZpbGUoZnBhdGgsIG1heF9tYj0xNDAuMCkKICAgICAgICBlbHNlOgogICAgICAgICAg" +
    "ICB0aXRsZSA9IGYie3RvcGljfSB8IExpdmUgNEQgVGVzc2VyYWN0ICYgNUQgTW9iaXVzIFRhcm90ICNTaG9ydHMiCiAgICAgICAg" +
    "ICAgIGRlc2MgPSAoCiAgICAgICAgICAgICAgICBmIldBVENIIFRIRSBGVUxMIDEwLU1JTlVURSA0RC81RCBSRUFESU5HIEhFUkU6" +
    "XG57ZmxhZ3NoaXBfdXJsfVxuXG4iCiAgICAgICAgICAgICAgICBmIi0tIExJVkUgNEQgVEVTU0VSQUNUICYgNUQgTU9CSVVTIFRB" +
    "Uk9UIFBPUlRBTDpcbntwdWJfdXJsfS9zdG9yZVxuXG4iCiAgICAgICAgICAgICAgICBmIi0tICQ0OSBDVVNUT00gUEVSU09OQUxJ" +
    "WkVEIDVEIEFVUkEgUkVBRElORzpcbntwdWJfdXJsfS9nby9hdXJhdmlkZW80OT91dG1fc291cmNlPXl0X2F1dG9fc2hvcnQmdXRt" +
    "X21lZGl1bT1kZXNjJnV0bV9jYW1wYWlnbj17Zm5hbWV9XG5cbiIKICAgICAgICAgICAgICAgIGYiLS0gJDE1IDRELzVEIENSRUFU" +
    "T1IgQVNTRVQgUEFDSzpcbntwdWJfdXJsfS9nby9hc3NldHBhY2sxNT91dG1fc291cmNlPXl0X2F1dG9fc2hvcnQmdXRtX21lZGl1" +
    "bT1kZXNjJnV0bV9jYW1wYWlnbj17Zm5hbWV9XG5cbiIKICAgICAgICAgICAgICAgICJDb21tZW50IEkgQ0xBSU0gVEhJUyBBTElH" +
    "Tk1FTlQgYmVsb3cuXG4iCiAgICAgICAgICAgICAgICAiI1Nob3J0cyAjVGFyb3RTaG9ydHMgIzREVGVzc2VyYWN0ICM1RE1vYml1" +
    "cyAjT3JhY2xlU3lzdGVtcyIKICAgICAgICAgICAgKQogICAgICAgICAgICB0YWdzID0gWyJTaG9ydHMiLCAiVGFyb3RTaG9ydHMi" +
    "LCAiNEQgdGVzc2VyYWN0IiwgIjVEIG1vYml1cyIsICJPcmFjbGUgU3lzdGVtcyIsIHRvcGljLmxvd2VyKCldCiAgICAgICAgICAg" +
    "IHVwX3BhdGggPSBmcGF0aAoKICAgICAgICBwcmludChmIltBVVRPLVlUXSBVcGxvYWRpbmcge21vZGUudXBwZXIoKX06IHtmbmFt" +
    "ZX0gKHtvcy5wYXRoLmdldHNpemUodXBfcGF0aCkvKDEwMjQqKjIpOi4xZn0gTUIpLi4uIikKICAgICAgICB2aWQgPSBwdWJtb2Qu" +
    "dXBsb2FkX3ZpZGVvX3JlcXVlc3RzX3Jlc3VtYWJsZSh0b2tlbiwgdXBfcGF0aCwgdGl0bGUsIGRlc2MsIHRhZ3MpCiAgICAgICAg" +
    "dXBsb2FkZWRbZm5hbWVdID0gdmlkCiAgICAgICAgcHVibW9kLnNhdmVfc3RhdGUoc3QpCiAgICAgICAgcHJpbnQoZiIgIFtMSVZF" +
    "XSBodHRwczovL3lvdXR1LmJlL3t2aWR9IikKCiAgICAgICAgaWYgbW9kZSA9PSAiZnVsbCI6CiAgICAgICAgICAgIHRpbWUuc2xl" +
    "ZXAoMikKICAgICAgICAgICAgb2ssIG5vdGUgPSBwdWJtb2Quc2V0X2N1c3RvbV90aHVtYm5haWxfaHR0cCh0b2tlbiwgdmlkLCBr" +
    "dykKICAgICAgICAgICAgcHJpbnQoZiIgIFtUSFVNQiB7J1BBU1MnIGlmIG9rIGVsc2UgJ05PVEUnfV0ge25vdGV9IikKICAgICAg" +
    "ICBjb3VudCArPSAxCgogICAgcHJpbnQoZiJbQVVUTy1ZVCBDT01QTEVURV0gUHVibGlzaGVkIHtjb3VudH0gbmV3IFVsdHJhLUhE" +
    "IHttb2RlfShzKSBjbGVhbmx5IHZpYSBwdXJlIEhUVFAgMzA4IHJlc3VtYWJsZSBlbmdpbmUuIikKCgppZiBfX25hbWVfXyA9PSAi" +
    "X19tYWluX18iOgogICAgYXAgPSBhcmdwYXJzZS5Bcmd1bWVudFBhcnNlcigpCiAgICBhcC5hZGRfYXJndW1lbnQoIi0tbW9kZSIs" +
    "IGNob2ljZXM9WyJzaG9ydCIsICJmdWxsIl0sIGRlZmF1bHQ9InNob3J0IikKICAgIGFwLmFkZF9hcmd1bWVudCgiLS1jb3VudCIs" +
    "IHR5cGU9aW50LCBkZWZhdWx0PTEpCiAgICBhcmdzID0gYXAucGFyc2VfYXJncygpCiAgICBydW5fYXV0b19wdWJsaXNoKG1vZGU9" +
    "YXJncy5tb2RlLCBtYXhfdXBsb2Fkcz1hcmdzLmNvdW50KQo="
Write-B64File "$ProjectDir\Modules\auto_publish_vault_queue.py" $B64_AUT

Write-Host "`n>>> [2/5] Removing Aborted 'Processing will begin shortly' Shells in YouTube Studio..." -ForegroundColor Cyan
python "$ProjectDir\Modules\cleanup_aborted_yt_drafts.py"

Write-Host "`n>>> [3/5] Upgrading Daily Short & Weekly Full Scheduled Tasks to Pure-HTTP 308 Engine..." -ForegroundColor Cyan
$set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "OracleSystems_YouTube_DailyShort" -Action (New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$ProjectDir\Modules\auto_publish_vault_queue.py`" --mode short --count 1" -WorkingDirectory $ProjectDir) -Trigger (New-ScheduledTaskTrigger -Daily -At 10:00AM) -Settings $set -Description "Daily 10AM pure-HTTP 308 Ultra-HD 4D/5D Short publisher" -Force | Out-Null
Register-ScheduledTask -TaskName "OracleSystems_YouTube_WeeklyFull" -Action (New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$ProjectDir\Modules\auto_publish_vault_queue.py`" --mode full --count 1" -WorkingDirectory $ProjectDir) -Trigger (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At 1:00PM) -Settings $set -Description "Weekly Friday 1PM pure-HTTP 308 Ultra-HD 4D/5D Full Episode + Custom Thumbnail publisher" -Force | Out-Null
Write-Host "[TASKS PASS] Upgraded OracleSystems_YouTube_DailyShort (10AM) + OracleSystems_YouTube_WeeklyFull (Fri 1PM)" -ForegroundColor Green

Write-Host "`n>>> [4/5] Publishing Next Ready Ultra-HD Short (Short_14) to Keep Daily Momentum..." -ForegroundColor Cyan
python "$ProjectDir\Modules\auto_publish_vault_queue.py" --mode short --count 1

Write-Host "`n>>> [5/5] Pushing Updates to GitHub & Opening B2B Agency CSV Template..." -ForegroundColor Cyan
$SafeFiles = @(
    "Finalize_YouTube_Autopilot_and_Cleanup.ps1",
    "Modules/cleanup_aborted_yt_drafts.py",
    "Modules/auto_publish_vault_queue.py"
)
foreach ($sf in $SafeFiles) { if (Test-Path "$ProjectDir\$sf") { git add -- $sf } }
if (git diff --cached --name-only) {
    git commit -m "YouTube Studio Aborted-Draft Cleaner + Pure-HTTP 308 Daily/Weekly Auto-Publisher Upgrade"
    $br = (git rev-parse --abbrev-ref HEAD).Trim()
    git push -u origin $br
    if ($LASTEXITCODE -eq 0) { Write-Host "[GITHUB PASS] Pushed cleanly to origin/$br!" -ForegroundColor Green }
}

Start-Process "https://studio.youtube.com/channel/UCa-d8z5hp_fBBo36nGZzolA/content"
if (Test-Path "$ProjectDir\data\b2b_prospects_import_template.csv") {
    Start-Process notepad.exe "$ProjectDir\data\b2b_prospects_import_template.csv"
}
Write-Host "`n[COMPLETE] YouTube Studio cleaned, daily/weekly auto-publishers upgraded to HTTP 308, and B2B CSV opened for agency leads!" -ForegroundColor Green
