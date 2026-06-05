import streamlit as st
import hashlib
from database import SessionLocal, User, engine

def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def seed_default_admin():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", password=_hash_pw("admin123"), role="admin"))
        db.commit()
    db.close()

def authenticate_user(username, password):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username, User.password == _hash_pw(password)).first()
    db.close()
    if user:
        return {"username": user.username, "role": user.role}
    return None

def register_user(username, password, role):
    db = SessionLocal()
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        db.close()
        return False, "Username already exists."
    db.add(User(username=username, password=_hash_pw(password), role=role))
    db.commit()
    db.close()
    return True, "Account created successfully!"

def render_login_gate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.username = None

    if not st.session_state.authenticated:
        # We ensure default admin is there
        seed_default_admin()
        
        # Inject styling specific for auth
        st.markdown("""
        <style>
        .login-card-container {
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 24px;
            padding: 40px 32px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            margin-top: 6vh;
        }
        [data-testid="stForm"] {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
        }
        /* Sleek Segmented Control Background for Radio Buttons */
        div[data-testid="stRadio"] > div {
            display: flex;
            gap: 12px;
            background: rgba(15, 23, 42, 0.5);
            padding: 8px 16px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 8px;
        }
        div[data-baseweb="input"] {
            background-color: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            border-radius: 12px !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        }
        div.stButton > button {
            border-radius: 12px !important;
            padding: 24px !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3) !important;
            transition: all 0.2s ease !important;
            margin-top: 12px;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(59, 130, 246, 0.5) !important;
        }
        .login-logo { text-align: center; margin-bottom: 24px; }
        .login-logo-icon { font-size: 3.5rem; filter: drop-shadow(0 4px 6px rgba(59,130,246,0.4)); }
        .login-logo-title { font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin-top: 8px; letter-spacing: -0.5px; }
        .login-logo-sub { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; font-weight: 500; }
        .role-badge {
            display: inline-block; padding: 6px 16px; border-radius: 20px;
            font-size: 0.75rem; font-weight: 700; margin-right: 6px;
            letter-spacing: 0.5px; text-transform: uppercase;
        }
        .role-admin { background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }
        .role-auditee { background: rgba(59,130,246,0.1); color: #93c5fd; border: 1px solid rgba(59,130,246,0.3); }
        .role-auditor { background: rgba(34,197,94,0.1); color: #86efac; border: 1px solid rgba(34,197,94,0.3); }
        </style>
        """, unsafe_allow_html=True)

        # Center the main login card
        _, col_main, _ = st.columns([1, 1.2, 1])

        with col_main:
            st.markdown('<div class="login-card-container">', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="login-logo">
                <div class="login-logo-icon">🛡️</div>
                <div class="login-logo-title">AICyberAuditBox</div>
                <div class="login-logo-sub">Agentic RAG · Cyber Security Audit Intelligence</div>
            </div>
            """, unsafe_allow_html=True)

            # Using inner columns to precisely center the radio segment so it doesn't stretch
            c1, c2, c3 = st.columns([1, 5, 1])
            with c2:
                login_role = st.radio(
                    "Select your role",
                    ["🔐 Admin", "📋 Auditee", "👁️ Auditor"],
                    horizontal=True,
                    label_visibility="collapsed"
                )

            role_map = {"🔐 Admin": "admin", "📋 Auditee": "auditee", "👁️ Auditor": "auditor"}
            selected_role = role_map[login_role]

            role_descriptions = {
                "admin": ("System Administrator", "Full access to settings, analyses, and records", "role-admin"),
                "auditee": ("Evidence Provider", "Upload documents and run guided assessments", "role-auditee"),
                "auditor": ("Compliance Auditor", "View-only access to finalized reports and logs", "role-auditor")
            }
            desc_title, desc_text, desc_class = role_descriptions[selected_role]
            st.markdown(f"""
            <div style='text-align:center; margin: 16px 0 24px 0; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.05);'>
                <span class='role-badge {desc_class}'>{desc_title}</span>
                <div style='color:#64748b; font-size:0.8rem; margin-top:12px; font-weight:500;'>{desc_text}</div>
            </div>
            """, unsafe_allow_html=True)

            if selected_role != "admin":
                _, col_action = st.columns([1, 1.5])
                with col_action:
                    auth_action = st.radio("Action", ["Login", "Create Account"], horizontal=True, label_visibility="collapsed")
                st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)
            else:
                auth_action = "Login"

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button(
                    "🔓 Secure Sign In" if auth_action == "Login" else "📝 Create Secure Account",
                    use_container_width=True, type="primary"
                )

            if submitted:
                if not username.strip() or not password.strip():
                    st.error("Please enter both username and password.")
                elif auth_action == "Login":
                    user = authenticate_user(username.strip(), password)
                    if user and user["role"] == selected_role:
                        st.session_state.authenticated = True
                        st.session_state.user_role = user["role"]
                        st.session_state.username = user["username"]
                        st.rerun()
                    elif user:
                        st.error(f"This account is registered as **{user['role'].capitalize()}**. Please switch tabs.")
                    else:
                        st.error("Invalid username or password.")
                else:
                    if len(password) < 4:
                        st.error("Password must be at least 4 characters.")
                    else:
                        ok, msg = register_user(username.strip(), password, selected_role)
                        if ok:
                            st.success(f"✅ {msg} You can now sign in.")
                        else:
                            st.error(msg)

            st.markdown("<div style='text-align:center;color:#475569;font-size:11px;margin-top:32px;letter-spacing:0.5px;'>Powered by AICyberAuditBox Engine · SOC 2 / ISO 27001 Ready</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True) # close card container
        st.stop()
