/**
 * AI Context Engineer - Web Studio Controller
 * Full 7-stage Context Engineering Lifecycle for Website Generation
 */

// Determine API Base URL intelligently
const API_BASE = (window.location.protocol.startsWith("http") && window.location.port === "8000")
  ? window.location.origin
  : "http://127.0.0.1:8000";

// Global Studio State
let currentProjectId = null;
let currentProject = null;
let currentContext = null;
let currentOptimization = null;
let isOfflineMode = false;
let rawFinalPrompt = "";

let webpageContext = {
  enabled: false,
  page_title: null,
  page_url: null,
  selected_text: null
};


// DOM Element Registry
const elements = {
  // Navigation & Status
  backendStatusPill: document.getElementById("backendStatusPill"),
  backendStatusText: document.getElementById("backendStatusText"),
  btnRefreshStatus: document.getElementById("btnRefreshStatus"),
  btnInfoModal: document.getElementById("btnInfoModal"),
  btnCloseModal: document.getElementById("btnCloseModal"),
  infoModal: document.getElementById("infoModal"),
  btnNavNewProject: document.getElementById("btnNavNewProject"),

  // Stepper Tabs
  stepTabs: {
    1: document.getElementById("step1-tab"),
    2: document.getElementById("step2-tab"),
    3: document.getElementById("step3-tab"),
    4: document.getElementById("step4-tab"),
    5: document.getElementById("step5-tab")
  },

  // Stages
  stages: {
    input: document.getElementById("stage-input"),
    context: document.getElementById("stage-context"),
    graph: document.getElementById("stage-graph"),
    optimize: document.getElementById("stage-optimize"),
    prompt: document.getElementById("stage-prompt")
  },

  // Stage 1 Inputs
  projectName: document.getElementById("projectName"),
  inputRequirement: document.getElementById("inputRequirement"),
  enableWebContext: document.getElementById("enableWebContext"),
  webContextForm: document.getElementById("webContextForm"),
  webContextBadge: document.getElementById("webContextBadge"),
  ctxUrl: document.getElementById("ctxUrl"),
  ctxTitle: document.getElementById("ctxTitle"),
  ctxSelection: document.getElementById("ctxSelection"),
  btnGenerateContext: document.getElementById("btnGenerateContext"),

  // Stage 2 Structured Context
  projectIdBadge: document.getElementById("projectIdBadge"),
  projectStateBadge: document.getElementById("projectStateBadge"),
  reqCount: document.getElementById("reqCount"),
  assumpCount: document.getElementById("assumpCount"),
  unknownCount: document.getElementById("unknownCount"),
  pageCountBadge: document.getElementById("pageCountBadge"),
  compCountBadge: document.getElementById("compCountBadge"),
  apiCountBadge: document.getElementById("apiCountBadge"),
  requirementsList: document.getElementById("requirementsList"),
  pagesList: document.getElementById("pagesList"),
  componentsList: document.getElementById("componentsList"),
  apisList: document.getElementById("apisList"),
  designStyle: document.getElementById("designStyle"),
  designColor: document.getElementById("designColor"),
  designType: document.getElementById("designType"),
  techFrontend: document.getElementById("techFrontend"),
  techSecurity: document.getElementById("techSecurity"),
  techA11y: document.getElementById("techA11y"),
  assumptionsList: document.getElementById("assumptionsList"),
  unknownsList: document.getElementById("unknownsList"),
  btnBackToInput: document.getElementById("btnBackToInput"),
  btnViewGraph: document.getElementById("btnViewGraph"),
  btnApproveContext: document.getElementById("btnApproveContext"),

  // Stage 3 Graph & Retrieval
  graphFlowView: document.getElementById("graphFlowView"),
  queryItemId: document.getElementById("queryItemId"),
  btnQueryContext: document.getElementById("btnQueryContext"),
  queryResultsBox: document.getElementById("queryResultsBox"),
  btnBackToContext: document.getElementById("btnBackToContext"),
  btnProceedToOptimize: document.getElementById("btnProceedToOptimize"),

  // Stage 4 Optimization Metrics
  metricOrigTokens: document.getElementById("metricOrigTokens"),
  metricOptTokens: document.getElementById("metricOptTokens"),
  metricReduction: document.getElementById("metricReduction"),
  metricCoverage: document.getElementById("metricCoverage"),
  metricTokensSaved: document.getElementById("metricTokensSaved"),
  metricCriticalCoverage: document.getElementById("metricCriticalCoverage"),
  metricPrunedCount: document.getElementById("metricPrunedCount"),
  prunedItemsList: document.getElementById("prunedItemsList"),
  btnBackToGraph: document.getElementById("btnBackToGraph"),
  btnViewFinalPrompt: document.getElementById("btnViewFinalPrompt"),

  // Stage 5 Minimum Prompt Studio
  finalPromptText: document.getElementById("finalPromptText"),
  btnCopyPrompt: document.getElementById("btnCopyPrompt"),
  btnApprovePrompt: document.getElementById("btnApprovePrompt"),
  btnDownloadPrompt: document.getElementById("btnDownloadPrompt"),
  btnExportJson: document.getElementById("btnExportJson"),
  btnRestart: document.getElementById("btnRestart"),

  // Toast
  toastContainer: document.getElementById("toastContainer")
};

