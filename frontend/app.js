const DEFAULT_MACHINE_STATE = {
  cpu: "N/A",
  gpu: "N/A",
  ram: "N/A",
  storage: "N/A",
  motherboard: "N/A",
};

const DEFAULT_DIAGNOSTICS = ["N/A"];

const DEFAULT_ROUTE = [
  { step: "N/A", action: "N/A", impact: "N/A" },
];

const initialState = {
  machine: structuredClone(DEFAULT_MACHINE_STATE),
  diagnostics: structuredClone(DEFAULT_DIAGNOSTICS),
  route: structuredClone(DEFAULT_ROUTE),
  catalog: [],
};

const STORAGE_KEYS = {
  apiBase:       "evoluipc.apiBase",
  engineApiBase: "evoluipc.engineApiBase",
  token:         "evoluipc.token",
};

// URLs fixas dos serviços no Render
const BACKEND_URL = "https://evoluipc-django.onrender.com";
const ENGINE_URL  = "https://evoluipc-engine.onrender.com";

function getDefaultApiBase()       { return BACKEND_URL; }
function getDefaultEngineApiBase() { return ENGINE_URL;  }

const state = structuredClone(initialState);

let catalogMeta = {
  provider:   "local",
  database:   "n/a",
  fetched_at: "",
  count:      0,
};

let autoFetchInterval = null;
let currentCatalogFilter = "all";


function startAutoFetch() {
  if (autoFetchInterval) return;
  
  autoFetchInterval = setInterval(async () => {
    if (state.machine.cpu === "N/A") {
      await fetchMachineFromApi(false);
      if (state.machine.cpu !== "N/A") {
        stopAutoFetch();
        setMessage("Setup detectado com sucesso!", "ok");
      }
    } else {
      stopAutoFetch();
    }
  }, 5000); 
}

function stopAutoFetch() {
  if (autoFetchInterval) {
    clearInterval(autoFetchInterval);
    autoFetchInterval = null;
  }
}

// localStorage seguro (não quebra em contextos bloqueados)

function safeStorageGet(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}
function safeStorageSet(key, value) {
  try { localStorage.setItem(key, value); } catch {}
}
function safeStorageRemove(key) {
  try { localStorage.removeItem(key); } catch {}
}

// Utilitários de URL e JSON

function sanitizeBaseUrl(url) {
  return String(url || "").replace(/\/+$/, "");
}

/**
 * Lê a resposta como texto e só faz JSON.parse se houver conteúdo.
 * Evita "Unexpected end of JSON input" em respostas vazias.
 */
async function parseJsonSafely(response) {
  const text = await response.text();
  if (!text || !text.trim()) return null;
  try {
    return JSON.parse(text);
  } catch (err) {
    console.error("[EvoluiPC] Resposta não é JSON válido:", text.slice(0, 300));
    throw new Error("A resposta da API não veio em JSON válido.");
  }
}

// Referências do DOM — autenticação

const authScreen     = document.getElementById("authScreen");
const dashboardScreen = document.getElementById("dashboardScreen");
const loginForm      = document.getElementById("loginForm");
const registerForm   = document.getElementById("registerForm");
const authUsername   = document.getElementById("authUsername");
const authPassword   = document.getElementById("authPassword");
const regUsername    = document.getElementById("regUsername");
const regEmail       = document.getElementById("regEmail");
const regPassword    = document.getElementById("regPassword");
const regPasswordConfirm = document.getElementById("regPasswordConfirm");
const authApiError   = document.getElementById("authApiError");
const authLoginMessage = document.getElementById("authLoginMessage");
const authRegError   = document.getElementById("authRegError");
const authRegMessage = document.getElementById("authRegMessage");

// Referências do DOM — dashboard

const metricGrid        = document.getElementById("metricGrid");
const diagnosticList    = document.getElementById("diagnosticList");
const routeList         = document.getElementById("upgradeRoute");
const catalogGrid       = document.getElementById("catalogGrid");
const catalogSourceInfo = document.getElementById("catalogSourceInfo");
const authTokenInput    = document.getElementById("authTokenInput");
const sessionTokenDisplay = document.getElementById("sessionToken");
const copyTokenBtn      = document.getElementById("copyTokenBtn");
const waitingBox        = document.getElementById("waitingBox");
const successBox        = document.getElementById("successBox");
const lastUpdate        = document.getElementById("lastUpdate");
const statusIndicator   = document.getElementById("statusIndicator");
const computerName      = document.getElementById("computerName");
const sessionInfo       = document.getElementById("sessionInfo");
const scanMessage       = document.getElementById("scanMessage");
const fetchMachineBtn   = document.getElementById("fetchMachineBtn");
const newSessionBtn     = document.getElementById("newSessionBtn");
const logoutTopbarBtn   = document.getElementById("logoutTopbarBtn");

// Alternância de telas

function showAuthScreen() {
  authScreen.classList.add("active");
  dashboardScreen.classList.remove("active");
}

function showDashboardScreen() {
  authScreen.classList.remove("active");
  dashboardScreen.classList.add("active");
  startAutoFetch();
}

// Geração de token de sessão para o Scanner

function generateSessionToken() {
  const alphabet = "abcdefghijklmnopqrstuvwxyz0123456789";
  let token = "evp_sess_";
  for (let i = 0; i < 32; i++) {
    token += alphabet.charAt(Math.floor(Math.random() * alphabet.length));
  }
  return token;
}

