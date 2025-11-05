# XAMPP MySQL Troubleshooting Guide

## Quick Fix Steps (Try in Order)

### 1. Check Port Conflicts (Most Common Issue)

MySQL might be trying to use port 3306, but it's already taken by another service.

**Check what's using port 3306:**
```powershell
netstat -ano | findstr :3306
```

**If something is using it, kill the process:**
```powershell
# Replace <PID> with the process ID from above
taskkill /PID <PID> /F
```

**Note:** Your Django is configured for port 3307, so you may need to:
- Configure XAMPP MySQL to use port 3307 in `xampp\mysql\bin\my.ini`, OR
- Change Django settings to use port 3306

### 2. Check for Windows MySQL Service

A Windows MySQL service might be conflicting with XAMPP:

**Check if MySQL service exists:**
```powershell
Get-Service -Name "*mysql*"
```

**Stop the service:**
```powershell
Stop-Service -Name "MySQL" -Force
```

**Disable it from starting automatically:**
```powershell
Set-Service -Name "MySQL" -StartupType Disabled
```

### 3. Check XAMPP MySQL Logs

1. Click the **"Logs"** button next to MySQL in XAMPP Control Panel
2. Look for specific error messages
3. Common errors:
   - `Can't create/write to file` - Permission issue
   - `InnoDB: Assertion failure` - Database corruption
   - `Access denied` - Authentication issue
   - `Port already in use` - Port conflict

### 4. Run XAMPP as Administrator

Right-click XAMPP Control Panel → **Run as Administrator**

This fixes permission issues.

### 5. Check MySQL Configuration (my.ini)

Location: `C:\xampp\mysql\bin\my.ini`

**Common fixes:**
- Make sure `port = 3306` (or your desired port)
- Check `datadir` path exists and has permissions
- Verify `basedir` points to correct XAMPP MySQL directory

**If you need MySQL on port 3307 for Django:**
```ini
[mysqld]
port = 3307
```

### 6. Fix Database Corruption

If the database is corrupted:

1. **Backup your data** (if possible)
2. Stop MySQL in XAMPP
3. Go to `C:\xampp\mysql\data`
4. **Backup important databases** (copy the folders)
5. Delete `ibdata1`, `ib_logfile0`, `ib_logfile1`
6. Delete folders for databases you don't need
7. Restart MySQL

⚠️ **WARNING:** This will delete databases. Only do this if you have backups!

### 7. Check Windows Event Viewer

1. Press `Win + R`
2. Type `eventvwr.msc` and press Enter
3. Go to **Windows Logs → Application**
4. Look for MySQL errors around the shutdown time

### 8. Reinstall XAMPP MySQL (Last Resort)

1. Stop all XAMPP services
2. Uninstall XAMPP (or just MySQL component)
3. Delete `C:\xampp\mysql` folder
4. Reinstall XAMPP
5. Restore your databases from backup

## Your Specific Configuration

Your Django settings show you're using:
- **Port:** 3307
- **Database:** fleetmanagement
- **User:** root
- **Password:** (empty)

**Make sure XAMPP MySQL is configured to run on port 3307**, or update Django to use port 3306.

## Testing MySQL Connection

After fixing the issue, test the connection:

```powershell
# From XAMPP MySQL bin directory
cd C:\xampp\mysql\bin
.\mysql.exe -u root -p
```

Or test from Python:
```python
import pymysql
conn = pymysql.connect(host='localhost', port=3307, user='root', password='')
print("Connected successfully!")
conn.close()
```

## Still Having Issues?

Run the PowerShell troubleshooting script:
```powershell
.\troubleshoot_xampp_mysql.ps1
```

For detailed error messages, check:
- XAMPP MySQL error log: `C:\xampp\mysql\data\*.err`
- XAMPP Control Panel → Logs button
- Windows Event Viewer → Application logs

