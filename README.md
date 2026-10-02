# Krishi Vidnyankendra (KVK) Database Management System

Desktop application for KVK offices to manage farmer activities, trainings, and reports with PostgreSQL-backed long-term storage.

## Features

- Role-based login (Admin/Staff)
- Sidebar-driven module navigation
- Dynamic data entry forms for all KVK activity modules
- Department/season-aware workflows
- Tabular reporting with filters and pagination (lazy loading)
- PDF export via ReportLab
- CSV export for reports
- SQL backup support
- User management (admin-only)
- Audit logging of user actions
- Windows EXE packaging via PyInstaller

## Tech Stack

- Python 3.10+
- PyQt5
- SQLAlchemy
- PostgreSQL
- ReportLab
- PyInstaller

## Quick Start

1. Create PostgreSQL database:
   - Database: `kvk_db`
2. Copy `.env.example` to `.env` and update values.
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run app:
   - `python main.py`

Detailed setup and EXE packaging steps are available in `SETUP_AND_PACKAGING.md`.

## Implemented Modules

1. Visitor Farmers
2. On Farm Testing (OFT)
3. Front Line Demonstrations (FLD)
4. Training Programmes
5. Vocational Training Programmes
6. Extension Activities
7. Other Extension Activities
8. Reports
9. Backup & Restore
10. User Management
11. Exit

## Folder Overview

- `ui/` - PyQt windows and widgets
- `models/` - SQLAlchemy ORM entities
- `controllers/` - Login/auth controller
- `services/` - Business logic (CRUD, reports, backup, users, audit)
- `reports/` - PDF report builders
- `database/` - DB configuration, session, schema, initialization
- `main.py` - Application entry point