function initializeSetupFlow() {
  if (!sessionTokenDisplay || !copyTokenBtn || !authTokenInput) return;

  const authToken = getStoredToken();

  if (!authToken) {
    sessionTokenDisplay.textContent = "Faça login para gerar o token";
    authTokenInput.value = "";
    return;
  }

  sessionTokenDisplay.textContent = authToken;
  authTokenInput.value = authToken;

  copyTokenBtn.onclick = async () => {
    authTokenInput.value = authToken;

    try {
      await navigator.clipboard.writeText(authToken);
      copyTokenBtn.textContent = "✅ Copiado!";
    } catch {
      copyTokenBtn.textContent = "Token pronto";
    }

    if (waitingBox) waitingBox.style.display = "flex";
    if (successBox) successBox.style.display = "none";
    if (lastUpdate) lastUpdate.textContent = "Sincronizando...";
    if (statusIndicator) statusIndicator.textContent = "Aguardando resposta";

    setTimeout(() => fetchMachineFromApi(true), 1200);
    setTimeout(() => {
      copyTokenBtn.textContent = "📋 Copiar";
    }, 2000);
  };
}

// Renderização

function renderOverview() {
  metricGrid.innerHTML = "";

  const metricLabels = {
    motherboard: "PLACA-MÃE",
    ram_type:    "TIPO RAM",
    storage:     "ARMAZENAMENTO",
  };

  Object.entries(state.machine).forEach(([key, value]) => {
    if (key === "cpu_tier" || key === "gpu_tier" || key === "bottleneck" || key === "psu") return;
    const card = document.createElement("article");
    card.className = "metric-card";
    card.innerHTML = `
      <p class="metric-label">${metricLabels[key] || key.toUpperCase()}</p>
      <p class="metric-value">${value}</p>
    `;
    metricGrid.appendChild(card);
  });

  diagnosticList.innerHTML = "";
  const diags = state.diagnostics.length ? state.diagnostics : DEFAULT_DIAGNOSTICS;
  diags.forEach((item) => {
    if (item === "N/A" || !item) return;
    const li = document.createElement("li");
    li.className = "diagnostic-item";
    
    let icon = "⚙️";
    let typeClass = "info";
    
    const lowerItem = item.toLowerCase();
    if (lowerItem.includes("gargalo") || lowerItem.includes("alto") || lowerItem.includes("atenção") || lowerItem.includes("limitando") || lowerItem.includes("warning") || lowerItem.includes("⚠️") || lowerItem.includes("antigo") || lowerItem.includes("atraso")) {
      icon = "⚠️";
      typeClass = "warning";
    } else if (lowerItem.includes("bom") || lowerItem.includes("suficiente") || lowerItem.includes("ok") || lowerItem.includes("sucesso") || lowerItem.includes("ótimo") || lowerItem.includes("ótima") || lowerItem.includes("compatível") || lowerItem.includes("excelente")) {
      icon = "✅";
      typeClass = "success";
    }
    
    li.innerHTML = `<span class="diag-icon">${icon}</span> <span class="diag-text">${item}</span>`;
    li.classList.add(typeClass);
    diagnosticList.appendChild(li);
  });
}

function renderRoute() {
  routeList.innerHTML = "";
  const route = state.route.length ? state.route : DEFAULT_ROUTE;
  route.forEach((entry) => {
    const li = document.createElement("li");
    li.className = "route-item";
    li.innerHTML = `<strong>${entry.step}: ${entry.action}</strong><span>${entry.impact}</span>`;
    routeList.appendChild(li);
  });
}

function formatBRL(price) {
  if (price === undefined || price === null || price === "Preço indisponível" || price === "N/A" || price === 0) {
    return "Preço indisponível";
  }
  
  let str = String(price).trim();
  
  // Remove "R$" se houver
  str = str.replace(/R\$\s*/g, "");
  
  // Se tiver um ponto seguido de 1 ou 2 dígitos no final da primeira parte antes da vírgula
  // Ex: "99.97,00"
  if (str.includes(".") && str.includes(",")) {
    const parts = str.split(",");
    const beforeComma = parts[0]; // "99.97" ou "1.250"
    const afterComma = parts[1];  // "00"
    
    // Procura o ponto final em beforeComma
    const dotIndex = beforeComma.lastIndexOf(".");
    const digitsAfterDot = beforeComma.length - 1 - dotIndex;
    
    if (digitsAfterDot === 2 || digitsAfterDot === 1) {
      // É decimal! Ignora o ",00" posterior e trata parts[0] como o número real
      str = beforeComma;
    } else {
      // É milhar! Ex: "1.250,00" -> remove ponto do milhar e troca virgula por ponto
      str = beforeComma.replace(/\./g, "") + "." + afterComma;
    }
  } else if (str.includes(",")) {
    // Se só tem vírgula: "99,87" -> troca por ponto
    str = str.replace(/\./g, "").replace(",", ".");
  }
  
  const num = parseFloat(str);
  if (!isNaN(num)) {
    return num.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }
  return String(price);
}

function classifyItem(item) {
  const name = (item.name || "").toLowerCase();
  const tag = (item.tag || "").toLowerCase();
  
  if (name.includes("ryzen") || name.includes("core") || name.includes("intel") || name.includes("amd ryzen") || name.includes("i3-") || name.includes("i5-") || name.includes("i7-") || name.includes("i9-") || tag.includes("cpu") || tag.includes("processador")) {
    return { id: "cpu", label: "Processador", icon: "🖥️", color: "#3b82f6" };
  }
  if (name.includes("rtx") || name.includes("gtx") || name.includes("rx ") || name.includes("radeon") || name.includes("geforce") || name.includes("placa de video") || name.includes("placa de vídeo") || tag.includes("gpu") || tag.includes("placa de video") || tag.includes("video")) {
    return { id: "gpu", label: "Placa de Vídeo", icon: "🎮", color: "#10b981" };
  }
  if (name.includes("prime") || name.includes("b550") || name.includes("a320") || name.includes("b650") || name.includes("h610") || name.includes("b660") || name.includes("z790") || name.includes("placa-mãe") || name.includes("placa mae") || name.includes("motherboard") || tag.includes("placa-mãe") || tag.includes("placa mae") || tag.includes("mobo") || tag.includes("motherboard")) {
    return { id: "motherboard", label: "Placa-mãe", icon: "🔌", color: "#f59e0b" };
  }
  if (name.includes("ram") || name.includes("ddr") || name.includes("memoria") || name.includes("memória") || tag.includes("ram") || tag.includes("memória") || tag.includes("memoria")) {
    return { id: "ram", label: "Memória RAM", icon: "⚡", color: "#a855f7" };
  }
  if (name.includes("fonte") || name.includes("corsair") || name.includes("watts") || name.includes(" psu") || name.includes("bronze") || name.includes("gold") || tag.includes("fonte") || tag.includes("psu") || tag.includes("power")) {
    return { id: "psu", label: "Fonte", icon: "🔋", color: "#6366f1" };
  }
  if (name.includes("ssd") || name.includes("hd ") || name.includes("hd") || name.includes("disco rigido") || name.includes("disco rígido") || name.includes("kingston") || name.includes("crucial") || name.includes("samsung evo") || name.includes("nvme") || name.includes("sata") || name.includes("armazenamento") || tag.includes("storage") || tag.includes("armazenamento") || tag.includes("ssd") || tag.includes("hd")) {
    return { id: "storage", label: "HD / SSD", icon: "💾", color: "#ec4899" };
  }
  return { id: "other", label: "Componente", icon: "⚙️", color: "#64748b" };
}

