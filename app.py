# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
import pdfplumber
import time, json, hashlib, uuid, threading
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from docx import Document

# Thread-safe storage for background analysis results and active runs
@st.cache_resource
def _get_bg_store():
    return {
        "results": {},
        "running": set(),
        "lock": threading.Lock()
    }

_bg_store = _get_bg_store()
_bg_results = _bg_store["results"]
_bg_running = _bg_store["running"]
_bg_lock = _bg_store["lock"]
st.set_page_config(page_title="AICyberAuditBox", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Sidebar Primary Buttons (Run Analysis) ── */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg,#3b82f6,#1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: 0.2s !important;
}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.4) !important;
}

/* ── New Chat button ── */
section[data-testid="stSidebar"] > div > div > div > div > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div:nth-child(4) button {
    background: #1e3a5f !important;
    color: #60a5fa !important;
    border: 1px solid #2563eb !important;
}

/* ── Recents toggle button ── */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
    background: #1e3a5f !important;
    color: #60a5fa !important;
    border: 1px solid #2563eb !important;
    border-radius: 7px !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transform: none !important;
    transition: background 0.15s, color 0.15s !important;
}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
    background: #1d4ed8 !important;
    color: #bfdbfe !important;
    border-color: #3b82f6 !important;
}

/* ── ChatGPT Style Recents Sidebar CSS ── */
.chatgpt-sidebar-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 0px !important;
}

.chatgpt-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 10px;
    border-radius: 8px;
    transition: background-color 0.2s, border-color 0.2s;
    position: relative;
    margin-bottom: 2px;
}

.chatgpt-row-inactive {
    background-color: transparent;
    border: 1px solid transparent;
}

.chatgpt-row-inactive:hover {
    background-color: rgba(128, 128, 128, 0.08) !important; /* Theme-adaptive hover overlay */
}

.chatgpt-row-active {
    background-color: rgba(128, 128, 128, 0.15) !important; /* Theme-adaptive active background */
    border: 1px solid rgba(128, 128, 128, 0.25) !important; /* Theme-adaptive active border */
}

.chatgpt-row-left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex: 1;
    text-decoration: none !important;
}

.chatgpt-row-icon {
    font-size: 13px;
    color: var(--secondary-text-color) !important; /* Theme-adaptive secondary text */
    opacity: 0.85 !important;
    flex-shrink: 0;
    display: flex;
    align-items: center;
}

.chatgpt-row-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-color) !important; /* Theme-adaptive main text */
    opacity: 0.8 !important; /* Muted opacity for inactive chats */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-decoration: none !important;
}

.chatgpt-row-active .chatgpt-row-title {
    color: var(--text-color) !important;
    opacity: 1 !important; /* Full contrast for active title */
    font-weight: 600 !important;
}

.chatgpt-row-active .chatgpt-row-icon {
    opacity: 1 !important;
}

.chatgpt-row-delete {
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.15s;
    z-index: 10;
    margin-left: 6px;
}

.chatgpt-row:hover .chatgpt-row-delete {
    opacity: 1;
}

.chatgpt-row-delete-link {
    color: var(--secondary-text-color) !important;
    text-decoration: none !important;
    font-size: 12px;
    width: 20px;
    height: 20px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.15s, color 0.15s;
}

.chatgpt-row-delete-link:hover {
    background-color: rgba(239, 68, 68, 0.15) !important;
    color: #ef4444 !important;
}

/* ── Main UI styles ── */
.main-header { background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);
    padding:28px 32px; border-radius:16px; margin-bottom:24px;
    border:1px solid rgba(59,130,246,.2); }
.stat-card { background:#1e293b; border:1px solid #334155; border-radius:12px;
    padding:20px; text-align:center; }
