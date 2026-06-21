# AI App Compiler

> **Natural Language → Intermediate Representation → Validated Schema → Executable Application**

A compiler-style AI pipeline that converts plain-text product descriptions into validated, executable app configurations — powered by **LangGraph + Gemini 2.0 Flash + Pydantic**.

🔗 **Live Demo**: [Streamlit Community Cloud](https://your-app.streamlit.app)
📦 **GitHub**: [compiler-ai](https://github.com/yourusername/compiler-ai)

---

## Architecture

This system is designed exactly like a compiler: each stage is a discrete transformation with a strict input/output contract.

```
USER PROMPT
    │
    ▼
┌──────────────────┐
│ Intent Extractor │  Stage 1: NL → Structured IR (IntentSchema)
└──────────────────┘
    │
    ▼
┌─────────────────────┐
│ Architecture Planner│  Stage 2: IR → Pages, Entities, Flows
└─────────────────────┘
    │
    ├────────────────────────────────────────┐
    ▼        ▼           ▼           ▼       │
[UI Gen] [API Gen]   [DB Gen]   [Auth Gen]  Stage 3
    │        │           │           │
    └────────┴───────────┴───────────┘
                    │
                    ▼
    ┌──────────────────────────┐
    │  Cross-Layer Validator   │  Stage 4: 6 consistency checks
    └──────────────────────────┘
                    │
          ┌─ errors?─┐
         Yes         No
          │           │
          ▼           ▼
    [Repair Engine] [Runtime Generator]  Stage 5/6
          │
    (re-validate, max 2 rounds)
```

**Implemented with LangGraph `StateGraph`** — the graph is the system. Each node is a compiler stage, and the conditional edge between the Validator and Repair Engine implements the retry loop without brute-force regeneration.

---

## Compiler Stages

| Stage | Node | Input | Output |
|-------|------|-------|--------|
| 1 | `intent_extractor` | NL Prompt | `IntentSchema` |
| 2 | `architecture_planner` | IntentSchema | `ArchitectureSchema` |
| 3a | `ui_generator` | Intent + Arch | `UISchema` |
| 3b | `api_generator` | Intent + Arch | `APISchema` |
| 3c | `db_generator` | Intent + Arch | `DBSchema` |
| 3d | `auth_generator` | Intent + Arch | `AuthSchema` |
| 4 | `cross_layer_validator` | All schemas | `List[ValidationError]` |
| 5 | `repair_engine` | Errors + schemas | Repaired schemas |
| 6 | `runtime_generator` | All schemas | Source code files |

---

## Cross-Layer Validation (Stage 4)

6 distinct checks:
1. **UI→API**: Every UI field must exist in an API response
2. **API→DB**: Every API response field must exist in a DB column
3. **Auth→UI**: Roles in UI pages must be defined in Auth schema
4. **Auth→API**: Roles in API routes must be defined in Auth schema
5. **Premium**: Premium features require pricing page + premium role
6. **Payments**: Payment feature requires a payments DB table

---

## Repair Engine (Stage 5)

**Targeted repair, not brute-force retry.**

When validation fails, the repair engine:
1. Identifies *which layer* failed (not just that something failed)
2. Generates a repair prompt with *only* the failing layer + error context
3. Regenerates *only* that layer (max 3 attempts per layer)
4. Re-runs validation to confirm the fix

This is significantly more token-efficient and reliable than full pipeline regeneration.

---

## Setup

```bash
git clone https://github.com/yourusername/compiler-ai
cd compiler-ai

# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# Run locally
streamlit run app.py
```

---

## Evaluation

```bash
# Run all 20 prompts
python evaluation/metrics.py

# Quick test (5 prompts)
python evaluation/metrics.py --quick

# Normal prompts only
python evaluation/metrics.py --normal-only

# Edge cases only
python evaluation/metrics.py --edge-only

# Specific prompt
python evaluation/metrics.py --id 1
```

---

## Evaluation Dataset (20 prompts)

### Normal (10)
1. CRM with login, contacts, dashboard, role-based access, payments, analytics
2. Learning Management System with courses, quizzes, progress tracking
3. Hospital Management with patients, doctors, billing, pharmacy
4. Inventory System with products, orders, suppliers, reports
5. Food Delivery with restaurants, orders, tracking, drivers
6. HRMS with employees, payroll, leave, performance reviews
7. Expense Tracker with budgets, receipts, approval workflows
8. School ERP with students, grades, timetable, parent portal
9. Hotel Booking with rooms, reservations, check-in/out
10. Job Portal with candidates, employers, job listings

### Edge Cases (10)
11. "Build something" (vague)
12. "CRM without users" (conflicting)
13. "No login but admin dashboard" (conflicting)
14. "Payments without products or users" (incomplete)
15. "Build Facebook in 2 pages" (impossible scope)
16. "Make an AI system that does everything" (too vague)
17. "Inventory with AI predictions and IoT integration" (ambiguous)
18. "Build a todo app" (too simple)
19. "E-commerce without authentication" (conflicting)
20. "Dashboard for analytics" (underspecified)

---

## Cost vs Quality Tradeoff

| Strategy | Cost | Quality | Latency |
|----------|------|---------|---------|
| Single prompt | Low | Poor | ~3s |
| Modular pipeline | Medium | High | ~12s |
| Pipeline + validation + repair | Medium+ | Very High | ~18s |
| Full regeneration on error | High | Inconsistent | ~35s |

**Our approach**: Modular pipeline + targeted repair.  
Gemini 2.0 Flash keeps per-stage latency low while temperature=0 ensures determinism.

---

## Determinism Guarantees

- `temperature=0.0` on all LLM calls
- `response_mime_type="application/json"` (Gemini JSON mode)
- Strict Pydantic schemas as LLM output contracts
- One LLM call per stage (no combined prompts)
- Versioned intermediate representations (`schema_version` field)

---

## Folder Structure

```
compiler-ai/
├── app.py                    # Streamlit demo UI
├── graph/
│   ├── pipeline_graph.py     # LangGraph StateGraph (centerpiece)
│   ├── nodes.py              # Node functions
│   └── state.py              # PipelineState TypedDict
├── pipeline/
│   ├── intent.py             # Stage 1
│   ├── planner.py            # Stage 2
│   ├── ui_generator.py       # Stage 3a
│   ├── api_generator.py      # Stage 3b
│   ├── db_generator.py       # Stage 3c
│   ├── auth_generator.py     # Stage 3d
│   ├── validator.py          # Stage 4
│   ├── repair.py             # Stage 5
│   └── runtime.py            # Stage 6
├── schemas/                  # Pydantic models
├── evaluation/
│   ├── dataset.json          # 20 test prompts
│   └── metrics.py            # Auto-evaluation script
└── requirements.txt
```

---

## Deployment

Deploy to Streamlit Community Cloud:
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `app.py` as entry point
4. Add `GEMINI_API_KEY` in Streamlit Secrets
5. Deploy 🚀
