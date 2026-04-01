# Step-by-Step Setup: 47.11.41.71 (Your Public IP)

## YOUR PUBLIC IP: 47.11.41.71

Use this IP for all remote machine configurations.

---

## STEP 1: PORT FORWARDING IN ROUTER

### What is Port Forwarding?
Port forwarding tells your router: "When someone tries to connect on port 5432 from the internet, redirect it to my computer (192.168.31.99)".

### How to Set Up:

#### Step 1A: Login to Your Router

1. Open browser and go to: `http://192.168.1.1` (or `http://192.168.0.1`)
2. Enter router login credentials:
   - Default username: `admin`
   - Default password: `admin` (or check router manual)

#### Step 1B: Find Port Forwarding Settings

Different router models have different menus. Look for:
- "Port Forwarding"
- "Virtual Server"
- "NAT"
- "Advanced" → "Port Forwarding"

#### Step 1C: Create Port Forward Rule

Create a NEW rule with these values:

| Setting | Value |
|---------|-------|
| **Rule Name** | PostgreSQL Remote Access |
| **Protocol** | TCP |
| **External Port** | 5432 |
| **Internal IP** | 192.168.31.99 |
| **Internal Port** | 5432 |
| **Enable** | ✓ Yes |

#### Step 1D: Save and Restart Router

Click "Save" or "Apply", then restart router if prompted.

#### Step 1E: Verify Port Forwarding

```powershell
# On host machine, check if port 5432 is open externally:
netstat -an | findstr "5432"
```

---

## STEP 2: PREPARE FILES FOR REMOTE MACHINES

### Files Needed on Remote Machines:

1. **KVKSystem.exe** (the main application)
2. **.env** (database configuration)
3. **START_REMOTE_350KM.bat** (auto-launcher)

### How to Prepare:

#### Option A: USB Drive (If You Visit Remote Site)

1. Create USB folder: `\KVK_System_Files\`
2. Copy these files there:
   ```
   KVKSystem.exe          (from d:\kvk\dist\)
   .env                   (from d:\kvk\)
   START_REMOTE_350KM.bat (from d:\kvk\)
   ```

#### Option B: Cloud Download (Recommended for 350 KM)

1. Upload to Google Drive / OneDrive:
   - KVKSystem.exe
   - .env
   - START_REMOTE_350KM.bat

2. Share download link with remote team

3. They download and extract to folder like: `C:\KVK\`

#### Option C: Email + Zip

1. Create folder: `KVK_System_Files`
2. Copy 3 files into it
3. Right-click → "Send to" → "Compressed (zipped) folder"
4. Email zip file to remote machines

---

## STEP 3: UPDATE BATCH FILE WITH YOUR PUBLIC IP

### File: START_REMOTE_350KM.bat

On **EACH remote machine**, you need to update this file with your IP.

#### What to Update:

Open `START_REMOTE_350KM.bat` in Notepad:

**Find this line:**
```batch
set HOST_PUBLIC_IP=103.45.123.45
```

**Change to:**
```batch
set HOST_PUBLIC_IP=47.11.41.71
```

**Also verify:**
```batch
set HOST_USERNAME=Administrator
set HOST_INTERNAL_IP=192.168.31.99
```

These should match your host machine's setup.

#### Full Updated Section:

```batch
REM CONFIGURATION - UPDATE THESE VALUES:
set HOST_PUBLIC_IP=47.11.41.71
set HOST_USERNAME=Administrator
set HOST_INTERNAL_IP=192.168.31.99
```

#### Alternative:

**For simplicity**, provide two versions:

**START_REMOTE_SITE_A.bat** - For Site A team
**START_REMOTE_SITE_B.bat** - For Site B team

Each has correct IP already set.

---

## STEP 4: CREATE .ENV FILE FOR REMOTE MACHINE

### File: .env

On **EACH remote machine**, create a `.env` file in same folder as `KVKSystem.exe`.

**Content:**
```env
# Remote Machine Configuration (350 KM away)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kvk
DB_USER=postgres
DB_PASSWORD=Ravi@2004
PG_BIN_DIR=
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