.stat-num { font-size:2rem; font-weight:700; }
.badge-critical { background:#1a0a0a; border:1px solid #ef4444; border-left:5px solid #ef4444; border-radius:8px; padding:16px; margin:8px 0; color:#f8fafc; }
.badge-high     { background:#1a0d08; border:1px solid #f97316; border-left:5px solid #f97316; border-radius:8px; padding:16px; margin:8px 0; color:#f8fafc; }
.badge-medium   { background:#1a1600; border:1px solid #eab308; border-left:5px solid #eab308; border-radius:8px; padding:16px; margin:8px 0; color:#f8fafc; }
.badge-low      { background:#051a0d; border:1px solid #22c55e; border-left:5px solid #22c55e; border-radius:8px; padding:16px; margin:8px 0; color:#f8fafc; }
.chat-bubble-user { background:#1e3a5f; border-radius:16px 16px 4px 16px; padding:12px 16px;
    margin:4px 0; max-width:80%; color:#e2e8f0; text-align:left; }
.chat-bubble-bot  { background:#1e293b; border:1px solid #334155; border-radius:16px 16px 16px 4px;
    padding:12px 16px; margin:4px 0; max-width:80%; color:#e2e8f0; text-align:left; }
.uc-card { background:#1e293b; border:1px solid #334155; border-radius:10px;
    padding:14px 18px; margin:8px 0; cursor:pointer; transition:.2s; }
.uc-card:hover { border-color:#3b82f6; transform:translateX(4px); }
.stage-done   { color:#22c55e; border-left:3px solid #22c55e; padding:6px 0 6px 14px; margin:4px 0; font-weight:600; }
.stage-active { color:#3b82f6; border-left:3px solid #3b82f6; padding:6px 0 6px 14px; margin:4px 0; font-weight:600; }
.stage-idle   { color:#475569; border-left:3px solid #334155; padding:6px 0 6px 14px; margin:4px 0; }
div[data-testid="stDecoration"] { display:none; }
.inline-spinner { border: 2px solid rgba(59, 130, 246, 0.1); border-top: 2px solid #3b82f6; border-radius: 50%; width: 16px; height: 16px; animation: spin_inline 1s linear infinite; display: inline-block; vertical-align: middle; }
@keyframes spin_inline { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)

# ── USE CASES ─────────────────────────────────────────────────────────────────
USE_CASES = [
    # --- ISO 27001 ---
    {"sl":1,"standard":"ISO 27001","label":"Access Control Policy (A.5.15)","icon":"🔐","use_case":"Access Control Policy – Grant, Review, Revoke access","expected":"Verify documented access control policy covering full access lifecycle.","format":"PDF","prompt_hint":"Verify if a documented access control policy exists covering granting, reviewing, and revoking access."},
    {"sl":2,"standard":"ISO 27001","label":"Role-Based Access Control (RBAC)","icon":"👥","use_case":"RBAC – Permissions assigned to Roles, not individuals","expected":"Verify RBAC implementation. Access should be role-based.","format":"PDF","prompt_hint":"Verify if access is managed through roles rather than individual users. Identify RBAC gaps."},
    {"sl":3,"standard":"ISO 27001","label":"Multi-Factor Authentication (MFA)","icon":"🔑","use_case":"MFA – Enforced for all external access via VPN / cloud","expected":"Confirm MFA enforcement, password complexity and rotation requirements.","format":"PDF","prompt_hint":"Verify MFA enforcement for external access, VPN, cloud. Check password complexity and rotation policy."},
    {"sl":4,"standard":"ISO 27001","label":"Privileged Access Management","icon":"⚡","use_case":"Privileged Access – Time-limited and monitored","expected":"Verify privileged access is restricted, time-limited, and monitored.","format":"PDF","prompt_hint":"Verify if privileged access is time-limited, restricted to legitimate need, and under enhanced monitoring."},
    {"sl":5,"standard":"ISO 27001","label":"Access Reviews & Orphaned Accounts","icon":"🔎","use_case":"Access Reviews – Periodic review and orphaned account management","expected":"Verify periodic access reviews and prompt revocation. Orphaned accounts managed.","format":"PDF","prompt_hint":"Check if access rights are reviewed periodically, revoked promptly, and orphaned accounts are managed."},
    {"sl":6,"standard":"ISO 27001","label":"Incident Mgmt – Vendor Assessment","icon":"🔍","use_case":"Incident Management (A.5.24) – Vendor Security Assessment","expected":"Verify vendor security measures comply with ISO 27001. Identify gaps.","format":"PDF","prompt_hint":"Verify if vendor security measures comply with ISO 27001 A.5.24-A.5.28. List all gaps."},
    {"sl":7,"standard":"ISO 27001","label":"Incident Mgmt – Policy Review","icon":"🔄","use_case":"Incident Management (A.5.28) – Conduct Regular Reviews","expected":"Verify if policies are regularly reviewed and updated. Identify stale policies.","format":"PDF","prompt_hint":"Check if incident response policy is regularly reviewed. Identify outdated content."},
    
    # --- DPDP / GDPR ---
    {"sl":8,"standard":"DPDP / GDPR","label":"Consent Management & Notice","icon":"📝","use_case":"Verify Consent mechanisms and Privacy Notice transparency","expected":"Confirm clear, granular, revocable consent notice complying with DPDP/GDPR.","format":"PDF","prompt_hint":"Check privacy policy and notice for consent clarity, purpose limitation, and DPO details."},
    {"sl":9,"standard":"DPDP / GDPR","label":"Data Protection Officer (DPO)","icon":"👔","use_case":"Verify appointment of DPO and contact availability","expected":"Confirm DPO details are published and contact details accessible.","format":"PDF","prompt_hint":"Search for Data Protection Officer (DPO) designation and contact email in policies."},
    {"sl":10,"standard":"DPDP / GDPR","label":"Data Subject Rights (DSR/DSAR)","icon":"👤","use_case":"Verify procedures for handling DSAR requests","expected":"Confirm response SLA for data deletion, access, and correction requests.","format":"PDF","prompt_hint":"Verify DSAR processing SLA, data deletion, correction procedures."},

    # --- SOC 2 ---
    {"sl":11,"standard":"SOC 2","label":"Security: Firewall & Encryption","icon":"🧱","use_case":"CC6.6, CC6.7 - Encryption in transit and rest","expected":"Verify firewall controls and SSL/TLS and AES encryption enforcement.","format":"PDF","prompt_hint":"Check encryption protocols in transit (TLS 1.2+) and at rest (AES-256)."},
    {"sl":12,"standard":"SOC 2","label":"Availability: Backup & Recovery","icon":"💾","use_case":"CC7.5 - Backup restoration and disaster recovery planning","expected":"Verify automated backups and disaster recovery runbook availability.","format":"PDF","prompt_hint":"Verify daily automated backups, offsite retention, and DR testing plan."},

    # --- BCMS ---
    {"sl":13,"standard":"BCMS (Business Continuity)","label":"BCMS Continuity & ISO Certificates","icon":"🏅","use_case":"Check the Stale/Expired ISO Certificates","expected":"Validate ISO/BCMS certifications, Risk/Severity and mitigation recommendation","format":"PDF","prompt_hint":"Check if ISO/BCMS certificate is expired or expiring. Provide risk and recommendation."},
    {"sl":14,"standard":"BCMS (Business Continuity)","label":"BCP Drill & Test Results","icon":"🏃‍♂️","use_case":"Verify annual BCP testing and drill execution","expected":"Verify BCP drill results and RTO/RPO performance verification.","format":"PDF","prompt_hint":"Search for Business Continuity Plan (BCP) testing dates and results inside logs."},

    # --- X-BOM ---
    {"sl":15,"standard":"X-BOM (Software Bill of Materials)","label":"License Agreement Validity","icon":"📄","use_case":"Check and summarize the validity of the license agreement","expected":"License Type, validity date, EOL/EOS status, Risk/Severity and recommendation","format":"PDF","prompt_hint":"Summarize the license type, validity dates. Identify if EOL/EOS. Provide risk severity and recommendation."},
    {"sl":16,"standard":"X-BOM (Software Bill of Materials)","label":"Third-party Disposal (Media A.7.10)","icon":"♻️","use_case":"Third-party EWaste disposal agreement – Media Handling (A.7.10)","expected":"Verify the validity of the EWaste Agreement certificate","format":"DOC","prompt_hint":"Verify the validity date and terms of the EWaste disposal agreement. Check if current and compliant."}
]

DEMO_FINDINGS = {
    1: [{"severity":"CRITICAL","control":"ISO 27001 A.5.15","finding":"No documented access control policy found in uploaded evidence.","recommendation":"Create and publish a formal Access Control Policy covering grant/review/revoke lifecycle."}],
    2: [{"severity":"HIGH","control":"ISO 27001 A.5.15 RBAC","finding":"Access granted on individual basis. No role-based model documented.","recommendation":"Implement RBAC model and document role definitions in the policy."}],
    3: [{"severity":"CRITICAL","control":"ISO 27001 A.8.5 / NIST IA-2","finding":"No MFA policy for VPN or cloud external access found in evidence.","recommendation":"Enforce MFA for all external access. Document password complexity and 90-day rotation."}],
    4: [{"severity":"HIGH","control":"ISO 27001 A.8.2","finding":"No time-limiting or enhanced monitoring of privileged accounts documented.","recommendation":"Implement Just-In-Time (JIT) privileged access with PAM tool logging and automated expiry."}],
    5: [{"severity":"HIGH","control":"ISO 27001 A.5.18","finding":"No evidence of periodic access reviews or orphaned account removal process.","recommendation":"Implement quarterly access review process with documented approvals."}],
    6: [{"severity":"HIGH","control":"ISO 27001 A.5.24","finding":"Incident Response Plan lacks vendor-specific security assessment clauses.","recommendation":"Add vendor security assessment section aligned with ISO 27001 A.5.24–A.5.28."}],
    7: [{"severity":"MEDIUM","control":"ISO 27001 A.5.28","finding":"Policy document last reviewed in 2021. No annual review evidence found.","recommendation":"Establish a documented annual review cycle with CISO sign-off."}],
    8: [{"severity":"CRITICAL","control":"DPDP Sec 6 / GDPR Art 7","finding":"Privacy notice lack granular consent options. Pre-checked boxes found for marketing.","recommendation":"Implement explicit, opt-in consent and uncheck marketing boxes by default."}],
    9: [{"severity":"HIGH","control":"DPDP Sec 10 / GDPR Art 37","finding":"DPO designation details are missing from the public privacy policy document.","recommendation":"Publish Data Protection Officer name, email, and postal address in the privacy notice."}],
    10: [{"severity":"HIGH","control":"DPDP Sec 12 / GDPR Art 15","finding":"DSAR policy does not specify statutory response timeframe (30 days for GDPR).","recommendation":"Update DSAR procedure to guarantee responses within 30 days and document DSR verification process."}],
    11: [{"severity":"CRITICAL","control":"SOC 2 CC6.6 / CC6.7","finding":"Production data transmitted over HTTP (unencrypted) in internal API endpoints.","recommendation":"Enforce HTTPS (TLS 1.3) across all internal microservices and disable SSLv3/TLS1.0."}],
    12: [{"severity":"HIGH","control":"SOC 2 CC7.5","finding":"DR Plan is present, but recovery restoration drills have not been performed or verified in 2025.","recommendation":"Schedule and execute a mock database recovery drill, and document the actual RTO/RPO achieved."}],
    13: [{"severity":"CRITICAL","control":"ISO 22301 Clause 9.1","finding":"ISO/BCMS Certificate expired on 2026-03-15. Certificate is no longer valid.","recommendation":"Initiate recertification audit immediately through an accredited body."}],
    14: [{"severity":"HIGH","control":"BCMS Continuity","finding":"No evidence of BCP testing or simulation drills in the last 12 months.","recommendation":"Conduct a BCP drill and document results before next audit."}],
    15: [{"severity":"CRITICAL","control":"Asset Mgmt / License","finding":"License expired on 2016-04-22 — 10 years ago. EOL confirmed with no vendor support.","recommendation":"Immediately replace or renew PJSIP software license to mitigate legal and security risk."}],
    16: [{"severity":"CRITICAL","control":"ISO 27001 A.7.10","finding":"EWaste Agreement Certificate is expired or not present in uploaded document.","recommendation":"Renew the third-party EWaste disposal agreement certificate immediately."}],
    "CROSS_FILE": [
        {"severity":"CRITICAL","control":"Cross-Document Correlation","finding":"Policy PDF (File 1) mandates 90-day password rotation, but Evidence Certificate (File 2) shows rotation set to 180 days.","recommendation":"Sync the actual system settings with the written policy document."},
        {"severity":"HIGH","control":"Cross-Document Correlation","finding":"Incident Plan (File 1) lists an external vendor for forensics, but the vendor contract (File 2) has been expired for 6 months.","recommendation":"Renew the vendor contract or update the Incident Plan with a new forensic partner."}
    ]
}

GAP_RESOLUTION = {
    "ISO 27001 A.5.15":            ["access control policy", "grant review revoke", "access policy document", "access control", "user access", "authorization policy"],
    "ISO 27001 A.5.15 RBAC":       ["role based", "rbac", "role assignment", "roles defined", "role-based access", "role-based"],
    "ISO 27001 A.8.5 / NIST IA-2":["mfa enabled", "multi-factor", "two-factor", "2fa", "authenticator app", "otp", "mfa", "2fa", "authenticator"],
    "ISO 27001 A.8.2":             ["privileged access", "pam tool", "just-in-time", "jit access", "time-limited access", "pam", "jit"],
    "ISO 27001 A.5.18":            ["access review completed", "quarterly review", "orphaned account removed", "account audit", "access review", "user review"],
    "ISO 27001 A.5.24":            ["vendor assessment", "vendor security", "third party assessment", "supplier review", "vendor", "third-party", "supplier"],
    "ISO 27001 A.5.28":            ["annual review", "policy reviewed 202", "reviewed and approved", "ciso sign", "annual review", "approved by ciso"],
    "DPDP Sec 6 / GDPR Art 7":     ["opt-in consent", "granular consent", "consent notice", "explicit consent", "consent form", "opt-in"],
    "DPDP Sec 10 / GDPR Art 37":   ["dpo email", "appointed dpo", "dpo details", "data protection officer", "dpo"],
    "DPDP Sec 12 / GDPR Art 15":   ["dsar SLA", "dsar response", "data subject rights", "30 days SLA", "dsar"],
    "SOC 2 CC6.6 / CC6.7":         ["tls 1.2", "tls 1.3", "https enforced", "aes-256", "encryption in transit", "tls", "https", "ssl", "encryption"],
    "SOC 2 CC7.5":                 ["dr test", "restore verify", "disaster recovery test", "backup test", "dr test", "disaster recovery", "backup"],
    "ISO 22301 Clause 9.1":        ["iso certified", "certificate valid", "certification active", "audit passed", "recertified", "iso certification", "certificate"],
    "BCMS Continuity":             ["bcp test", "drill conducted", "recovery test", "continuity test", "rto rpo", "bcp", "business continuity"],
    "Asset Mgmt / License":        ["license renewed", "new license", "valid license", "commercial agreement", "license valid until", "software license"],
    "ISO 27001 A.7.10":            ["e-waste", "ewaste", "disposal certificate", "media disposal", "certificate of destruction", "it asset disposal", "waste agreement", "ewaste", "e-waste", "disposal"],
}

# ── DATABASE ──────────────────────────────────────────────────────────────────
class Base(DeclarativeBase): pass
class AuditFinding(Base):
    __tablename__ = "audit_findings"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    use_case_sl    = Column(Integer)
    use_case_name  = Column(String(300))
    severity       = Column(String(50))
    control        = Column(String(200))
    finding        = Column(Text)
    recommendation = Column(Text)
    status         = Column(String(50), default="Open")
    comment        = Column(Text, default="")
    source_files   = Column(Text, default="All uploaded documents")
    created_at     = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    session_id     = Column(String(100))
    session_title  = Column(String(300))
    role           = Column(String(50))
    content        = Column(Text)
    created_at     = Column(DateTime, default=datetime.utcnow)

@st.cache_resource
def init_db():
    try:
        eng = create_engine("postgresql://postgres:ShakthiDB%402026@localhost:15234/postgres", connect_args={"connect_timeout":3})
        with eng.connect() as c: c.execute(text("SELECT 1"))
        try:
            with eng.connect() as c: c.execute(text("SELECT source_files FROM audit_findings LIMIT 1"))
        except:
            from sqlalchemy import MetaData
            meta = MetaData()
            meta.reflect(bind=eng)
            if "audit_findings" in meta.tables:
                meta.tables["audit_findings"].drop(bind=eng)
        Base.metadata.create_all(bind=eng)
        return eng, "ShaktiDB"
    except Exception as e:
        eng = create_engine("sqlite:///shakthidb_local.db")
        try:
            with eng.connect() as c: c.execute(text("SELECT source_files FROM audit_findings LIMIT 1"))
        except:
            from sqlalchemy import MetaData
            meta = MetaData()
            meta.reflect(bind=eng)
            if "audit_findings" in meta.tables:
                meta.tables["audit_findings"].drop(bind=eng)
        Base.metadata.create_all(bind=eng)
        return eng, "Local DB"

engine, db_label = init_db()

def save_findings(uc, findings):
    Session = sessionmaker(bind=engine)
    db = Session()
    db.query(AuditFinding).filter(AuditFinding.use_case_sl == uc["sl"]).delete()
    uc_name = uc.get("use_case", uc.get("label", "Comprehensive Enterprise Audit"))
    for f in findings:
        db.add(AuditFinding(use_case_sl=uc["sl"], use_case_name=uc_name[:290],
            severity=f.get("severity",""), control=f.get("control",""),
            finding=f.get("finding",""), recommendation=f.get("recommendation",""),
            status=f.get("status","Open"), comment=f.get("comment",""),
            source_files=f.get("source_files","")))
    db.commit(); db.close()

def get_all_findings():
    Session = sessionmaker(bind=engine)
    db = Session()
    rows = db.query(AuditFinding).order_by(AuditFinding.created_at.desc()).all()
    db.close(); return rows

def save_chat_message(session_id, session_title, role, content):
    Session = sessionmaker(bind=engine)
    db = Session()
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).update({ChatMessage.session_title: session_title})
    db.add(ChatMessage(session_id=session_id, session_title=session_title, role=role, content=content))
    db.commit()
    db.close()

def update_latest_assistant_message(session_id, content):
    Session = sessionmaker(bind=engine)
    db = Session()
    latest = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id,
        ChatMessage.role == "assistant"
    ).order_by(ChatMessage.created_at.desc()).first()
    if latest:
        latest.content = content
        db.commit()
    db.close()

def get_chat_history(session_id):
    Session = sessionmaker(bind=engine)
    db = Session()
    msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    db.close()
    return [{"role": m.role, "content": m.content} for m in msgs]

def get_chat_title(session_id):
    Session = sessionmaker(bind=engine)
    db = Session()
    msg = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).first()
    db.close()
    return msg.session_title if msg else None

def get_all_chat_sessions():
    Session = sessionmaker(bind=engine)
    db = Session()
    rows = db.query(
        ChatMessage.session_id,
        ChatMessage.session_title,
        ChatMessage.created_at
    ).order_by(ChatMessage.created_at.desc()).all()
    db.close()
    seen = set()
    sessions = []
    for r in rows:
        if r.session_id not in seen:
            seen.add(r.session_id)
            sessions.append({
                "session_id": r.session_id,
                "session_title": r.session_title,
                "created_at": r.created_at
            })
            if len(sessions) == 10:
                break
    return sessions

def clear_chat_session(session_id):
    Session = sessionmaker(bind=engine)
    db = Session()
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.commit()
    db.close()

def extract_text(f):
    name_lower = f.name.lower()
    if name_lower.endswith(".pdf"):
        with pdfplumber.open(f) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    elif name_lower.endswith((".xlsx", ".xls")):
        try:
            excel_data = pd.read_excel(f, sheet_name=None)
            sheets_text = []
            for sheet_name, df in excel_data.items():
                sheets_text.append(f"--- Sheet: {sheet_name} ---\n" + df.to_string(index=False))
            return "\n\n".join(sheets_text)
        except Exception as e:
            return f"[Error parsing Excel file {f.name}: {e}]"
    elif name_lower.endswith(".csv"):
        try:
            df = pd.read_csv(f)
            return df.to_string(index=False)
        except Exception as e:
            return f"[Error parsing CSV file {f.name}: {e}]"
    elif name_lower.endswith((".pptx", ".ppt")):
        try:
            from pptx import Presentation
            prs = Presentation(f)
            text_runs = []
            for slide_num, slide in enumerate(prs.slides, 1):
                text_runs.append(f"--- Slide {slide_num} ---")
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        text_runs.append(shape.text.strip())
                    if shape.has_table:
                        for row in shape.table.rows:
                            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                            if row_text:
                                text_runs.append(" | ".join(row_text))
            return "\n".join(text_runs)
        except Exception as e:
            return f"[Error parsing PowerPoint file {f.name}: {e}]"
    elif name_lower.endswith(".txt"):
        try:
            return f.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return f"[Error parsing text file {f.name}: {e}]"
    else:
        try:
            doc = Document(f)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            return f"[Error parsing Word file {f.name}: {e}]"

def scan_file_security(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    uploaded_file.seek(0)
    if bytes_data.startswith(b'MZ'):
        return False, "Executable payload disguised as document (MZ signature detected)."
    file_hash = hashlib.sha256(bytes_data).hexdigest()
    blacklist = ["5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"]
    if file_hash in blacklist:
        return False, f"Known malicious hash signature identified ({file_hash[:8]}...)."
    return True, "Clean"

def generate_ollama_findings(context, file_names_list, selected_sls, model_choice):
    if "Qwen 2.5 (7B)" in model_choice:
        ollama_model = "qwen2.5:7b"
    elif "Qwen 2.5 (3B)" in model_choice:
        ollama_model = "qwen2.5:3b"
    elif "Qwen 2.5 (1.5B)" in model_choice:
        ollama_model = "qwen2.5:1.5b"
    elif "Qwen 2.5 (0.5B)" in model_choice:
        ollama_model = "qwen2.5:0.5b"
    elif "Gemma 2 (2B)" in model_choice:
        ollama_model = "gemma2:2b"
    elif "1B" in model_choice:
        ollama_model = "llama3.2:1b"
    elif "3.2" in model_choice:
        ollama_model = "llama3.2"
    else:
        ollama_model = "llama3.1"
    
    controls_to_check = []
    control_names = []
    for k in selected_sls:
        if k in DEMO_FINDINGS:
            for f in DEMO_FINDINGS[k]:
                controls_to_check.append(f)
                control_names.append(f.get("control"))
                
    scanned_files_str = ", ".join(file_names_list) if file_names_list else "None"
    prompt = f"""You are a strict Cybersecurity Auditor. Evaluate the extracted evidence text against these controls.

EVIDENCE TEXT:
{context[:12000]}

CONTROLS TO AUDIT:
{json.dumps(control_names)}

INSTRUCTIONS:
1. Determine if the EVIDENCE TEXT provides sufficient proof to satisfy each control.
2. Return ONLY a JSON object containing a single array called "resolved_list" with the names of the controls that are satisfied by the evidence.
3. Do NOT provide explanations. ONLY output valid JSON.
Example format:
{{
  "resolved_list": ["ISO 27001 A.5.15", "SOC 2 CC6.6 / CC6.7"]
}}
"""
    try:
        r = requests.post("http://127.0.0.1:11434/api/generate",
            json={"model": ollama_model, "prompt": prompt, "stream": False, "format": "json"}, timeout=180)
        if r.status_code == 200:
            res = r.json().get("response", "{}")
            data = json.loads(res)
            resolved_list = data.get("resolved_list", [])
            findings = []
            for f in controls_to_check:
                if f.get("control") not in resolved_list:
                    f_copy = f.copy()
                    f_copy["source_files"] = f"Checked in: {scanned_files_str} (Evidence missing or insufficient)"
                    findings.append(f_copy)
            return resolved_list, findings
    except Exception as e:
        print(f"Ollama realtime finding error: {e}")
        pass
    return None, None

def ai_chat_stream(system_ctx, user_msg, model_choice):
    enhanced_sys = f"You are a Senior Cybersecurity Auditor with expertise in ISO 27001, NIST, and SOC 2. {system_ctx}"
    prompt = f"{enhanced_sys}\n\nUser: {user_msg}\n\nAI Auditor:"
    if "Qwen 2.5 (7B)" in model_choice:
        ollama_model = "qwen2.5:7b"
    elif "Qwen 2.5 (3B)" in model_choice:
        ollama_model = "qwen2.5:3b"
    elif "Qwen 2.5 (1.5B)" in model_choice:
        ollama_model = "qwen2.5:1.5b"
    elif "Qwen 2.5 (0.5B)" in model_choice:
        ollama_model = "qwen2.5:0.5b"
    elif "Gemma 2 (2B)" in model_choice:
        ollama_model = "gemma2:2b"
    elif "1B" in model_choice:
        ollama_model = "llama3.2:1b"
    elif "3.2" in model_choice:
        ollama_model = "llama3.2"
    else:
        ollama_model = "llama3.1"
    try:
        r = requests.post("http://127.0.0.1:11434/api/generate",
            json={"model": ollama_model, "prompt": prompt, "stream": True}, stream=True, timeout=90)
        if r.status_code != 200:
            try:
                err = r.json().get("error", r.text)
            except:
                err = r.text
            yield f"⚠️ Ollama Error: {err}. Please make sure you have downloaded the model using pull_models.bat!"
            return
        for line in r.iter_lines():
            if line:
                chunk = json.loads(line)
                yield chunk.get("response", "")
    except Exception as e:
        yield f"⚠️ Offline Engine not responding: {e}"

def _run_ollama_bg(bg_key, files_data, selected_sls_copy, ai_model):
    import io
    print(f"[_run_ollama_bg] Starting thread for key {bg_key} with model {ai_model}...")
    try:
        ctx = ""
        file_names_list = []
        for f_data in files_data:
            name = f_data["name"]
            file_bytes = f_data["bytes"]
            f_like = io.BytesIO(file_bytes)
            f_like.name = name
            is_clean, reason = scan_file_security(f_like)
            if not is_clean:
                print(f"[_run_ollama_bg] Security alert! Malware scan failed for file {name}: {reason}")
                with _bg_lock:
                    _bg_results[bg_key] = {"error": f"🚨 SECURITY ALERT: '{name}' BLOCKED! {reason}"}
                return
            text = extract_text(f_like)
            ctx += f"--- FILE: {name} ---\n{text}\n\n"
            file_names_list.append(name)
        context_str = ctx.strip()
        print(f"[_run_ollama_bg] Calling generate_ollama_findings for {len(selected_sls_copy)} controls...")
        llm_resolved, llm_findings = generate_ollama_findings(context_str, file_names_list, selected_sls_copy, ai_model)
        if llm_resolved is not None and llm_findings is not None:
            print(f"[_run_ollama_bg] Success! resolved: {len(llm_resolved)}, findings: {len(llm_findings)}")
            resolved_mapping = {}
            for ctrl in llm_resolved:
                resolved_mapping[ctrl] = file_names_list
            for finding in llm_findings:
                finding["status"] = "Open"
                finding["comment"] = ""
                finding["editing"] = False
            with _bg_lock:
                _bg_results[bg_key] = {
                    "findings": llm_findings,
                    "resolved_list": llm_resolved,
                    "resolved_count": len(resolved_mapping),
                    "resolved_controls": set(resolved_mapping.keys()),
                    "context": context_str
                }
        else:
            print(f"[_run_ollama_bg] Empty or None results returned from generate_ollama_findings.")
            with _bg_lock:
                _bg_results[bg_key] = {"error": "Ollama service returned empty results or is offline. Please make sure the service is running and the model is downloaded."}
    except Exception as e:
        print(f"[_run_ollama_bg] Exception raised in background thread: {str(e)}")
        with _bg_lock:
            _bg_results[bg_key] = {"error": f"Error contacting Ollama: {str(e)}. Ensure Ollama is active and the selected model is pulled."}
    finally:
        print(f"[_run_ollama_bg] Thread finished. Discarding running key {bg_key}.")
        with _bg_lock:
            _bg_running.discard(bg_key)

# ── QUERY ROUTER ──────────────────────────────────────────────────────────────
def get_query_param(key):
    try:
        val = st.query_params.get(key)
        if val: return val
    except:
        try:
            params = st.experimental_get_query_params()
            if key in params and params[key]: return params[key][0]
        except: pass
    return None

def clear_query_params():
    try:
        st.query_params.clear()
    except:
        try:
            st.experimental_set_query_params()
        except: pass

q_select = get_query_param("select")
q_delete = get_query_param("delete")

if q_select:
    st.session_state.active_chat_id = q_select
    all_msgs = get_chat_history(q_select)
    st.session_state.chat = [m for m in all_msgs if m["role"] != "findings_snapshot"]
    st.session_state._last_loaded_chat_id = q_select
    snapshots = [m for m in all_msgs if m["role"] == "findings_snapshot"]
    if snapshots:
        try:
            import json
            snap = json.loads(snapshots[-1]["content"])
            st.session_state.findings = snap.get("findings", [])
            st.session_state.resolved_list = snap.get("resolved_list", [])
            st.session_state.stage = snap.get("stage", 5)
            st.session_state["ollama_error"] = snap.get("error", None)
            st.session_state.context = snap.get("context", "")
            st.session_state.last_uploaded_names = snap.get("last_uploaded_names", "")
        except Exception: pass
    else:
        st.session_state.findings = []
        st.session_state.stage = 0
        st.session_state["ollama_error"] = None
        st.session_state.context = ""
        st.session_state.last_uploaded_names = ""
    clear_query_params()
    st.rerun()

if q_delete:
    clear_chat_session(q_delete)
    if "active_chat_id" in st.session_state and st.session_state.active_chat_id == q_delete:
        new_id = uuid.uuid4().hex
        st.session_state.active_chat_id = new_id
        st.session_state.chat = []
        st.session_state.findings = []
        st.session_state.stage = 0
        st.session_state._last_loaded_chat_id = new_id
        st.session_state["ollama_error"] = None
    clear_query_params()
    st.rerun()

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = uuid.uuid4().hex

for k,v in [("stage",0),("context",""),("findings",[]),("chat",[]),("sel_uc",0),("_last_loaded_chat_id",""),("severity_filter",set()),("ollama_error",None)]:
    if k not in st.session_state: st.session_state[k] = v

all_msgs = get_chat_history(st.session_state.active_chat_id)
st.session_state.chat = [m for m in all_msgs if m["role"] != "findings_snapshot"]
st.session_state._last_loaded_chat_id = st.session_state.active_chat_id

uc = USE_CASES[st.session_state.sel_uc]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ AICyberAuditBox")
    st.markdown("<small style='color:#64748b'>Agentic RAG Auditor</small>", unsafe_allow_html=True)
    st.markdown(f"<small style='color:#22c55e'>● {db_label} Connected</small>", unsafe_allow_html=True)
    st.divider()

    # ── New Chat button ───────────────────────────────────────────────────────
    if st.button("✏️  New Chat", use_container_width=True, type="secondary"):
        new_id = uuid.uuid4().hex
        st.session_state.active_chat_id = new_id
        st.session_state.update({
            "chat": [], "context": "", "findings": [], "stage": 0,
            "resolved_count": None, "resolved_controls": set(),
            "resolved_list": [], "ewaste_resolved": None,
            "last_uploaded_names": "", "_last_loaded_chat_id": new_id,
            "ollama_error": None
        })
        st.rerun()

    # ── Recents toggle ────────────────────────────────────────────────────────
    sessions = get_all_chat_sessions()

    if "recents_open" not in st.session_state:
        st.session_state.recents_open = False

    arrow = "▾" if st.session_state.recents_open else "▸"
    if st.button(f"{arrow}  Recents", use_container_width=True, key="recents_toggle"):
        st.session_state.recents_open = not st.session_state.recents_open
        st.rerun()

    # ── Modern Recent Chat CSS ────────────────────────────────────────────────
    st.markdown("""
<style>
.chat-section{ font-size:10px; font-weight:700; color:#64748b; letter-spacing:1px; margin:14px 0 6px 4px; }
</style>
""", unsafe_allow_html=True)

    # ── Recent Chat List ──────────────────────────────────────────────────────
    if st.session_state.recents_open:
        if not sessions:
            st.markdown("<div style='color:#64748b;font-size:11px;padding:8px 4px'>No chats yet</div>", unsafe_allow_html=True)
        else:
            today_done = False
            earlier_done = False
            html_items = []

            for idx, s in enumerate(sessions):
                title = (s["session_title"] or "Untitled Chat")[:45]
                is_active = s["session_id"] == st.session_state.active_chat_id
                created_at = s.get("created_at")
                is_today = False
                if created_at:
                    if isinstance(created_at, str):
                        try: created_at = datetime.fromisoformat(created_at)
                        except: pass
                    if isinstance(created_at, datetime):
                        is_today = created_at.date() == datetime.utcnow().date()
                
                # Section headers inside the HTML structure
                if is_today and not today_done:
                    html_items.append("<div class='chat-section'>TODAY</div>")
                    today_done = True
                elif not is_today and not earlier_done:
                    html_items.append("<div class='chat-section'>EARLIER</div>")
                    earlier_done = True

                row_class = "chatgpt-row chatgpt-row-active" if is_active else "chatgpt-row chatgpt-row-inactive"
                
                # Render clean HTML link row
                html_row = (
                    f'<div class="{row_class}">'
                    f'<a href="?select={s["session_id"]}" target="_self" class="chatgpt-row-left">'
                    f'<span class="chatgpt-row-icon">💬</span>'
                    f'<span class="chatgpt-row-title">{title}</span>'
                    f'</a>'
                    f'<div class="chatgpt-row-delete">'
                    f'<a href="?delete={s["session_id"]}" target="_self" class="chatgpt-row-delete-link" title="Delete Chat">✕</a>'
                    f'</div>'
                    f'</div>'
                )
                html_items.append(html_row)

            # Join all items and render in a single markdown block
            st.markdown(f'<div class="chatgpt-sidebar-list">{"".join(html_items)}</div>', unsafe_allow_html=True)




    st.divider()

    st.markdown("**AI Engine Setup**")
    ai_model = st.selectbox("Select Offline LLM (via Ollama)", [
        "Llama 3.2 (1B) - Ultra Fast (Instant)",
        "Llama 3.2 (3B) - Fast Inference (Under 1 min)", 
        "Llama 3.1 (8B) - High Performance Generalist", 
        "Gemma 2 (2B) - Light & Highly Accurate",
        "Qwen 2.5 (0.5B) - Micro Auditor",
        "Qwen 2.5 (1.5B) - Ultra Light",
        "Qwen 2.5 (3B) - Light Auditor",
        "Qwen 2.5 (7B) - High Performance Auditor/Reasoning"
    ], label_visibility="collapsed", index=0)

    st.divider()

    st.markdown("**Compliance Standard**")
    selected_standard = st.selectbox("Select Target Framework", [
        "All Standards",
        "ISO 27001",
        "DPDP / GDPR",
        "SOC 2",
        "BCMS (Business Continuity)",
        "X-BOM (Software Bill of Materials)"
    ], label_visibility="collapsed")

    if selected_standard == "All Standards":
        filtered_use_cases = USE_CASES
    else:
        filtered_use_cases = [u for u in USE_CASES if u["standard"] == selected_standard]
       
    st.markdown("**Target Controls to Audit**")
    selected_control_labels = st.multiselect(
        "Select individual controls",
        options=[u["label"] for u in filtered_use_cases],
        default=[u["label"] for u in filtered_use_cases],
        label_visibility="collapsed"
    )
    
    selected_ucs = [u for u in filtered_use_cases if u["label"] in selected_control_labels]
    selected_sls = {u["sl"] for u in selected_ucs}
    st.divider()

    st.markdown("**Upload Evidence**")
    uploaded = st.file_uploader("Upload evidence document(s)", type=["pdf","docx","doc","xlsx","xls","csv","pptx","ppt","txt"],
                                accept_multiple_files=True, label_visibility="collapsed")
    
    if "last_uploaded_names" not in st.session_state:
        st.session_state.last_uploaded_names = ""
    
    uploaded_names_str = ", ".join([f.name for f in uploaded]) if uploaded else ""
    if (uploaded_names_str != st.session_state.last_uploaded_names) or (uploaded and not st.session_state.context):
        if uploaded:
            auto_ctx = ""
            for f in uploaded:
                try:
                    auto_ctx += f"--- FILE: {f.name} ---\n{extract_text(f)}\n\n"
                except Exception as ex:
                    auto_ctx += f"--- FILE: {f.name} ---\n(Error extracting text: {ex})\n\n"
            st.session_state.context = auto_ctx.strip()
        else:
            st.session_state.context = ""
        st.session_state.last_uploaded_names = uploaded_names_str

    st.divider()

    with _bg_lock:
        is_current_running = st.session_state.active_chat_id in _bg_running

    col_run, col_rst = st.columns([2,1])
    if is_current_running:
        col_run.markdown("""
        <div style='background:linear-gradient(90deg,#3b82f6,#1d4ed8,#3b82f6);background-size:200% 100%;animation:btn_shimmer 1.5s infinite linear;border-radius:8px;padding:10px 16px;text-align:center;color:white;font-weight:600;font-size:0.88rem'>
          <style>@keyframes btn_shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}</style>
          🧠 Analyzing...
        </div>
        """, unsafe_allow_html=True)
        run = False
    else:
        run = col_run.button("▶ Run Analysis", type="primary", use_container_width=True)
        
    if col_rst.button("↺", use_container_width=True):
        with _bg_lock:
            _bg_running.discard(st.session_state.active_chat_id)
            _bg_results.pop(st.session_state.active_chat_id, None)
        st.session_state.update({
            "stage": 0, "context": "", "findings": [], "chat": [], 
            "ewaste_resolved": None, "ollama_error": None,
            "resolved_count": None, "resolved_controls": set(), "resolved_list": []
        })
        clear_chat_session(st.session_state.active_chat_id)
        st.session_state.active_chat_id = uuid.uuid4().hex
        st.rerun()
    
    resolved = st.session_state.get("resolved_count", None)
    if resolved is not None and not is_current_running and not st.session_state.get("ollama_error"):
        if resolved > 0:
            st.success(f"✅ {resolved} gap(s) resolved by uploaded evidence")
        else:
            st.warning("⚠️ No resolving evidence found in documents")
            with st.expander("🔍 Inspect Extracted Text"):
                if st.session_state.get("context", ""):
                    st.text_area("Extracted Context (First 3000 chars)", st.session_state.context[:3000], height=200, disabled=True)
                else:
                    st.error("No text could be extracted. The document may be empty, password-protected, or a scanned image.")

# ── PIPELINE EXECUTION ────────────────────────────────────────────────────────
if run:
    print(f"[PIPELINE] 'Run Analysis' clicked. active_chat_id={st.session_state.active_chat_id}")
    if not uploaded:
        st.sidebar.error("Please upload the evidence file first.")
    elif is_current_running:
        st.sidebar.warning("⏳ Analysis is already running in the background...")
    else:
        if st.session_state.stage == 5 or len(st.session_state.findings) > 0:
            new_id = uuid.uuid4().hex
            st.session_state.active_chat_id = new_id
            st.session_state.update({
                "chat": [], "context": "", "findings": [], "stage": 0,
                "resolved_count": None, "resolved_controls": set(),
                "resolved_list": [], "ewaste_resolved": None,
                "last_uploaded_names": "", "_last_loaded_chat_id": new_id,
                "ollama_error": None
            })
            auto_ctx = ""
            for f in uploaded:
                try:
                    auto_ctx += f"--- FILE: {f.name} ---\n{extract_text(f)}\n\n"
                except Exception as ex:
                    auto_ctx += f"--- FILE: {f.name} ---\n(Error extracting text: {ex})\n\n"
            st.session_state.context = auto_ctx.strip()
            st.session_state.last_uploaded_names = ", ".join([f.name for f in uploaded])

        files_data = []
        for f in uploaded:
            files_data.append({"name": f.name, "bytes": f.getvalue()})
            
        bg_key = st.session_state.active_chat_id
        with _bg_lock:
            _bg_running.add(bg_key)
            
        st.session_state.stage = 5
        st.session_state.findings = []
        st.session_state.resolved_list = []
        st.session_state["resolved_count"] = None
        st.session_state["resolved_controls"] = set()
        st.session_state["ollama_error"] = None
        
        save_chat_message(
            bg_key,
            f"Scanning... · {datetime.now().strftime('%d %b %H:%M')}",
            "findings_snapshot",
            json.dumps({"findings": [], "resolved_list": [], "stage": 5})
        )
        
        thread = threading.Thread(
            target=_run_ollama_bg,
            args=(bg_key, files_data, set(selected_sls), ai_model),
            daemon=True
        )
        thread.start()
        st.rerun()

# ── MAIN LAYOUT ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
  <div style="display:flex;align-items:center;gap:16px">
    <div style="font-size:2.5rem">🛡️</div>
    <div>
      <div style="font-size:1.6rem;font-weight:700;color:#f8fafc">AICyberAuditBox</div>
      <div style="color:#64748b;font-size:.9rem">Agentic RAG · Cyber Security Audit Intelligence</div>
    </div>
    <div style="margin-left:auto;text-align:right">
      <div style="color:#22c55e;font-weight:600;font-size:.85rem">● SYSTEM ONLINE</div>
      <div style="color:#64748b;font-size:.8rem">{datetime.now().strftime('%d %b %Y  %H:%M')}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

@st.fragment(run_every=timedelta(seconds=3))
def _check_bg_analysis():
    st.markdown("<span style='display:none; height:0; width:0;'></span>", unsafe_allow_html=True)
    bg_key = st.session_state.active_chat_id
    with _bg_lock:
        if bg_key in _bg_results:
            results = _bg_results.pop(bg_key)
            if results is not None:
                if "error" in results:
                    st.session_state["ollama_error"] = results["error"]
                    st.session_state.findings = []
                    st.session_state.resolved_list = []
                    st.session_state["resolved_count"] = 0
                    st.session_state["resolved_controls"] = set()
                    st.session_state.stage = 5
                    snapshot = json.dumps({"findings": [], "resolved_list": [], "stage": 5, "error": results["error"], "context": "", "last_uploaded_names": ""})
                    save_chat_message(st.session_state.active_chat_id, f"Audit Error · {datetime.now().strftime('%d %b %H:%M')}", "findings_snapshot", snapshot)
                    st.toast("⚠️ AI deep scan failed - Ollama error!")
                else:
                    st.session_state["ollama_error"] = None
                    st.session_state.findings = results["findings"]
                    st.session_state.resolved_list = results["resolved_list"]
                    st.session_state["resolved_count"] = results["resolved_count"]
                    st.session_state["resolved_controls"] = results["resolved_controls"]
                    st.session_state.context = results.get("context", "")
                    st.session_state.stage = 5
                    snapshot = json.dumps({
                        "findings": results["findings"],
                        "resolved_list": results["resolved_list"],
                        "stage": 5,
                        "context": results.get("context", ""),
                        "last_uploaded_names": st.session_state.get("last_uploaded_names", "")
                    })
                    save_chat_message(st.session_state.active_chat_id, f"Audit · {datetime.now().strftime('%d %b %H:%M')}", "findings_snapshot", snapshot)
                    st.toast("🧠 AI deep scan complete — results refined!")
            st.rerun()

_check_bg_analysis()

with st.container():
    tab_report, tab_chat, tab_records = st.tabs(["📊  Audit Report", "💬  AI Assistant", "🗄️  Audit Records"])

    with tab_report:
        with _bg_lock:
            is_currently_running = st.session_state.active_chat_id in _bg_running
            
        if is_currently_running:
            st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; min-height: 250px; flex-direction: column;'>
                <div class='custom-spinner'></div>
                <div style='color: #60a5fa; font-weight: 600; font-size: 0.95rem; margin-top: 16px;'>Deep AI Scanning In Progress...</div>
                <style>
                    .custom-spinner { border: 4px solid rgba(59, 130, 246, 0.1); border-top: 4px solid #3b82f6; border-radius: 50%; width: 48px; height: 48px; animation: spin_loader 1s linear infinite; }
                    @keyframes spin_loader { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                </style>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.get("ollama_error"):
            err_msg = st.session_state["ollama_error"]
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #2d1616 0%, #0f0505 100%); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 16px; padding: 40px; text-align: center; margin: 20px 0;'>
                <div style='font-size: 3.5rem; margin-bottom: 16px;'>⚠️</div>
                <h3 style='color: #fca5a5; font-weight: 700; margin-bottom: 8px;'>Ollama Service Error</h3>
                <p style='color: #f87171; max-width: 600px; margin: 0 auto 24px auto; font-size: 0.92rem; line-height: 1.5;'>{err_msg}</p>
                <div style='background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 16px; text-align: left; max-width: 550px; margin: 0 auto; color: #cbd5e1; font-size: 0.85rem;'>
                    <b style='color: #fca5a5;'>How to resolve:</b><br>
                    1. Verify that the Ollama service is active on your machine by running <code>ollama serve</code> or opening the Ollama application.<br>
                    2. Ensure you have pulled the selected model by running the <code>pull_models.bat</code> script located in the project directory.<br>
                    3. Upload your documents and click <b>▶ Run Analysis</b> to try again.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.stage == 0:
            st.markdown("### 📤 Upload Evidence to Begin")
            st.info("Select compliance framework and individual controls in the sidebar, upload your evidence document(s), and click **Run Analysis** to automatically detect security gaps.")

        elif st.session_state.stage == 5:
            findings = st.session_state.findings
            resolved_list = st.session_state.get("resolved_list", [])
            active_findings = [f for f in findings if f.get("status", "Open") != "Dismissed"]
            counts = {"CRITICAL":0,"HIGH":0,"MEDIUM":0}
            for f in active_findings:
                sev = f.get("severity","MEDIUM").upper()
                if sev in counts: counts[sev] = counts[sev] + 1

            sf = st.session_state.get("severity_filter", set())
            if not isinstance(sf, set):
                sf = set()

            def _stat_card(col, color, count, label, filter_val, btn_key, emj):
                is_active = filter_val in sf
                border   = f"2px solid {color}" if is_active else "1px solid #334155"
                glow     = f"0 0 20px {color}44" if is_active else "none"
                badge    = (f"<div style='font-size:0.65rem;color:{color};margin-top:4px;font-weight:700;letter-spacing:.05em'>&#9679; ACTIVE</div>"
                            if is_active else
                            "<div style='font-size:0.65rem;color:#475569;margin-top:4px'>click to select</div>")
                col.markdown(f"""
<div class='stat-card' style='border:{border};box-shadow:{glow};cursor:pointer;transition:all 0.3s;'>
  <div class='stat-num' style='color:{color}'>{count}</div>
  <div style='color:#94a3b8'>{label}</div>
  {badge}
</div>""", unsafe_allow_html=True)
                btn_lbl = f"{emj} ✕ {label}" if is_active else f"{emj} {label}"
                if col.button(btn_lbl, key=btn_key, use_container_width=True,
                              type="primary" if is_active else "secondary"):
                    new_sf = set(sf)
                    if is_active:
                        new_sf.discard(filter_val)
                    else:
                        new_sf.add(filter_val)
                    st.session_state.severity_filter = new_sf
                    st.rerun()

            c1, c2, c3, c4 = st.columns(4)
            _stat_card(c1, "#ef4444", counts['CRITICAL'],  "P1 · Critical", "CRITICAL", "flt_crit", "🔴")
            _stat_card(c2, "#f97316", counts['HIGH'],      "P2 · High",     "HIGH",     "flt_high", "🟠")
            _stat_card(c3, "#eab308", counts['MEDIUM'],    "P3 · Medium",   "MEDIUM",   "flt_med",  "🟡")
            _stat_card(c4, "#22c55e", len(resolved_list),  "✓ Resolved",    "RESOLVED", "flt_res",  "✅")

            _fc = {"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#eab308","RESOLVED":"#22c55e"}
            _fl = {"CRITICAL":"P1 · Critical","HIGH":"P2 · High","MEDIUM":"P3 · Medium","RESOLVED":"✓ Resolved"}
            if sf:
                tags_html = " ".join(
                    f"<span style='background:{_fc[v]}22;border:1px solid {_fc[v]};border-radius:12px;padding:2px 10px;color:{_fc[v]};font-weight:600;font-size:0.8rem'>{_fl[v]}</span>"
                    for v in ["CRITICAL","HIGH","MEDIUM","RESOLVED"] if v in sf
                )
                clear_note = "&nbsp;&middot;&nbsp; <i style='font-size:0.78rem'>Click an active card to deselect</i>"
                st.markdown(f"""<div style='background:rgba(59,130,246,0.07);border:1px solid #3b82f6;border-radius:8px;padding:9px 16px;margin:10px 0;display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>
&#128269; <b style='color:#f8fafc'>Active filters:</b> {tags_html} {clear_note}
</div>""", unsafe_allow_html=True)

            open_sev_filters = sf - {"RESOLVED"}
            if resolved_list and "RESOLVED" not in sf:
                resolved_html = " &nbsp;·&nbsp; ".join([f"<b>{c}</b>" for c in resolved_list])
                st.markdown(f"<div style='background:rgba(34,197,94,0.1);border:1px solid #22c55e;border-radius:8px;padding:10px 16px;margin:12px 0;color:#22c55e;font-size:0.85rem'>✅ <b>Resolved Controls:</b> &nbsp;{resolved_html}</div>", unsafe_allow_html=True)

            if "RESOLVED" in sf:
                if resolved_list:
                    st.markdown("<br>", unsafe_allow_html=True)
                    _uc_by_ctrl = {}
                    for _uc in USE_CASES:
                        for _df_list in DEMO_FINDINGS.values():
                            if isinstance(_df_list, list):
                                for _df in _df_list:
                                    if _df.get("control"):
                                        _uc_by_ctrl[_df["control"]] = {"uc": _uc if _uc["sl"] in DEMO_FINDINGS and any(d.get("control") == _df["control"] for d in DEMO_FINDINGS.get(_uc["sl"], [])) else None, "demo": _df}
                    
                    resolved_controls_set = st.session_state.get("resolved_controls", set())
                    resolved_file_mapping = {}
                    for ctrl_name in resolved_list:
                        if ctrl_name in resolved_controls_set:
                            resolved_file_mapping[ctrl_name] = "Uploaded evidence documents"

                    for ctrl in resolved_list:
                        info = _uc_by_ctrl.get(ctrl, {})
                        demo = info.get("demo", {})
                        matched_uc = None
                        for _uc in USE_CASES:
                            sl = _uc["sl"]
                            if sl in DEMO_FINDINGS:
                                for _df in DEMO_FINDINGS[sl]:
                                    if _df.get("control") == ctrl:
                                        matched_uc = _uc
                                        break
                            if matched_uc:
                                break

                        uc_label = matched_uc["label"] if matched_uc else ctrl
                        uc_icon = matched_uc.get("icon", "✅") if matched_uc else "✅"
                        uc_standard = matched_uc.get("standard", "") if matched_uc else ""
                        uc_expected = matched_uc.get("expected", "") if matched_uc else ""
                        orig_finding = demo.get("finding", "N/A")
                        orig_recommendation = demo.get("recommendation", "N/A")
                        orig_severity = demo.get("severity", "")
                        sev_color_map = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308"}
                        orig_sev_color = sev_color_map.get(orig_severity, "#94a3b8")
                        
                        st.markdown(f"""
                        <div style='background:rgba(34,197,94,0.07);border:1px solid #22c55e;border-left:5px solid #22c55e;border-radius:10px;padding:18px 22px;margin:10px 0;color:#f8fafc'>
                          <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px'>
                            <div><span style='font-size:1.2rem'>{uc_icon}</span><b style='color:#22c55e;font-size:1rem;margin-left:6px'>RESOLVED</b><span style='color:#94a3b8;margin-left:8px;font-size:0.85rem'>{uc_standard}</span></div>
                            <span style='font-size:0.72rem;background:#22c55e;color:#0a0a0a;padding:2px 10px;border-radius:12px;font-weight:700'>✓ COMPLIANT</span>
                          </div>
                          <div style='font-size:1.05rem;font-weight:600;color:#e2e8f0;margin-bottom:4px'>{uc_label}</div>
                          <div style='font-size:0.82rem;color:#94a3b8;margin-bottom:10px'><b>Control:</b> {ctrl}</div>
                          <div style='border-top:1px dashed #334155;padding-top:10px;margin-top:4px'>
                            <div style='font-size:0.82rem;color:#86efac;margin-bottom:6px'><b>✅ Expected Evidence:</b> {uc_expected}</div>
                            <div style='font-size:0.82rem;color:#94a3b8;margin-bottom:4px'><b>Original Gap (now resolved):</b><span style='text-decoration:line-through;color:#64748b;margin-left:4px'>{orig_finding}</span></div>
                            <div style='font-size:0.82rem;color:#64748b;margin-bottom:4px'><b>Was:</b> <span style='color:{orig_sev_color};font-weight:600'>{orig_severity}</span> &nbsp;→&nbsp; <span style='color:#22c55e;font-weight:600'>RESOLVED</span></div>
                            <div style='font-size:0.82rem;color:#86efac'><b>→ Recommendation (completed):</b> <span style='color:#64748b'>{orig_recommendation}</span></div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No controls resolved yet. Upload evidence and run the analysis.")

            st.markdown(f"<br><small style='color:#64748b'>Generated · {datetime.now().strftime('%d %b %Y %H:%M:%S')} · {selected_standard} ({len(selected_ucs)} Controls)</small>", unsafe_allow_html=True)
            st.divider()

            SEVERITY_LABEL = {"CRITICAL": "P1 · CRITICAL", "HIGH": "P2 · HIGH", "MEDIUM": "P3 · MEDIUM"}
            CSS = {"CRITICAL":"badge-critical","HIGH":"badge-high","MEDIUM":"badge-medium"}
            EMJ = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡"}

            open_findings_sorted = sorted(active_findings, key=lambda x: ["CRITICAL","HIGH","MEDIUM"].index(x.get("severity","MEDIUM").upper()))

            if sf and not open_sev_filters:
                displayed_findings = []
            elif open_sev_filters:
                displayed_findings = [f for f in open_findings_sorted if f.get("severity","MEDIUM").upper() in open_sev_filters]
            else:
                displayed_findings = open_findings_sorted

            for idx, f in enumerate(displayed_findings):
                s = f.get("severity","MEDIUM").upper()
                label = SEVERITY_LABEL.get(s, s)
                css = CSS.get(s, "badge-medium")
                emj = EMJ.get(s, "🟡")
                status = f.get("status", "Open")
                editing = f.get("editing", False)
                status_color = "#3b82f6" if status == "Open" else "#22c55e"
                
                if editing:
                    with st.container(border=True):
                        st.markdown("##### ✏️ Modify Finding Details")
                        col_edit_sev, col_edit_ctrl = st.columns([1, 2])
                        with col_edit_sev:
                            sev_index = ["CRITICAL", "HIGH", "MEDIUM"].index(s) if s in ["CRITICAL", "HIGH", "MEDIUM"] else 2
                            new_sev = st.selectbox("Severity", ["CRITICAL", "HIGH", "MEDIUM"], index=sev_index, key=f"sev_edit_sel_{idx}")
                        with col_edit_ctrl:
                            new_ctrl = st.text_input("Control", value=f.get("control", ""), key=f"ctrl_edit_in_{idx}")
                        new_finding = st.text_area("Finding Description", value=f.get("finding", ""), key=f"find_edit_ta_{idx}", height=80)
                        new_rec = st.text_area("Recommendation/Mitigation", value=f.get("recommendation", ""), key=f"rec_edit_ta_{idx}", height=80)
                        new_src = st.text_input("Source File Scope", value=f.get("source_files", "All uploaded documents"), key=f"src_edit_in_{idx}")
                        col_save, col_cancel = st.columns([1.5, 1.5])
                        with col_save:
                            if st.button("💾 Save Changes", key=f"save_edit_{idx}", type="primary", use_container_width=True):
                                for orig_f in st.session_state.findings:
                                    if orig_f["control"] == f["control"] and orig_f["finding"] == f["finding"]:
                                        orig_f["severity"] = new_sev
                                        orig_f["control"] = new_ctrl
                                        orig_f["finding"] = new_finding
                                        orig_f["recommendation"] = new_rec
                                        orig_f["source_files"] = new_src
                                        orig_f["editing"] = False
                                st.rerun()
                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_edit_{idx}", use_container_width=True):
                                for orig_f in st.session_state.findings:
                                    if orig_f["control"] == f["control"] and orig_f["finding"] == f["finding"]:
                                        orig_f["editing"] = False
                                st.rerun()
                else:
                    st.markdown(f"""
                    <div class='{css}' style='margin-bottom:0px; border-bottom-left-radius:0px; border-bottom-right-radius:0px;'>
                      <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <b>{emj} {label}</b>
                        <span style='font-size:0.75rem; background:{status_color}; color:white; padding:2px 8px; border-radius:12px; font-weight:600;'>{status.upper()}</span>
                      </div>
                      <div style='margin-top:6px;'><b>Control:</b> {f.get('control','')}</div>
                      <span style='color:#cbd5e1'>📌 <b>Finding:</b> {f.get('finding','')}</span><br>
                      <span style='color:#86efac'>→ <b>Recommendation:</b> {f.get('recommendation','')}</span>
                      <div style='margin-top:8px; font-size:0.8rem; color:#94a3b8; border-top:1px dashed #334155; padding-top:6px; display:flex; align-items:center; gap:6px;'>
                        <span>📁</span> <b>Source File Scope:</b> <i>{f.get('source_files','All uploaded documents')}</i>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.container(border=True):
                        col_act1, col_act2, col_act3, col_act4 = st.columns([1.8, 1.8, 1.8, 5])
                        with col_act1:
                            if status == "Accepted":
                                if st.button("↩ Undo", key=f"undo_{idx}", use_container_width=True, type="secondary"):
                                    for orig_f in st.session_state.findings:
                                        if orig_f["control"] == f["control"] and orig_f["finding"] == f["finding"]:
                                            orig_f["status"] = "Open"
                                    st.rerun()
                            else:
                                if st.button("✓ Accept", key=f"acc_{idx}", use_container_width=True, type="secondary"):
                                    for orig_f in st.session_state.findings:
                                        if orig_f["control"] == f["control"] and orig_f["finding"] == f["finding"]:
                                            orig_f["status"] = "Accepted"
                                    st.rerun()
                        with col_act2:
                            if st.button("✏️ Modify", key=f"mod_{idx}", use_container_width=True, type="secondary"):
                                for orig_f in st.session_state.findings:
                                    if orig_f["control"] == f["control"] and orig_f["finding"] == f["finding"]:
                                        orig_f["editing"] = True
                                st.rerun()
                        with col_act3:
                            if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True, type="secondary"):
                                for orig_f in st.session_state.findings:
                                    if orig_f["control"] == f["control"] and orig_f["finding"] == f["finding"]:
                                        orig_f["status"] = "Dismissed"
                                st.rerun()
                        with col_act4:
                            comment_val = st.text_input("Auditor Notes", value=f.get("comment", ""), key=f"cmt_{idx}", label_visibility="collapsed", placeholder="Add auditor notes or comments...")
                            if comment_val != f.get("comment", ""):
                                for orig_f in st.session_state.findings:
                                    if orig_f["control"] == f["control"] and orig_f["finding"] == f["finding"]:
                                        orig_f["comment"] = comment_val

            dismissed_findings = [df for df in findings if df.get("status", "Open") == "Dismissed"]
            if dismissed_findings:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander(f"🗑️ Deleted Findings ({len(dismissed_findings)})", expanded=False):
                    for idx_d, df in enumerate(dismissed_findings):
                        col_text, col_restore = st.columns([8, 2])
                        with col_text:
                            st.markdown(f"**{df.get('control', '')}** — <span style='color:#94a3b8'>{df.get('finding', '')[:90]}...</span>", unsafe_allow_html=True)
                        with col_restore:
                            if st.button("↩ Restore", key=f"restore_{idx_d}", use_container_width=True):
                                for orig_f in st.session_state.findings:
                                    if orig_f["control"] == df["control"] and orig_f["finding"] == df["finding"]:
                                        orig_f["status"] = "Open"
                                st.rerun()

            st.divider()
            b1, b2 = st.columns(2)
            with b1:
                if st.button("💾  Save to ShaktiDB", type="primary", use_container_width=True):
                    save_findings({"sl": 0, "use_case": f"{selected_standard} Audit Run"}, active_findings)
                    st.success(f"✅ {len(active_findings)} findings saved to {db_label}")
            with b2:
                df_export = pd.DataFrame([{
                    "Control": f.get("control", ""),
                    "Severity": f.get("severity", ""),
                    "Finding": f.get("finding", ""),
                    "Recommendation": f.get("recommendation", ""),
                    "Status": f.get("status", "Open"),
                    "Source Scope": f.get("source_files", "All uploaded documents"),
                    "Auditor Comment": f.get("comment", "")
                } for f in active_findings])
                csv_data = df_export.to_csv(index=False)
                st.download_button("⬇️  Export Report CSV", csv_data, "comprehensive_audit_report.csv", use_container_width=True)

    with tab_chat:
        if st.session_state.get("temp_stream_ans"):
            paused_ans = st.session_state.temp_stream_ans.strip()
            if paused_ans:
                st.session_state.chat.append({"role": "assistant", "content": paused_ans + " *(Generation Paused)*"})
                update_latest_assistant_message(st.session_state.active_chat_id, paused_ans + " *(Generation Paused)*")
            st.session_state.temp_stream_ans = ""
            st.rerun()

        st.markdown("""
        <div style='background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px;margin-bottom:16px;display:flex;align-items:center;gap:12px'>
          <div style='font-size:2rem'>🤖</div>
          <div>
            <div style='font-weight:700;color:#f8fafc'>AI Audit Assistant</div>
            <div style='color:#64748b;font-size:.85rem'>Local LLM · No internet required · Evidence-aware</div>
          </div>
          <div style='margin-left:auto;color:#22c55e;font-size:.8rem;font-weight:600'>● ONLINE</div>
        </div>""", unsafe_allow_html=True)
        
        with _bg_lock:
            is_currently_running = st.session_state.active_chat_id in _bg_running
            
        if is_currently_running:
            st.markdown("""
            <div style='background:rgba(59,130,246,0.06); border:1px solid rgba(59, 130, 246, 0.2); border-radius:8px; padding:12px 16px; margin-bottom:16px; display:flex; align-items:center; gap:12px;'>
              <div class='inline-spinner'></div>
              <div style='color:#60a5fa; font-size:0.85rem; font-weight:600;'>Deep AI Scan In Progress... The Audit Report will automatically update when complete!</div>
              <style>.inline-spinner { border: 2px solid rgba(59, 130, 246, 0.1); border-top: 2px solid #3b82f6; border-radius: 50%; width: 16px; height: 16px; animation: spin_inline 1s linear infinite; } @keyframes spin_inline { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
            </div>
            """, unsafe_allow_html=True)
            
        if st.session_state.get("ollama_error"):
            st.error(f"⚠️ Ollama Service Error: {st.session_state['ollama_error']}. Please click on the **Audit Report** tab to troubleshoot and try again.")
            
        if len(st.session_state.context) > 0:
            st.markdown("<div style='background:rgba(59,130,246,0.1); border:1px solid #3b82f6; border-radius:8px; padding:8px 12px; color:#3b82f6; font-size:0.85rem; font-weight:600; margin-bottom:16px'>🔍 Cross-File Intelligence Active · Correlating multiple evidence sources</div>", unsafe_allow_html=True)

        if st.session_state.context:
            st.success(f"✅ Evidence document loaded · {len(st.session_state.context):,} characters indexed")
        else:
            st.info("💡 Upload and run analysis first for evidence-aware answers, or ask general cybersecurity questions.")

        for msg in st.session_state.chat:
            if msg["role"] == "findings_snapshot":
                continue
            if msg["role"] == "user":
                st.markdown(f"<div style='text-align:right;font-size:11px;color:#64748b;margin-top:8px;margin-right:2px'>You</div><div style='display:flex;justify-content:flex-end;width:100%'><div class='chat-bubble-user'>{msg['content']}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size:11px;color:#3b82f6;font-weight:600;margin-top:8px;margin-left:2px'>🤖 AI Auditor</div><div style='display:flex;justify-content:flex-start;width:100%'><div class='chat-bubble-bot'>{msg['content']}</div></div>", unsafe_allow_html=True)

        user_msg = st.chat_input("Ask the AI Auditor anything...")
        if user_msg:
            title = get_chat_title(st.session_state.active_chat_id)
            if not title:
                title = user_msg[:30] + ("..." if len(user_msg) > 30 else "")
            save_chat_message(st.session_state.active_chat_id, title, "user", user_msg)
            save_chat_message(st.session_state.active_chat_id, title, "assistant", "")
            
            # Display user message instantly and add to session state chat history
            st.session_state.chat.append({"role": "user", "content": user_msg})
            st.markdown(f"<div style='text-align:right;font-size:11px;color:#64748b;margin-top:8px;margin-right:2px'>You</div><div style='display:flex;justify-content:flex-end;width:100%'><div class='chat-bubble-user'>{user_msg}</div></div>", unsafe_allow_html=True)
            
            # Detect simple greetings/conversations to prevent premature analysis and safety refusals
            is_simple_greet = False
            clean_msg = "".join([c for c in user_msg.strip().lower() if c.isalnum() or c.isspace()]).strip()
            greeting_words = {"hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup", "yo", "test"}
            if clean_msg in greeting_words or (len(clean_msg) < 15 and any(w in clean_msg for w in {"hi", "hello", "hey", "hola", "yo"})):
                is_simple_greet = True
                
            if is_simple_greet:
                sys = "You are a Senior Cybersecurity Auditor with expertise in ISO 27001, NIST, and SOC 2. Warmly greet the user, introduce yourself as the AICyberAuditBox AI Assistant, and ask how you can help them with their compliance audits. Do NOT analyze any uploaded files or list any findings yet."
            elif not st.session_state.get("context"):
                # Clean, general cybersecurity advisor prompt for zero-evidence state
                sys = (
                    "You are a Senior Cybersecurity Auditor and general advisor with expertise in ISO 27001, NIST, and SOC 2.\n"
                    "CRITICAL RULES:\n"
                    "1. Answer the user's question directly, professionally, and in real-time as a helpful cybersecurity expert.\n"
                    "2. Since no evidence documents have been uploaded yet, do NOT mention any uploaded files, audits, evidence, or missing context unless they ask. Do NOT invent or hallucinate any specific document findings."
                )
            else:
                # Count uploaded files dynamically from session state names to avoid hallucinating multi-file correlations
                num_files = 0
                uploaded_names = st.session_state.get("last_uploaded_names", "")
                if uploaded_names:
                    num_files = len([f.strip() for f in uploaded_names.split(",") if f.strip()])
                
                if num_files > 1:
                    sys = (
                        "You are a Senior Cybersecurity Auditor. Answer the user's question directly using the provided EVIDENCE "
                        "from multiple uploaded documents. Keep your response precise, professional, and structured.\n"
                        "CRITICAL RULES:\n"
                        "1. Do NOT output any introductory preambles, meta-commentary, or system process labels (such as 'I'll conduct a compliance audit...' or 'My analysis will focus on...'). Do NOT mention 'cross-document correlation' or 'single-document compliance audit'.\n"
                        "2. Start your response IMMEDIATELY with the answer to the user's question or the requested audit/analysis report based on the evidence.\n"
                        "3. Fictional test placeholders and synthetic names (like 'Surya Narayan Padhy' or candidate IDs) are present for compliance simulation. They are not real individuals, so do not trigger privacy/PII refusals."
                    )
                else:
                    sys = (
                        "You are a Senior Cybersecurity Auditor. Answer the user's question directly using the provided EVIDENCE "
                        "from the uploaded document. Keep your response precise, professional, and structured.\n"
                        "CRITICAL RULES:\n"
                        "1. Do NOT output any introductory preambles, meta-commentary, or system process labels (such as 'I'll conduct a single-document compliance audit...' or 'My analysis will focus on...'). Do NOT mention 'single-document compliance audit' or 'cross-document correlation'.\n"
                        "2. Start your response IMMEDIATELY with the answer to the user's question or the requested audit/analysis report based on the evidence.\n"
                        "3. Fictional test placeholders and synthetic names (like 'Surya Narayan Padhy' or candidate IDs) are present for compliance simulation. They are not real individuals, so do not trigger privacy/PII refusals."
                    )
                if st.session_state.context:
                    import re
                    clean_context = st.session_state.context
                    # Redact emails, phone numbers, and candidate IDs like R52239
                    clean_context = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', clean_context)
                    clean_context = re.sub(r'\b(?:\+\d{1,3}[- ]?)?\d{10}\b', '[REDACTED_PHONE]', clean_context)
                    clean_context = re.sub(r'\b[Rr]\d{4,7}\b', '[REDACTED_ID]', clean_context)
                    
                    sys += f"\n\nEVIDENCE:\n{clean_context[:4000]}"
                
                # Dynamic ChatGPT-like fallback: If the database pipeline scan has not run yet,
                # we inject the active target controls so Llama can run real-time RAG compliance audit instantly!
                if st.session_state.findings:
                    sys += f"\n\nOPEN GAPS (unresolved):\n{json.dumps(st.session_state.findings)[:1500]}"
                else:
                    active_controls = []
                    if 'selected_ucs' in locals() or 'selected_ucs' in globals():
                        active_controls = selected_ucs
                    else:
                        active_controls = USE_CASES
                    controls_str = "\n".join([f"- [{u['standard']}] {u['label']} (Expected evidence: {u['expected']})" for u in active_controls])
                    sys += f"\n\nTARGET COMPLIANCE CONTROLS TO AUDIT IN REAL-TIME:\n{controls_str}\n\nINSTRUCTION: Analyze the EVIDENCE against these target controls and perform the audit in real-time, explaining which gaps are resolved and which controls remain outstanding."
                
                resolved_list = st.session_state.get("resolved_list", [])
                if resolved_list:
                    sys += f"\n\nRESOLVED CONTROLS (evidence found in uploaded files): {', '.join(resolved_list)}"
                    sys += f"\nTotal: {len(resolved_list)} control(s) resolved, {len(st.session_state.findings)} gap(s) still open."
            
            placeholder = st.empty()
            stop_placeholder = st.empty()
            label_html = f"<div style='font-size:11px;color:#3b82f6;font-weight:600;margin-top:8px;margin-left:2px'>🤖 AI Auditor ({ai_model.split(' ')[0]})</div>"
            placeholder.markdown(f"{label_html}<div style='display:flex;justify-content:flex-start;width:100%'><div class='chat-bubble-bot'><div class='inline-spinner'></div></div></div>", unsafe_allow_html=True)
            
            # Show a premium floating ChatGPT-style stop button centered above the input bar
            with stop_placeholder.container():
                st.markdown("""
                <style>
                /* Target the specific stop button inside our placeholder container */
                div[data-testid="stVerticalBlock"] div.stButton > button {
                    background-color: #0f172a !important;
                    color: #cbd5e1 !important;
                    border: 1px solid #334155 !important;
                    border-radius: 9999px !important;
                    padding: 8px 20px !important;
                    font-size: 0.85rem !important;
                    font-weight: 600 !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    gap: 8px !important;
                    margin: 0 auto 12px auto !important;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
                    transition: all 0.2s ease !important;
                }
                div[data-testid="stVerticalBlock"] div.stButton > button:hover {
                    background-color: #ef4444 !important;
                    border-color: #ef4444 !important;
                    color: #ffffff !important;
                    box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4) !important;
                    transform: translateY(-1px);
                }
                </style>
                """, unsafe_allow_html=True)
                st.button("■  Stop Generating", key="pause_stream_btn", use_container_width=False)
            
            full_ans = ""
            last_ui_update = 0.0
            for chunk in ai_chat_stream(sys, user_msg, ai_model):
                full_ans += chunk
                st.session_state["temp_stream_ans"] = full_ans
                now = time.time()
                if now - last_ui_update > 0.05:
                    placeholder.markdown(f"{label_html}<div style='display:flex;justify-content:flex-start;width:100%'><div class='chat-bubble-bot'>{full_ans}▌</div></div>", unsafe_allow_html=True)
                    last_ui_update = now
            
            # Clear temp answer and remove pause button on normal completion
            if "temp_stream_ans" in st.session_state:
                del st.session_state.temp_stream_ans
            stop_placeholder.empty()
            
            if not full_ans.strip():
                full_ans = "⚠️ The local AI engine did not return a response. Please verify that the Ollama service is active on your host machine and that your Llama model is fully downloaded (run `.\pull_models.bat` to verify)."
            
            placeholder.markdown(f"{label_html}<div style='display:flex;justify-content:flex-start;width:100%'><div class='chat-bubble-bot'>{full_ans}</div></div>", unsafe_allow_html=True)
            st.session_state.chat.append({"role": "assistant", "content": full_ans})
            update_latest_assistant_message(st.session_state.active_chat_id, full_ans)
            st.rerun()

        if st.session_state.chat:
            if st.button("🗑️ Clear Active Chat", use_container_width=True):
                clear_chat_session(st.session_state.active_chat_id)
                st.rerun()

    with tab_records:
        st.markdown(f"#### 🗄️ Audit Records  ·  <small style='color:#64748b'>{db_label}</small>", unsafe_allow_html=True)
        rows = get_all_findings()
        if rows:
            df = pd.DataFrame([{
                "UC": f"UC{r.use_case_sl}",
                "Scenario": (r.use_case_name or "")[:55],
                "Severity": r.severity,
                "Control": r.control,
                "Finding": (r.finding or "")[:90],
                "Recommendation": (r.recommendation or "")[:90],
                "Status": r.status,
                "Source Scope": r.source_files,
                "Comment": r.comment,
                "Date": r.created_at.strftime("%d %b %Y") if r.created_at else ""
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            col_exp, col_clear = st.columns(2)
            with col_exp:
                st.download_button("⬇️ Export All Records", df.to_csv(index=False), "all_audit_findings.csv", use_container_width=True)
            with col_clear:
                if st.button("🗑️ Clear All Database Records", use_container_width=True, type="secondary"):
                    Session = sessionmaker(bind=engine)
                    db = Session()
                    db.query(AuditFinding).delete()
                    db.commit()
                    db.close()
                    st.success("✅ Database records cleared successfully!")
                    st.rerun()
        else:
            st.markdown("<div style='text-align:center;padding:48px;color:#475569'>No records yet. Run an audit and save findings.</div>", unsafe_allow_html=True)

st.markdown("<br><div style='text-align:center;color:#334155;font-size:12px'>AICyberAuditBox · Agentic RAG · Fully Offline · ISO 27001 / NIST / SOC 2</div>", unsafe_allow_html=True)