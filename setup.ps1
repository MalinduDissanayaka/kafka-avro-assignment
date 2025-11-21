# Setup Script for Kafka Avro Assignment
# Run this script to set up the entire environment

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "KAFKA AVRO ASSIGNMENT - SETUP SCRIPT" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker is running" -ForegroundColor Green
Write-Host ""

# Step 2: Start Kafka Infrastructure
Write-Host "Step 2: Starting Kafka infrastructure..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Docker containers" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Kafka infrastructure started" -ForegroundColor Green
Write-Host ""

# Step 3: Wait for services to be ready
Write-Host "Step 3: Waiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host "✅ Services should be ready" -ForegroundColor Green
Write-Host ""

# Step 4: Install Python dependencies
Write-Host "Step 4: Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 5: Verify containers
Write-Host "Step 5: Verifying containers..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# Final instructions
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open a new terminal and run: " -NoNewline -ForegroundColor White
Write-Host "python consumer.py" -ForegroundColor Cyan
Write-Host "2. Open another terminal and run: " -NoNewline -ForegroundColor White
Write-Host "python producer.py" -ForegroundColor Cyan
Write-Host "3. (Optional) Monitor DLQ: " -NoNewline -ForegroundColor White
Write-Host "python dlq_monitor.py" -ForegroundColor Cyan
Write-Host ""
