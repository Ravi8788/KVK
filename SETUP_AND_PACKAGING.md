# Setup and EXE Packaging Guide

## 1. Install PostgreSQL

1. Install PostgreSQL (recommended 13+).
2. Create a database:
   - Name: `kvk_db`
3. Ensure PostgreSQL service is running locally.

## 2. Configure Environment

1. Copy `.env.example` to `.env`.
2. Update values in `.env`:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
   - Optional `PG_BIN_DIR` (PostgreSQL `bin` folder path) if backup/restore tools are not in PATH.

## 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Run Application

```powershell
python main.py
```

On first run, app will:
- Test PostgreSQL connection
- Create tables automatically
- Seed departments
- Create default admin user (`admin/admin123`) if not present

## 5. Apply SQL Schema Manually (Optional)

If your IT policy requires manual SQL migration:

```powershell
psql -U postgres -d kvk_db -f database/schema.sql
```

## 6. Build Windows EXE

```powershell
pyinstaller --onefile --windowed main.py
```

Generated executable will be in `dist/main.exe`.

## 7. Recommended Production Build Command

```powershell
pyinstaller --name KVKSystem --onefile --windowed --clean --noconfirm main.py
```

## 8. Offline Deployment Notes

- Install PostgreSQL on each target machine.
- Copy `.env` with machine-specific database credentials.
- Use strong admin password before production rollout.
- Schedule regular SQL backups to external storage.

## 9. Role-Based Access Behavior

- `admin`: Full access to all modules including User Management and Restore.
- `staff`: User Management disabled; selected modules open in read-only mode.
- `staff`: Can run database backup but cannot run restore.

## 10. Safe Restore Workflow

When restore is triggered from Backup & Restore module:

1. Application shows target database metadata (host, db name, table count).
2. User must confirm restore and type `RESTORE`.
3. Application creates automatic safety backup in `backups/pre_restore`.
4. Application runs restore from selected `.sql` file.

## 11. Government Rollout Checklist

Use [PRODUCTION_DEPLOYMENT_CHECKLIST.md](PRODUCTION_DEPLOYMENT_CHECKLIST.md) for deployment governance and long-term operations.
