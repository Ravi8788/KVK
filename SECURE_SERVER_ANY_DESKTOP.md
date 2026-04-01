# Secure Server + Any Desktop Access (Recommended)

This setup is secure for internet use and supports any desktop/laptop.

## Important Reality
No system can be guaranteed "unhackable". But you can make it very hard to attack by removing public exposure and using private network access.

## Secure Architecture (Use This)
- Host machine runs PostgreSQL.
- Do NOT expose PostgreSQL (5432) directly on public internet.
- Do NOT expose SSH (22) publicly unless absolutely required.
- Use a private mesh VPN (Tailscale) and allow DB only from that private network.

---

## 1) Host Hardening (One Time)

### A. Remove risky public exposure
- Remove router port-forward rules for:
  - 5432 (PostgreSQL)
  - 22 (SSH)

### B. Install Tailscale on host
- Download and install Tailscale on host machine.
- Sign in.
- Note host Tailscale IP (example: 100.x.x.x).

### C. PostgreSQL network restrictions
Edit postgresql.conf:
- listen_addresses = '*'

Edit pg_hba.conf and allow only Tailscale range:
- host    kvk    postgres    100.64.0.0/10    scram-sha-256

Then restart PostgreSQL service.

### D. Windows Firewall lock-down
Allow PostgreSQL only from Tailscale interface/IP range.
Block all other inbound 5432 traffic.

### E. Strong credentials (must do)
- Change DB password from default.
- Change app admin default password (admin123) immediately.
- Use at least 16+ chars with letters, numbers, symbols.

### F. System security baseline
- Keep Windows updates ON.
- Keep antivirus ON.
- Run app on standard user account, not permanent admin.
- Enable scheduled database backups.

---

## 2) Any Desktop Usage (Remote/Outstation)

Every desktop/laptop can connect if it has:
1. Tailscale installed and logged in to same tailnet.
2. KVKSystem.exe.
3. .env file pointing to host Tailscale IP.

### Remote .env template
Use this on every remote desktop (same folder as KVKSystem.exe):

DB_HOST=100.100.100.100
DB_PORT=5432
DB_NAME=kvk
DB_USER=postgres
DB_PASSWORD=REPLACE_WITH_STRONG_PASSWORD
PG_BIN_DIR=
ADMIN_USERNAME=admin
ADMIN_PASSWORD=REPLACE_ADMIN_PASSWORD

Replace DB_HOST with your host Tailscale IP.

### Run steps on any desktop
1. Start Tailscale and ensure status = connected.
2. Double-click KVKSystem.exe.
3. Login with your app user credentials.
4. Data is live from central host database.

---

## 3) Quick Connectivity Test (Remote Desktop)

Use PowerShell on remote desktop:

Test-NetConnection 100.100.100.100 -Port 5432

Expected:
- TcpTestSucceeded : True

If False:
- Check host Tailscale is online.
- Check firewall allows 5432 only from Tailscale.
- Check PostgreSQL service is running.

---

## 4) Minimum Safe Operations Policy

- No direct internet DB access.
- No shared admin account for all users.
- Keep separate users for admin/staff.
- Weekly full backup + daily incremental backup.
- Monthly password rotation.

---

## 5) Deployment Pack for Each New Desktop

Copy these files to remote machine folder:
- KVKSystem.exe
- .env (configured with host Tailscale IP)

Install once on remote machine:
- Tailscale client

Then launch:
- KVKSystem.exe

That is all.
