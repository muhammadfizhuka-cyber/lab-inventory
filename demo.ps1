# Skrip bantu rekaman video: demo Data Immunity (hapus container backend, data harus tetap ada)
$api = "http://localhost:8081/api/inventory"

Write-Host "`n[1] Tambah data uji..." -ForegroundColor Cyan
$body = @{ name = "Mikrotik hAP ac2"; category = "Router"; quantity = 3; status = "Tersedia" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri $api -ContentType "application/json" -Body $body | Out-Host

Write-Host "`n[2] Data sebelum container dihapus:" -ForegroundColor Cyan
(Invoke-RestMethod $api).items | Format-Table

Write-Host "`n[3] docker rm -f lab-backend" -ForegroundColor Yellow
docker rm -f lab-backend

Write-Host "`n[4] Jalankan ulang stack..." -ForegroundColor Yellow
docker compose up -d
Start-Sleep -Seconds 4

Write-Host "`n[5] Data sesudah container dibuat ulang (harus sama):" -ForegroundColor Green
(Invoke-RestMethod $api).items | Format-Table

Write-Host "`n[6] Volume:" -ForegroundColor Cyan
docker volume ls --filter name=lab-inventory
