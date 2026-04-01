# Multi-PC Deployment Guide: 350 KM Remote (Internet-Based)

## Overview
KVK System deployed across **350 km distance** with machines connecting via **Internet**.

- **Host Machine (192.168.31.99)**: PostgreSQL server + App
- **Remote Machines (350 km away)**: Only KVKSystem.exe (no local DB)

---

## ⚠️ IMPORTANT: Security Warning

Direct PostgreSQL exposure over internet is **NOT secure**. We will use **SSH Tunneling** (recommended) or **VPN** for encrypted connections.

---

## PART A: HOST MACHINE SETUP

### Step 1: Configure PostgreSQL to Listen on Network

Edit `C:\Program Files\PostgreSQL\17\data\postgresql.conf`:

Find and change:
```
listen_addresses = 'localhost'
```

To:
```
listen_addresses = '*'
```

### Step 2: Configure pg_hba.conf (Network Auth)

Edit `C:\Program Files\PostgreSQL\17\data\pg_hba.conf`

Add at the end:
```
# Allow all connections with MD5 password
host    kvk         postgres    0.0.0.0/0    md5
```

### Step 3: Restart PostgreSQL Service

```powershell
net stop PostgreSQL-X64-17
net start PostgreSQL-X64-17
```

### Step 4: Open Windows Firewall (Port 5432)

Run as Administrator:
```powershell
netsh advfirewall firewall add rule name="PostgreSQL" dir=in action=allow protocol=tcp localport=5432
```

### Step 5: Configure Router (Port Forwarding)

⚠️ **CRITICAL FOR INTERNET ACCESS:**

1. Open your router admin panel (usually 192.168.1.1)
2. Go to **Port Forwarding** settings
3. Set up:
   - **External Port:** 5432
   - **Internal IP:** 192.168.31.99
   - **Internal Port:** 5432
   - **Protocol:** TCP

This allows remote machines to reach PostgreSQL from internet.

### Step 6: Find Your Public IP

Go to: https://www.whatismyipaddress.com/

Example: `103.45.123.45` (your public IP)

**Note down this IP** - You'll give it to remote machines.

### Step 7: Update Host .env

```env
DB_HOST=192.168.31.99
DB_PORT=5432
DB_NAME=kvk
DB_USER=postgres
DB_PASSWORD=Ravi@2004
PG_BIN_DIR=C:\Program Files\PostgreSQL\17\bin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### Step 8: Test Local Connection

```powershell
psql -h 192.168.31.99 -U postgres -d kvk -c "SELECT version();"
```

---

## PART B: REMOTE MACHINE SETUP (350 KM Away)

### RECOMMENDED: SSH Tunneling Method

This is the **most secure** method for internet connectivity.

#### Step B1: Install OpenSSH (Remote Machine)

1. Download OpenSSH from: https://github.com/PowerShell/Win32-OpenSSH/releases
2. Extract to `C:\Program Files\OpenSSH\`
3. Run PowerShell as Admin:
   ```powershell
   cd C:\Program Files\OpenSSH
   .\Install-OpenSSH.ps1
   Start-Service sshd
   Set-Service -Name sshd -StartupType Automatic
   ```

#### Step B2: Create SSH Tunnel

On **remote machine**, create a PowerShell script named `start_tunnel.ps1`:

```powershell
# SSH Tunnel to Host Machine
# This script creates an encrypted tunnel to the database

$hostPublicIP = "103.45.123.45"  # Replace with YOUR public IP
$hostUsername = "Administrator"   # Username on host machine
$hostPort = 22                     # SSH port

# Start SSH tunnel
ssh -L 5432:192.168.31.99:5432 "$hostUsername@$hostPublicIP" -N
```

#### Step B3: Create Remote Machine .env

In same folder as `KVKSystem.exe`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kvk
DB_USER=postgres
DB_PASSWORD=Ravi@2004
PG_BIN_DIR=
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

**Key Points:**
- `DB_HOST=localhost` (tunnel redirects to host)
- SSH tunnel must be running BEFORE launching KVKSystem.exe

#### Step B4: Create Batch File to Auto-Start (Remote)

Create `start_kvk.bat`:

```batch
@echo off
REM Start SSH tunnel in background
start "PostgreSQL Tunnel" powershell -NoExit -Command "ssh -L 5432:192.168.31.99:5432 Administrator@103.45.123.45 -N"

REM Wait for tunnel to establish
timeout /t 2

REM Launch KVK System
KVKSystem.exe
```

**Usage:** Double-click `start_kvk.bat` to launch both tunnel and app.

#### Step B5: Test SSH Tunnel (Remote)

```powershell
ssh -L 5432:192.168.31.99:5432 Administrator@103.45.123.45 -N
```

Then in another PowerShell window:
```powershell
psql -h localhost -U postgres -d kvk -c "SELECT current_user;"
```

---

## ALTERNATIVE: Direct Internet Method (Less Secure)

If SSH tunneling is not feasible:

### On Remote Machine .env:

```env
DB_HOST=103.45.123.45
DB_PORT=5432
DB_NAME=kvk
DB_USER=postgres
DB_PASSWORD=Ravi@2004
PG_BIN_DIR=
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

**Replace `103.45.123.45` with your PUBLIC IP**

⚠️ **Security Risks:**
- Password sent over internet (not encrypted)
- PostgreSQL exposed to potential attacks
- Use only if behind corporate firewall

---