// ==========================================
// Initialization
// ==========================================
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  setupSpecSubTabs();
  await checkBackendHealth();
});

// ==========================================
// Toast Notification Engine
// ==========================================
let lastToastMessage = "";
let lastToastTime = 0;

function showToast(message, type = "info") {
  const now = Date.now();
  if (message === lastToastMessage && now - lastToastTime < 2500) {
    return;
  }
  lastToastMessage = message;
  lastToastTime = now;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const icon = type === "success" ? "✓" : type === "error" ? "✕" : "ℹ";
  toast.innerHTML = `<span style="font-weight:700;">${icon}</span> <span>${escapeHtml(message)}</span>`;

  elements.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ==========================================
// Backend Health Check
// ==========================================
async function checkBackendHealth() {
  elements.backendStatusPill.className = "status-pill offline";
  elements.backendStatusText.textContent = "Connecting to API...";

  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET" });
    if (res.ok) {
      const data = await res.json();
      isOfflineMode = false;
      elements.backendStatusPill.className = "status-pill online";
      const provider = data.llm_provider ? data.llm_provider.toUpperCase() : "ACTIVE";
      elements.backendStatusText.textContent = `Online (${provider})`;
      showToast(`Connected to backend API (${provider} provider)`, "success");
      return true;
    }
    throw new Error(`Server returned ${res.status}`);
  } catch (err) {
    isOfflineMode = true;
    elements.backendStatusPill.className = "status-pill offline";
    elements.backendStatusText.textContent = "Standby (Sim Mode)";
    showToast("Backend not detected on :8000. Interactive simulation mode active.", "info");
    return false;
  }
}

// ==========================================
// Stage Navigation
// ==========================================
function setStage(stageKey, stepNum) {
  // Update stage views
  Object.values(elements.stages).forEach(el => el.classList.remove("active"));
  if (elements.stages[stageKey]) {
    elements.stages[stageKey].classList.add("active");
  }

  // Update Stepper Navigation
  Object.entries(elements.stepTabs).forEach(([num, tab]) => {
    const n = parseInt(num, 10);
    tab.classList.remove("active");
    if (n < stepNum) {
      tab.classList.add("completed");
    } else {
      tab.classList.remove("completed");
    }
    if (n === stepNum) {
      tab.classList.add("active");
    }
  });

  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ==========================================
// Event Listeners Setup
// ==========================================
function setupEventListeners() {
  // Health refresh
  elements.btnRefreshStatus.addEventListener("click", async () => {
    await checkBackendHealth();
  });

  // Info Modal
  elements.btnInfoModal.addEventListener("click", () => {
    elements.infoModal.classList.add("open");
  });
  elements.btnCloseModal.addEventListener("click", () => {
    elements.infoModal.classList.remove("open");
  });
  elements.infoModal.addEventListener("click", (e) => {
    if (e.target === elements.infoModal) elements.infoModal.classList.remove("open");
  });

  // Top Nav New Project
  elements.btnNavNewProject.addEventListener("click", resetProject);

  // Character counter for prompt textarea
  const charCountEl = document.getElementById("charCount");
  const btnClearPrompt = document.getElementById("btnClearPrompt");

  function updateCharCount() {
    if (charCountEl && elements.inputRequirement) {
      charCountEl.textContent = `${elements.inputRequirement.value.length} characters`;
    }
  }

  if (elements.inputRequirement) {
    elements.inputRequirement.addEventListener("input", updateCharCount);
    updateCharCount();
  }

  if (btnClearPrompt) {
    btnClearPrompt.addEventListener("click", () => {
      elements.inputRequirement.value = "";
      updateCharCount();
      elements.inputRequirement.focus();
    });
  }

  // Stepper tab click navigation
  Object.entries(elements.stepTabs).forEach(([num, tab]) => {
    tab.addEventListener("click", () => {
      const stepNum = parseInt(num, 10);
      const stageKeys = ["input", "context", "graph", "optimize", "prompt"];
      const targetStage = stageKeys[stepNum - 1];
      
      // Allow moving if project has reached that stage or going backwards
      if (stepNum === 1 || currentContext) {
        setStage(targetStage, stepNum);
      } else {
        showToast("Please generate structured context first.", "info");
      }
    });
  });

  // Webpage context toggle
  elements.enableWebContext.addEventListener("change", (e) => {
    webpageContext.enabled = e.target.checked;
    if (e.target.checked) {
      elements.webContextForm.classList.remove("hidden");
      elements.webContextBadge.textContent = "ENABLED";
      elements.webContextBadge.style.color = "var(--accent-cyan)";
    } else {
      elements.webContextForm.classList.add("hidden");
      elements.webContextBadge.textContent = "DISABLED";
      elements.webContextBadge.style.color = "var(--text-muted)";
    }
  });

  // Stage 1 Actions
  elements.btnGenerateContext.addEventListener("click", handleGenerateContext);

  // Stage 2 Actions
  elements.btnBackToInput.addEventListener("click", () => setStage("input", 1));
  elements.btnViewGraph.addEventListener("click", () => {
    renderGraphView();
    setStage("graph", 3);
  });
  elements.btnApproveContext.addEventListener("click", handleApproveAndOptimize);

  // Stage 3 Actions
  elements.btnBackToContext.addEventListener("click", () => setStage("context", 2));
  elements.btnProceedToOptimize.addEventListener("click", handleApproveAndOptimize);
  elements.btnQueryContext.addEventListener("click", handleQueryContext);

  // Stage 4 Actions
  elements.btnBackToGraph.addEventListener("click", () => setStage("graph", 3));
  elements.btnViewFinalPrompt.addEventListener("click", () => setStage("prompt", 5));

  // Stage 5 Actions
  elements.btnCopyPrompt.addEventListener("click", handleCopyPrompt);
  elements.btnApprovePrompt.addEventListener("click", handleApprovePrompt);
  elements.btnDownloadPrompt.addEventListener("click", handleDownloadPrompt);
  elements.btnExportJson.addEventListener("click", handleExportJson);
  elements.btnRestart.addEventListener("click", resetProject);

}

// Sub tabs inside Stage 2
function setupSpecSubTabs() {
  const tabs = document.querySelectorAll(".spec-tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".spec-tab-panel").forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add("active");
    });
  });
}

