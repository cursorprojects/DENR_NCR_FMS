# XAMPP MySQL Troubleshooting Script
# Run this script in PowerShell to diagnose MySQL issues

Write-Host "XAMPP MySQL Troubleshooting Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if port 3306 is in use
Write-Host "1. Checking if port 3306 is in use..." -ForegroundColor Yellow
$port3306 = Get-NetTCPConnection -LocalPort 3306 -ErrorAction SilentlyContinue
if ($port3306) {
    Write-Host "   ERROR: Port 3306 is already in use!" -ForegroundColor Red
    Write-Host "   Process using port 3306:" -ForegroundColor Yellow
    $process = Get-Process -Id $port3306.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "   - Process Name: $($process.ProcessName)" -ForegroundColor Red
        Write-Host "   - Process ID: $($process.Id)" -ForegroundColor Red
        Write-Host "   - Command: netstat -ano | findstr :3306" -ForegroundColor Yellow
    }
} else {
    Write-Host "   Port 3306 is free" -ForegroundColor Green
}

# Check if port 3307 is in use (as per your Django config)
Write-Host ""
Write-Host "2. Checking if port 3307 is in use (Django config port)..." -ForegroundColor Yellow
$port3307 = Get-NetTCPConnection -LocalPort 3307 -ErrorAction SilentlyContinue
if ($port3307) {
    Write-Host "   Port 3307 is in use" -ForegroundColor Yellow
    $process = Get-Process -Id $port3307.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "   - Process Name: $($process.ProcessName)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   Port 3307 is free" -ForegroundColor Green
}

# Check for MySQL service
Write-Host ""
Write-Host "3. Checking for MySQL Windows Service..." -ForegroundColor Yellow
$mysqlService = Get-Service -Name "*mysql*" -ErrorAction SilentlyContinue
if ($mysqlService) {
    Write-Host "   Found MySQL service(s):" -ForegroundColor Yellow
    $mysqlService | ForEach-Object {
        Write-Host "   - $($_.Name): $($_.Status)" -ForegroundColor $(if ($_.Status -eq 'Running') { 'Red' } else { 'Green' })
        if ($_.Status -eq 'Running') {
            Write-Host "     WARNING: A Windows MySQL service is running. This may conflict with XAMPP!" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   No MySQL Windows service found (good for XAMPP)" -ForegroundColor Green
}

# Check XAMPP directory
Write-Host ""
Write-Host "4. Checking common XAMPP locations..." -ForegroundColor Yellow
$xamppPaths = @(
    "C:\xampp",
    "C:\Program Files\xampp",
    "${env:ProgramFiles(x86)}\xampp"
)

$foundXampp = $false
foreach ($path in $xamppPaths) {
    if (Test-Path $path) {
        Write-Host "   Found XAMPP at: $path" -ForegroundColor Green
        $foundXampp = $true
        
        # Check for my.ini
        $myIni = Join-Path $path "mysql\bin\my.ini"
        if (Test-Path $myIni) {
            Write-Host "   MySQL config found at: $myIni" -ForegroundColor Green
        }
        
        # Check for data directory
        $dataDir = Join-Path $path "mysql\data"
        if (Test-Path $dataDir) {
            Write-Host "   MySQL data directory found at: $dataDir" -ForegroundColor Green
        }
    }
}

if (-not $foundXampp) {
    Write-Host "   Could not find XAMPP installation in common locations" -ForegroundColor Yellow
}

# Check Event Viewer for MySQL errors
Write-Host ""
Write-Host "5. Suggestions for further troubleshooting:" -ForegroundColor Yellow
Write-Host "   - Check XAMPP MySQL logs: Click 'Logs' button in XAMPP Control Panel" -ForegroundColor White
Write-Host "   - Check Windows Event Viewer: winrm quickconfig (if needed)" -ForegroundColor White
Write-Host "   - Verify my.ini configuration is correct" -ForegroundColor White
Write-Host "   - Try running XAMPP Control Panel as Administrator" -ForegroundColor White
Write-Host ""
Write-Host "Common fixes:" -ForegroundColor Cyan
Write-Host "   1. Stop any Windows MySQL services" -ForegroundColor White
Write-Host "   2. Kill processes using port 3306: netstat -ano | findstr :3306" -ForegroundColor White
Write-Host "   3. Check XAMPP MySQL error log in: xampp\mysql\data\*.err" -ForegroundColor White
Write-Host "   4. Backup and recreate database if corrupted" -ForegroundColor White
Write-Host "   5. Reinstall XAMPP if all else fails" -ForegroundColor White
Write-Host ""