**Important:**
- `DB_HOST=localhost` (NOT your public IP)
- SSH tunnel will handle the connection
- `PG_BIN_DIR` stays EMPTY (remote machines don't backup)

---

## STEP 5: TEST SSH CONNECTION (CRITICAL)

### What is SSH?
SSH is a **secure encrypted tunnel** for remote access.

### Prerequisites:

- [ ] Host machine has SSH running
- [ ] Remote machine has SSH client (Windows 10+ has built-in)

### Test from Remote Machine:

#### Step 5A: Open PowerShell on Remote Machine

Press: `Win + R` → Type `powershell` → Enter

#### Step 5B: Test SSH Connection

```powershell
ssh -v Administrator@47.11.41.71 -p 22
```

**What you'll see:**
- First time: "Are you sure you want to continue? (yes/no)" → Type: `yes`
- Then: "Password:" → Enter: `YOUR_HOST_PASSWORD`

**Success looks like:**
```
Welcome to Microsoft Windows
...
administrator@HOST-NAME:~$
```

**If fails, check:**

1. **Host machine SSH service running:**
   ```powershell
   # On HOST machine
   Get-Service sshd
   ```
   Should show: `Running`

2. **Windows Firewall allows SSH:**
   ```powershell
   # On HOST machine (as Admin)
   netsh advfirewall firewall add rule name="SSH" dir=in action=allow protocol=tcp localport=22
   ```

3. **Router allows port 22:**
   - Add second port forward rule:
     - External Port: 22
     - Internal Port: 22
     - Internal IP: 192.168.31.99

#### Step 5C: Test PostgreSQL Through Tunnel

Keep the SSH session open, then in **another PowerShell on remote machine**:

```powershell
ssh -L 5432:192.168.31.99:5432 Administrator@47.11.41.71 -N
```

Then in **another PowerShell window**:

```powershell
psql -h localhost -U postgres -d kvk -c "SELECT current_database();"
```

Enter password: `Ravi@2004`

**Expected output:**
```
 current_database
------------------
 kvk
(1 row)
```

---

## STEP 6: FINAL SETUP ON REMOTE MACHINE

### Folder Structure on Remote Machine:

```
C:\KVK\
├── KVKSystem.exe
├── .env
└── START_REMOTE_350KM.bat
```

### To Launch (on Remote Machine):

**Method 1: Double-click batch file**
```
Double-click: START_REMOTE_350KM.bat
```

This will:
1. Start SSH tunnel automatically
2. Wait 3 seconds
3. Launch KVKSystem.exe
4. You can login and work!

**Method 2: Manual (if batch fails)**

```powershell
# Terminal 1 - Start SSH tunnel
ssh -L 5432:192.168.31.99:5432 Administrator@47.11.41.71 -N

# Terminal 2 - Launch app (keep terminal 1 running)
C:\KVK\KVKSystem.exe
```

---

## QUICK CHECKLIST

### ✅ HOST MACHINE (192.168.31.99)

- [ ] PostgreSQL service running
- [ ] `postgresql.conf` has `listen_addresses = '*'`
- [ ] `pg_hba.conf` has remote auth configured
- [ ] SSH service running: `Get-Service sshd` → Running
- [ ] Windows Firewall allows ports:
  - [ ] Port 5432 (PostgreSQL)
  - [ ] Port 22 (SSH)
- [ ] Router port forwarding configured:
  - [ ] External 5432 → Internal 192.168.31.99:5432
  - [ ] External 22 → Internal 192.168.31.99:22
- [ ] Public IP confirmed as: **47.11.41.71**

### ✅ REMOTE MACHINE (350 KM Away)

- [ ] Files copied to `C:\KVK\`:
  - [ ] KVKSystem.exe
  - [ ] .env (with DB_HOST=localhost)
  - [ ] START_REMOTE_350KM.bat (with PUBLIC_IP=47.11.41.71)
- [ ] SSH connection test PASSED:
  - [ ] `ssh Administrator@47.11.41.71` works
  - [ ] `psql` through tunnel works
- [ ] Double-click START_REMOTE_350KM.bat works
- [ ] KVKSystem.exe launches
- [ ] Login successful (admin/admin123)

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "Connection refused" on remote | Check router port forwarding for 5432 |
| "SSH connection refused" | Check router port forwarding for 22 + SSH service on host |
| "Password authentication failed" | Verify PostgreSQL password is `Ravi@2004` |
| "Database kvk does not exist" | Run app once on host to init database |
| "Tunnel timeout" | Increase `timeout /t 5` in batch file |

---

## TESTING DATA SYNC

### Create Test Data

1. **On HOST machine:**
   - Run KVKSystem.exe
   - Login: admin/admin123
   - Create test activity record
   - Note the Farmer Name (e.g., "Test Farmer")

2. **On REMOTE machine (350 KM away):**
   - Run START_REMOTE_350KM.bat
   - Login: admin/admin123
   - View records → Should see "Test Farmer" record
   - Create another test record
   - Note the name (e.g., "Remote Test")

3. **Back on HOST machine:**
   - Refresh the table
   - Should see "Remote Test" record created by remote machine

**✅ If both can see each other's data = System works!**

---

## YOUR CONFIGURATION

Use these values everywhere:

```
Public IP:          47.11.41.71
Internal IP (Host): 192.168.31.99
Database:           kvk
Username:           postgres
Password:           Ravi@2004
Admin Login:        admin / admin123
SSH Port:           22
DB Port:            5432
```

**Ready to deploy!** 🚀
