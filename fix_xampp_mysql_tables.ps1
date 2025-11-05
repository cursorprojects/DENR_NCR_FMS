# Fix XAMPP MySQL Missing System Tables
# This script will recreate the mysql system database tables

Write-Host "XAMPP MySQL System Tables Fix" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Check if XAMPP MySQL exists
$xamppPaths = @(
    "C:\xampp",
    "C:\Program Files\xampp",
    "${env:ProgramFiles(x86)}\xampp"
)

$xamppPath = $null
foreach ($path in $xamppPaths) {
    if (Test-Path $path) {
        $xamppPath = $path
        Write-Host "Found XAMPP at: $xamppPath" -ForegroundColor Green
        break
    }
}

if (-not $xamppPath) {
    Write-Host "ERROR: Could not find XAMPP installation!" -ForegroundColor Red
    Write-Host "Please update the script with your XAMPP path." -ForegroundColor Yellow
    exit 1
}

$mysqlBin = Join-Path $xamppPath "mysql\bin"
$mysqlData = Join-Path $xamppPath "mysql\data"

if (-not (Test-Path $mysqlBin)) {
    Write-Host "ERROR: MySQL bin directory not found at: $mysqlBin" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "IMPORTANT: This will recreate the MySQL system database." -ForegroundColor Yellow
Write-Host "Your user databases (like 'fleetmanagement') should be safe, but" -ForegroundColor Yellow
Write-Host "any MySQL users and privileges will be reset to defaults." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Do you want to continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Stopping MySQL (if running)..." -ForegroundColor Cyan

# Try to stop MySQL process
$mysqlProcess = Get-Process -Name "mysqld" -ErrorAction SilentlyContinue
if ($mysqlProcess) {
    Write-Host "MySQL process found. Please stop it from XAMPP Control Panel first!" -ForegroundColor Red
    Write-Host "Press any key after stopping MySQL..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host "MySQL is not running (good)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Backing up mysql database folder..." -ForegroundColor Cyan

$mysqlDbPath = Join-Path $mysqlData "mysql"
$mysqlDbBackup = Join-Path $mysqlData "mysql_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

if (Test-Path $mysqlDbPath) {
    Write-Host "Creating backup at: $mysqlDbBackup" -ForegroundColor Yellow
    Copy-Item -Path $mysqlDbPath -Destination $mysqlDbBackup -Recurse -Force
    Write-Host "Backup created successfully" -ForegroundColor Green
} else {
    Write-Host "MySQL database folder not found (will be created)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Recreating mysql system database..." -ForegroundColor Cyan

# Navigate to mysql bin directory
Push-Location $mysqlBin

# Check if mysql_install_db exists (older versions) or use mysqld --initialize
$installDb = Join-Path $mysqlBin "mysql_install_db.exe"
$mysqld = Join-Path $mysqlBin "mysqld.exe"

if (Test-Path $installDb) {
    Write-Host "Using mysql_install_db.exe..." -ForegroundColor Yellow
    & $installDb --datadir=$mysqlData
} else {
    Write-Host "mysql_install_db.exe not found, using mysqld --initialize-insecure..." -ForegroundColor Yellow
    Write-Host "This will recreate system tables with no root password." -ForegroundColor Yellow
    
    # Remove old mysql folder if it exists but is corrupted
    if (Test-Path $mysqlDbPath) {
        Write-Host "Removing corrupted mysql database..." -ForegroundColor Yellow
        Remove-Item -Path $mysqlDbPath -Recurse -Force
    }
    
    # Initialize database
    & $mysqld --initialize-insecure --datadir=$mysqlData --console
}

Pop-Location

Write-Host ""
Write-Host "Step 4: Setting root password (optional)..." -ForegroundColor Cyan
Write-Host "The root user will have no password after this fix." -ForegroundColor Yellow
Write-Host "You can set it later or leave it empty (as per your Django config)." -ForegroundColor Yellow

Write-Host ""
Write-Host "FIX COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start MySQL from XAMPP Control Panel" -ForegroundColor White
Write-Host "2. Verify it starts without errors" -ForegroundColor White
Write-Host "3. Your 'fleetmanagement' database should still exist" -ForegroundColor White
Write-Host "4. If needed, recreate any MySQL users from the admin panel" -ForegroundColor White
Write-Host ""
Write-Host "To test connection:" -ForegroundColor Cyan
Write-Host "  cd $mysqlBin" -ForegroundColor White
Write-Host "  .\mysql.exe -u root" -ForegroundColor White
Write-Host ""