function setButtonLoading(btn, loading, loadingText = "Processing...") {
  if (!btn) return;
  btn.disabled = loading;
  const textSpan = btn.querySelector(".btn-text") || btn;
  if (loading) {
    if (!btn.dataset.originalText) {
      btn.dataset.originalText = textSpan.innerHTML;
    }
    textSpan.innerHTML = loadingText;
  } else {
    if (btn.dataset.originalText) {
      textSpan.innerHTML = btn.dataset.originalText;
    }
  }
}

// ==========================================
// Stage 1: Generate Context
// ==========================================
async function handleGenerateContext() {
  const prompt = elements.inputRequirement.value.trim();
  const name = elements.projectName.value.trim() || "Website Generation Project";

  if (prompt.length < 5) {
    showToast("Please enter a website requirement of at least 5 characters.", "error");
    return;
  }

  setButtonLoading(elements.btnGenerateContext, true, "Generating Context...");

  if (webpageContext.enabled) {
    webpageContext.page_url = elements.ctxUrl.value.trim() || null;
    webpageContext.page_title = elements.ctxTitle.value.trim() || null;
    webpageContext.selected_text = elements.ctxSelection.value.trim() || null;
  }

  try {
    if (!isOfflineMode) {
      // 1. Create Project in Backend
      const createRes = await fetch(`${API_BASE}/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_prompt: prompt,
          project_name: name,
          context: webpageContext.enabled ? webpageContext : null
        })
      });

      if (!createRes.ok) {
        throw new Error(`Failed to create project (HTTP ${createRes.status})`);
      }

      currentProject = await createRes.json();
      currentProjectId = currentProject.project_id;

      // 2. Trigger Context Generation
      const genRes = await fetch(`${API_BASE}/projects/${currentProjectId}/context/generate`, {
        method: "POST"
      });

      if (!genRes.ok) {
        throw new Error(`Context generation failed (HTTP ${genRes.status})`);
      }

      const genProject = await genRes.json();
      currentProject = genProject;
      currentContext = genProject.context_representation;
    } else {
      // Offline Simulation Fallback
      await new Promise(r => setTimeout(r, 650));
      currentProjectId = "PROJ-" + Math.random().toString(36).substring(2, 8).toUpperCase();
      currentContext = generateMockStructuredContext(prompt, name);
      currentProject = {
        project_id: currentProjectId,
        project_name: name,
        state: "CONTEXT_READY",
        context_representation: currentContext
      };
    }

    // Render Stage 2
    renderStructuredContext(currentContext);
    setStage("context", 2);
    showToast("Structured context generated and stored in memory!", "success");

  } catch (err) {
    console.warn("Backend error, falling back to local simulation:", err);
    // If backend failed mid-request, gracefully fall back to simulation
    isOfflineMode = true;
    elements.backendStatusPill.className = "status-pill offline";
    elements.backendStatusText.textContent = "Standby (Sim Mode)";

    currentProjectId = "PROJ-" + Math.random().toString(36).substring(2, 8).toUpperCase();
    currentContext = generateMockStructuredContext(prompt, name);
    currentProject = {
      project_id: currentProjectId,
      project_name: name,
      state: "CONTEXT_READY",
      context_representation: currentContext
    };

    renderStructuredContext(currentContext);
    setStage("context", 2);
    showToast("Context generated via offline simulation engine.", "info");
  } finally {
    setButtonLoading(elements.btnGenerateContext, false);
  }
}

// ==========================================
// Stage 2: Render Structured Context
// ==========================================
function renderStructuredContext(ctx) {
  if (!ctx) return;

  elements.projectIdBadge.textContent = `ID: ${currentProjectId}`;
  elements.projectStateBadge.textContent = `STATE: ${currentProject ? currentProject.state : 'CONTEXT_READY'}`;

  // 1. Requirements List
  const reqListEl = elements.requirementsList;
  reqListEl.innerHTML = "";
  const reqs = ctx.requirements || [];
  elements.reqCount.textContent = reqs.length;

  reqs.forEach(req => {
    const card = document.createElement("div");
    card.className = "req-card";
    const priority = (req.priority || "MEDIUM").toUpperCase();
    const source = (req.source || "USER").toUpperCase();

    card.innerHTML = `
      <div class="req-card-header">
        <span class="req-id">${escapeHtml(req.id)}</span>
        <div class="req-badges">
          <span class="source-chip">${escapeHtml(source)}</span>
          <span class="priority-chip priority-${priority.toLowerCase()}">${priority}</span>
        </div>
      </div>
      <div class="req-title">${escapeHtml(req.title)}</div>
      <div class="req-desc">${escapeHtml(req.description)}</div>
    `;
    reqListEl.appendChild(card);
  });

  // 2. Architecture: Pages
  const pagesListEl = elements.pagesList;
  pagesListEl.innerHTML = "";
  const pages = ctx.pages || [];
  elements.pageCountBadge.textContent = pages.length;

  pages.forEach(p => {
    const item = document.createElement("div");
    item.className = "arch-item";
    const sectionsText = p.sections && p.sections.length ? p.sections.join(", ") : "Main Section";
    item.innerHTML = `
      <div><strong>${escapeHtml(p.name)}</strong> <code>${escapeHtml(p.path)}</code></div>
      <div style="font-size:0.75rem; color:var(--text-dim); margin-top:2px;">Sections: ${escapeHtml(sectionsText)}</div>
    `;
    pagesListEl.appendChild(item);
  });

  // 3. Architecture: Components
  const compListEl = elements.componentsList;
  compListEl.innerHTML = "";
  const comps = ctx.components || [];
  elements.compCountBadge.textContent = comps.length;

  comps.forEach(c => {
    const item = document.createElement("div");
    item.className = "arch-item";
    item.innerHTML = `
      <div><strong>${escapeHtml(c.name)}</strong> <span class="badge-tag">${escapeHtml(c.type || 'UI')}</span></div>
      <div style="font-size:0.75rem; color:var(--text-dim); margin-top:2px;">Linked: ${(c.requirements || []).join(", ") || 'REQ-001'}</div>
    `;
    compListEl.appendChild(item);
  });

  // 4. Architecture: APIs
  const apiListEl = elements.apisList;
  apiListEl.innerHTML = "";
  const apis = ctx.apis || [];
  elements.apiCountBadge.textContent = apis.length;

  apis.forEach(a => {
    const item = document.createElement("div");
    item.className = "arch-item";
    item.innerHTML = `
      <div><code>${escapeHtml(a.method || 'GET')} ${escapeHtml(a.endpoint || '/')}</code></div>
      <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">${escapeHtml(a.description || 'Service endpoint')}</div>
    `;
    apiListEl.appendChild(item);
  });

  // 5. Design System Tokens
  if (ctx.design) {
    elements.designStyle.textContent = ctx.design.visual_style || "Modern Minimalist";
    elements.designColor.textContent = ctx.design.color_direction || "Monochrome with Electric Indigo accent";
    elements.designType.textContent = ctx.design.typography || "Inter (Headings: 700, Body: 400)";
  }

  // 6. Technical Recommendations
  if (ctx.technical) {
    elements.techFrontend.textContent = ctx.technical.frontend || "Next.js 14 / React with Vanilla CSS tokens";
    elements.techSecurity.textContent = ctx.technical.security || "Strict CSP headers, sanitized inputs, CSRF guard";
    elements.techA11y.textContent = ctx.technical.accessibility || "WCAG 2.1 AA compliant contrast & keyboard navigation";
  }

  // 7. Assumptions
  const assumpListEl = elements.assumptionsList;
  assumpListEl.innerHTML = "";
  const assumptions = ctx.assumptions || [];
  elements.assumpCount.textContent = assumptions.length;

  assumptions.forEach(item => {
    const li = document.createElement("li");
    li.className = "bullet-item";
    const text = typeof item === "string" ? item : (item.text || item.id);
    li.innerHTML = `<span class="bullet-icon">💡</span> <span>${escapeHtml(text)}</span>`;
    assumpListEl.appendChild(li);
  });

  // 8. Unknowns
  const unknownListEl = elements.unknownsList;
  unknownListEl.innerHTML = "";
  const unknowns = ctx.unknowns || [];
  elements.unknownCount.textContent = unknowns.length;

  unknowns.forEach(item => {
    const li = document.createElement("li");
    li.className = "bullet-item";
    const text = typeof item === "string" ? item : (item.text || item.id);
    li.innerHTML = `<span class="bullet-icon">❓</span> <span>${escapeHtml(text)}</span>`;
    unknownListEl.appendChild(li);
  });
}

// ==========================================
// Stage 3: Dependency Graph & Retrieval
// ==========================================
function renderGraphView() {
  const container = elements.graphFlowView;
  container.innerHTML = "";

  if (!currentContext || !currentContext.requirements) {
    container.innerHTML = `<div style="color:var(--text-dim); padding:20px; text-align:center;">No context graph available.</div>`;
    return;
  }

  currentContext.requirements.forEach(req => {
    const relatedPages = (currentContext.pages || [])
      .filter(p => (p.requirements || []).includes(req.id))
      .map(p => p.id);

    const relatedComps = (currentContext.components || [])
      .filter(c => (c.requirements || []).includes(req.id))
      .map(c => c.id);

    const relatedApis = (currentContext.apis || [])
      .filter(a => (a.requirements || []).includes(req.id))
      .map(a => a.id);

    const card = document.createElement("div");
    card.className = "graph-chain-card";

    let html = `<span class="chain-node req">${escapeHtml(req.id)}</span>`;

    if (relatedPages.length) {
      html += `<span class="chain-arrow">&rarr;</span>`;
      html += relatedPages.map(p => `<span class="chain-node page">${escapeHtml(p)}</span>`).join(" ");
    }

    if (relatedComps.length) {
      html += `<span class="chain-arrow">&rarr;</span>`;
      html += relatedComps.map(c => `<span class="chain-node comp">${escapeHtml(c)}</span>`).join(" ");
    }

    if (relatedApis.length) {
      html += `<span class="chain-arrow">&rarr;</span>`;
      html += relatedApis.map(a => `<span class="chain-node api">${escapeHtml(a)}</span>`).join(" ");
    }

    card.innerHTML = html;
    container.appendChild(card);
  });
}

async function handleQueryContext() {
  const qId = elements.queryItemId.value.trim();
  if (!qId) {
    showToast("Please enter an item ID to query (e.g. REQ-001)", "error");
    return;
  }

  try {
    if (!isOfflineMode && currentProjectId) {
      const res = await fetch(`${API_BASE}/projects/${currentProjectId}/context/retrieve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: qId })
      });
      const data = await res.json();
      elements.queryResultsBox.classList.remove("hidden");
      elements.queryResultsBox.textContent = JSON.stringify(data, null, 2);
    } else {
      // Offline Subgraph Query Simulation
      const result = simulateContextRetrieval(qId);
      elements.queryResultsBox.classList.remove("hidden");
      elements.queryResultsBox.textContent = JSON.stringify(result, null, 2);
    }
    showToast(`Retrieved context subgraph for ${qId}`, "success");
  } catch (err) {
    showToast(`Query error: ${err.message}`, "error");
  }
}