function renderCatalog() {
  catalogGrid.innerHTML = "";

  const filteredCatalog = state.catalog.filter(item => {
    if (currentCatalogFilter === "all") return true;
    const cat = classifyItem(item);
    return cat.id === currentCatalogFilter;
  });

  if (!filteredCatalog.length) {
    const card = document.createElement("article");
    card.className = "catalog-card";
    card.style.gridColumn = "1/-1";
    card.style.textAlign = "center";
    card.style.padding = "40px";
    card.innerHTML = `
      <span class="catalog-badge fallback">Sem itens</span>
      <h3 style="margin-top: 12px; color: var(--ink);">Nenhum componente encontrado</h3>
      <p style="color: var(--ink-soft); font-size: 0.9rem;">Não encontramos itens desta categoria no seu catálogo de recomendações.</p>
    `;
    catalogGrid.appendChild(card);
    return;
  }

  filteredCatalog.forEach((item) => {
    const card = document.createElement("article");
    card.className = "catalog-card";
    const isNeo4j = item.origin === "neo4j";
    const cat = classifyItem(item);
    
    card.style.display = "flex";
    card.style.flexDirection = "column";
    card.style.justifyContent = "space-between";
    card.style.gap = "14px";
    
    card.innerHTML = `
      <div>
        <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 6px;">
          <span class="catalog-category-badge" style="background: ${cat.color}15; color: ${cat.color}; border: 1px solid ${cat.color}30; padding: 3px 8px; border-radius: 8px; font-size: 0.72rem; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;">
            <span class="catalog-category-icon">${cat.icon}</span> ${cat.label}
          </span>
        </div>
        <h3 style="margin: 8px 0 4px 0; font-size: 1.05rem; font-weight: 700; line-height: 1.4; color: var(--ink);">${item.name || "N/A"}</h3>
        <p style="margin: 0; color: var(--ink-soft); font-size: 0.85rem;">${item.tag || "Sem tag"}</p>
      </div>
      <div>
        <p class="catalog-meta" style="margin: 12px 0 0 0; font-weight: 700; color: var(--accent); font-size: 1.05rem;">${formatBRL(item.price)}</p>
        <p style="margin: 2px 0 12px 0; font-size: 0.72rem; color: var(--ink-soft); font-family: monospace;">Fonte: ${item.source || "N/A"}</p>
        ${item.name ? `<button class="primary-btn" onclick="abrirModalOfertas('${item.name.replace(/'/g, "\\'")}')" style="width:100%;font-size:0.82rem;padding:8px 12px;border-radius:10px;cursor:pointer; font-weight: 700;">🛒 Comparar Ofertas</button>` : ""}
      </div>
    `;
    catalogGrid.appendChild(card);
  });
}

function applyPayload(payload) {
  if (
    payload.machine    === undefined ||
    payload.diagnostics === undefined ||
    payload.route      === undefined ||
    payload.catalog    === undefined
  ) {
    throw new Error("Payload incompleto. Esperado: machine, diagnostics, route e catalog.");
  }

  state.machine     = Object.keys(payload.machine).length    ? payload.machine    : structuredClone(DEFAULT_MACHINE_STATE);
  state.diagnostics = payload.diagnostics.length             ? payload.diagnostics : structuredClone(DEFAULT_DIAGNOSTICS);
  state.route       = payload.route.length                   ? payload.route      : structuredClone(DEFAULT_ROUTE);
  state.catalog     = payload.catalog;

  renderOverview();
  renderRoute();
  renderCatalog();
  saveAppState();
}

// Mensagens de UI

function setMessage(text, type) {
  if (!scanMessage) return;
  scanMessage.hidden    = false;
  scanMessage.textContent = text;
  scanMessage.className = `message ${type}`;
}

function setSessionInfo(text) {
  if (!sessionInfo) return;
  sessionInfo.hidden    = false;
  sessionInfo.textContent = text;
}

function setCatalogSourceInfo(text, status = "") {
  if (!catalogSourceInfo) return;
  catalogSourceInfo.textContent = text;
  catalogSourceInfo.classList.remove("source-info-ok", "source-info-error");
  if (status === "ok")    catalogSourceInfo.classList.add("source-info-ok");
  if (status === "error") catalogSourceInfo.classList.add("source-info-error");
}

// Sessão e armazenamento

function getStoredToken()          { return safeStorageGet(STORAGE_KEYS.token); }
function getStoredApiBase()        { return safeStorageGet(STORAGE_KEYS.apiBase)       || getDefaultApiBase(); }
function getStoredEngineApiBase()  { return safeStorageGet(STORAGE_KEYS.engineApiBase) || getDefaultEngineApiBase(); }

function saveAuthSession(token) {
  safeStorageSet(STORAGE_KEYS.token, String(token || "").trim());
  if (!safeStorageGet(STORAGE_KEYS.engineApiBase)) {
    safeStorageSet(STORAGE_KEYS.engineApiBase, getDefaultEngineApiBase());
  }
  if (!safeStorageGet(STORAGE_KEYS.apiBase)) {
    safeStorageSet(STORAGE_KEYS.apiBase, getDefaultApiBase());
  }
}

function clearAuthSession() {
  safeStorageRemove(STORAGE_KEYS.token);
  safeStorageRemove(STORAGE_KEYS.apiBase);
  safeStorageRemove(STORAGE_KEYS.engineApiBase);
}

function saveApiBases(djangoBase, engineBase) {
  safeStorageSet(STORAGE_KEYS.apiBase,       String(djangoBase  || "").trim());
  safeStorageSet(STORAGE_KEYS.engineApiBase, String(engineBase  || "").trim());
}

// Expõe saveApiBases no escopo window para garantir acessibilidade
window.saveApiBases = saveApiBases;

function getAppStateStorageKey() { return "evoluipc.appState"; }
function saveAppState()          {}
function loadAppState()          { return false; }

// Detecção de erros

function isNetworkFetchError(error) {
  const m = String(error?.message || "").toLowerCase();
  return (
    m.includes("failed to fetch") ||
    m.includes("networkerror")    ||
    m.includes("load failed")     ||
    m.includes("network request failed")
  );
}

function isUnauthorizedError(error) {
  const m = String(error?.message || "").toLowerCase();
  return (
    m.includes("falha 401")    ||
    m.includes("status 401")   ||
    m.includes("unauthorized") ||
    m.includes("falha 403")    ||
    m.includes("status 403")   ||
    m.includes("forbidden")
  );
}

// Mensagens de autenticação

function clearAuthMessages() {
  [authApiError, authLoginMessage, authRegError, authRegMessage].forEach((el) => {
    el.textContent = "";
    el.classList.remove("show");
  });
}

function showAuthError(message, isRegister = false) {
  const el = isRegister ? authRegError : authApiError;
  el.textContent = message;
  el.classList.add("show");
}

function showAuthSuccess(message, isRegister = false) {
  const el = isRegister ? authRegMessage : authLoginMessage;
  el.textContent = message;
  el.classList.add("show");
}

// Validação de campos

function getFieldErrorElement(input) {
  let el = input.parentElement.querySelector(".field-error");
  if (!el) {
    el = document.createElement("p");
    el.className = "field-error";
    input.parentElement.appendChild(el);
  }
  return el;
}

function setFieldValidationState(input, message, forceShow = false) {
  const fieldError = getFieldErrorElement(input);
  const hasValue   = input.value.trim().length > 0;
  const touched    = input.dataset.touched === "true";
  const show       = forceShow || touched || hasValue;

  input.classList.remove("is-valid", "is-invalid");
  fieldError.textContent = "";
  fieldError.classList.remove("show");

  if (!show) { input.removeAttribute("aria-invalid"); return !message; }

  if (message) {
    input.classList.add("is-invalid");
    input.setAttribute("aria-invalid", "true");
    fieldError.textContent = message;
    fieldError.classList.add("show");
    return false;
  }

  input.classList.add("is-valid");
  input.setAttribute("aria-invalid", "false");
  return true;
}

function validateLoginUsername(f = false) {
  const v = authUsername.value.trim();
  let msg = "";
  if (!v)          msg = "Informe seu usuário.";
  else if (v.length < 3) msg = "Usuário precisa ter pelo menos 3 caracteres.";
  return setFieldValidationState(authUsername, msg, f);
}

function validateLoginPassword(f = false) {
  const v = authPassword.value;
  let msg = "";
  if (!v)          msg = "Informe sua senha.";
  else if (v.length < 6) msg = "Senha precisa ter pelo menos 6 caracteres.";
  return setFieldValidationState(authPassword, msg, f);
}

function validateRegisterUsername(f = false) {
  const v = regUsername.value.trim();
  let msg = "";
  if (!v)          msg = "Escolha um usuário.";
  else if (v.length < 3) msg = "Usuário precisa ter pelo menos 3 caracteres.";
  return setFieldValidationState(regUsername, msg, f);
}

function validateRegisterEmail(f = false) {
  const v = regEmail.value.trim();
  let msg = "";
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!v)               msg = "Informe seu e-mail.";
  else if (!pattern.test(v)) msg = "E-mail inválido.";
  return setFieldValidationState(regEmail, msg, f);
}

function validateRegisterPassword(f = false) {
  const v = regPassword.value;
  let msg = "";
  if (!v)          msg = "Crie uma senha.";
  else if (v.length < 6) msg = "Senha precisa ter pelo menos 6 caracteres.";
  return setFieldValidationState(regPassword, msg, f);
}

function validateRegisterPasswordConfirm(f = false) {
  const v = regPasswordConfirm.value;
  let msg = "";
  if (!v)                    msg = "Confirme sua senha.";
  else if (v !== regPassword.value) msg = "As senhas não conferem.";
  return setFieldValidationState(regPasswordConfirm, msg, f);
}

function validateLoginForm(f = false) {
  return validateLoginUsername(f) & validateLoginPassword(f);
}

function validateRegisterForm(f = false) {
  return (
    validateRegisterUsername(f) &
    validateRegisterEmail(f)    &
    validateRegisterPassword(f) &
    validateRegisterPasswordConfirm(f)
  );
}

function clearFieldValidationStates() {
  [authUsername, authPassword, regUsername, regEmail, regPassword, regPasswordConfirm].forEach((input) => {
    input.classList.remove("is-valid", "is-invalid");
    input.removeAttribute("aria-invalid");
    input.dataset.touched = "false";
    const el = input.parentElement.querySelector(".field-error");
    if (el) { el.textContent = ""; el.classList.remove("show"); }
  });
}

function registerRealtimeValidation(input, validator) {
  input.addEventListener("input", () => {
    validator(false);
    if (input === regPassword) validateRegisterPasswordConfirm(false);
  });
  input.addEventListener("blur", () => {
    input.dataset.touched = "true";
    validator(true);
    if (input === regPassword) validateRegisterPasswordConfirm(true);
  });
}

// Requisições HTTP

async function apiRequest(path, token, method = "GET", payload = null, baseUrlOverride = null) {
  const baseUrl = sanitizeBaseUrl((baseUrlOverride || getStoredApiBase()).trim());
  const url     = `${baseUrl}${path}`;

  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Token ${token}`;

  console.log(`[EvoluiPC] ${method} ${url}`);

  const response = await fetch(url, {
    method,
    headers,
    body: payload ? JSON.stringify(payload) : null,
  });

  if (!response.ok) {
    const errBody = await response.text();
    throw new Error(`Falha ${response.status}. ${errBody}`);
  }

  return await parseJsonSafely(response);
}

async function fetchCatalogFromEngine(engineBase) {
  const url = `${sanitizeBaseUrl(engineBase)}/api/recommendations/me`;
  console.log("[EvoluiPC] Engine GET", url);

  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    const errBody = await response.text();
    throw new Error(`Engine falhou ${response.status}. ${errBody}`);
  }

  return await parseJsonSafely(response);
}

