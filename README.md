# AICyberAuditBox: Plug. Deploy. Audit. (Q2 2026)

## Overview
The **AICyberAuditBox** is a next-generation, RAG-powered AI tool designed for Cybersecurity Audits and Assessments. It provides a completely private, offline, and secure pipeline for analyzing sensitive audit evidence.

## Architecture
- **Intelligence Engine**: Local Ollama (Llama 3.1 8B / Qwen 2.5 7B)
- **Database Engine**: ShaktiDB (Built on PostgreSQL 17.7) - Hosted in an isolated Linux environment.
- **Frontend Dashboard**: Streamlit (Python 3.14+)

## Pipeline Stages
1. **Ingest & Parse**: Multi-format input handling (PDF, Word, Scanned OCR).
2. **Chunk & Embed**: 1,500-dimensional vector transformation.
3. **Semantic Mapping**: Matching compliance controls (ISO 27001, SOC 2, NIST, GDPR) to evidence.
4. **Gap Detection**: Cross-source assurance and contradiction analysis.
5. **Actionable Reports**: Severity-ranked findings persisted to ShaktiDB.

## Quick Start (Handover Instructions)

### Step 1: Initialize the Isolated Environment (ShaktiDB)
- Import the provided `AICyberAuditBox_Server.ova` into VirtualBox/VMware.
- Start the VM and ensure ShaktiDB is active.

### Step 2: Initialize the Dashboard
- Open a terminal in the project directory.
- Run the installer/launcher:
  ```powershell
  .\run_demo.bat
  ```

### Step 3: Local AI Integration
- Ensure **Ollama** is running on the host machine.
- Pull the required model: `ollama pull llama3.1` and `ollama pull qwen2.5:7b`

## Troubleshooting (Auto-Local Feature)
If the primary ShaktiDB server (VM) is not reachable, the AICyberAuditBox will automatically switch to **Local SQLite Storage** (`shakthidb_local.db`) to ensure zero-downtime during presentations.

---
**Developed for CERT-In Samvaad 2026**
## .\run_demo.bat

## docker-compose up -d
## .\pull_models.bat
## ## Ran docker rm -f shakthidb_service to remove the conflicting container.

## docker-compose up -d to create and launch the fresh ShaktiDB instance successfully.


## python -m py_compile app.py