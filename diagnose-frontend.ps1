$ErrorActionPreference = 'Continue'

Write-Host ""
Write-Host "=== API Data Diagnostic Tool ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000"

# Test the actual endpoint that's being called
Write-Host "Testing GET /api/municipality/115..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/municipality/115" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] API Response: SUCCESS (200 OK)" -ForegroundColor Green
        
        $data = $response.Content | ConvertFrom-Json
        
        Write-Host ""
        Write-Host "=== FULL JSON RESPONSE ===" -ForegroundColor Cyan
        Write-Host ($data | ConvertTo-Json -Depth 10)
        
        Write-Host ""
        Write-Host "=== PROPERTY BY PROPERTY ANALYSIS ===" -ForegroundColor Cyan
        $data.PSObject.Properties | ForEach-Object {
            $propName = $_.Name
            $propValue = $_.Value
            $propType = if ($propValue -eq $null) { "NULL" } else { $propValue.GetType().Name }
            
            Write-Host ""
            Write-Host "Property: $propName" -ForegroundColor Yellow
            Write-Host "  Type: $propType" -ForegroundColor Gray
            Write-Host "  Value: $propValue" -ForegroundColor White
            
            # Check if this is population or area
            if ($propName -match "population|area" -or $propName -match "Population|Area") {
                if ($propValue -eq $null -or $propValue -eq "") {
                    Write-Host "  >>> THIS IS NULL/EMPTY! <<<" -ForegroundColor Red
                } else {
                    Write-Host "  >>> This looks good! <<<" -ForegroundColor Green
                }
            }
        }
        
        Write-Host ""
        Write-Host "=== FRONTEND MAPPING CHECK ===" -ForegroundColor Yellow
        Write-Host "The frontend is looking for these property names:"
        Write-Host "  - population OR Population"
        Write-Host "  - area OR Area"
        Write-Host ""
        
        # Check what the backend actually has
        $hasPopulation = $data.PSObject.Properties.Name -contains "population"
        $hasPopulationCap = $data.PSObject.Properties.Name -contains "Population"
        $hasArea = $data.PSObject.Properties.Name -contains "area"
        $hasAreaCap = $data.PSObject.Properties.Name -contains "Area"
        
        Write-Host "Backend actually has:" -ForegroundColor Cyan
        if ($hasPopulation) {
            Write-Host "  [FOUND] 'population' = $($data.population)" -ForegroundColor Green
        } elseif ($hasPopulationCap) {
            Write-Host "  [FOUND] 'Population' = $($data.Population)" -ForegroundColor Green
        } else {
            Write-Host "  [NOT FOUND] No 'population' or 'Population' property!" -ForegroundColor Red
            Write-Host "  Available properties that might be population:" -ForegroundColor Yellow
            $data.PSObject.Properties | Where-Object { $_.Name -match "pop|Pop|people|People|citizens|Citizens|inhabitants|Inhabitants" } | ForEach-Object {
                Write-Host "    - $($_.Name) = $($_.Value)" -ForegroundColor White
            }
        }
        
        if ($hasArea) {
            Write-Host "  [FOUND] 'area' = $($data.area)" -ForegroundColor Green
        } elseif ($hasAreaCap) {
            Write-Host "  [FOUND] 'Area' = $($data.Area)" -ForegroundColor Green
        } else {
            Write-Host "  [NOT FOUND] No 'area' or 'Area' property!" -ForegroundColor Red
            Write-Host "  Available properties that might be area:" -ForegroundColor Yellow
            $data.PSObject.Properties | Where-Object { $_.Name -match "area|Area|size|Size|surface|Surface|km|Km" } | ForEach-Object {
                Write-Host "    - $($_.Name) = $($_.Value)" -ForegroundColor White
            }
        }
        
    }
} catch {
    Write-Host "[FAILED] API FAILED: $_" -ForegroundColor Red
    Write-Host "Backend may not be running on port 5000" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== SOLUTION ===" -ForegroundColor Cyan
Write-Host "Once you see the actual property names above, update MunicipalityPanel.jsx"
Write-Host "to use those exact names instead of 'population' and 'area'."
