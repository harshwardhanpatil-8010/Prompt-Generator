const API_BASE = "http://127.0.0.1:8000";

let currentProjectId = null;
let currentContext = null;
let currentOptimization = null;
let webpageContext = {
  page_title: null,
  page_url: null,
  selected_text: null,
  enabled: false
};

// DOM Elements
const statusIndicator = document.getElementById("backendStatus");
const statusText = document.getElementById("statusText");
const alertBox = document.getElementById("alertBox");

// Stage views
const stages = {
  input: document.getElementById("stage-input"),
  context: document.getElementById("stage-context"),
  graph: document.getElementById("stage-graph"),
  optimize: document.getElementById("stage-optimize"),
  prompt: document.getElementById("stage-prompt")
};

// Nav steps
const stepTabs = {
  1: document.getElementById("step1-tab"),
  2: document.getElementById("step2-tab"),
  3: document.getElementById("step3-tab"),
  4: document.getElementById("step4-tab"),
  5: document.getElementById("step5-tab")
};

// Inputs & Buttons
const projectName = document.getElementById("projectName");
const inputRequirement = document.getElementById("inputRequirement");
const enableWebContext = document.getElementById("enableWebContext");
const webContextPreview = document.getElementById("webContextPreview");

const btnGenerateContext = document.getElementById("btnGenerateContext");
const btnBackToInput = document.getElementById("btnBackToInput");
const btnViewGraph = document.getElementById("btnViewGraph");
const btnApproveContext = document.getElementById("btnApproveContext");

const btnBackToContext = document.getElementById("btnBackToContext");
const btnProceedToOptimize = document.getElementById("btnProceedToOptimize");
const btnQueryContext = document.getElementById("btnQueryContext");
const queryItemId = document.getElementById("queryItemId");
const queryResultsBox = document.getElementById("queryResultsBox");

const btnBackToGraph = document.getElementById("btnBackToGraph");
const btnViewFinalPrompt = document.getElementById("btnViewFinalPrompt");

const btnCopyPrompt = document.getElementById("btnCopyPrompt");
const btnApprovePrompt = document.getElementById("btnApprovePrompt");
const btnRestart = document.getElementById("btnRestart");
const finalPromptText = document.getElementById("finalPromptText");

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
  checkBackendHealth();
  setupEventListeners();
  setupSpecTabs();
});

function showAlert(message, type = "info") {
  alertBox.textContent = message;
  alertBox.className = `alert-box ${type}`;
  alertBox.classList.remove("hidden");
  setTimeout(() => {
    alertBox.classList.add("hidden");
  }, 4000);
}

async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      const data = await res.json();
      statusIndicator.className = "status-indicator online";
      statusText.textContent = `Online (${data.llm_provider})`;
    } else {
      throw new Error();
    }
  } catch {
    statusIndicator.className = "status-indicator offline";
    statusText.textContent = "Offline";
  }
}

function setStage(stageKey, stepNum) {
  Object.values(stages).forEach(el => el.classList.remove("active"));
  Object.values(stepTabs).forEach(el => el.classList.remove("active"));

  if (stages[stageKey]) stages[stageKey].classList.add("active");
  if (stepTabs[stepNum]) stepTabs[stepNum].classList.add("active");
}

