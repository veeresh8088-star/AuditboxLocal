# 🛡️ AICyberAuditBox — Local Audit

> **Agentic RAG · ISO 27001 Compliance Audit Intelligence**  
> Powered by Ollama (offline LLM) · ShaktiDB (PostgreSQL) · Streamlit

---

## Features

### 🔍 AI-Powered ISO 27001 Auditing
- **Compliance checking** — automated evaluation of evidence text against controls
- **Compliance Statuses**: Compliant, Non-Compliant
- **Severity Scale**: Critical, High, Medium, Low

### 📁 Evidence Upload
| Format | Support |
|---|---|
| PDF | ✅ Native text + OCR for scanned pages |
| Word (.docx/.doc) | ✅ |
| Excel (.xlsx/.xls) | ✅ All sheets |
| CSV | ✅ |
| PowerPoint (.pptx/.ppt) | ✅ All slides |
| Plain Text (.txt) | ✅ |
| PNG / JPG / JPEG | ✅ OCR (EasyOCR) |
| **ZIP (folder upload)** | ✅ Recursively extracts all supported files |

> **Folder upload:** Zip your folder → upload the `.zip` file. All files inside are automatically extracted, processed and combined as evidence.

### ⚡ Crash-Resilient Checkpointing
If the app crashes or shuts down mid-audit:
1. Progress is saved to ShaktiDB after **every batch** (~10 controls)
2. On restart, a **"Resume Interrupted Audit"** banner appears automatically
3. One click resumes from the last completed batch — prior results are preserved and merged

### 📊 Audit Report
- Interactive finding cards with Control ID, Control Name, Severity, Finding, Recommendation
- Severity filter cards (Critical/High/Medium/Low + Resolved)
- Accept / Modify / Delete / Auditor Notes per finding
- Export full CSV with Control ID, Control Name, Severity, Finding, Recommendation, Workflow Status, Source Scope, Auditor Comment

### 🗄️ Database
- **Primary**: ShaktiDB (PostgreSQL on `localhost:15234`)  
- **Auto-fallback**: Local SQLite (`shakthidb_local.db`) — zero-downtime during presentations

---

## Quick Start

```bat
.\run_demo.bat
```

Or manually:

```bat
docker-compose up -d
streamlit run app.py
```

---

## Architecture

```
app.py              — Main Streamlit application
database.py         — SQLAlchemy ORM (AuditFinding, AuditCheckpoint, ChatMessage, User)
auth.py             — Login gate / role management
controls_data.py    — ISO 27001 control definitions
scoping_engine.py   — Automatic document scope detection
```

---

## Troubleshooting

- **ShaktiDB not reachable?** App auto-switches to SQLite local DB.
- **Ollama not running?** Start with `docker-compose up -d`, then pull models with `.\pull_models.bat`.
- **Schema upgrade?** On first restart after an update, `audit_findings` and `audit_checkpoints` tables are automatically recreated.

```bat
## Useful commands
docker-compose up -d
.\pull_models.bat
python -m py_compile app.py   # syntax check
```