// Fluxo de autenticação

async function handleLogin(event) {
  event.preventDefault();
  clearAuthMessages();

  if (!validateLoginForm(true)) {
    showAuthError("Corrija os campos de login para continuar.");
    return;
  }

  const username = authUsername.value.trim();
  const password = authPassword.value;
  const loginBtn = loginForm.querySelector("button[type='submit']");
  loginBtn.disabled = true;

  try {
    const data = await apiRequest("/api/auth/login", null, "POST", { username, password });

    if (!data?.token) throw new Error("Login não retornou token. Verifique o backend.");

    saveAuthSession(data.token);
    initializeSetupFlow();
    showAuthSuccess(`Bem-vindo, ${data.user?.username || username}! Redirecionando...`);

    setTimeout(async () => {
      authPassword.value = "";
      await populateDashboardFromSession();
      showDashboardScreen();
      resetDashboardToNaState();
      fetchMachineFromApi();
    }, 1000);
  } catch (error) {
    if (isNetworkFetchError(error)) {
      showAuthError("Não foi possível conectar ao backend. Verifique se o servidor está rodando.");
      return;
    }
    showAuthError(error.message || "Falha no login. Verifique suas credenciais.");
  } finally {
    loginBtn.disabled = false;
  }
}

async function handleRegister(event) {
  event.preventDefault();
  clearAuthMessages();

  if (!validateRegisterForm(true)) {
    showAuthError("Corrija os campos de cadastro para continuar.", true);
    return;
  }

  const username = regUsername.value.trim();
  const email    = regEmail.value.trim();
  const password = regPassword.value;
  const registerBtn = registerForm.querySelector("button[type='submit']");
  registerBtn.disabled = true;

  try {
    const data = await apiRequest("/api/auth/register", null, "POST", { username, email, password });

    if (!data?.token) throw new Error("Cadastro não retornou token. Verifique o backend.");

    saveAuthSession(data.token);
    initializeSetupFlow();
    showAuthSuccess(`Conta criada com sucesso! Bem-vindo, ${data.user?.username || username}!`, true);

    setTimeout(async () => {
      regPassword.value = "";
      regPasswordConfirm.value = "";
      await populateDashboardFromSession();
      showDashboardScreen();
      resetDashboardToNaState();
      fetchMachineFromApi();
    }, 1000);
  } catch (error) {
    if (isNetworkFetchError(error)) {
      showAuthError("Não foi possível conectar ao backend.", true);
      return;
    }
    showAuthError(error.message || "Falha no cadastro.", true);
  } finally {
    registerBtn.disabled = false;
  }
}