function setupEventListeners() {
  // Toggle webpage context
  enableWebContext.addEventListener("change", async (e) => {
    webpageContext.enabled = e.target.checked;
    if (e.target.checked) {
      await fetchActiveTabContext();
      webContextPreview.classList.remove("hidden");
    } else {
      webContextPreview.classList.add("hidden");
      webpageContext.page_title = null;
      webpageContext.page_url = null;
      webpageContext.selected_text = null;
    }
  });

  // Stage 1 -> 2
  btnGenerateContext.addEventListener("click", handleGenerateContext);

  // Stage 2 Navigation
  btnBackToInput.addEventListener("click", () => setStage("input", 1));
  btnViewGraph.addEventListener("click", () => {
    renderGraphView();
    setStage("graph", 3);
  });
  btnApproveContext.addEventListener("click", handleApproveAndOptimize);

  // Stage 3 Navigation
  btnBackToContext.addEventListener("click", () => setStage("context", 2));
  btnProceedToOptimize.addEventListener("click", handleApproveAndOptimize);
  btnQueryContext.addEventListener("click", handleQueryContext);

  // Stage 4 Navigation
  btnBackToGraph.addEventListener("click", () => setStage("graph", 3));
  btnViewFinalPrompt.addEventListener("click", () => setStage("prompt", 5));

  // Stage 5 Actions
  btnCopyPrompt.addEventListener("click", () => {
    if (!finalPromptText.value) return;
    navigator.clipboard.writeText(finalPromptText.value).then(() => {
      const copyText = document.getElementById("copyBtnText");
      const prevText = copyText.textContent;
      copyText.textContent = "Copied to Clipboard!";
      showAlert("Prompt copied to clipboard!", "info");
      setTimeout(() => {
        copyText.textContent = prevText;
      }, 2000);
    });
  });

  btnApprovePrompt.addEventListener("click", async () => {
    if (!currentProjectId) return;
    try {
      await fetch(`${API_BASE}/projects/${currentProjectId}/prompt/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved: true, edited_prompt: finalPromptText.value })
      });
      showAlert("Final prompt approved and ready for external agents!", "info");
    } catch (err) {
      showAlert(`Error: ${err.message}`, "error");
    }
  });

  btnRestart.addEventListener("click", () => {
    inputRequirement.value = "";
    currentProjectId = null;
    currentContext = null;
    currentOptimization = null;
    finalPromptText.value = "";
    setStage("input", 1);
  });
}

function setupSpecTabs() {
  const tabs = document.querySelectorAll(".spec-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });
}

async function fetchActiveTabContext() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id) return;

    webpageContext.page_title = tab.title || "Active Page";
    webpageContext.page_url = tab.url || "";

    document.getElementById("ctxTitle").textContent = tab.title || "N/A";
    document.getElementById("ctxUrl").textContent = tab.url || "N/A";

    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => window.getSelection().toString()
      });
      if (results && results[0] && results[0].result) {
        webpageContext.selected_text = results[0].result.trim();
        document.getElementById("ctxSelection").textContent =
          webpageContext.selected_text.slice(0, 80) + (webpageContext.selected_text.length > 80 ? "..." : "");
      }
    } catch {
      document.getElementById("ctxSelection").textContent = "None (or restricted page)";
    }
  } catch (err) {
    console.warn("Context fetch error:", err);
  }
}

function setButtonLoading(btn, loading) {
  const text = btn.querySelector(".btn-text");
  const spinner = btn.querySelector(".spinner");
  btn.disabled = loading;
  if (loading) {
    if (text) text.classList.add("hidden");
    if (spinner) spinner.classList.remove("hidden");
  } else {
    if (text) text.classList.remove("hidden");
    if (spinner) spinner.classList.add("hidden");
  }
}

async function handleGenerateContext() {
  const prompt = inputRequirement.value.trim();
  if (prompt.length < 5) {
    showAlert("Please enter a requirement of at least 5 characters.", "error");
    return;
  }

  setButtonLoading(btnGenerateContext, true);

  try {
    // 1. Create Project
    const createRes = await fetch(`${API_BASE}/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        original_prompt: prompt,
        project_name: projectName.value || "Website Generation Project",
        context: webpageContext.enabled ? webpageContext : null
      })
    });

    if (!createRes.ok) {
      throw new Error(`Failed to create project (${createRes.status})`);
    }

    const project = await createRes.json();
    currentProjectId = project.project_id;
    document.getElementById("projectIdBadge").textContent = `ID: ${currentProjectId}`;

    // 2. Generate Structured Context
    const genRes = await fetch(`${API_BASE}/projects/${currentProjectId}/context/generate`, { method: "POST" });
    const genProject = await genRes.json();

    currentContext = genProject.context_representation;
    renderStructuredContext(currentContext);
    setStage("context", 2);
    showAlert("Structured context generated & stored in memory!", "info");
  } catch (err) {
    showAlert(`Error: ${err.message}`, "error");
  } finally {
    setButtonLoading(btnGenerateContext, false);
  }
}

