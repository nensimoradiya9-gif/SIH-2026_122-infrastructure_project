PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(6)))),
 full_name TEXT NOT NULL, username TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
 phone TEXT, company TEXT, department TEXT, role TEXT NOT NULL DEFAULT 'Project Manager', preferred_language TEXT NOT NULL DEFAULT 'en', theme TEXT NOT NULL DEFAULT 'light',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS projects (
 id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(6)))),
 owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, name TEXT NOT NULL, client TEXT, location TEXT, state TEXT, start_date TEXT, end_date TEXT,
 planned_progress REAL NOT NULL DEFAULT 0, actual_progress REAL NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'In Progress', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS activities (
 id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(6)))),
 project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, code TEXT NOT NULL, name TEXT NOT NULL, planned_progress REAL NOT NULL DEFAULT 0, actual_progress REAL NOT NULL DEFAULT 0, planned_start TEXT, planned_end TEXT, status TEXT NOT NULL DEFAULT 'In Progress', UNIQUE(project_id, code)
);
CREATE TABLE IF NOT EXISTS reports (
 id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(6)))),
 owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, project_id TEXT REFERENCES projects(id) ON DELETE SET NULL, activity_id TEXT REFERENCES activities(id) ON DELETE SET NULL,
 report_date TEXT NOT NULL, location_text TEXT, latitude REAL, longitude REAL, description TEXT, quantity REAL, unit TEXT, ai_match_score REAL, match_source TEXT DEFAULT 'database', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS alerts (
 id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(6)))),
 owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, project_id TEXT REFERENCES projects(id) ON DELETE CASCADE, activity_id TEXT REFERENCES activities(id) ON DELETE CASCADE,
 type TEXT NOT NULL, severity TEXT NOT NULL DEFAULT 'medium', title TEXT NOT NULL, message TEXT NOT NULL, resolved INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS documents (
 id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(6)))),
 owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, project_id TEXT REFERENCES projects(id) ON DELETE SET NULL, original_name TEXT NOT NULL, mime_type TEXT, size_bytes INTEGER, extracted_text TEXT, extracted_at TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS chat_messages (
 id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(6)))),
 owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, role TEXT NOT NULL, content TEXT NOT NULL, language TEXT NOT NULL DEFAULT 'en', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS audit_logs (
 id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(2))) || '-' || lower(hex(randomblob(6)))),
 owner_id TEXT REFERENCES users(id) ON DELETE SET NULL, action TEXT NOT NULL, entity_type TEXT, entity_id TEXT, metadata TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project_id);
CREATE INDEX IF NOT EXISTS idx_reports_owner_date ON reports(owner_id, report_date DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_owner_resolved ON alerts(owner_id, resolved);
CREATE INDEX IF NOT EXISTS idx_chat_owner_created ON chat_messages(owner_id, created_at);
CREATE UNIQUE INDEX IF NOT EXISTS users_email_lower_unique ON users(lower(email));
CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower_unique ON users(lower(username));
CREATE INDEX IF NOT EXISTS idx_documents_owner_created ON documents(owner_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_owner_status ON projects(owner_id, status);
CREATE INDEX IF NOT EXISTS idx_activities_project_status ON activities(project_id, status);

CREATE TABLE IF NOT EXISTS document_facts (
 id INTEGER PRIMARY KEY AUTOINCREMENT, document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, fact_type TEXT NOT NULL, payload_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_document_facts_document ON document_facts(document_id,status);
