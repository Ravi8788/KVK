# ✅ HOST MACHINE SETUP CHECKLIST

**Machine:** 192.168.31.99  
**Public IP:** 47.11.41.71  
**Start Date:** March 19, 2026

---

## 🖥️ PHASE 1: PostgreSQL CONFIGURATION

### ☐ Step 1: Locate PostgreSQL Config Files

Find these files:
```
C:\Program Files\PostgreSQL\17\data\postgresql.conf
C:\Program Files\PostgreSQL\17\data\pg_hba.conf
```

(If PostgreSQL 16, 15, 14, adjust version number)

### ☐ Step 2: Edit `postgresql.conf`

1. **Open in Notepad:**
   - Right-click `postgresql.conf` → Open with Notepad

2. **Find line:** `listen_addresses = 'localhost'`

3. **Change to:** `listen_addresses = '*'`

4. **Find line:** `#port = 5432` (with # in front)

5. **Change to:** `port = 5432` (remove # if present)

6. **Save file** (Ctrl+S)

### ☐ Step 3: Edit `pg_hba.conf`

1. **Open in Notepad:**
   - Right-click `pg_hba.conf` → Open with Notepad

2. **Go to end of file** (Ctrl+End)

3. **Add this NEW line:**
```
host    kvk         postgres    0.0.0.0/0    md5
```

This allows connections from anywhere (we'll restrict with firewall later).

4. **Save file** (Ctrl+S)

### ☐ Step 4: Restart PostgreSQL Service

Open **Command Prompt as Administrator** and run:

```cmd
net stop PostgreSQL-X64-17
net start PostgreSQL-X64-17
```

**Expected output:**
```
The PostgreSQL-X64-17 service is stopping.
The PostgreSQL-X64-17 service has been stopped.
The PostgreSQL-X64-17 service is starting.
The PostgreSQL-X64-17 service has been started successfully.
```

---

## 🔒 PHASE 2: WINDOWS FIREWALL RULES

### ☐ Step 5: Add PostgreSQL Firewall Rule

Open **PowerShell as Administrator** and run:

```powershell
netsh advfirewall firewall add rule name="PostgreSQL" dir=in action=allow protocol=tcp localport=5432
```

**Expected:** `Ok.`

### ☐ Step 6: Add SSH Firewall Rule

```powershell
netsh advfirewall firewall add rule name="SSH" dir=in action=allow protocol=tcp localport=22
```

**Expected:** `Ok.`

### ☐ Step 7: Verify Rules Added

```powershell
netsh advfirewall firewall show rule name="PostgreSQL"
netsh advfirewall firewall show rule name="SSH"
```

Both should show: `Enabled: Yes` and `Direction: In`

---

## 🌐 PHASE 3: ROUTER PORT FORWARDING

### ☐ Step 8: Access Your Router

1. Open browser
2. Go to: `http://192.168.1.1` or `http://192.168.0.1`
3. Login (default: admin/admin or check router manual)

### ☐ Step 9: Create Rule 1 - PostgreSQL

Find **Port Forwarding** menu (name varies by router):

| Setting | Value |
|---------|-------|
| Rule Name | PostgreSQL Remote |
| Protocol | TCP |
| External Port | 5432 |
| Internal IP | 192.168.31.99 |
| Internal Port | 5432 |
| Enable | ✓ YES |

**Click: Save/Apply**

### ☐ Step 10: Create Rule 2 - SSH

| Setting | Value |
|---------|-------|
| Rule Name | SSH Access |
| Protocol | TCP |
| External Port | 22 |
| Internal IP | 192.168.31.99 |
| Internal Port | 22 |
| Enable | ✓ YES |

**Click: Save/Apply**

### ☐ Step 11: Restart Router (if requested)

Some routers need restart to apply changes. Click "Restart" if offered.

---

## 🔑 PHASE 4: SSH SERVICE SETUP

### ☐ Step 12: Enable SSH Service

Open **PowerShell as Administrator** and run:

```powershell
Get-Service sshd
```

**If it says "Running":** ✅ Good, skip to Step 13

**If it says "Stopped":** Run these:
```powershell
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

### ☐ Step 13: Verify SSH Service

```powershell
Get-Service sshd
```

Should show: `Status       : Running`

---

## 🧪 PHASE 5: LOCAL TEST (On Host Machine)

### ☐ Step 14: Test PostgreSQL Locally

Open **PowerShell** and run:

```powershell
psql -h 192.168.31.99 -U postgres -d kvk -c "SELECT version();"
```

When prompted: `Password:` → Enter: `Ravi@2004`

**Expected:** Shows PostgreSQL version info

### ☐ Step 15: Test SSH Locally

```powershell
ssh -v Administrator@127.0.0.1
```

When asked: `Continue?` → Type: `yes`  
When asked: `Password:` → Enter: `YOUR_WINDOWS_PASSWORD`

**Expected:** Shows welcome message

---

## 🌍 PHASE 6: REMOTE TEST (From Remote Machine 350 KM Away)

### ☐ Step 16: Get Your Public IP

Open browser on **host machine** and go to:
https://www.whatismyipaddress.com/

**Note:** Should show `47.11.41.71` ✓

### ☐ Step 17: Remote SSH Test

On **remote machine**, open PowerShell and run:

```powershell
ssh -v Administrator@47.11.41.71
```

When asked: `Continue?` → Type: `yes`  
When asked: `Password:` → Enter: `YOUR_WINDOWS_PASSWORD`

**Expected:** Welcome message (proves port 22 works)

### ☐ Step 18: Remote PostgreSQL Through Tunnel

Keep SSH session open, then in **new PowerShell on remote machine**:

```powershell
ssh -L 5432:192.168.31.99:5432 Administrator@47.11.41.71 -N
```

Then in **another PowerShell on remote machine**:

```powershell
psql -h localhost -U postgres -d kvk -c "SELECT current_database();"
```

**Expected:** Shows `kvk`

---

## 📊 PHASE 7: APP DEPLOYMENT TEST

### ☐ Step 19: Test on Host Machine

1. Launch `KVKSystem.exe`
2. Login: `admin` / `admin123`
3. Create test record "Test_Host_Data"
4. Go to Report module, export to verify

### ☐ Step 20: Test on Remote Machine (350 KM)

Copy files to remote:
- KVKSystem.exe
- .env (with DB_HOST=localhost)
- LAUNCHER_FOR_REMOTE_MACHINES.bat

On remote machine:
1. Double-click launcher
2. Wait for tunnel
3. Login: `admin` / `admin123`
4. View records → Should see "Test_Host_Data"
5. Create test record "Test_Remote_Data"

### ☐ Step 21: Verify Sync

Back on **host machine**:
1. Refresh the app
2. Should see "Test_Remote_Data" record

✅ **If you see it → System works perfectly!**

---

## 🔐 PHASE 8: SECURITY & MAINTENANCE

### ☐ Step 22: Change Default Passwords (Optional)

For production, change:
- PostgreSQL `postgres` user password (in pgAdmin)
- Windows admin password (if sharing credentials)

### ☐ Step 23: Enable PostgreSQL Backup

In KVKSystem.exe on host:
1. Go to "Backup and Restore"
2. Click "Backup Database"
3. Save to external drive weekly

### ☐ Step 24: Document Your Setup

Create a file `MY_SETUP.txt` with:
```
Host Machine IP: 192.168.31.99
Public IP: 47.11.41.71
PostgreSQL Port: 5432
SSH Port: 22
Admin User: admin
DB User: postgres
```

---

## ✅ FINAL CHECKLIST

- [ ] PostgreSQL listens on all interfaces (*)
- [ ] Route ports 5432 and 22 forwarded correctly
- [ ] Windows Firewall allows inbound connections
- [ ] SSH service running and enabled
- [ ] Local PostgreSQL test passed
- [ ] Local SSH test passed
- [ ] Remote SSH test passed (from 350 KM away)
- [ ] Remote tunnel test passed
- [ ] KVKSystem.exe works on host
- [ ] KVKSystem.exe works on remote machine
- [ ] Data syncs between host and remote
- [ ] Backup strategy documented

---

## 🎉 YOU'RE DONE!

Your KVK System is now set up for multi-site deployment across 350 KM via internet.

**Remote teams can now:**
- ✅ Access central database from 350 KM away
- ✅ Work offline if internet drops (local data cached)
- ✅ Sync data when back online
- ✅ All changes visible in real-time (when connected)

---

**Status:** ✅ Ready for Production  
**Public IP:** 47.11.41.71  
**Setup Date:** March 19, 2026