async function populateDashboardFromSession() {
  const token = getStoredToken();
  authTokenInput.value = token || "";

  if (!token) { setSessionInfo("Sem sessão ativa."); return; }

  try {
    const me = await apiRequest("/api/auth/me", token);
    setSessionInfo(`Autenticado como ${me?.user?.username || "usuário"}.`);
  } catch {
    setSessionInfo("Sessão ativa, aguardando leitura do perfil.");
  }
}

function resetDashboardToNaState() {
  state.machine     = structuredClone(DEFAULT_MACHINE_STATE);
  state.diagnostics = structuredClone(DEFAULT_DIAGNOSTICS);
  state.route       = structuredClone(DEFAULT_ROUTE);
  renderOverview();
  renderRoute();
}

function handleLogout() {
  stopAutoFetch();
  safeStorageRemove("evoluipc.appState");
  clearAuthSession();
  clearAuthMessages();
  clearFieldValidationStates();

  authUsername.value       = "";
  authPassword.value       = "";
  regUsername.value        = "";
  regEmail.value           = "";
  regPassword.value        = "";
  regPasswordConfirm.value = "";
  authTokenInput.value     = "";

  showAuthScreen();
  setSessionInfo("Sessão encerrada.");
}

// Dados do dashboard

async function fetchMachineFromApi(isManual = true) {
  const token      = authTokenInput.value.trim();
  const djangoBase = sanitizeBaseUrl(getStoredApiBase().trim());
  const engineBase = sanitizeBaseUrl(getStoredEngineApiBase().trim());

  if (!token) {
    if (isManual) setMessage("Token de autenticação ausente.", "error");
    return;
  }

  // Salva as URLs da API com verificação segura
  try {
    if (typeof window.saveApiBases === 'function') {
      window.saveApiBases(djangoBase, engineBase);
    } else {
      safeStorageSet(STORAGE_KEYS.apiBase, String(djangoBase || "").trim());
      safeStorageSet(STORAGE_KEYS.engineApiBase, String(engineBase || "").trim());
    }
  } catch (e) {
    console.error("[EvoluiPC] Erro ao salvar URLs da API:", e);
  }
  
  if (isManual) {
    fetchMachineBtn.disabled = true;
    setMessage("Buscando dados no backend e no Engine Neo4j...", "ok");
  }

  try {
    const [machineData, routeData] = await Promise.all([
      apiRequest("/api/machine/me", token, "GET", null, djangoBase),
      apiRequest("/api/upgrade-route/me/", token, "GET", null, djangoBase),
    ]);

    let recommendationData;
    let catalogSource = "Engine Neo4j";

    try {
      recommendationData = await fetchCatalogFromEngine(engineBase);
      catalogMeta = recommendationData?.meta || {
        provider:   "neo4j",
        database:   "desconhecido",
        fetched_at: "",
        count:      (recommendationData?.catalog || []).length,
      };
      setCatalogSourceInfo(
        `Origem: Neo4j | DB: ${catalogMeta.database} | itens: ${catalogMeta.count}`,
        "ok"
      );
    } catch (engineError) {
      console.warn("[EvoluiPC] Engine indisponível, usando fallback Django.", engineError.message);
      recommendationData = await apiRequest("/api/recommendations/me/", token, "GET", null, djangoBase);
      catalogSource = "Django (fallback)";
      const fallbackCatalog = recommendationData?.catalog || recommendationData || [];
      fallbackCatalog.forEach((item) => { item.origin = "fallback"; });
      recommendationData = { catalog: fallbackCatalog };
      setCatalogSourceInfo(
        `Catálogo via Django (fallback). Motivo: ${engineError.message}`,
        "error"
      );
    }

    const payload = {
      machine:     machineData?.machine    || machineData    || {},
      diagnostics: machineData?.diagnostics || [],
      route:       routeData?.route        || routeData      || [],
      catalog:     recommendationData?.catalog || [],
    };

    applyPayload(payload);
    
    if (isManual) setMessage(`Dados carregados. Catálogo via ${catalogSource}.`, "ok");

    if (waitingBox)      waitingBox.style.display  = "none";
    if (successBox)      successBox.style.display  = "flex";
    if (statusIndicator) statusIndicator.textContent = "Sincronizado";
    if (lastUpdate) {
      lastUpdate.textContent = new Date().toLocaleString("pt-BR", {
        dateStyle: "short",
        timeStyle: "short",
      });
    }
    if (computerName) {
      computerName.textContent =
        machineData?.machine?.computer_name ||
        machineData?.machine?.hostname      ||
        "Setup ativo";
    }
  } catch (error) {
    if (isUnauthorizedError(error)) {
      stopAutoFetch();
      clearAuthSession();
      showAuthScreen();
      setMessage("Sessão expirada. Faça login novamente.", "error");
      return;
    }

    if (isNetworkFetchError(error)) {
      setCatalogSourceInfo("Catálogo: armazenamento local (sem conexão).", "error");
      setMessage("Backend indisponível. Sem dados de máquina no momento.", "error");
      return;
    }

    setMessage(error.message || "Erro ao consultar API.", "error");
    if (waitingBox) waitingBox.style.display = "flex";
    if (successBox) successBox.style.display = "none";
  } finally {
    fetchMachineBtn.disabled = false;
  }
}

