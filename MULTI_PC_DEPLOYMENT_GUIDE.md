# Multi-PC Deployment Guide: KVK Database Management System

## Overview
This guide explains how to set up KVK Database System across multiple machines:
- **Host Machine (192.168.31.99)**: Runs PostgreSQL server (central database)
- **Remote Machines**: Run KVKSystem.exe to connect to central database (out-of-station locations)

---

## PART A: HOST MACHINE SETUP (192.168.31.99)

### Step 1: Configure PostgreSQL to Accept Remote Connections

PostgreSQL by default only listens on `localhost` (127.0.0.1). We need to configure it to listen on all network interfaces.

#### Option 1: Via pgAdmin
1. Open pgAdmin on the host machine
2. Right-click **Server** → **Properties**
3. Go to **Connection** tab
4. Verify the database is running and accessible

#### Option 2: Manually Edit PostgreSQL Config
1. Find PostgreSQL configuration file:
   - Windows: `C:\Program Files\PostgreSQL\17\data\postgresql.conf` (adjust version number)
   
2. Open `postgresql.conf` in Notepad
   
3. Find line: `listen_addresses = 'localhost'`
   
4. Change to: `listen_addresses = '*'`
   
5. Find line: `#port = 5432`
   
6. Change to: `port = 5432` (uncomment if needed)
   
7. Save and close
   
8. Restart PostgreSQL Service:
   ```
   net stop PostgreSQL-X64-17
   net start PostgreSQL-X64-17
   ```
   (Adjust version number as needed)

### Step 2: Configure PostgreSQL to Allow Remote Authentication

Find the file `pg_hba.conf` in the same PostgreSQL data directory:

```
C:\Program Files\PostgreSQL\17\data\pg_hba.conf
```

Add this line near the end (before any `reject` rules):

```
host    kvk         postgres    192.168.31.0/24    md5
```

This allows connections from IP range 192.168.31.0-192.168.31.255 (your local network).

**Note:** For internet access, you may need to configure:
- Firewall rules (open port 5432)
- VPN or SSH tunneling for security
- SSL certificates for encrypted connections

After editing, restart PostgreSQL:
```
net stop PostgreSQL-X64-17
net start PostgreSQL-X64-17
```

### Step 3: Update Host's .env File

Edit `d:\kvk\.env` on the host machine:

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

### Step 4: Test Remote Connectivity (from host)

Run this command to verify PostgreSQL accepts remote connections:

```powershell
psql -h 192.168.31.99 -U postgres -d kvk -c "SELECT version();"
```

Password will be: `Ravi@2004`

**Expected output:** PostgreSQL version info (if successful)

---

## PART B: REMOTE MACHINES SETUP (Out-of-Station)

### Step 1: Copy KVKSystem.exe and .env to Remote Machine

1. From host machine, copy:
   - `dist/KVKSystem.exe` 
   - Template `.env` file (provided below)

