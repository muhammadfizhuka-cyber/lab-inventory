# Dipakai Jenkins stage Health Check. Retry sampai 15x (2 detik per percobaan).
$urls = @("http://localhost:5000/health", "http://localhost:8081/api/health")
foreach ($url in $urls) {
    $ok = $false
    for ($i = 1; $i -le 15; $i++) {
        try {
            $r = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 3
            if ($r.StatusCode -eq 200) { Write-Host "OK  $url"; $ok = $true; break }
        } catch { Write-Host "Menunggu $url ($i/15)..." }
        Start-Sleep -Seconds 2
    }
    if (-not $ok) { Write-Host "GAGAL $url"; exit 1 }
}
Write-Host "Health check lulus."
exit 0