async function syncCatalogFromEngineOnLoad() {
  const engineBase = sanitizeBaseUrl(getStoredEngineApiBase().trim());
  setCatalogSourceInfo(`Sincronizando catálogo com Engine...`, "");

  try {
    const data = await fetchCatalogFromEngine(engineBase);
    state.catalog = data?.catalog || data || [];
    catalogMeta = data?.meta || {
      provider:   "neo4j",
      database:   "desconhecido",
      fetched_at: "",
      count:      (data?.catalog || []).length,
    };
    renderCatalog();
    saveAppState();
    setCatalogSourceInfo(
      `Origem: Neo4j | DB: ${catalogMeta.database} | itens: ${catalogMeta.count}`,
      "ok"
    );
  } catch (error) {
    console.warn("[EvoluiPC] Engine indisponível no carregamento.", error.message);
    setCatalogSourceInfo(`Catálogo local (Engine indisponível). Motivo: ${error.message}`, "error");
  }
}

// Rota de upgrade (botão "Analisar meu setup")

async function carregarRotaUpgrade() {
  const btn         = document.getElementById("btn-upgrade");
  const resultadoDiv = document.getElementById("upgrade-resultado");

  btn.textContent       = "Consultando Banco de Grafos...";
  btn.disabled          = true;
  btn.style.backgroundColor = "#9e9e9e";

  try {
    const token = safeStorageGet("evoluipc.token");

    if (!token) {
      resultadoDiv.innerHTML  = `<p style="color:red;">Você precisa estar logado para ver recomendações.</p>`;
      resultadoDiv.style.display = "block";
      return;
    }

    const resposta = await fetch(
      `${BACKEND_URL}/api/upgrade-route/me/`,
      {
        method:  "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization:  `Token ${token}`,
        },
      }
    );

    if (!resposta.ok) throw new Error(`Erro na API: Status ${resposta.status}`);

    const dados = await parseJsonSafely(resposta);

    const lista = Array.isArray(dados) ? dados : (dados?.route || []);

    if (lista.length > 0) {
      const upgrade = lista[0];

      if (upgrade.recommendation) {
        const sourceLabel = upgrade.source === "neo4j" ? "🗄️ Base de Dados" : "📋 Recomendação Padrão";
        const sourceBgColor = upgrade.source === "neo4j" ? "#0d1b2a" : "#1a1410";
        const sourceBorderColor = upgrade.source === "neo4j" ? "#00d4ff" : "#ffa500";
        const sourceBadgeBg = upgrade.source === "neo4j" ? "#00d4ff" : "#ffa500";
        
        resultadoDiv.innerHTML = `
          <div style="background:${sourceBgColor};padding:24px;border-radius:12px;border-left:6px solid ${sourceBorderColor};box-shadow:0 2px 8px rgba(0,0,0,0.3);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
              <h3 style="margin:0;color:${sourceBorderColor};font-size:16px;">🔥 Upgrade Recomendado: ${upgrade.component || "Componente"}</h3>
              <span style="background:${sourceBadgeBg};color:#000;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:bold;">${sourceLabel}</span>
            </div>
            <h2 style="margin:16px 0 8px 0;font-size:28px;color:#ffffff;">${upgrade.recommendation}</h2>
            <p style="margin:8px 0;font-size:18px;color:#b0b0b0;"><strong>Investimento estimado:</strong> <span style="color:${sourceBorderColor};font-size:20px;font-weight:bold;">${formatBRL(upgrade.estimatedPrice)}</span></p>
            <p style="margin:12px 0;color:#a0a0a0;line-height:1.6;"><strong>Por que?</strong> ${upgrade.reason || "Sem justificativa disponível."}</p>
            ${upgrade.device_type ? `<p style="margin:8px 0;color:#808080;font-size:13px;">📱 Dispositivo: <strong style="color:${sourceBorderColor};">${upgrade.device_type}</strong></p>` : ""}
            ${upgrade.note ? `<p style="margin:8px 0;color:#ffcccc;font-size:13px;background:#332222;padding:8px 12px;border-radius:4px;border-left:3px solid #ff6b6b;">⚠️ ${upgrade.note}</p>` : ""}
            
            <div class="offers-section">
              <h4 class="offers-title">🛒 Melhores Preços Online (Tempo Real):</h4>
              <div id="upgradeOffersGrid" class="offers-grid">
                <div style="grid-column: 1/-1; color: var(--ink-soft); font-size: 0.9rem; padding: 12px 0;">
                  <span class="loader" style="width:16px;height:16px;display:inline-block;vertical-align:middle;margin-right:8px;border-width:2px;"></span>
                  Pesquisando ofertas nas lojas...
                </div>
              </div>
            </div>
          </div>`;

        // Async fetch for real-time offers
        const recName = upgrade.recommendation;
        setTimeout(async () => {
          try {
            const data = await fetchOffersForHardware(recName);
            const grid = document.getElementById("upgradeOffersGrid");
            if (grid) {
              renderOffersIntoContainer(grid, data?.offers || []);
            }
          } catch (err) {
            console.error("Erro ao carregar ofertas do upgrade recomendado:", err);
            const grid = document.getElementById("upgradeOffersGrid");
            if (grid) {
              grid.innerHTML = `<p style="color:var(--warn);font-size:0.9rem;grid-column:1/-1;">Falha ao carregar ofertas em tempo real.</p>`;
            }
          }
        }, 50);
      } else {
        const sourceLabel = upgrade.source === "neo4j" ? "🗄️ Base de Dados" : "📋 Recomendação Padrão";
        const sourceBgColor = upgrade.source === "neo4j" ? "#0d1b2a" : "#1a1410";
        const sourceBorderColor = upgrade.source === "neo4j" ? "#00d4ff" : "#ffa500";
        const sourceBadgeBg = upgrade.source === "neo4j" ? "#00d4ff" : "#ffa500";
        
        resultadoDiv.innerHTML = `
          <div style="background:${sourceBgColor};padding:24px;border-radius:12px;border-left:6px solid ${sourceBorderColor};box-shadow:0 2px 8px rgba(0,0,0,0.3);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
              <h3 style="margin:0;color:${sourceBorderColor};font-size:16px;">🔥 Próximo Upgrade</h3>
              <span style="background:${sourceBadgeBg};color:#000;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:bold;">${sourceLabel}</span>
            </div>
            <h2 style="margin:16px 0 8px 0;font-size:28px;color:#ffffff;">${upgrade.action || "N/A"}</h2>
            <p style="margin:8px 0;font-size:18px;color:#b0b0b0;"><strong>Etapa:</strong> <strong style="color:${sourceBorderColor};">${upgrade.step || "N/A"}</strong></p>
            <p style="margin:12px 0;color:#a0a0a0;line-height:1.6;"><strong>Impacto:</strong> ${upgrade.impact || "Sem impacto informado."}</p>
          </div>`;
      }
    } else {
      resultadoDiv.innerHTML = "<p>Nenhuma recomendação encontrada no momento.</p>";
    }

    resultadoDiv.style.display = "block";
  } catch (erro) {
    console.error("[EvoluiPC] Falha ao buscar upgrade:", erro);
    resultadoDiv.innerHTML     = `<p style="color:red;">Erro ao conectar com a API. Verifique o console (F12).</p>`;
    resultadoDiv.style.display = "block";
  } finally {
    btn.textContent            = "Analisar Meu Setup 🚀";
    btn.disabled               = false;
    btn.style.backgroundColor  = "#4CAF50";
  }
}

