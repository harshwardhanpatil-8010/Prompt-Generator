# AI Context-Engineered Website Generation System

A research prototype for **Context Engineering** in AI website generation. The system transforms high-level, ambiguous user requirements into structured, stored, retrievable, manageable, and optimized context representations—synthesizing a **minimum-sufficient high-density prompt** tailored for external AI website-generation agents with **&ge;50% token reduction and 100% critical requirement coverage**.

---

## The Core Research Problem

AI website-generation agents often struggle with high-level, ambiguous user requirements. Manually creating detailed requirements, design specifications, architecture, database/API specifications, and task documents produces very large contexts. Large contexts increase token consumption and introduce irrelevant or redundant information.

This system solves this by implementing the full **Context Lifecycle**:

```
User Input (+ Optional Webpage Context)
                     ↓
         1. [Context Generation]
                     ↓
       2. [Context Representation]
 (Requirements, Pages, Components, APIs, DB, Design)
                     ↓
          3. [Context Storage]
        (InMemoryContextStore)
                     ↓
         4. [Context Retrieval]
 (Query by ID, Type, Requirement, Subgraph)
                     ↓
        5. [Context Management]
  (Human Review, Status Transitions, Merging)
                     ↓
        [Human Approval Gate]
                     ↓
        6. [Context Optimization]
   (Dependency Graph & Heuristic Evaluator)
   (&ge;50% Token Reduction, 100% Critical Coverage)
                     ↓
   7. [Minimum-Sufficient Final Prompt]
                     ↓
(External AI Website Generation Agent - Future Scope)
```

---

## Implemented Context Lifecycle Stages

1. **Context Generation (`backend/context/generator.py`)**:
   - Takes raw prompt and optional active webpage context (title, URL, selection).
   - Dynamically extracts intent, goals, domain, target users, functional & non-functional requirements, pages, components, APIs, database entities, design system tokens, technical recommendations, constraints, assumptions, and unknowns.
   - Strictly tags every item with its provenance source: `USER`, `MODEL_INFERRED`, `WEBPAGE`, `ASSUMPTION`, or `UNKNOWN`.

2. **Context Representation (`backend/context/representation.py`)**:
   - Strongly typed Pydantic models with stable IDs (`REQ-001`, `PAGE-001`, `COMP-001`, `API-001`, `DB-001`, `TASK-001`, `ASSUMP-001`, `UNK-001`, `DEC-001`).
   - Categorized by priority (`HIGH`, `MEDIUM`, `LOW`) and status (`ACTIVE`, `REVIEW`, `APPROVED`, `REJECTED`, `ARCHIVED`).

3. **Context Storage (`backend/context/storage.py`)**:
   - `ContextStore` abstract interface and `InMemoryContextStore` implementation.
   - Clean persistence boundary enabling future drop-in database backends without touching the pipeline.

4. **Context Retrieval (`backend/context/retrieval.py`)**:
   - Provides structured querying by Project, Entity Type, Item ID, Related Entities, and Requirement dependency links.

5. **Context Management (`backend/context/management.py`)**:
   - Supports CRUD operations, status updates, source labeling, and relational merging.

6. **Context Optimization (`backend/context/optimizer.py`, `evaluator.py`, `graph.py`, `token_counter.py`)**:
   - Models relationships in an in-memory `DependencyGraph`.
   - Computes heuristic scores for `relevance`, `importance`, `redundancy`, and `dependency_score`.
   - Compresses narrative fluff into high-density technical specifications.
   - Prunes isolated boilerplate while strictly preserving 100% of critical functional requirements, security rules, and accessibility constraints.

7. **Minimum-Sufficient Final Prompt (`backend/context/prompt_builder.py`)**:
   - Synthesizes a structured, information-dense specification ready to be pasted into any external AI code-generation agent (Claude, GPT-4, Gemini, bolt.new, v0, etc.).

---

## Project Structure

```
prompt-generator/
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── train.jsonl
│       ├── validation.jsonl
│       └── test.jsonl
│
├── scripts/
│   ├── inspect_datasets.py
│   ├── prepare_dataset.py
│   └── validate_dataset.py
│
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI REST server & CORS routing
│   ├── config.py                   # Pydantic Settings configuration
│   ├── models.py                   # Strongly typed Project and API models
│   ├── pipeline.py                 # Pipeline Orchestrator coordinating lifecycle
│   ├── state_machine.py            # 9-state ProjectStateMachine & approval gates
│   │
│   ├── context/                    # Context Lifecycle Subsystem
│   │   ├── __init__.py
│   │   ├── generator.py            # Stage 1: Context Generation
│   │   ├── representation.py       # Stage 2: Context Representation
│   │   ├── storage.py              # Stage 3: Context Storage
│   │   ├── retrieval.py            # Stage 4: Context Retrieval
│   │   ├── management.py           # Stage 5: Context Management
│   │   ├── graph.py                # In-memory Dependency Graph
│   │   ├── evaluator.py            # Heuristic Context Evaluator
│   │   ├── optimizer.py            # Stage 6: Context Optimizer
│   │   ├── token_counter.py        # Token counting & metric computation
│   │   └── prompt_builder.py       # Stage 7: Minimum-Sufficient Prompt
│   │
│   ├── llm/                        # LLM Provider Layer
│   │   ├── __init__.py             # Provider factory
│   │   ├── base.py                 # BaseLLMProvider abstract interface
│   │   ├── mock.py                 # Content-aware deterministic mock
│   │   └── ollama.py               # Local Ollama provider with fallback
│   │
│   └── tests/                      # Automated Test Suite (16 tests)
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_graph.py
│       ├── test_llm.py
│       ├── test_management.py
│       ├── test_optimizer.py
│       ├── test_pipeline.py
│       ├── test_retrieval.py
│       ├── test_state_machine.py
│       └── test_storage.py
│
├── extension/                      # Chrome Extension (Manifest V3)
│   ├── manifest.json
│   ├── content.js                  # Safe webpage context collector
│   ├── popup.html                  # 5-stage modern dark UI
│   ├── popup.css                   # Stylesheet
│   └── popup.js                    # Controller & async API client
│
├── training/
│   └── train_colab.ipynb           # Qwen 2.5 3B QLoRA training notebook (untouched)
│
├── .env.example
├── .gitignore
├── pytest.ini
├── backend/requirements.txt
└── README.md
```