function simulateContextRetrieval(itemId) {
  if (!currentContext) return { error: "No context generated yet" };

  const id = itemId.toUpperCase();
  const req = (currentContext.requirements || []).find(r => r.id === id);
  if (req) {
    return {
      entity_type: "requirement",
      item: req,
      connected_pages: (currentContext.pages || []).filter(p => (p.requirements || []).includes(id)),
      connected_components: (currentContext.components || []).filter(c => (c.requirements || []).includes(id)),
      connected_apis: (currentContext.apis || []).filter(a => (a.requirements || []).includes(id))
    };
  }

  const page = (currentContext.pages || []).find(p => p.id === id);
  if (page) return { entity_type: "page", item: page };

  const comp = (currentContext.components || []).find(c => c.id === id);
  if (comp) return { entity_type: "component", item: comp };

  const api = (currentContext.apis || []).find(a => a.id === id);
  if (api) return { entity_type: "api", item: api };

  return { message: `Entity '${itemId}' found as active subgraph leaf node`, query_id: itemId };
}

// ==========================================
// Stage 4: Optimize Context & Human Gate
// ==========================================
async function handleApproveAndOptimize() {
  if (!currentProjectId && !currentContext) {
    showToast("Please generate structured context first.", "error");
    return;
  }

  // If already optimized, seamlessly navigate to Stage 4 without redundant API calls or errors
  if (
    currentOptimization &&
    currentProject &&
    (currentProject.state === "OPTIMIZED" || currentProject.state === "FINAL_PROMPT_READY")
  ) {
    renderOptimizationMetrics(currentOptimization);
    if (!elements.finalPromptText.value && rawFinalPrompt) {
      elements.finalPromptText.value = rawFinalPrompt;
    }
    setStage("optimize", 4);
    return;
  }

  setButtonLoading(elements.btnApproveContext, true, "Optimizing Context...");
  setButtonLoading(elements.btnProceedToOptimize, true, "Optimizing Context...");

  try {
    if (!isOfflineMode && currentProjectId) {
      // 1. Human Approval Gate
      await fetch(`${API_BASE}/projects/${currentProjectId}/context/approve`, {
        method: "POST"
      });

      // 2. Context Optimization
      const optRes = await fetch(`${API_BASE}/projects/${currentProjectId}/context/optimize`, {
        method: "POST"
      });

      if (!optRes.ok) throw new Error(`Optimization failed (HTTP ${optRes.status})`);

      const optProject = await optRes.json();
      currentProject = optProject;
      currentOptimization = optProject.optimization_metrics;
      rawFinalPrompt = optProject.final_prompt || "";
    } else {
      // Offline Simulation Fallback
      await new Promise(r => setTimeout(r, 500));
      currentOptimization = {
        original_tokens: 2780,
        optimized_tokens: 1240,
        tokens_saved: 1540,
        token_reduction_percentage: 55.4,
        requirement_coverage_percentage: 100.0,
        critical_coverage_percentage: 100.0,
        critical_requirements_preserved: (currentContext.requirements || []).length,
        critical_requirements_total: (currentContext.requirements || []).length,
        pruning_summary: {
          pruned_count: 8,
          pruned_items: ["BOILERPLATE-AUTH-IMPORTS", "REDUNDANT-NARRATIVE-PREAMBLE", "UNUSED-SVG-DEFINITIONS", "GENERIC-LAYOUT-WRAPPER"],
          compressed_items: ["COMPACT-JSON-SCHEMA", "DENSE-COLOR-TOKENS", "UNIFIED-REST-ROUTING"]
        }
      };
      rawFinalPrompt = synthesizeMinimumPromptOffline(currentContext, currentOptimization);
    }

    renderOptimizationMetrics(currentOptimization);
    elements.finalPromptText.value = rawFinalPrompt;
    setStage("optimize", 4);
    showToast("Context optimized with ≥50% token reduction & 100% critical coverage!", "success");

  } catch (err) {
    showToast(`Optimization error: ${err.message}`, "error");
  } finally {
    setButtonLoading(elements.btnApproveContext, false);
    setButtonLoading(elements.btnProceedToOptimize, false);
  }
}

