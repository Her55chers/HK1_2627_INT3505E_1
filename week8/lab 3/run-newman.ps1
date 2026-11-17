# Lab 3 — chạy collection bằng Newman, xuất CLI + JUnit.
# Yêu cầu: Node 18+, Books API đang chạy ở http://127.0.0.1:5000 (xem readme.md).
# Chạy:  powershell -ExecutionPolicy Bypass -File ".\run-newman.ps1"
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:5000/health" -TimeoutSec 3 | Out-Null
} catch {
    Write-Error "Books API chưa chạy ở 127.0.0.1:5000. Hãy start server trước (xem readme.md)."
}

New-Item -ItemType Directory -Force reports | Out-Null
npx --yes newman run books-api.postman_collection.json `
    -e local.postman_environment.json `
    -r cli,junit --reporter-junit-export reports/junit.xml
exit $LASTEXITCODE