window.carregarRotaUpgrade = carregarRotaUpgrade;

// Navegação por abas

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b)   => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// Filtro do catálogo
document.querySelectorAll(".filter-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentCatalogFilter = btn.dataset.category;
    renderCatalog();
  });
});

document.querySelectorAll(".auth-tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    clearAuthMessages();
    clearFieldValidationStates();
    document.querySelectorAll(".auth-tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".auth-form").forEach((f)   => f.classList.remove("active"));
    btn.classList.add("active");
    document.querySelector(`.auth-form[data-form="${btn.dataset.tab}"]`).classList.add("active");
  });
});

// Registro de eventos

registerRealtimeValidation(authUsername,       validateLoginUsername);
registerRealtimeValidation(authPassword,       validateLoginPassword);
registerRealtimeValidation(regUsername,        validateRegisterUsername);
registerRealtimeValidation(regEmail,           validateRegisterEmail);
registerRealtimeValidation(regPassword,        validateRegisterPassword);
registerRealtimeValidation(regPasswordConfirm, validateRegisterPasswordConfirm);

loginForm.addEventListener("submit",    handleLogin);
registerForm.addEventListener("submit", handleRegister);
fetchMachineBtn.addEventListener("click", () => fetchMachineFromApi(true));
logoutTopbarBtn.addEventListener("click", handleLogout);

