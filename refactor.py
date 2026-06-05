import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_auth_gate = False
skip_db_models = False

for i, line in enumerate(lines):
    # Detect Auth Gate start
    if "# ── AUTHENTICATION GATE ───────────────────────────────────────────────────────" in line:
        skip_auth_gate = True
        new_lines.append("# ── AUTHENTICATION GATE ───────────────────────────────────────────────────────\n")
        new_lines.append("render_login_gate()\n\n")
        continue
    
    if skip_auth_gate:
        if "# ── USE CASES ─────────────────────────────────────────────────────────────────" in line:
            skip_auth_gate = False
            new_lines.append(line)
        continue

    # Detect DB models start
    if "# ── DATABASE ──────────────────────────────────────────────────────────────────" in line:
        skip_db_models = True
        continue

    if skip_db_models:
        if "def save_findings" in line:
            skip_db_models = False
            # This is the start of the DB queries. We don't skip this, we let it process.
        else:
            continue

    # Update Session = sessionmaker(bind=engine) -> db = SessionLocal() inside functions
    if "Session = sessionmaker(bind=engine)" in line:
        continue
    if "db = Session()" in line:
        new_lines.append(line.replace("db = Session()", "db = SessionLocal()"))
        continue

    new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Refactor complete.")