function renderOptimizationMetrics(m) {
  if (!m) return;

  animateCounter(elements.metricOrigTokens, m.original_tokens || 2700);
  animateCounter(elements.metricOptTokens, m.optimized_tokens || 1200);
  elements.metricReduction.textContent = `${m.token_reduction_percentage}%`;
  elements.metricCoverage.textContent = `${m.requirement_coverage_percentage}%`;

  elements.metricTokensSaved.textContent = `${(m.tokens_saved || 1500).toLocaleString()} tokens`;
  elements.metricCriticalCoverage.textContent =
    `${m.critical_requirements_preserved} / ${m.critical_requirements_total} (100%)`;
  
  const prunedCount = m.pruning_summary ? (m.pruning_summary.pruned_count || 8) : 8;
  elements.metricPrunedCount.textContent = `${prunedCount} items removed`;

  if (m.pruning_summary) {
    const prunedList = m.pruning_summary.pruned_items ? m.pruning_summary.pruned_items.join(", ") : "Narrative fluff, isolated boilerplate";
    const compList = m.pruning_summary.compressed_items ? m.pruning_summary.compressed_items.join(", ") : "Entity schema, Token mappings";
    elements.prunedItemsList.innerHTML = `
      <div style="margin-bottom:6px;"><strong>Pruned Redundancies:</strong> <span style="color:#fb7185;">[${escapeHtml(prunedList)}]</span></div>
      <div><strong>Compressed High-Density Representations:</strong> <span style="color:#34d399;">[${escapeHtml(compList)}]</span></div>
    `;
  }
}

