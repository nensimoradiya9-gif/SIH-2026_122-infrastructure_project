# Infra-Pulse PS122 — Professional Build (No PostgreSQL Required)

This build keeps the supplied Infra-Pulse landing/login/registration visual language and uses a **local SQLite database file**. You do **not** need PostgreSQL, Docker, or any database server.

## Requirements
- Windows
- Node.js 18+ (Node.js LTS recommended)

## Run
1. Extract the ZIP.
2. Open PowerShell in the extracted `Infra-Pulse-PS122-Professional` folder.
3. Run:

```powershell
npm install
npm start
```

Or simply:

```powershell
.\setup-local.ps1
```

4. Open **http://localhost:4000**.

## Database
The application automatically creates:

`data/infrapulse.sqlite`

This is the real persistent database for users, projects, activities, reports, alerts, uploaded-document metadata/text, and AI chat history. It is created automatically on first run. No PostgreSQL installation is required.

## Authentication
- No demo account.
- Each person registers their own account.
- One email = one account (case-insensitive).
- One username = one account (case-insensitive).
- Passwords are bcrypt hashed.
- Login accepts username or registered email.
- CAPTCHA is required.
- Different users' project/report/document/chat data is isolated by account.

## Test files
- `sample-data/daily-progress.csv`
- `sample-data/site-progress-report.pdf`

## Reset local database
Stop the server, then delete:

`data/infrapulse.sqlite`

Start the server again and a fresh database will be created.


## Stable final-build scope
This final build deliberately keeps the offline feature set dependable: PDF, CSV and TXT document extraction are supported. Uploaded facts are reviewed before they modify project data. Accepted project/activity facts update the Projects and Schedule views, and the Risk Radar recalculates from stored records. The AI Copilot is a deterministic database agent: it does not call an external AI service and it does not execute user-supplied SQL. It answers from the authenticated user's SQLite records and stored document text only.

## Document Intelligence flow
1. Data Files -> Upload CSV/TXT/PDF.
2. Infra-Pulse extracts the actual file contents.
3. Review facts.
4. Accept pending facts.
5. Accepted project/activity facts are written to SQLite.
6. Open Projects, the project-specific Schedule, Analytics and Risk Radar to verify the changes.

## Voice
The AI page uses the browser Speech Recognition API when the browser supports it. Chrome/Edge on localhost or HTTPS are recommended. If the browser does not support it, Infra-Pulse reports that clearly rather than pretending voice is active.
