-- KVK Database Management System schema
-- PostgreSQL 13+

CREATE TABLE IF NOT EXISTS departments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'staff')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS farmers (
    id BIGSERIAL PRIMARY KEY,
    farmer_name VARCHAR(150) NOT NULL,
    village VARCHAR(150) NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS activities (
    id BIGSERIAL PRIMARY KEY,
    module_type VARCHAR(60) NOT NULL,
    farmer_id BIGINT NOT NULL REFERENCES farmers(id) ON DELETE RESTRICT,
    department_id BIGINT NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    season VARCHAR(20) NOT NULL CHECK (season IN ('Kharif', 'Rabi')),
    activity_type VARCHAR(150) NOT NULL,
    activity_date DATE NOT NULL,
    description TEXT,
    remarks TEXT,
    visitor_scientist VARCHAR(150),
    visitor_district VARCHAR(100),
    visitor_tehsil VARCHAR(100),
    oft_title VARCHAR(255),
    oft_batch_key VARCHAR(64),
    oft_crop_variety VARCHAR(255),
    oft_farmer_count INTEGER,
    oft_technical_assessment TEXT,
    oft_area VARCHAR(255),
    oft_farmer_scientist VARCHAR(150),
    oft_farmer_purpose VARCHAR(100),
    oft_farmer_district VARCHAR(100),
    oft_farmer_tehsil VARCHAR(100),
    oft_farmer_category VARCHAR(50),
    training_title VARCHAR(255),
    training_type VARCHAR(50),
    training_end_date DATE,
    clientele VARCHAR(10),
    thematic_area VARCHAR(255),
    venue VARCHAR(255),
    venue_is_offline BOOLEAN,
    venue_village VARCHAR(150),
    venue_taluka VARCHAR(150),
    venue_district VARCHAR(150),
    training_farmer_count INTEGER,
    training_farmer_category VARCHAR(50),
    training_farmer_scientist VARCHAR(150),
    training_farmer_purpose VARCHAR(100),
    training_farmer_district VARCHAR(100),
    training_farmer_tehsil VARCHAR(100),
    extension_venue VARCHAR(255),
    extension_location VARCHAR(255),
    extension_department VARCHAR(150),
    extension_purpose TEXT,
    extension_farmer_count INTEGER,
    other_extension_title VARCHAR(255),
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_activity_clientele CHECK (clientele IS NULL OR clientele IN ('PF', 'RY', 'EF'))
);

CREATE TABLE IF NOT EXISTS reports (
    id BIGSERIAL PRIMARY KEY,
    report_name VARCHAR(200) NOT NULL,
    generated_by BIGINT REFERENCES users(id) ON DELETE SET NULL,
    filter_json JSONB,
    file_path TEXT,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    module_type VARCHAR(60),
    record_id BIGINT,
    details TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Performance indexes for long-term scale.
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(activity_date);
CREATE INDEX IF NOT EXISTS idx_activities_department ON activities(department_id);
CREATE INDEX IF NOT EXISTS idx_activities_module ON activities(module_type);
CREATE INDEX IF NOT EXISTS idx_activities_activity_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_farmer ON activities(farmer_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_reports_generated_at ON reports(generated_at);

-- Seed departments (safe to run multiple times).
INSERT INTO departments (name)
VALUES
    ('Agronomy'),
    ('Horticulture'),
    ('Plant Protection'),
    ('Veterinary Science'),
    ('Soil Science'),
    ('Home Science'),
    ('Agricultural Extension')
ON CONFLICT (name) DO NOTHING;