function renderStructuredContext(ctx) {
  if (!ctx) return;

  // Requirements
  const reqListEl = document.getElementById("requirementsList");
  reqListEl.innerHTML = "";
  document.getElementById("reqCount").textContent = ctx.requirements ? ctx.requirements.length : 0;

  if (ctx.requirements) {
    ctx.requirements.forEach(req => {
      const card = document.createElement("div");
      card.className = "req-item-card";
      card.innerHTML = `
        <div class="req-item-header">
          <span class="req-title">${req.id}: ${escapeHtml(req.title)}</span>
          <div>
            <span class="source-chip">${escapeHtml(req.source || 'USER')}</span>
            <span class="priority-chip priority-${(req.priority || 'medium').toLowerCase()}">${req.priority}</span>
          </div>
        </div>
        <p class="req-desc">${escapeHtml(req.description)}</p>
      `;
      reqListEl.appendChild(card);
    });
  }

  // Pages & Components
  const pagesListEl = document.getElementById("pagesList");
  pagesListEl.innerHTML = "";
  if (ctx.pages) {
    ctx.pages.forEach(p => {
      const div = document.createElement("div");
      div.className = "compact-item";
      div.innerHTML = `<strong>${escapeHtml(p.name)}</strong> (${escapeHtml(p.path)}) - ${p.sections.length} sections`;
      pagesListEl.appendChild(div);
    });
  }

  const componentsListEl = document.getElementById("componentsList");
  componentsListEl.innerHTML = "";
  if (ctx.components) {
    ctx.components.forEach(c => {
      const div = document.createElement("div");
      div.className = "compact-item";
      div.innerHTML = `<strong>${escapeHtml(c.name)}</strong> [${escapeHtml(c.type)}]`;
      componentsListEl.appendChild(div);
    });
  }

  const apisListEl = document.getElementById("apisList");
  apisListEl.innerHTML = "";
  if (ctx.apis) {
    ctx.apis.forEach(a => {
      const div = document.createElement("div");
      div.className = "compact-item";
      div.innerHTML = `<code>${escapeHtml(a.method)} ${escapeHtml(a.endpoint)}</code> - ${escapeHtml(a.description)}`;
      apisListEl.appendChild(div);
    });
  }

  // Design & Tech
  if (ctx.design) {
    document.getElementById("designStyle").textContent = ctx.design.visual_style || "-";
    document.getElementById("designColor").textContent = ctx.design.color_direction || "-";
    document.getElementById("designType").textContent = ctx.design.typography || "-";
  }

  if (ctx.technical) {
    document.getElementById("techFrontend").textContent = ctx.technical.frontend || "-";
    document.getElementById("techSecurity").textContent = ctx.technical.security || "-";
    document.getElementById("techA11y").textContent = ctx.technical.accessibility || "-";
  }

  // Assumptions
  const assumptionsListEl = document.getElementById("assumptionsList");
  assumptionsListEl.innerHTML = "";
  if (ctx.assumptions) {
    ctx.assumptions.forEach(item => {
      const li = document.createElement("li");
      li.textContent = typeof item === "string" ? item : `${item.id}: ${item.text}`;
      assumptionsListEl.appendChild(li);
    });
  }

  // Unknowns
  const unknownsListEl = document.getElementById("unknownsList");
  unknownsListEl.innerHTML = "";
  if (ctx.unknowns) {
    ctx.unknowns.forEach(item => {
      const li = document.createElement("li");
      li.textContent = typeof item === "string" ? item : `${item.id}: ${item.text}`;
      unknownsListEl.appendChild(li);
    });
  }
}

