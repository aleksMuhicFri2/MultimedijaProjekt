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

# Test 3: Search endpoint (checks category scores are not constant)
Write-Host "`n3. Testing POST /api/search..."
try {
    $body = @{
        search_type = "rent"
        max_monthly_rent = 1000
        desired_m2 = 60
        has_car = $false
        workplace_city_code = ""
        max_commute_minutes = 60
        weights = @{
            affordability = 10
            demographics = 10
            transportation = 10
            healthcare = 10
            education = 10
            weather = 10
            price_diversity = 10
            market_liquidity = 10
        }
        limit = 5
    } | ConvertTo-Json -Depth 5

    $response = Invoke-WebRequest -Uri "$baseUrl/api/search" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 20
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
        $payload = $response.Content | ConvertFrom-Json
        $first = $payload.results[0]
        Write-Host "   Top result: $($first.city.name)"
        Write-Host "   Weather score: $($first.category_scores.weather)"
        Write-Host "   Transport score: $($first.category_scores.transportation)"
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
