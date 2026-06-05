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

def init_db():
    try:
        eng = create_engine("postgresql://postgres:ShakthiDB%402026@localhost:15234/postgres", connect_args={"connect_timeout":3}, pool_pre_ping=True)
        with eng.connect() as c: c.execute(text("SELECT 1"))
        try:
            with eng.connect() as c: c.execute(text("SELECT evidence_snippet FROM audit_findings LIMIT 1"))
        except:
            from sqlalchemy import MetaData
            meta = MetaData()
            meta.reflect(bind=eng)
            if "audit_findings" in meta.tables:
                meta.tables["audit_findings"].drop(bind=eng)
        Base.metadata.create_all(bind=eng)
        return eng, "ShaktiDB"
    except Exception as e:
        eng = create_engine("sqlite:///shakthidb_local.db", pool_pre_ping=True)
        try:
            with eng.connect() as c: c.execute(text("SELECT evidence_snippet FROM audit_findings LIMIT 1"))
        except:
            from sqlalchemy import MetaData
            meta = MetaData()
            meta.reflect(bind=eng)
            if "audit_findings" in meta.tables:
                meta.tables["audit_findings"].drop(bind=eng)
        Base.metadata.create_all(bind=eng)
        return eng, "Local DB"

# Initialize single global connection to export
engine, db_label = init_db()
SessionLocal = sessionmaker(bind=engine)
