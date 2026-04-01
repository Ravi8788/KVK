# KVK Production Deployment Checklist

## 1. Infrastructure Baseline

1. Provision Windows machine with minimum 16 GB RAM and SSD storage.
2. Install PostgreSQL 13+ and set service startup mode to automatic.
3. Create dedicated PostgreSQL role for application use (avoid using superuser in production).
4. Create database `kvk_db` with UTF-8 encoding.

## 2. Security Controls

1. Change default admin password at first login.
2. Restrict local machine access to authorized KVK staff only.
3. Keep `.env` file readable only by trusted operators.
4. Enable Windows Defender and scheduled malware scanning.

## 3. Database Reliability

1. Apply schema from `database/schema.sql` or allow app bootstrap.
2. Validate indexes exist on `activities` and audit/report tables.
3. Set PostgreSQL `shared_buffers`, `work_mem`, and autovacuum for long-term performance.
4. Run monthly `VACUUM (ANALYZE)` maintenance.

## 4. Backup and Restore Policy

1. Configure daily SQL backups to local backup folder and weekly copy to external drive.
2. Retain daily backups for 30 days and monthly snapshots for 7 years minimum.
3. Use built-in Safe Restore flow: metadata check + pre-restore backup.
4. Test restore process at least once per quarter on a test machine.

## 5. Application Deployment

1. Install Python dependencies:
   - `pip install -r requirements.txt`
2. Build executable:
   - `pyinstaller --name KVKSystem --onefile --windowed --clean --noconfirm main.py`
3. Copy `dist/KVKSystem.exe` and `.env` to target machine.
4. Verify login, module save flow, report export, and backup operations.

## 6. Operational Governance

1. Create named admin users and disable shared credentials.
2. Keep staff users as least-privilege accounts.
3. Review audit logs monthly for unusual activity.
4. Keep signed deployment notes and backup logs for compliance audits.

## 7. Annual Health Review

1. Check disk usage growth and archive old report exports.
2. Validate random historical records for data integrity.
3. Upgrade Python and dependencies in a controlled yearly maintenance window.
4. Rebuild EXE and run full UAT before replacing production binary.