2. Create a folder on remote machine (e.g., `C:\KVK\`)

3. Place files in this folder

### Step 2: Create .env on Remote Machine

Create a file named `.env` in the same folder as `KVKSystem.exe`:

```env
DB_HOST=192.168.31.99
DB_PORT=5432
DB_NAME=kvk
DB_USER=postgres
DB_PASSWORD=Ravi@2004
PG_BIN_DIR=
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

**Important:**
- `DB_HOST` must be the IP address or hostname of your host machine
- `DB_PASSWORD` must match the PostgreSQL password on the host
- Leave `PG_BIN_DIR` empty (remote machines don't need backup tools)

### Step 3: Test Connection

Before running the full app, test database connectivity:

```powershell
# On remote machine, open PowerShell and run:
psql -h 192.168.31.99 -U postgres -d kvk -c "SELECT current_user, current_database();"
```

Enter password: `Ravi@2004`

**Expected output:** Shows current user and database name

### Step 4: Run KVKSystem.exe

Double-click `KVKSystem.exe` to launch the application.

**Login credentials:**
- Username: `admin`
- Password: `admin123`

All data entered will be saved to the central database on the host machine.

---

## PART C: TESTING MULTI-PC SETUP

### Test Data Consistency

1. **On Host Machine:**
   - Run KVKSystem.exe
   - Login as admin
   - Create a test activity record
   - Check in pgAdmin that data is saved

2. **On Remote Machine:**
   - Run KVKSystem.exe
   - Login as admin
   - View records → Should see the record created on host machine
   - Create another test record

3. **Back on Host Machine:**
   - Refresh view → Should see the record created on remote machine

---

## PART D: TROUBLESHOOTING

### Error: "could not translate host name to address"
**Cause:** Incorrect IP address or hostname in `.env`
**Solution:** 
- Verify `DB_HOST` is correct (192.168.31.99 or available on network)
- Try connecting with the hostname instead: `psql -h HOSTNAME -U postgres`

### Error: "connection refused"
**Cause:** PostgreSQL not listening on network interface or firewall blocking
**Solution:**
- Verify `listen_addresses = '*'` in PostgreSQL config
- Check Windows Firewall allows PostgreSQL (port 5432)
- Add firewall rule: `netsh advfirewall firewall add rule name="PostgreSQL" dir=in action=allow protocol=tcp localport=5432`

### Error: "authentication failed"
**Cause:** Wrong password or user not configured
**Solution:**
- Verify `DB_PASSWORD` matches the PostgreSQL password
- Check `postgres` user exists in PostgreSQL
- Ensure `pg_hba.conf` allows MD5 authentication from your network

### Error: "database kvk does not exist"
**Cause:** Database not initialized on host
**Solution:**
- Run `d:\kvk\main.py` once on the host machine to initialize database
- Verify database exists: `psql -h 192.168.31.99 -U postgres -l`

---

## PART E: NETWORK SECURITY (FOR INTERNET ACCESS)

⚠️ **WARNING:** Direct PostgreSQL exposure over internet is **NOT recommended**.

For internet access, use one of these secure methods:

### Option 1: SSH Tunneling (Recommended)
```powershell
# On remote machine, create SSH tunnel to host
ssh -L 5432:localhost:5432 user@192.168.31.99

# Then update .env to use localhost instead
DB_HOST=localhost
```

### Option 2: VPN
- Set up VPN on host machine
- Connect remote machines via VPN
- Use internal IP in `.env`

### Option 3: PostgreSQL SSL/TLS
- Generate SSL certificates
- Configure PostgreSQL with SSL
- Update remote `.env` with SSL connection string

---

## PART F: DATA BACKUP ACROSS MULTIPLE PCs

### Weekly Backup Protocol

1. **On Host Machine** (every week):
   - Open KVKSystem.exe
   - Go to **Backup and Restore** module
   - Click **Backup Database**
   - Save to external drive or cloud storage

2. **Before Updating App**:
   - Always create a backup first
   - Copy backup file to external storage
   - Only then update .exe on remote machines

---

## PART G: DEPLOYMENT CHECKLIST

- [ ] PostgreSQL configured to listen on `*` (all interfaces)
- [ ] `pg_hba.conf` allows remote connections from your network
- [ ] `postgresql.conf` and `pg_hba.conf` changes applied (service restarted)
- [ ] Host `.env` updated with `DB_HOST=192.168.31.99`
- [ ] Remote `.env` file created with correct host IP and password
- [ ] Connectivity test successful: `psql -h 192.168.31.99 -U postgres -d kvk`
- [ ] KVKSystem.exe runs on both host and remote machines
- [ ] Test data created on one machine visible on other machine
- [ ] Backup strategy documented

---

## PART H: QUICK REFERENCE

| Item | Host (192.168.31.99) | Remote Machine |
|------|----------------------|-----------------|
| PostgreSQL | ✓ Must run here | ✗ Not needed |
| KVKSystem.exe | ✓ Can run | ✓ Must run |
| .env file | ✓ Has DB_HOST=192.168.31.99 | ✓ Has DB_HOST=192.168.31.99 |
| Backup tool | ✓ Available | ✗ Not needed |
| Database access | Direct | Via network (host IP) |

---

For questions or issues, refer to the **TROUBLESHOOTING** section above.
