param()
$ErrorActionPreference = 'Stop'

function Command-Exists { param($name) return (Get-Command $name -ErrorAction SilentlyContinue) -ne $null }

function Wait-ForElasticsearch {
	param([int]$MaxWaitSeconds = 120)
	
	Write-Host "Waiting for Elasticsearch to be ready..."
	$elapsed = 0
	$interval = 5
	
	while ($elapsed -lt $MaxWaitSeconds) {
		try {
			$response = Invoke-WebRequest -Uri "http://localhost:9200/_cluster/health" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
			if ($response.StatusCode -eq 200) {
				$content = $response.Content | ConvertFrom-Json
				if ($content.status -eq "green" -or $content.status -eq "yellow") {
					Write-Host "Elasticsearch is ready with status: $($content.status)"
					Start-Sleep -Seconds 5  # Extra delay to ensure full readiness
					return $true
				}
			}
		} catch {
			# Elasticsearch not ready yet
		}
		
		Write-Host "  Waiting for Elasticsearch... ($elapsed/$MaxWaitSeconds seconds)"
		Start-Sleep -Seconds $interval
		$elapsed += $interval
	}
	
	Write-Warning "Elasticsearch did not become ready within $MaxWaitSeconds seconds. Backend may fail to connect."
	return $false
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Backend = Join-Path $Root 'backend'
$Frontend = Join-Path $Root 'frontend'

Write-Host "`n== Project root: $Root`n"

# 1) Start Elasticsearch + Kibana via docker-compose (try docker-compose, then docker compose)
if (Command-Exists 'docker-compose') {
	Write-Host "Starting Docker containers with docker-compose..."
	cd $Root
	docker-compose up -d
} elseif (Command-Exists 'docker') {
	Write-Host "Starting Docker containers with 'docker compose'..."
	cd $Root
	docker compose up -d
} else {
	Write-Warning "Docker CLI not found. Please install Docker Desktop and ensure 'docker' is on PATH."
}

# Wait for Elasticsearch to be ready
Wait-ForElasticsearch

# 2) Backend: create venv if needed, install requirements, start backend in new window
if (-not (Test-Path $Backend)) {
	Write-Warning "Backend folder not found at $Backend. Skipping backend setup."
} else {
	if (-not (Command-Exists 'python')) {
		Write-Warning "Python not found. Please install Python 3.10+ and re-run the script."
	} else {
		$VenvPath = Join-Path $Backend 'venv'
		$VenvPython = Join-Path $VenvPath 'Scripts\python.exe'

		if (-not (Test-Path $VenvPython)) {
			Write-Host "Creating Python virtual environment..."
			& python -m venv $VenvPath
		}

		if (-not (Test-Path $VenvPython)) {
			Write-Warning "Virtual environment creation failed or python executable missing in venv."
		} else {
			Write-Host "Upgrading pip and installing backend requirements..."
			& $VenvPython -m pip install --upgrade pip
			$reqFile = Join-Path $Backend 'requirements.txt'
			if (Test-Path $reqFile) {
				Write-Host "Installing dependencies from requirements.txt..."
				& $VenvPython -m pip install -r $reqFile
				if ($LASTEXITCODE -ne 0) {
					Write-Warning "pip install failed. Check requirements.txt and ensure all packages (e.g., pandas) are listed."
					Write-Warning "Manually verify requirements.txt contains: pandas, flask, elasticsearch, flask-cors, etc."
					Write-Host "`nAttempting to install Flask manually as a fallback..."
					& $VenvPython -m pip install flask flask-cors "elasticsearch==7.17.9" pandas googlemaps
				}
			} else {
				Write-Warning "requirements.txt not found in backend. Installing essential packages manually..."
				& $VenvPython -m pip install flask flask-cors "elasticsearch==7.17.9" pandas googlemaps
			}

			# Verify Flask is installed
			Write-Host "Verifying Flask installation..."
			$flaskCheck = & $VenvPython -c "import flask; print('OK')" 2>&1
			if ($flaskCheck -notmatch "OK") {
				Write-Error "Flask installation verification failed. Cannot start backend."
				Write-Host "Please run manually: & '$VenvPython' -m pip install flask flask-cors elasticsearch pandas"
				Write-Host "Press any key to continue with frontend setup..."
				$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
			} else {
				Write-Host "Flask verified successfully."

			# Kill existing backend processes on port 5000
			Write-Host "Checking for existing backend processes..."
			$existingBackend = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
			if ($existingBackend) {
				$processId = $existingBackend.OwningProcess
				Write-Host "Found existing backend on port 5000 (PID: $processId). Stopping it..."
				Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
				Start-Sleep -Seconds 2
			}

			# Also try to kill by process name (app.py)
			Get-Process | Where-Object { $_.CommandLine -like "*app.py*" } | ForEach-Object {
				Write-Host "Stopping old backend process: $($_.Id)"
				Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
			}

			# Read Google Maps API key from apikey.txt
			$apiKeyFile = Join-Path $Backend 'apikey.txt'
			$apiKey = ""
			if (Test-Path $apiKeyFile) {
				Write-Host "Reading Google Maps API key from apikey.txt..."
				$apiKey = (Get-Content $apiKeyFile -Raw).Trim()
			} else {
				Write-Warning "apikey.txt not found in backend. Google Maps features may not work."
			}

			Write-Host "Starting backend in a new PowerShell window..."
			if ($apiKey) {
				$cmd = "cd '$Backend'; `$env:GOOGLE_MAPS_API_KEY='$apiKey'; & '$VenvPython' app.py"
			} else {
				$cmd = "cd '$Backend'; & '$VenvPython' app.py"
			}
			Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoExit', '-Command', $cmd -WorkingDirectory $Backend
			}
		}
	}
}

# 3) Frontend: npm install if needed, start dev server in new window
if (-not (Test-Path $Frontend)) {
	Write-Warning "Frontend folder not found at $Frontend. Skipping frontend setup."
} else {
	if (-not (Command-Exists 'node')) {
		Write-Warning "Node.js not found. Please install Node 20+ and re-run the script."
	} else {
		# Kill existing frontend dev server
		Write-Host "Checking for existing frontend dev server..."
		$existingFrontend = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
		if ($existingFrontend) {
			$processId = $existingFrontend.OwningProcess
			Write-Host "Found existing frontend on port 5173 (PID: $processId). Stopping it..."
			Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
			Start-Sleep -Seconds 2
		}

<<<<<<< HEAD
		Push-Location $Frontend

		$nodeModules = Join-Path $Frontend 'node_modules'
		$pkgJson = Join-Path $Frontend 'package.json'
		$pkgLock = Join-Path $Frontend 'package-lock.json'

		$shouldNpmInstall = $false

		# Install if node_modules is missing
		if (-not (Test-Path $nodeModules)) { $shouldNpmInstall = $true }

		# Install if package.json changed after package-lock.json
		if ((Test-Path $pkgJson) -and (Test-Path $pkgLock)) {
			if ((Get-Item $pkgJson).LastWriteTime -gt (Get-Item $pkgLock).LastWriteTime) {
				$shouldNpmInstall = $true
			}
		}

		# Install if chart deps are missing (fixes "Failed to resolve import chart.js/auto")
		$chartJsPkg = Join-Path $nodeModules 'chart.js\package.json'
		$reactChartPkg = Join-Path $nodeModules 'react-chartjs-2\package.json'
		if (-not (Test-Path $chartJsPkg) -or -not (Test-Path $reactChartPkg)) {
			$shouldNpmInstall = $true
		}

		if ($shouldNpmInstall) {
			Write-Host "Installing/updating frontend dependencies (npm install)..."
			npm install
		}

		Pop-Location

=======
		$nodeModules = Join-Path $Frontend 'node_modules'
		if (-not (Test-Path $nodeModules)) {
			Write-Host "Installing frontend dependencies (npm install)..."
			Push-Location $Frontend
			npm install
			Pop-Location
		}
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
		Write-Host "Starting frontend dev server in a new PowerShell window..."
		$cmd2 = "cd '$Frontend'; npm run dev"
		Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoExit', '-Command', $cmd2 -WorkingDirectory $Frontend
	}
}

Write-Host "`n== Done. Useful links:"
Write-Host " - Frontend: http://localhost:5173"
Write-Host " - Backend:  http://localhost:5000"
Write-Host "`n== API Endpoints:"
Write-Host " - GET /api/municipalities/regions - List all regions"
Write-Host " - GET /api/municipality/<id> - Get municipality by ID"
Write-Host " - POST /api/load - Load data into Elasticsearch"
Write-Host " - POST /api/score - Calculate scores"
Write-Host "`n== Debugging tips for white screen issues:"
Write-Host " 1. Open browser DevTools (F12) and check the Console tab for JavaScript errors"
Write-Host " 2. Check the Network tab to see if API responses contain valid data"
Write-Host " 3. Look for React error boundaries or component rendering issues"
Write-Host " 4. Common causes: undefined data properties, routing errors, or missing error handling"
Write-Host " 5. VERIFY API ENDPOINT MISMATCH: Frontend may be calling wrong endpoint names"
Write-Host "`n== Diagnose White Screen:"
Write-Host " Run: .\diagnose-frontend.ps1"
Write-Host " This will show the API response structure and help identify the issue"
Write-Host "`n== Quick API Test:"
Write-Host " Test if backend is responding: curl http://localhost:5000/api/municipalities/regions"
Write-Host "`nIf PowerShell blocks script execution, run: powershell -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Definition)`""
