import re

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Import replacement
    if "from sqlalchemy import create_engine, Column" in line:
        new_lines.append("from docx import Document\n")
        new_lines.append("from database import engine, db_label, AuditFinding, ChatMessage, SessionLocal\n")
        new_lines.append("from auth import render_login_gate\n")
        skip = True # skip the next few imports
        continue
    if skip and "from docx import Document" in line:
        skip = False
        continue
    if skip:
        continue

    # UI block replacement
    if "# ── AUTHENTICATION GATE ───────────────────────────────────────────────────────" in line:
        new_lines.append(line)
        new_lines.append("render_login_gate()\n\n")
        skip = True
        continue
    if skip and "st.stop()" in line:
        skip = False
        continue
    if skip and "# ── USE CASES ─────────────────────────────────────────────────────────────────" in line:
        # Just in case we overshot
        skip = False
        new_lines.append(line)
        continue
    if skip:
        continue
        
    # DB block removal
    if "# ── DATABASE ──────────────────────────────────────────────────────────────────" in line:
        skip = True
        continue
    if skip and "# ── AUTH HELPERS ───────────────────────────────────────────────────────────────" in line:
        continue # still skip auth helpers
    if skip and "seed_default_admin()" in line:
        skip = False
        continue
    if skip and "def save_findings" in line:
        skip = False
        # fall through to process save_findings
        
    if skip:
        continue

    # Sessionmaker replacements
    if "Session = sessionmaker(bind=engine)" in line:
        new_lines.append("    db = SessionLocal()\n")
        skip = True # skip the next line `db = Session()`
        continue
    if skip and "db = Session()" in line:
        skip = False
        continue

    new_lines.append(line)

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