---

## System States

The project enforces an explicit 9-state lifecycle via `ProjectStateMachine`:

```
INITIAL
   ↓
GENERATING_CONTEXT
   ↓
CONTEXT_READY
   ↓
REVIEW
   ↓
APPROVED (Human Approval Gate)
   ↓
MANAGED
   ↓
OPTIMIZING
   ↓
OPTIMIZED
   ↓
FINAL_PROMPT_READY (Human Prompt Approval Gate)
```

---

## Setup & Installation

### 1. Open Terminal and Navigate to Project
```bash
cd ~/Desktop/Prompt\ Generator
```

### 2. Activate Virtual Environment
```bash
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```
Default configuration (`.env`):
```env
LLM_PROVIDER=mock
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=prompt-generator
API_HOST=127.0.0.1
API_PORT=8000
```

---

## Running the Backend & Tests

### Run Automated Tests
```bash
.venv/bin/pytest -v
```

### Start the FastAPI Server
```bash
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Root: `http://127.0.0.1:8000/`
- Web Application Studio: `http://127.0.0.1:8000/app/`
- Health Check: `http://127.0.0.1:8000/health`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

---

## Accessing the Web Application (Browser Studio)

You can use the full **AI Context Engineer** website directly in any web browser without needing to install the Chrome Extension:

1. Start the server:
   ```bash
   source .venv/bin/activate
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. Open in your browser:
   **[http://127.0.0.1:8000/app/](http://127.0.0.1:8000/app/)**
3. Features:
   - Full-screen 5-stage context engineering lifecycle
   - Pre-configured starter presets (Sneaker Drops, SaaS Analytics, Telehealth, AI Canvas)
   - Interactive structured context explorer (Requirements, Architecture, Design tokens, Assumptions, Unknowns)
   - Visual dependency graph flow viewer and subgraph retriever
   - Real-time token reduction and critical coverage KPI dashboard (&ge;50% reduction)
   - Minimum-sufficient prompt studio with agent target presets (Claude, GPT-4o, Bolt.new), 1-click clipboard copy, and Markdown/JSON downloads.

---

## Loading the Chrome Extension

1. Open **Google Chrome**.
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode** toggle in the top-right corner.
4. Click **Load unpacked** in the top-left corner.
5. Select the `extension/` directory:
   `/Users/harshwardhanpatil/Desktop/Prompt Generator/extension`
6. Pin the **AI Context Engineer** extension to your toolbar.

---

## Example REST API Requests

### 1. Create Project
```bash
curl -X POST http://127.0.0.1:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"original_prompt": "Create a modern e-commerce website for a sneaker store with catalog, size selector, and cart.", "project_name": "Sneaker Hub"}'
```

### 2. Generate Structured Context
```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/context/generate
```

### 3. Retrieve Specific Context Item
```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/context/retrieve \
  -H "Content-Type: application/json" \
  -d '{"item_id": "REQ-001"}'
```

### 4. Approve Context (Human Gate)
```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/context/approve
```

### 5. Run Context Optimization
```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/context/optimize
```

### 6. Approve Final Prompt
```bash
curl -X POST http://127.0.0.1:8000/projects/{project_id}/prompt/approve \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'
```

---

## Switching LLM Providers

- **Mock Provider (Default)**:
  ```env
  LLM_PROVIDER=mock
  ```
- **Local Ollama Provider (Optional)**:
  ```env
  LLM_PROVIDER=ollama
  OLLAMA_BASE_URL=http://127.0.0.1:11434
  OLLAMA_MODEL=prompt-generator
  ```

---

## Future Qwen 2.5 3B Model Integration

The Qwen 2.5 3B QLoRA model is being fine-tuned in Google Colab (`training/train_colab.ipynb`).
When training completes:
1. Export model adapter or GGUF / Ollama Modelfile.
2. Load into Ollama (`ollama create prompt-generator -f ./Modelfile`) or local inference server.
3. Set `LLM_PROVIDER=ollama` in `.env`.

---

## Scope Limits & Known Limitations

- **Scope Boundary**: The system ends at the production of the minimum-sufficient prompt. Autonomous code execution, automated deployment, and browser runtime repairs are future scope.
- **In-Memory Store**: Project context is held in-memory during this stage of the prototype.
- **Dependency Graph**: Graph traversal and dependency mapping are performed in-memory via adjacency sets and BFS rather than a heavy graph database.
# Prompt-Generator