## PART C: FIREWALL RULES (Host Machine)

### Windows Defender Firewall

Add exceptions:

```powershell
# Allow SSH (if using SSH Tunnel)
netsh advfirewall firewall add rule name="SSH" dir=in action=allow protocol=tcp localport=22

# Allow PostgreSQL
netsh advfirewall firewall add rule name="PostgreSQL" dir=in action=allow protocol=tcp localport=5432
```

### Router Firewall

Forward these ports to your host machine (192.168.31.99):
- **Port 5432** → PostgreSQL traffic
- **Port 22** → SSH traffic (if using tunneling)

---

## PART D: TESTING MULTI-PC OVER INTERNET

### Test 1: From Remote Machine (350 KM Away)

```powershell
# Start SSH tunnel
ssh -L 5432:192.168.31.99:5432 Administrator@103.45.123.45 -N

# In another window, test connection
psql -h localhost -U postgres -d kvk -c "SELECT current_database();"
```

Expected: Shows `kvk` database

### Test 2: Run KVKSystem.exe

Once tunnel works:
1. Keep tunnel running
2. Launch `KVKSystem.exe`
3. Login with admin/admin123
4. Create test record
5. Check on host machine → should see same record

---

## PART E: DATA SYNC STRATEGY (Multi-Site)

### Daily Workflow

1. **Morning (Site A):** Sync data from Site B
   - Check for backup from previous day
   - Restore if needed
   
2. **Work During Day:** Everyone uses system
   
3. **End of Day (Host):** Backup database
   - KVKSystem.exe → Backup & Restore module
   - Save backup to cloud storage (OneDrive, Google Drive, etc.)

4. **Next Morning (Site B):** Download backup and check

### Weekly Full Backup

```powershell
# On Host Machine
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "D:\kvk\backups\kvk_backup_$timestamp.sql"

# Trigger backup via app (automatic)
# Then upload to cloud
Copy-Item $backupFile "C:\OneDrive\KVK_Backups\"
```

---

## PART F: TROUBLESHOOTING

### Error: "connection refused"
- [ ] Router port forwarding configured
- [ ] Windows Firewall allows port 5432
- [ ] SSH tunnel running (if using SSH method)
- [ ] PostgreSQL service started on host

### Error: "authentication failed for user 'postgres'"
- [ ] Password in .env matches host password
- [ ] PostgreSQL password is `Ravi@2004`
- [ ] Run: `psql -h hostIP -U postgres -c "\password"` to reset

### Error: "getaddrinfo failed"
- [ ] Check your public IP is correct
- [ ] Verify remote machine can reach internet
- [ ] Test ping: `ping 8.8.8.8`

### SSH Tunnel Won't Connect
- [ ] SSH service running on host: `Get-Service sshd`
- [ ] SSH port 22 forwarded in router
- [ ] Windows Firewall allows port 22
- [ ] Try: `ssh -v Administrator@103.45.123.45` (verbose mode)

### Slow 350 KM Connection
- [ ] Use SSH tunnel (encrypted, optimized)
- [ ] Reduce table page size (100 → 50 rows)
- [ ] Add connection pooling timeout
- [ ] Consider local caching if data heavy

---

## PART G: DEPLOYMENT CHECKLIST

### Host Machine
- [ ] PostgreSQL `listen_addresses = '*'`
- [ ] `pg_hba.conf` allows connections
- [ ] Windows Firewall ports 5432 & 22 open
- [ ] Router port forwarding configured (5432 → 192.168.31.99)
- [ ] Public IP found and noted
- [ ] SSH service running (net start sshd)
- [ ] Test local connection works: `psql -h 192.168.31.99 -U postgres -d kvk`

### Remote Machine
- [ ] OpenSSH installed and service running
- [ ] .env file created with correct DB_HOST
- [ ] SSH tunnel tested: `ssh -L 5432:... -N`
- [ ] Connection through tunnel works: `psql -h localhost -U postgres`
- [ ] `start_kvk.bat` created and tested
- [ ] KVKSystem.exe runs and shows data from host

### Network
- [ ] Firewall rules allow traffic
- [ ] Router port forwarding verified
- [ ] Both machines can ping each other (optional)
- [ ] Latency acceptable for 350 KM

---

## PART H: QUICK START (Remote Machine)

1. **Copy these files to remote machine:**
   - `KVKSystem.exe`
   - `.env` (with DB_HOST=localhost)
   - `start_kvk.bat` (updated with your public IP)

2. **On host machine, find public IP:**
   ```powershell
   # Or visit https://www.whatismyipaddress.com/
   ```

3. **Update `start_kvk.bat` with your public IP:**
   ```batch
   ssh -L 5432:192.168.31.99:5432 Administrator@YOUR_PUBLIC_IP -N
   ```

4. **Double-click `start_kvk.bat` on remote machine**

5. **When tunnel connects, KVKSystem.exe launches**

Done! Remote machine now works with central database 350 KM away.

---

## PART I: INTERNET SECURITY BEST PRACTICES

⚠️ **NEVER:**
- Share public IP widely
- Use weak PostgreSQL passwords
- Disable firewall
- Port forward without SSH encryption

✅ **DO:**
- Use SSH tunneling for remote access
- Change default PostgreSQL password
- Keep Windows updates current
- Use VPN if available
- Monitor PostgreSQL logs for suspicious activity

---

**Need help?** Use the error sections above or contact your IT administrator.
