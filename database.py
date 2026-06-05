import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class AuditFinding(Base):
    __tablename__ = "audit_findings"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    use_case_sl      = Column(Integer)
    use_case_name    = Column(String(300))
    control_id       = Column(String(100))
    relevance_score  = Column(Integer)
    evidence_found   = Column(String(50))
    evidence_snippet = Column(Text)
    severity         = Column(String(50))
    control          = Column(String(200))
    finding          = Column(Text)
    recommendation   = Column(Text)
    reasoning        = Column(Text)
    status           = Column(String(50), default="Open")
    comment          = Column(Text, default="")
    source_files     = Column(Text, default="All uploaded documents")
    created_at       = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    session_id     = Column(String(100))
    session_title  = Column(String(300))
    role           = Column(String(50))
    content        = Column(Text)
    created_at     = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String(100), unique=True, nullable=False)
    password   = Column(String(200), nullable=False)
    role       = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditCheckpoint(Base):
    """Stores mid-audit progress so an interrupted run can be resumed after a crash or restart."""
    __tablename__ = "audit_checkpoints"
    id                   = Column(Integer, primary_key=True, autoincrement=True)
    session_id           = Column(String(100), index=True)   # maps to active_chat_id
    bg_key               = Column(String(100))
    ai_model             = Column(String(200))
    selected_sls_json    = Column(Text)   # JSON list of int SL numbers
    file_names_json      = Column(Text)   # JSON list of file name strings
    context_text         = Column(Text)   # full combined evidence context
    total_controls       = Column(Integer, default=0)
    completed_batches    = Column(Integer, default=0)
    batch_size           = Column(Integer, default=10)
    partial_results_json = Column(Text, default="[]")   # JSON array of result dicts so far
    status               = Column(String(50), default="in_progress")  # in_progress / completed / failed
    created_at           = Column(DateTime, default=datetime.utcnow)
    updated_at           = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    def _ensure_schema(eng):
        """Probe for required columns; drop+recreate only audit_findings if schema is stale."""
        try:
            with eng.connect() as c:
                c.execute(text("SELECT evidence_snippet FROM audit_findings LIMIT 1"))
        except Exception:
            from sqlalchemy import MetaData
            meta = MetaData()
            meta.reflect(bind=eng)
            if "audit_findings" in meta.tables:
                meta.tables["audit_findings"].drop(bind=eng)
        # Always create all tables (including new ones like audit_checkpoints)
        Base.metadata.create_all(bind=eng)

    try:
        eng = create_engine(
            "postgresql://postgres:ShakthiDB%402026@localhost:15234/postgres",
            connect_args={"connect_timeout": 3},
            pool_pre_ping=True
        )
        with eng.connect() as c:
            c.execute(text("SELECT 1"))
        _ensure_schema(eng)
        return eng, "ShaktiDB"
    except Exception:
        eng = create_engine("sqlite:///shakthidb_local.db", pool_pre_ping=True)
        _ensure_schema(eng)
        return eng, "Local DB"

# Initialize single global connection to export
engine, db_label = init_db()
SessionLocal = sessionmaker(bind=engine)