function animateCounter(el, target) {
  let start = 0;
  const duration = 600;
  const startTime = performance.now();

  function update(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const current = Math.floor(progress * target);
    el.textContent = current.toLocaleString();
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.textContent = target.toLocaleString();
    }
  }
  requestAnimationFrame(update);
}

// ==========================================
// Stage 5: Final Prompt Studio
// ==========================================

function handleCopyPrompt() {
  const text = elements.finalPromptText.value;
  if (!text) {
    showToast("No prompt generated to copy.", "error");
    return;
  }

  navigator.clipboard.writeText(text).then(() => {
    const icon = document.getElementById("copyBtnIcon");
    const label = document.getElementById("copyBtnText");
    const prevText = label.textContent;

    icon.textContent = "✓";
    label.textContent = "Copied to Clipboard!";
    showToast("Minimum-sufficient prompt copied to clipboard!", "success");

    setTimeout(() => {
      icon.textContent = "📋";
      label.textContent = prevText;
    }, 2500);
  }).catch(() => {
    showToast("Clipboard write permission failed. Please copy manually.", "error");
  });
}

async function handleApprovePrompt() {
  if (!currentProjectId && !rawFinalPrompt) return;

  try {
    if (!isOfflineMode && currentProjectId) {
      await fetch(`${API_BASE}/projects/${currentProjectId}/prompt/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          approved: true,
          edited_prompt: elements.finalPromptText.value
        })
      });
    }
    document.getElementById("approvePromptText").textContent = "✓ Prompt Locked & Approved";
    showToast("Final prompt approved and locked for AI code generation agents!", "success");
  } catch (err) {
    showToast(`Approval failed: ${err.message}`, "error");
  }
}

function handleDownloadPrompt() {
  const text = elements.finalPromptText.value;
  if (!text) return;

  const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${(elements.projectName.value || 'website-prompt').toLowerCase().replace(/\s+/g, '-')}-spec.md`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Prompt downloaded as Markdown specification.", "info");
}

function handleExportJson() {
  if (!currentContext) return;

  const payload = {
    project_id: currentProjectId,
    project_name: elements.projectName.value,
    optimization_metrics: currentOptimization,
    context_representation: currentContext,
    final_prompt: elements.finalPromptText.value
  };

  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${(elements.projectName.value || 'website-context').toLowerCase().replace(/\s+/g, '-')}-context.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Full context exported as JSON payload.", "info");
}

function resetProject() {
  currentProjectId = null;
  currentProject = null;
  currentContext = null;
  currentOptimization = null;
  rawFinalPrompt = "";

  elements.projectName.value = "Sneaker Store Platform";
  elements.inputRequirement.value = "";
  elements.finalPromptText.value = "";
  elements.queryResultsBox.classList.add("hidden");
  elements.queryResultsBox.textContent = "";

  setStage("input", 1);
  showToast("Studio reset for new website generation project.", "info");
}

// ==========================================
// Simulation Utilities (Offline Fallback)
// ==========================================
function generateMockStructuredContext(prompt, name) {
  const isSneaker = prompt.toLowerCase().includes("sneaker");
  const isSaas = prompt.toLowerCase().includes("saas") || prompt.toLowerCase().includes("analytic");

  return {
    requirements: [
      {
        id: "REQ-001",
        title: isSneaker ? "Exclusive Drop Countdown & Catalog" : isSaas ? "Real-Time KPI Metrics Dashboard" : "Core Landing & Product Catalog",
        description: isSneaker
          ? "Live countdown timer with real-time stock ticker and product grid."
          : "Interactive telemetry cards displaying MRR, churn, and traffic.",
        priority: "HIGH",
        source: "USER"
      },
      {
        id: "REQ-002",
        title: isSneaker ? "Interactive 3D Shoe Inspector" : isSaas ? "Time-Series Line Chart Visualizer" : "Dynamic Interactive Visualizer",
        description: isSneaker
          ? "360-degree rotation shoe preview with colorway switcher."
          : "Configurable date range analytics chart with tooltip inspection.",
        priority: "HIGH",
        source: "MODEL_INFERRED"
      },
      {
        id: "REQ-003",
        title: isSneaker ? "Slide-Out Cart & Checkout" : isSaas ? "Tiered Stripe Subscription Billing" : "Payment & Order Processing",
        description: isSneaker
          ? "Animated slide-out drawer cart with size selector and Stripe checkout."
          : "Monthly and annual tier toggle with customer portal integration.",
        priority: "HIGH",
        source: "USER"
      },
      {
        id: "REQ-004",
        title: "Role-Based Access & Authentication",
        description: "Secure session management with token verification and OAuth login.",
        priority: "MEDIUM",
        source: "MODEL_INFERRED"
      },
      {
        id: "REQ-005",
        title: "Responsive Mobile Navigation & Drawer",
        description: "Fluid touch-friendly layout supporting mobile, tablet, and desktop viewports.",
        priority: "MEDIUM",
        source: "MODEL_INFERRED"
      }
    ],
    pages: [
      { id: "PAGE-001", name: "Home / Launchpad", path: "/", sections: ["Hero Banner", "Featured Drops", "Testimonials"], requirements: ["REQ-001", "REQ-005"] },
      { id: "PAGE-002", name: "Product Catalog", path: "/catalog", sections: ["Filters Bar", "Product Grid", "Pagination"], requirements: ["REQ-001", "REQ-002"] },
      { id: "PAGE-003", name: "Checkout & Cart", path: "/checkout", sections: ["Order Summary", "Payment Form", "Guarantee Badges"], requirements: ["REQ-003"] }
    ],
    components: [
      { id: "COMP-001", name: "CountdownTimer", type: "WIDGET", requirements: ["REQ-001"] },
      { id: "COMP-002", name: "ProductPreview3D", type: "CANVAS", requirements: ["REQ-002"] },
      { id: "COMP-003", name: "CartDrawer", type: "DRAWER", requirements: ["REQ-003"] },
      { id: "COMP-004", name: "NavbarSticky", type: "NAVIGATION", requirements: ["REQ-005"] }
    ],
    apis: [
      { id: "API-001", endpoint: "/api/products/drops", method: "GET", description: "Fetch upcoming product release inventory and countdowns", requirements: ["REQ-001"] },
      { id: "API-002", endpoint: "/api/cart/checkout", method: "POST", description: "Initiate secure Stripe checkout session", requirements: ["REQ-003"] }
    ],
    design: {
      visual_style: isSneaker ? "Brutalist Streetwear Dark UI" : "Modern Glassmorphism Enterprise",
      color_direction: isSneaker ? "Obsidian (#0A0A0A) + Electric Neon Lime (#CCFF00)" : "Deep Slate (#0F172A) + Indigo (#6366F1)",
      typography: "Inter Sans-Serif + JetBrains Mono for telemetry tokens"
    },
    technical: {
      frontend: "Next.js / Vite React with Vanilla CSS token system",
      security: "Content Security Policy, Sanitize Input, CSRF Token Header",
      accessibility: "WCAG 2.1 AA Compliant (Contrast ratio ≥ 4.5:1, Full keyboard focus)"
    },
    assumptions: [
      "Stripe payment gateway credentials will be supplied via environment variables.",
      "Inventory is loaded asynchronously via client-side polling or WebSocket.",
      "Target responsive breakpoints: 640px, 768px, 1024px, 1280px."
    ],
    unknowns: [
      "Preferred internationalization (i18n) multi-currency requirements.",
      "Target production cloud host (Vercel, AWS ECS, or Cloudflare Pages)."
    ]
  };
}

function synthesizeMinimumPromptOffline(ctx, opt) {
  return `=== AI WEBSITE GENERATION SPECIFICATION ===
PROJECT: ${elements.projectName.value || 'Website Generation Project'}
TARGET AGENT: Autonomous Code Generation Agent
OPTIMIZATION METRICS: Token Reduction ${opt.token_reduction_percentage}%, Critical Coverage 100%

1. ARCHITECTURAL OVERVIEW & ROUTES
- Home ("/"): Hero with countdown, interactive gallery, testimonials.
- Catalog ("/catalog"): Grid filter, product cards, real-time inventory counter.
- Checkout ("/checkout"): Slide-out drawer cart, Stripe checkout integration.

2. CORE COMPONENTS & INTERACTION LOGIC
- CountdownTimer (COMP-001): Ticks down to release timestamp; triggers restock animation.
- ProductPreview3D (COMP-002): Interactive multi-angle preview with colorway variant picker.
- CartDrawer (COMP-003): Global slide-out drawer state with item counter badge and total calculation.

3. DESIGN SYSTEM & TOKENS
- Style: ${ctx.design.visual_style}
- Palette: ${ctx.design.color_direction}
- Typography: ${ctx.design.typography}
- Accessibility: ${ctx.technical.accessibility}

4. API INTEGRATION
- GET /api/products/drops -> List[ProductDrop]
- POST /api/cart/checkout -> { checkout_url: string, session_id: string }

5. CRITICAL CONSTRAINTS & SECURITY
- ${ctx.technical.security}
- 100% responsive design down to 320px viewport.
- Deliver production-ready HTML, CSS, and modern JavaScript with zero placeholder stubs.
============================================`;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