function renderGraphView() {
  const container = document.getElementById("graphFlowView");
  container.innerHTML = "";

  if (!currentContext) return;

  if (currentContext.requirements) {
    currentContext.requirements.forEach(req => {
      const relatedPages = currentContext.pages ? currentContext.pages.filter(p => p.requirements.includes(req.id)).map(p => p.id) : [];
      const relatedComps = currentContext.components ? currentContext.components.filter(c => c.requirements.includes(req.id)).map(c => c.id) : [];
      const relatedApis = currentContext.apis ? currentContext.apis.filter(a => a.requirements.includes(req.id)).map(a => a.id) : [];

      const pageStr = relatedPages.length ? ` &rarr; <span class="color-page">${relatedPages.join(", ")}</span>` : "";
      const compStr = relatedComps.length ? ` &rarr; <span class="color-comp">${relatedComps.join(", ")}</span>` : "";
      const apiStr = relatedApis.length ? ` &rarr; <span class="color-api">${relatedApis.join(", ")}</span>` : "";

      const div = document.createElement("div");
      div.className = "graph-chain-item";
      div.innerHTML = `<span class="color-req">${req.id}</span>${pageStr}${compStr}${apiStr}`;
      container.appendChild(div);
    });
  }
}

async function handleQueryContext() {
  if (!currentProjectId) return;
  const qId = queryItemId.value.trim();
  if (!qId) return;

  try {
    const res = await fetch(`${API_BASE}/projects/${currentProjectId}/context/retrieve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_id: qId })
    });
    const data = await res.json();
    queryResultsBox.classList.remove("hidden");
    queryResultsBox.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    showAlert(`Query error: ${err.message}`, "error");
  }
}

async function handleApproveAndOptimize() {
  if (!currentProjectId) return;
  setButtonLoading(btnApproveContext, true);

  try {
    // 1. Human Approval Gate
    await fetch(`${API_BASE}/projects/${currentProjectId}/context/approve`, { method: "POST" });

    // 2. Optimization
    const optRes = await fetch(`${API_BASE}/projects/${currentProjectId}/context/optimize`, { method: "POST" });
    if (!optRes.ok) {
      throw new Error(`Optimization failed (${optRes.status})`);
    }

    const optProject = await optRes.json();
    currentOptimization = optProject.optimization_metrics;

    renderOptimizationMetrics(currentOptimization);
    finalPromptText.value = optProject.final_prompt || "";

    setStage("optimize", 4);
    showAlert("Context successfully optimized!", "info");
  } catch (err) {
    showAlert(`Error: ${err.message}`, "error");
  } finally {
    setButtonLoading(btnApproveContext, false);
  }
}

function renderOptimizationMetrics(m) {
  if (!m) return;

  document.getElementById("metricOrigTokens").textContent = m.original_tokens.toLocaleString();
  document.getElementById("metricOptTokens").textContent = m.optimized_tokens.toLocaleString();
  document.getElementById("metricReduction").textContent = `${m.token_reduction_percentage}%`;
  document.getElementById("metricCoverage").textContent = `${m.requirement_coverage_percentage}%`;

  document.getElementById("metricTokensSaved").textContent = `${m.tokens_saved.toLocaleString()} tokens`;
  document.getElementById("metricCriticalCoverage").textContent =
    `${m.critical_requirements_preserved} / ${m.critical_requirements_total} (${m.critical_coverage_percentage}%)`;
  document.getElementById("metricPrunedCount").textContent =
    `${m.pruning_summary ? m.pruning_summary.pruned_count : 0} items`;

  const prunedBox = document.getElementById("prunedItemsList");
  if (m.pruning_summary && m.pruning_summary.pruned_items) {
    prunedBox.innerHTML = `Pruned IDs: [${m.pruning_summary.pruned_items.join(", ") || "None"}]<br>Compressed IDs: [${m.pruning_summary.compressed_items.join(", ") || "None"}]`;
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
