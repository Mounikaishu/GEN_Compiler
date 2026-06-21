"""
AI App Compiler — Streamlit Demo UI
The main entry point. Shows:
1. LangGraph graph visualization (Mermaid diagram)
2. Prompt input
3. Live pipeline execution with stage progress
4. Tabbed JSON schema viewers
5. Validation report with error details
6. Generated code file browser
7. Evaluation metrics dashboard
"""
import os
import sys
import json
import time
import streamlit as st
from dotenv import load_dotenv

# ── Add project root to path ─────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI App Compiler",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #7C3AED 0%, #2563EB 50%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 700;
    text-align: center;
    padding: 1rem 0 0.5rem 0;
    line-height: 1.2;
}

.subtitle {
    text-align: center;
    color: #94A3B8;
    font-size: 1.05rem;
    margin-bottom: 2rem;
    font-weight: 400;
}

.stage-card {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%);
    border: 1px solid #2D3748;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin: 0.3rem 0;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    transition: all 0.3s ease;
}

.stage-success { border-color: #059669 !important; }
.stage-running { border-color: #7C3AED !important; animation: pulse 1.5s infinite; }
.stage-failed  { border-color: #DC2626 !important; }
.stage-pending { border-color: #374151 !important; opacity: 0.6; }

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.4); }
    50%       { box-shadow: 0 0 0 8px rgba(124, 58, 237, 0); }
}

.metric-card {
    background: linear-gradient(135deg, #1A1A2E, #0F172A);
    border: 1px solid #2D3748;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #7C3AED;
}

.metric-label {
    color: #94A3B8;
    font-size: 0.85rem;
    margin-top: 0.3rem;
}

.error-badge {
    background: rgba(220, 38, 38, 0.15);
    border: 1px solid #DC2626;
    color: #FCA5A5;
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    margin: 0.3rem 0;
    font-size: 0.85rem;
}

.repair-badge {
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid #F59E0B;
    color: #FCD34D;
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    margin: 0.3rem 0;
    font-size: 0.85rem;
}

.success-badge {
    background: rgba(5, 150, 105, 0.15);
    border: 1px solid #059669;
    color: #6EE7B7;
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    font-size: 0.85rem;
}

.code-file-header {
    background: #1E293B;
    border: 1px solid #334155;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 0.5rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    color: #94A3B8;
    font-size: 0.85rem;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 500;
}

.stButton > button {
    background: linear-gradient(135deg, #7C3AED, #2563EB);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    width: 100%;
    transition: all 0.3s;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
}

.compiler-tag {
    display: inline-block;
    background: rgba(124, 58, 237, 0.2);
    border: 1px solid #7C3AED;
    color: #C4B5FD;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "running" not in st.session_state:
    st.session_state.running = False

# ── Sidebar: LangGraph Graph + Config ────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ AI App Compiler")
    st.markdown("*Natural Language → Working Application*")
    st.divider()

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("🔑 Gemini API Key", type="password",
                                 help="Get from console.cloud.google.com")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            import google.generativeai as genai
            genai.configure(api_key=api_key)
    else:
        st.success("✅ API Key loaded")

    st.divider()

    # LangGraph architecture diagram
    st.markdown("### 🔀 Compiler Graph (LangGraph)")
    st.markdown("""
```
START
  │
  ▼
[Intent Extractor]        Stage 1
  │
  ▼
[Architecture Planner]    Stage 2
  │
  ├──────────────┐
  ▼              ▼
[UI Gen]     [API Gen]    Stage 3
[DB Gen]     [Auth Gen]
  │
  ▼
[Cross-Layer Validator]   Stage 4
  │
  ├─errors─▶ [Repair Engine] ─┐
  │                            │
  │◀───────────────────────────┘
  ▼
[Runtime Generator]       Stage 6
  │
  ▼
END (Source Files)
```
""")

    st.divider()
    st.markdown("### ⚙️ Settings")
    st.caption(f"🤖 Model: `gemini-2.0-flash`")
    st.caption("🌡️ Temperature: `0.0` (deterministic)")
    st.caption("📋 JSON Mode: `enabled`")
    st.caption("🔄 Max repair rounds: `2`")

    st.divider()
    if st.button("📊 Run Evaluation Suite"):
        st.session_state.run_eval = True

# ── Main content ──────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🏗️ AI App Compiler</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Natural Language → Validated Schema → Executable Application</div>',
    unsafe_allow_html=True
)

# Compiler stage tags
st.markdown("""
<div style="text-align:center; margin-bottom: 1.5rem;">
<span class="compiler-tag">📝 Intent IR</span>
<span class="compiler-tag">🏛️ Architecture</span>
<span class="compiler-tag">🎨 UI Schema</span>
<span class="compiler-tag">⚡ API Schema</span>
<span class="compiler-tag">🗄️ DB Schema</span>
<span class="compiler-tag">🔐 Auth Schema</span>
<span class="compiler-tag">🔎 Validator</span>
<span class="compiler-tag">🔧 Repair</span>
<span class="compiler-tag">🚀 Runtime</span>
</div>
""", unsafe_allow_html=True)

# ── Example prompts ───────────────────────────────────────────────────────────
EXAMPLES = [
    "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
    "Learning Management System with courses, students, instructors, quiz engine, and progress tracking. Teachers can manage content.",
    "Hospital management system with patients, doctors, appointments, billing, and pharmacy. Admins manage staff.",
    "Build a job portal with candidates, employers, job listings, applications, and resume uploads. Premium employers get featured listings.",
    "Build something", # edge case
]

col1, col2 = st.columns([3, 1])
with col1:
    prompt = st.text_area(
        "📝 Describe your application",
        height=120,
        placeholder="e.g. Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments...",
        help="Be as detailed or vague as you like — the system handles both!",
    )
with col2:
    st.markdown("**💡 Try an example:**")
    for i, ex in enumerate(EXAMPLES):
        if st.button(f"Ex {i+1}", key=f"ex_{i}", help=ex[:60] + "..."):
            st.session_state.example_prompt = ex
            st.rerun()

# Use example if selected
if "example_prompt" in st.session_state:
    prompt = st.session_state.example_prompt
    del st.session_state.example_prompt

# ── Run button ────────────────────────────────────────────────────────────────
run_col, _ = st.columns([1, 2])
with run_col:
    run_clicked = st.button("🚀 Compile Application", disabled=not prompt or not api_key)

# ── Pipeline execution ────────────────────────────────────────────────────────
if run_clicked and prompt:
    st.divider()
    st.markdown("### ⚡ Pipeline Execution")

    # Stage progress display
    stage_names = [
        ("intent_extractor",      "📝 Intent Extraction",        "Stage 1: NL → Structured IR"),
        ("architecture_planner",  "🏛️ Architecture Planning",    "Stage 2: IR → Pages, Entities, Flows"),
        ("ui_generator",          "🎨 UI Generation",            "Stage 3a: UI Schema"),
        ("api_generator",         "⚡ API Generation",            "Stage 3b: API Routes"),
        ("db_generator",          "🗄️ DB Generation",            "Stage 3c: Tables & Columns"),
        ("auth_generator",        "🔐 Auth Generation",          "Stage 3d: Roles & Permissions"),
        ("cross_layer_validator", "🔎 Cross-Layer Validation",   "Stage 4: Consistency Checks"),
        ("repair_engine",         "🔧 Repair Engine",            "Stage 5: Targeted Repair"),
        ("runtime_generator",     "🚀 Runtime Generation",       "Stage 6: Code Files"),
    ]

    # Build stage placeholders
    stage_placeholders = {}
    progress_col1, progress_col2 = st.columns(2)
    with progress_col1:
        for key, name, desc in stage_names[:5]:
            ph = st.empty()
            ph.markdown(f"""
            <div class="stage-card stage-pending">
                <span>⏳</span>
                <div>
                    <div style="font-weight:600; color:#94A3B8;">{name}</div>
                    <div style="font-size:0.75rem; color:#475569;">{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)
            stage_placeholders[key] = ph

    with progress_col2:
        for key, name, desc in stage_names[5:]:
            ph = st.empty()
            ph.markdown(f"""
            <div class="stage-card stage-pending">
                <span>⏳</span>
                <div>
                    <div style="font-weight:600; color:#94A3B8;">{name}</div>
                    <div style="font-size:0.75rem; color:#475569;">{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)
            stage_placeholders[key] = ph

    # Overall progress bar
    prog_bar = st.progress(0, text="Initializing compiler...")
    status_text = st.empty()

    def update_stage(key, name, desc, status, latency=None):
        """Update a stage card's visual status."""
        icon = {"success": "✅", "running": "🔄", "failed": "❌", "repaired": "🔧"}.get(status, "⏳")
        css_class = f"stage-{status}"
        timing = f" <span style='color:#6EE7B7; font-size:0.75rem;'>({latency:.1f}ms)</span>" if latency else ""
        if key in stage_placeholders:
            stage_placeholders[key].markdown(f"""
            <div class="stage-card {css_class}">
                <span style="font-size:1.2rem;">{icon}</span>
                <div>
                    <div style="font-weight:600; color:#E2E8F0;">{name}{timing}</div>
                    <div style="font-size:0.75rem; color:#64748B;">{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    # Mark Stage 1 as running
    update_stage("intent_extractor", "📝 Intent Extraction", "Stage 1: NL → Structured IR", "running")
    prog_bar.progress(5, text="Stage 1: Extracting intent from prompt...")

    try:
        # Import and run pipeline
        from graph.pipeline_graph import run_pipeline

        # ── Actually run the LangGraph pipeline ──
        start_total = time.time()
        result = run_pipeline(prompt)
        total_time = (time.time() - start_total) * 1000

        st.session_state.result = result

        # ── Update stage cards from logs ──────────────────────────────────────
        stage_key_map = {
            "Intent Extraction":       "intent_extractor",
            "Architecture Planning":   "architecture_planner",
            "UI Generation":           "ui_generator",
            "API Generation":          "api_generator",
            "DB Generation":           "db_generator",
            "Auth Generation":         "auth_generator",
            "Cross-Layer Validation":  "cross_layer_validator",
            "Repair Round 1":          "repair_engine",
            "Repair Round 2":          "repair_engine",
            "Runtime Generation":      "runtime_generator",
        }
        stage_info_map = {k: (n, d) for k, n, d in stage_names}

        for i, log in enumerate(result.get("stage_logs", [])):
            stage_name = log["stage"]
            node_key = stage_key_map.get(stage_name, "")
            status = "success" if log["status"] == "success" else "failed"
            latency = log.get("latency_ms", 0)
            if node_key and node_key in stage_info_map:
                n, d = stage_info_map[node_key]
                update_stage(node_key, n, d, status, latency)
            prog = min(10 + (i + 1) * 10, 95)
            prog_bar.progress(prog, text=f"Completed: {stage_name}")

        # Mark validation + repair visually
        errors = result.get("validation_errors", [])
        repairs = result.get("repair_actions", [])
        if repairs:
            n, d = stage_info_map.get("repair_engine", ("🔧 Repair Engine", ""))
            update_stage("repair_engine", "🔧 Repair Engine", f"{len(repairs)} repair(s) applied", "repaired", 0)

        prog_bar.progress(100, text=f"✅ Pipeline complete in {total_time/1000:.1f}s")

    except Exception as e:
        prog_bar.progress(100, text="❌ Pipeline failed")
        st.error(f"Pipeline error: {e}")
        st.exception(e)
        st.session_state.result = None

# ── Results display ───────────────────────────────────────────────────────────
if st.session_state.result:
    result = st.session_state.result
    st.divider()

    # ── Summary metrics ───────────────────────────────────────────────────────
    st.markdown("### 📊 Run Summary")
    errors = result.get("validation_errors", [])
    repairs = result.get("repair_actions", [])
    logs = result.get("stage_logs", [])
    files = result.get("generated_files", {})
    total_tokens = sum(l.get("token_usage", 0) for l in logs)
    total_latency = sum(l.get("latency_ms", 0) for l in logs)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{'✅' if result.get('success') else '❌'}</div>
            <div class="metric-label">Pipeline Status</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{len(errors)}</div>
            <div class="metric-label">Validation Errors</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{len(repairs)}</div>
            <div class="metric-label">Repairs Applied</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_latency/1000:.1f}s</div>
            <div class="metric-label">Total Latency</div>
        </div>""", unsafe_allow_html=True)
    with m5:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{len(files)}</div>
            <div class="metric-label">Files Generated</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main tabs ─────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📝 Intent IR",
        "🏛️ Architecture",
        "🎨 UI Schema",
        "⚡ API Schema",
        "🗄️ DB Schema",
        "🔐 Auth Schema",
        "🔎 Validation",
        "🚀 Generated Code",
        "📋 Exec Logs",
    ])

    def show_json(data, label=""):
        if data:
            st.json(data, expanded=False)
        else:
            st.info(f"No {label} data generated yet.")

    with tabs[0]:
        st.markdown("#### Stage 1 Output: Structured Intent (Intermediate Representation)")
        intent = result.get("intent", {})
        if intent:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**App:** `{intent.get('app_name', 'N/A')}`")
                st.markdown(f"**Type:** `{intent.get('app_type', 'N/A')}`")
                st.markdown(f"**Description:** {intent.get('description', '')}")
                features = intent.get("features", [])
                st.markdown(f"**Features ({len(features)}):** {', '.join(features)}")
            with col_b:
                st.markdown(f"**Roles:** `{'`, `'.join(intent.get('roles', []))}`")
                st.markdown(f"**Entities:** `{'`, `'.join(intent.get('entities', []))}`")
                flags = []
                if intent.get("has_auth"): flags.append("🔐 Auth")
                if intent.get("has_premium"): flags.append("⭐ Premium")
                if intent.get("has_payments"): flags.append("💳 Payments")
                if intent.get("has_analytics"): flags.append("📊 Analytics")
                st.markdown(f"**Flags:** {' '.join(flags) or 'None'}")
            if intent.get("assumptions"):
                st.warning("**Assumptions made:** " + " | ".join(intent["assumptions"]))
            if intent.get("clarifications_needed"):
                st.info("**Clarifications needed:** " + " | ".join(intent["clarifications_needed"]))
        st.markdown("---")
        st.markdown("**Raw JSON:**")
        show_json(intent, "intent")

    with tabs[1]:
        st.markdown("#### Stage 2 Output: Application Architecture")
        arch = result.get("architecture", {})
        if arch:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Pages ({len(arch.get('pages', []))}):** {', '.join(arch.get('pages', []))}")
                st.markdown(f"**Entities ({len(arch.get('entities', []))}):** {', '.join(arch.get('entities', []))}")
            with col_b:
                rels = arch.get("data_relationships", [])
                st.markdown(f"**Relationships ({len(rels)}):**")
                for r in rels[:5]:
                    st.markdown(f"  - `{r['from_entity']}` → `{r['to_entity']}` ({r['relation_type']})")
            flows = arch.get("flows", [])
            if flows:
                st.markdown(f"**User Flows ({len(flows)}):**")
                for fl in flows:
                    st.markdown(f"  - **{fl['name']}** ({', '.join(fl.get('actors', []))})")
        st.markdown("---")
        show_json(arch, "architecture")

    with tabs[2]:
        st.markdown("#### Stage 3a Output: UI Schema")
        ui = result.get("ui_schema", {})
        if ui:
            pages = ui.get("pages", [])
            st.markdown(f"**{len(pages)} pages** | Global: `{', '.join(ui.get('global_components', []))}`")
            for page in pages:
                with st.expander(f"📄 {page['name']} — `{page.get('route', '/')}`"):
                    badges = []
                    if page.get("is_protected"): badges.append("🔐 Protected")
                    if page.get("is_premium"): badges.append("⭐ Premium")
                    if page.get("roles_allowed"): badges.append(f"👥 {', '.join(page['roles_allowed'])}")
                    st.markdown(" ".join(badges) or "Public")
                    for comp in page.get("components", []):
                        fields = [f['name'] for f in comp.get('fields', [])]
                        st.markdown(f"  - **{comp['name']}** ({comp.get('component_type', 'component')}): `{', '.join(fields) or 'no fields'}`")
        st.markdown("---")
        show_json(ui, "UI schema")

    with tabs[3]:
        st.markdown("#### Stage 3b Output: API Schema")
        api = result.get("api_schema", {})
        if api:
            all_routes = api.get("routes", []) + api.get("auth_routes", [])
            st.markdown(f"**{len(all_routes)} routes** | Base: `{api.get('base_path', '/api')}`")
            for route in all_routes:
                method = route.get("method", "GET")
                color = {"GET": "🟢", "POST": "🔵", "PUT": "🟡", "DELETE": "🔴", "PATCH": "🟠"}.get(method, "⚪")
                resp_fields = [f['name'] for f in route.get('response_fields', [])]
                roles = route.get("roles_allowed", [])
                with st.expander(f"{color} `{method}` {route['path']}"):
                    st.markdown(f"**Summary:** {route.get('summary', '')}")
                    st.markdown(f"**DB Table:** `{route.get('db_table', 'N/A')}`")
                    st.markdown(f"**Auth:** {'Required' if route.get('auth_required') else 'Public'}")
                    st.markdown(f"**Roles:** `{', '.join(roles) or 'all'}`")
                    st.markdown(f"**Response fields:** `{', '.join(resp_fields) or 'none'}`")
        st.markdown("---")
        show_json(api, "API schema")

    with tabs[4]:
        st.markdown("#### Stage 3c Output: DB Schema")
        db = result.get("db_schema", {})
        if db:
            tables = db.get("tables", [])
            st.markdown(f"**{len(tables)} tables** | DB: `{db.get('db_type', 'SQLite')}`")
            for table in tables:
                cols = table.get("columns", [])
                with st.expander(f"🗄️ `{table['name']}` ({len(cols)} columns)"):
                    st.markdown(f"*{table.get('description', '')}*")
                    col_data = [[c['name'], c['col_type'],
                                 '✅' if c.get('primary_key') else '',
                                 '🔑' if c.get('foreign_key') else '',
                                 c.get('foreign_key', '')] for c in cols]
                    import pandas as pd
                    df = pd.DataFrame(col_data, columns=["Column", "Type", "PK", "FK", "References"])
                    st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("---")
        show_json(db, "DB schema")

    with tabs[5]:
        st.markdown("#### Stage 3d Output: Auth Schema")
        auth = result.get("auth_schema", {})
        if auth:
            roles = auth.get("roles", [])
            st.markdown(f"**Roles ({len(roles)}):** `{'`, `'.join(roles)}`")
            st.markdown(f"**Method:** `{auth.get('auth_method', 'JWT')}`")
            jwt = auth.get("jwt_config", {})
            st.markdown(f"**Token expiry:** `{jwt.get('access_token_expire_minutes', 30)}min`")
            for rp in auth.get("role_permissions", []):
                with st.expander(f"👤 {rp['role']}" + (" 👑 Admin" if rp.get('is_admin') else "") + (" ⭐ Premium" if rp.get('can_access_premium') else "")):
                    for perm in rp.get("permissions", []):
                        st.markdown(f"  - `{perm['resource']}`: {', '.join(perm.get('actions', []))}")
        st.markdown("---")
        show_json(auth, "Auth schema")

    with tabs[6]:
        st.markdown("#### Stage 4: Cross-Layer Validation Report")
        errors = result.get("validation_errors", [])
        repairs = result.get("repair_actions", [])

        if not errors:
            st.markdown('<div class="success-badge">✅ All cross-layer checks passed — no inconsistencies found</div>', unsafe_allow_html=True)
        else:
            real_errors = [e for e in errors if e.get("severity") == "error"]
            warnings = [e for e in errors if e.get("severity") == "warning"]
            st.markdown(f"**{len(real_errors)} errors** | **{len(warnings)} warnings**")
            for err in real_errors:
                st.markdown(f"""<div class="error-badge">
                    ❌ <b>[{err['layer']}]</b> {err['location']} → <code>{err['field']}</code><br>
                    {err['message'][:200]}
                </div>""", unsafe_allow_html=True)
            for warn in warnings:
                st.markdown(f"""<div class="repair-badge">
                    ⚠️ <b>[{warn['layer']}]</b> {warn['location']}<br>
                    {warn['message'][:200]}
                </div>""", unsafe_allow_html=True)

        if repairs:
            st.markdown("---")
            st.markdown(f"#### 🔧 Repair Engine Log ({len(repairs)} repair(s))")
            for r in repairs:
                icon = "✅" if r.get("success") else "❌"
                st.markdown(f"""<div class="repair-badge">
                    {icon} <b>Layer: {r['layer']}</b> (Attempt {r['attempt']})<br>
                    <b>Fixed:</b> {r['error_fixed'][:150]}<br>
                    <b>Action:</b> {r['action_taken'][:150]}
                </div>""", unsafe_allow_html=True)

    with tabs[7]:
        st.markdown("#### Stage 6: Generated Source Files")
        files = result.get("generated_files", {})
        if not files:
            st.info("No files generated yet.")
        else:
            st.markdown(f"**{len(files)} files generated** — ready to run")

            # File type filter
            all_files = list(files.keys())
            react_files = [f for f in all_files if f.startswith("frontend")]
            backend_files = [f for f in all_files if f.startswith("backend")]
            other_files = [f for f in all_files if not f.startswith("frontend") and not f.startswith("backend")]

            file_col, code_col = st.columns([1, 2])
            with file_col:
                st.markdown("**📁 File Tree**")
                if react_files:
                    st.markdown("📂 `frontend/`")
                    for f in react_files:
                        display = f.replace("frontend/", "  └─ ")
                        if st.button(display, key=f"file_{f}"):
                            st.session_state.selected_file = f
                if backend_files:
                    st.markdown("📂 `backend/`")
                    for f in backend_files:
                        display = f.replace("backend/", "  └─ ")
                        if st.button(display, key=f"file_{f}"):
                            st.session_state.selected_file = f
                for f in other_files:
                    if st.button(f"📄 {f}", key=f"file_{f}"):
                        st.session_state.selected_file = f

            with code_col:
                selected = st.session_state.get("selected_file", all_files[0] if all_files else None)
                if selected and selected in files:
                    ext = selected.split(".")[-1]
                    lang = {"tsx": "tsx", "py": "python", "md": "markdown"}.get(ext, "text")
                    st.markdown(f'<div class="code-file-header">📄 {selected}</div>', unsafe_allow_html=True)
                    st.code(files[selected], language=lang)

            # Download all as JSON
            st.download_button(
                "⬇️ Download All Generated Files (JSON)",
                data=json.dumps(files, indent=2),
                file_name="generated_app.json",
                mime="application/json"
            )

    with tabs[8]:
        st.markdown("#### Execution Log — Per-Stage Timing & Token Usage")
        logs = result.get("stage_logs", [])
        if logs:
            import pandas as pd
            df_data = []
            for log in logs:
                status_icon = "✅" if "success" in log.get("status", "") else "❌" if "failed" in log.get("status", "") else "🔧"
                df_data.append({
                    "Stage": log["stage"],
                    "Status": f"{status_icon} {log['status']}",
                    "Latency (ms)": f"{log.get('latency_ms', 0):.0f}",
                    "Tokens": log.get("token_usage", 0),
                    "Error": log.get("error", "") or "—",
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Latency breakdown chart
            import plotly.express as px
            latencies = [l.get("latency_ms", 0) for l in logs]
            stages = [l["stage"] for l in logs]
            fig = px.bar(
                x=stages, y=latencies,
                title="Stage Latency Breakdown (ms)",
                color=latencies,
                color_continuous_scale="Viridis",
                labels={"x": "Stage", "y": "Latency (ms)"}
            )
            fig.update_layout(
                plot_bgcolor="#0F0F1A",
                paper_bgcolor="#0F0F1A",
                font_color="#E2E8F0",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

# ── Evaluation suite ──────────────────────────────────────────────────────────
if st.session_state.get("run_eval"):
    st.divider()
    st.markdown("### 📊 Evaluation Suite — 20 Prompts")
    st.info("Running evaluation in a separate process. Use `python evaluation/metrics.py` in terminal for full results.")
    st.session_state.run_eval = False

    from evaluation.metrics import EVAL_PROMPTS
    st.dataframe(
        [{"#": i+1, "Prompt": p["prompt"][:80]+"...", "Type": p["type"]} for i, p in enumerate(EVAL_PROMPTS)],
        use_container_width=True
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#475569; font-size:0.8rem;">
    Built with LangGraph + Gemini 2.0 Flash + Pydantic + Streamlit
    | <b>NL → IR → Schema → Validation → Repair → Runtime</b>
    | Compiler-style AI pipeline
</div>
""", unsafe_allow_html=True)
