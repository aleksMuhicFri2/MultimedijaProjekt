# Quick API endpoint tester
$ErrorActionPreference = 'Continue'

Write-Host "`n=== Testing Backend API Endpoints ===`n"

$baseUrl = "http://localhost:5000"

# Test 1: Regions endpoint
Write-Host "1. Testing GET /api/municipalities/regions..."
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/municipalities/regions" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ FAILED - $_" -ForegroundColor Red
}

# Test 2: Municipality endpoint
Write-Host "`n2. Testing GET /api/municipality/123..."
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/municipality/123" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        Write-Host "   Data structure: $($data.PSObject.Properties.Name -join ', ')"
    }
} catch {
    Write-Host "   ✗ FAILED - $_" -ForegroundColor Red
}

Write-Host "`n=== Frontend Check ===`n"
Write-Host "If white screen persists:"
Write-Host "1. Check browser console (F12) for errors like:"
Write-Host "   - 'Cannot read property X of undefined'"
Write-Host "   - '404 Not Found' on API calls"
Write-Host "   - React component errors"
Write-Host "`n2. Common fixes:"
Write-Host "   - Verify frontend is calling correct endpoint: /api/municipality/<id>"
Write-Host "   - Check if API response data structure matches frontend expectations"
Write-Host "   - Add error handling in frontend for API failures"
Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