newSessionBtn.addEventListener("click", () => {
  applyPayload(structuredClone(initialState));
  saveAppState();
  setMessage("Sessão resetada para estado N/A.", "ok");
});

// Inicialização

async function initializeApp() {
  initializeSetupFlow();

  const token = getStoredToken();

  renderOverview();
  renderRoute();
  renderCatalog();
  setCatalogSourceInfo("Sincronizando catálogo com o Engine Neo4j...", "");

  if (token && !token.startsWith("local-")) {
    showDashboardScreen();
    setSessionInfo("Validando sessão salva...");
  } else {
    showAuthScreen();
  }

  syncCatalogFromEngineOnLoad();

  if (token) {
    if (token.startsWith("local-")) {
      clearAuthSession();
      setSessionInfo("Sessão local antiga removida. Faça login novamente.");
      showAuthScreen();
      return;
    }

    try {
      const me = await apiRequest("/api/auth/me", token);
      if (!me?.user?.username) throw new Error("Sessão inválida.");
    } catch (error) {
      if (isUnauthorizedError(error)) {
        clearAuthSession();
        setSessionInfo("Sessão expirada. Faça login novamente.");
        showAuthScreen();
        return;
      } else {
        setSessionInfo("Servidor reconectando... O painel será carregado temporariamente.");
        console.warn("Backend indisponível no F5, mas o token foi mantido.", error.message);
      }
    }

    await populateDashboardFromSession();
    resetDashboardToNaState();
    fetchMachineFromApi();
  }
}

initializeApp();


async function fetchOffersForHardware(name) {
  const token = getStoredToken();
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Token ${token}`;
  }
  
  const response = await fetch(
    `${BACKEND_URL}/api/hardware/offers?query=${encodeURIComponent(name)}`,
    {
      method: "GET",
      headers: headers,
    }
  );
  
  if (!response.ok) {
    throw new Error(`Erro status: ${response.status}`);
  }
  
  return await response.json();
}

function renderOffersIntoContainer(container, offers) {
  container.innerHTML = "";
  
  if (!offers || offers.length === 0) {
    container.innerHTML = `<p style="color:var(--ink-soft);grid-column: 1/-1;font-size:0.9rem;padding: 12px 0;">Nenhuma oferta encontrada para esta peça no momento.</p>`;
    return;
  }
  
  offers.forEach(offer => {
    const card = document.createElement("div");
    card.className = "offer-card";
    
    // Normalize class name for store badge
    let storeClass = (offer.store || "").toLowerCase().replace(/[^a-z0-9]/g, "");
    if (storeClass.includes("mercadolivre")) storeClass = "mercadolivre";
    if (storeClass.includes("amazon")) storeClass = "amazon";
    if (storeClass.includes("kabum")) storeClass = "kabum";
    if (storeClass.includes("pichau")) storeClass = "pichau";
    if (storeClass.includes("terabyte")) storeClass = "terabyteshop";
    
    const fallbackImage = "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=150&auto=format&fit=crop&q=60";
    const thumbUrl = offer.thumbnail || fallbackImage;
    
    const formattedPrice = typeof offer.price === "number" 
      ? offer.price.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
      : `R$ ${offer.price}`;
      
    const liveIndicator = offer.is_live 
      ? `<span class="offer-status-badge live">● LIVE</span>`
      : `<span class="offer-status-badge estimado">● ESTIMADO</span>`;
      
    card.innerHTML = `
      <div class="offer-header">
        <div class="offer-thumb-container">
          <img class="offer-thumb" src="${thumbUrl}" alt="Thumbnail" onerror="this.src='${fallbackImage}'" />
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex: 1;">
          <span class="offer-store-badge ${storeClass}">${offer.store}</span>
          ${liveIndicator}
        </div>
      </div>
      <h5 class="offer-title" title="${offer.title}">${offer.title}</h5>
      <div class="offer-price-container">
        <span class="offer-price">${formattedPrice}</span>
        <a href="${offer.link}" target="_blank" class="offer-buy-btn">Comprar ➔</a>
      </div>
    `;
    
    container.appendChild(card);
  });
}

async function abrirModalOfertas(name) {
  
  fecharModalOfertas();
  
  
  const modalOverlay = document.createElement("div");
  modalOverlay.className = "ep-modal-overlay";
  modalOverlay.id = "epOffersModal";
  
  modalOverlay.innerHTML = `
    <div class="ep-modal-container">
      <div class="ep-modal-header">
        <h3>Melhores Ofertas: ${name}</h3>
        <button class="ep-modal-close" onclick="fecharModalOfertas()">&times;</button>
      </div>
      <div class="ep-modal-body">
        <div id="modalOffersGrid" class="offers-grid">
          <div style="grid-column: 1/-1; text-align: center; color: var(--ink-soft); padding: 40px 0;">
            <div class="loader" style="margin: 0 auto 16px auto; border-width:2px; width:30px; height:30px;"></div>
            Buscando os melhores preços na internet...
          </div>
        </div>
      </div>
    </div>
  `;
  
  document.body.appendChild(modalOverlay);
  
  
  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
      fecharModalOfertas();
    }
  });
  
  try {
    const data = await fetchOffersForHardware(name);
    const grid = document.getElementById("modalOffersGrid");
    if (grid) {
      renderOffersIntoContainer(grid, data?.offers || []);
    }
  } catch (err) {
    console.error("Erro ao carregar ofertas no modal:", err);
    const grid = document.getElementById("modalOffersGrid");
    if (grid) {
      grid.innerHTML = `<p style="color:var(--warn);grid-column: 1/-1;text-align:center;padding:24px 0;">Erro ao carregar ofertas em tempo real. Tente novamente mais tarde.</p>`;
    }
  }
}

function fecharModalOfertas() {
  const modal = document.getElementById("epOffersModal");
  if (modal) {
    modal.remove();
  }
}


window.abrirModalOfertas = abrirModalOfertas;
window.fecharModalOfertas = fecharModalOfertas;