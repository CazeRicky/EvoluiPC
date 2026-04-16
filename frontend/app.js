// Estado inicial do app

const initialState = {
  machine: {
    cpu: "Intel Core i5-9500",
    gpu: "GTX 1050 Ti 4GB",
    ram: "8GB DDR4 2400 MHz",
    storage: "SSD SATA 240GB",
    motherboard: "H310M",
    psu: "430W White",
    bottleneck: "GPU",
  },
  diagnostics: [
    "CPU ainda atende tarefas gerais, mas limita alguns jogos competitivos.",
    "GPU e o gargalo principal para Full HD em presets medio.",
    "16GB RAM melhora significativamente a experiencia em multitarefa e jogos atuais, dando mais desempenho e folga para o sistema.",
  ],
  route: [
    {
      step: "Upgrade 1",
      action: "Trocar GPU para RX 6600 / RTX 3060 usada",
      impact: "+80% media em FPS 1080p",
    },
    {
      step: "Upgrade 2",
      action: "Subir RAM para 16GB (2x8)",
      impact: "Melhora estabilidade e tempo de resposta",
    },
    {
      step: "Upgrade 3",
      action: "SSD NVMe 1TB (se placa suportar)",
      impact: "Carregamento mais rapido e maior vida util",
    },
  ],
  catalog: [
    {
      name: "RX 6600 8GB",
      price: "R$ 1.249",
      source: "Marketplace parceiro",
      tag: "Melhor custo x FPS",
    },
    {
      name: "Kit RAM 16GB DDR4",
      price: "R$ 299",
      source: "Loja nacional",
      tag: "Upgrade imediato",
    },
    {
      name: "SSD NVMe 1TB Gen3",
      price: "R$ 359",
      source: "E-commerce",
      tag: "Sistema mais agil",
    },
  ],
};

const STORAGE_KEYS = {
  apiBase: "evoluipc.apiBase",
  engineApiBase: "evoluipc.engineApiBase",
  token: "evoluipc.token",
  email: "evoluipc.email",
  username: "evoluipc.username",
  appState: "evoluipc.appState",
};

const state = structuredClone(initialState);
let catalogMeta = {
  provider: "local",
  database: "n/a",
  fetched_at: "",
  count: state.catalog.length,
};

// Alterna entre login e dashboard

const authScreen = document.getElementById("authScreen");
const dashboardScreen = document.getElementById("dashboardScreen");

function showAuthScreen() {
  // Exibe tela de autenticação.
  authScreen.classList.add("active");
  dashboardScreen.classList.remove("active");
}

function showDashboardScreen() {
  // Exibe painel principal após login.
  authScreen.classList.remove("active");
  dashboardScreen.classList.add("active");
}

// Campos de autenticação

const authApiBase = document.getElementById("authApiBase");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const authUsername = document.getElementById("authUsername");
const authPassword = document.getElementById("authPassword");
const regUsername = document.getElementById("regUsername");
const regEmail = document.getElementById("regEmail");
const regPassword = document.getElementById("regPassword");
const regPasswordConfirm = document.getElementById("regPasswordConfirm");
const authApiError = document.getElementById("authApiError");
const authLoginMessage = document.getElementById("authLoginMessage");
const authRegError = document.getElementById("authRegError");
const authRegMessage = document.getElementById("authRegMessage");

// Campos do dashboard

const metricGrid = document.getElementById("metricGrid");
const diagnosticList = document.getElementById("diagnosticList");
const routeList = document.getElementById("upgradeRoute");
const catalogGrid = document.getElementById("catalogGrid");
const catalogSourceInfo = document.getElementById("catalogSourceInfo");
const apiBaseInput = document.getElementById("apiBaseInput");
const engineApiBaseInput = document.getElementById("engineApiBaseInput");
const emailInput = document.getElementById("emailInput");
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const authTokenInput = document.getElementById("authTokenInput");
const sessionInfo = document.getElementById("sessionInfo");
const scanMessage = document.getElementById("scanMessage");
const fetchMachineBtn = document.getElementById("fetchMachineBtn");
const newSessionBtn = document.getElementById("newSessionBtn");
const logoutTopbarBtn = document.getElementById("logoutTopbarBtn");

// Renderização principal

function renderOverview() {
  // Renderiza métricas e diagnóstico.
  metricGrid.innerHTML = "";
  Object.entries(state.machine).forEach(([key, value]) => {
    const card = document.createElement("article");
    card.className = "metric-card";
    card.innerHTML = `
      <p class="metric-label">${key.toUpperCase()}</p>
      <p class="metric-value">${value}</p>
    `;
    metricGrid.appendChild(card);
  });

  diagnosticList.innerHTML = "";
  state.diagnostics.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    diagnosticList.appendChild(li);
  });
}

function renderRoute() {
  // Renderiza rota de upgrades.
  routeList.innerHTML = "";
  state.route.forEach((entry) => {
    const li = document.createElement("li");
    li.className = "route-item";
    li.innerHTML = `<strong>${entry.step}: ${entry.action}</strong><span>${entry.impact}</span>`;
    routeList.appendChild(li);
  });
}

function renderCatalog() {
  // Renderiza catálogo recomendado.
  catalogGrid.innerHTML = "";
  state.catalog.forEach((item) => {
    const card = document.createElement("article");
    card.className = "catalog-card";
    const originLabel = item.origin === "neo4j" ? "Neo4j" : "Fallback";
    const originClass = item.origin === "neo4j" ? "catalog-badge neo4j" : "catalog-badge fallback";
    card.innerHTML = `
      <span class="${originClass}">${originLabel}</span>
      <h3>${item.name}</h3>
      <p>${item.tag}</p>
      <p class="catalog-meta">${item.price} · ${item.source}</p>
    `;
    catalogGrid.appendChild(card);
  });
}

function applyPayload(payload) {
  // Atualiza estado com dados recebidos.
  if (!payload.machine || !payload.diagnostics || !payload.route || !payload.catalog) {
    throw new Error("Payload incompleto. Esperado: machine, diagnostics, route e catalog.");
  }

  state.machine = payload.machine;
  state.diagnostics = payload.diagnostics;
  state.route = payload.route;
  state.catalog = payload.catalog;

  renderOverview();
  renderRoute();
  renderCatalog();
  saveAppState();
}

function setMessage(text, type) {
  // Exibe mensagens do painel.
  scanMessage.textContent = text;
  scanMessage.className = `message ${type}`;
}

function setSessionInfo(text) {
  // Exibe resumo da sessão atual.
  sessionInfo.textContent = text;
}

function setCatalogSourceInfo(text, status = "") {
  // Informa a origem atual do catálogo.
  if (!catalogSourceInfo) {
    return;
  }

  catalogSourceInfo.textContent = text;
  catalogSourceInfo.classList.remove("source-info-ok", "source-info-error");

  if (status === "ok") {
    catalogSourceInfo.classList.add("source-info-ok");
  }

  if (status === "error") {
    catalogSourceInfo.classList.add("source-info-error");
  }
}

async function fetchCatalogFromEngine(engineBase) {
  // Busca catálogo direto do Engine Neo4j.
  const response = await fetch(`${engineBase}/api/recommendations/me`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Engine falhou ${response.status}. ${errorBody}`);
  }

  return response.json();
}

// Utilitários de sessão

function sanitizeBaseUrl(url) {
  // Remove barra final da URL.
  return url.replace(/\/+$/, "");
}

function saveAuthSession(token, username, email, apiBase) {
  // Salva sessão autenticada localmente.
  localStorage.setItem(STORAGE_KEYS.token, token.trim());
  localStorage.setItem(STORAGE_KEYS.username, username.trim());
  localStorage.setItem(STORAGE_KEYS.email, email.trim());
  localStorage.setItem(STORAGE_KEYS.apiBase, apiBase.trim());

  if (!localStorage.getItem(STORAGE_KEYS.engineApiBase)) {
    localStorage.setItem(STORAGE_KEYS.engineApiBase, "http://127.0.0.1:8002");
  }
}

function clearAuthSession() {
  // Limpa dados de autenticação.
  localStorage.removeItem(STORAGE_KEYS.token);
  localStorage.removeItem(STORAGE_KEYS.username);
  localStorage.removeItem(STORAGE_KEYS.email);
  localStorage.removeItem(STORAGE_KEYS.apiBase);
}

function saveApiBases(djangoBase, engineBase) {
  // Salva bases de API usadas no painel.
  localStorage.setItem(STORAGE_KEYS.apiBase, djangoBase.trim());
  localStorage.setItem(STORAGE_KEYS.engineApiBase, engineBase.trim());
}

function saveAppState() {
  // Salva estado atual do app.
  localStorage.setItem(STORAGE_KEYS.appState, JSON.stringify(state));
}

function loadAppState() {
  // Carrega estado salvo do app.
  const rawState = localStorage.getItem(STORAGE_KEYS.appState);

  if (!rawState) {
    return false;
  }

  try {
    const parsedState = JSON.parse(rawState);

    if (!parsedState.machine || !parsedState.diagnostics || !parsedState.route || !parsedState.catalog) {
      return false;
    }

    state.machine = parsedState.machine;
    state.diagnostics = parsedState.diagnostics;
    state.route = parsedState.route;
    state.catalog = parsedState.catalog;
    return true;
  } catch {
    return false;
  }
}

function isNetworkFetchError(error) {
  // Detecta falhas de rede.
  const message = String(error?.message || "").toLowerCase();
  return message.includes("failed to fetch") || message.includes("networkerror") || message.includes("load failed");
}

function isUnauthorizedError(error) {
  // Detecta sessão inválida por 401.
  const message = String(error?.message || "").toLowerCase();
  return message.includes("falha 401") || message.includes("status 401") || message.includes("unauthorized");
}

function getStoredToken() {
  // Lê token salvo.
  return localStorage.getItem(STORAGE_KEYS.token);
}

function getStoredApiBase() {
  // Lê base da API salva.
  return localStorage.getItem(STORAGE_KEYS.apiBase) || "http://127.0.0.1:8000";
}

function getStoredEngineApiBase() {
  // Lê base do engine salva.
  return localStorage.getItem(STORAGE_KEYS.engineApiBase) || "http://127.0.0.1:8002";
}

// Mensagens de validação

function clearAuthMessages() {
  // Limpa mensagens de login/cadastro.
  authApiError.textContent = "";
  authApiError.classList.remove("show");
  authLoginMessage.textContent = "";
  authLoginMessage.classList.remove("show");
  authRegError.textContent = "";
  authRegError.classList.remove("show");
  authRegMessage.textContent = "";
  authRegMessage.classList.remove("show");
}

function showAuthError(message, isRegister = false) {
  // Exibe erro no formulário ativo.
  if (isRegister) {
    authRegError.textContent = message;
    authRegError.classList.add("show");
  } else {
    authApiError.textContent = message;
    authApiError.classList.add("show");
  }
}

function showAuthSuccess(message, isRegister = false) {
  // Exibe sucesso no formulário ativo.
  if (isRegister) {
    authRegMessage.textContent = message;
    authRegMessage.classList.add("show");
  } else {
    authLoginMessage.textContent = message;
    authLoginMessage.classList.add("show");
  }
}

function getFieldErrorElement(input) {
  // Garante container de erro por campo.
  let fieldError = input.parentElement.querySelector(".field-error");

  if (!fieldError) {
    fieldError = document.createElement("p");
    fieldError.className = "field-error";
    input.parentElement.appendChild(fieldError);
  }

  return fieldError;
}

function setFieldValidationState(input, message, forceShow = false) {
  // Define estado visual de validação.
  const fieldError = getFieldErrorElement(input);
  const hasValue = input.value.trim().length > 0;
  const touched = input.dataset.touched === "true";
  const shouldShowMessage = forceShow || touched || hasValue;

  input.classList.remove("is-valid", "is-invalid");
  fieldError.textContent = "";
  fieldError.classList.remove("show");

  if (!shouldShowMessage) {
    input.removeAttribute("aria-invalid");
    return !message;
  }

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

function validateLoginUsername(forceShow = false) {
  // Valida usuário do login.
  const value = authUsername.value.trim();
  let message = "";

  if (!value) {
    message = "Informe seu usuario.";
  } else if (value.length < 3) {
    message = "Usuario precisa ter pelo menos 3 caracteres.";
  }

  return setFieldValidationState(authUsername, message, forceShow);
}

function validateLoginPassword(forceShow = false) {
  // Valida senha do login.
  const value = authPassword.value;
  let message = "";

  if (!value) {
    message = "Informe sua senha.";
  } else if (value.length < 6) {
    message = "Senha precisa ter pelo menos 6 caracteres.";
  }

  return setFieldValidationState(authPassword, message, forceShow);
}

function validateRegisterUsername(forceShow = false) {
  // Valida usuário do cadastro.
  const value = regUsername.value.trim();
  let message = "";

  if (!value) {
    message = "Escolha um usuario.";
  } else if (value.length < 3) {
    message = "Usuario precisa ter pelo menos 3 caracteres.";
  }

  return setFieldValidationState(regUsername, message, forceShow);
}

function validateRegisterEmail(forceShow = false) {
  // Valida email do cadastro.
  const value = regEmail.value.trim();
  let message = "";
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!value) {
    message = "Informe seu email.";
  } else if (!emailPattern.test(value)) {
    message = "Email invalido.";
  }

  return setFieldValidationState(regEmail, message, forceShow);
}

function validateRegisterPassword(forceShow = false) {
  // Valida senha do cadastro.
  const value = regPassword.value;
  let message = "";

  if (!value) {
    message = "Crie uma senha.";
  } else if (value.length < 6) {
    message = "Senha precisa ter pelo menos 6 caracteres.";
  }

  return setFieldValidationState(regPassword, message, forceShow);
}

function validateRegisterPasswordConfirm(forceShow = false) {
  // Confere confirmação de senha.
  const value = regPasswordConfirm.value;
  let message = "";

  if (!value) {
    message = "Confirme sua senha.";
  } else if (value !== regPassword.value) {
    message = "As senhas nao conferem.";
  }

  return setFieldValidationState(regPasswordConfirm, message, forceShow);
}

function validateLoginForm(forceShow = false) {
  // Valida formulário de login completo.
  const usernameOk = validateLoginUsername(forceShow);
  const passwordOk = validateLoginPassword(forceShow);
  return usernameOk && passwordOk;
}

function validateRegisterForm(forceShow = false) {
  // Valida formulário de cadastro completo.
  const usernameOk = validateRegisterUsername(forceShow);
  const emailOk = validateRegisterEmail(forceShow);
  const passwordOk = validateRegisterPassword(forceShow);
  const confirmOk = validateRegisterPasswordConfirm(forceShow);
  return usernameOk && emailOk && passwordOk && confirmOk;
}

function clearFieldValidationStates() {
  // Reseta estado de validação dos campos.
  [authUsername, authPassword, regUsername, regEmail, regPassword, regPasswordConfirm].forEach((input) => {
    input.classList.remove("is-valid", "is-invalid");
    input.removeAttribute("aria-invalid");
    input.dataset.touched = "false";

    const fieldError = input.parentElement.querySelector(".field-error");
    if (fieldError) {
      fieldError.textContent = "";
      fieldError.classList.remove("show");
    }
  });
}

function registerRealtimeValidation(input, validator) {
  // Liga validação em tempo real.
  input.addEventListener("input", () => {
    validator(false);
    if (input === regPassword) {
      validateRegisterPasswordConfirm(false);
    }
  });

  input.addEventListener("blur", () => {
    input.dataset.touched = "true";
    validator(true);
    if (input === regPassword) {
      validateRegisterPasswordConfirm(true);
    }
  });
}

// Requisições à API

async function apiRequest(path, token, method = "GET", payload = null, baseUrlOverride = null) {
  // Faz requisição HTTP para API.
  const baseUrl = sanitizeBaseUrl((baseUrlOverride || authApiBase.value || "").trim());
  const headers = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers.Authorization = `Token ${token}`;
  }

  const response = await fetch(`${baseUrl}${path}`, {
    method,
    headers,
    body: payload ? JSON.stringify(payload) : null,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Falha ${response.status}. ${errorBody}`);
  }

  return response.json();
}

// Fluxo de autenticação

async function handleLogin(event) {
  // Processa login do usuário.
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
    const loginData = await apiRequest("/api/auth/login", null, "POST", {
      username,
      password,
    });

    saveAuthSession(
      loginData.token,
      loginData.user.username,
      loginData.user.email || "",
      authApiBase.value
    );

    showAuthSuccess(`Bem-vindo, ${loginData.user.username}! Redirecionando...`);

    setTimeout(() => {
      authPassword.value = "";
      populateDashboardFromSession();
      showDashboardScreen();
    }, 1000);
  } catch (error) {
    if (isNetworkFetchError(error)) {
      showAuthError("Nao foi possivel conectar ao backend. Verifique se o servidor esta rodando.");
      return;
    }

    showAuthError(error.message || "Falha no login. Verifique suas credenciais.");
  } finally {
    loginBtn.disabled = false;
  }
}

async function handleRegister(event) {
  // Processa cadastro do usuário.
  event.preventDefault();
  clearAuthMessages();

  if (!validateRegisterForm(true)) {
    showAuthError("Corrija os campos de cadastro para continuar.", true);
    return;
  }

  const username = regUsername.value.trim();
  const email = regEmail.value.trim();
  const password = regPassword.value;

  const registerBtn = registerForm.querySelector("button[type='submit']");
  registerBtn.disabled = true;

  try {
    const registerData = await apiRequest("/api/auth/register", null, "POST", {
      username,
      email,
      password,
    });

    saveAuthSession(
      registerData.token,
      registerData.user.username,
      registerData.user.email || "",
      authApiBase.value
    );

    showAuthSuccess(`Conta criada com sucesso! Bem-vindo, ${registerData.user.username}!`);

    setTimeout(() => {
      regPassword.value = "";
      regPasswordConfirm.value = "";
      populateDashboardFromSession();
      showDashboardScreen();
    }, 1000);
  } catch (error) {
    if (isNetworkFetchError(error)) {
      showAuthError("Nao foi possivel conectar ao backend. Verifique se o servidor esta rodando.", true);
      return;
    }

    showAuthError(error.message || "Falha no cadastro.", true);
  } finally {
    registerBtn.disabled = false;
  }
}

function populateDashboardFromSession() {
  // Preenche painel com sessão salva.
  const token = getStoredToken();
  const username = localStorage.getItem(STORAGE_KEYS.username);
  const email = localStorage.getItem(STORAGE_KEYS.email);

  apiBaseInput.value = getStoredApiBase();
  engineApiBaseInput.value = getStoredEngineApiBase();
  usernameInput.value = username;
  emailInput.value = email;
  authTokenInput.value = token;

  setSessionInfo(`Autenticado como ${username || "usuário"}.`);
}

function handleLogout() {
  // Encerra sessão do usuário.
  clearAuthSession();
  clearAuthMessages();
  clearFieldValidationStates();
  authUsername.value = "";
  authPassword.value = "";
  regUsername.value = "";
  regEmail.value = "";
  regPassword.value = "";
  regPasswordConfirm.value = "";

  showAuthScreen();
  setSessionInfo("Sessão encerrada.");
}

// Dados do dashboard

async function fetchMachineFromApi() {
  // Busca dados da máquina no backend.
  const token = authTokenInput.value.trim();
  const djangoBase = sanitizeBaseUrl((apiBaseInput.value || getStoredApiBase()).trim());
  const engineBase = sanitizeBaseUrl((engineApiBaseInput.value || getStoredEngineApiBase()).trim());

  if (!token) {
    setMessage("Informe o token de autenticação.", "error");
    return;
  }

  saveApiBases(djangoBase, engineBase);

  fetchMachineBtn.disabled = true;
  setMessage("Buscando dados no backend e no Engine Neo4j...", "ok");

  try {
    const [machineData, routeData] = await Promise.all([
      apiRequest("/api/machine/me", token, "GET", null, djangoBase),
      apiRequest("/api/upgrade-route/me", token, "GET", null, djangoBase),
    ]);

    let recommendationData;
    let catalogSource = "Engine Neo4j";

    try {
      recommendationData = await fetchCatalogFromEngine(engineBase);
      catalogMeta = recommendationData.meta || {
        provider: "neo4j",
        database: "desconhecido",
        fetched_at: "",
        count: (recommendationData.catalog || []).length,
      };
      setCatalogSourceInfo(
        `Origem: Neo4j | DB: ${catalogMeta.database} | itens: ${catalogMeta.count}`,
        "ok"
      );
    } catch (engineError) {
      recommendationData = await apiRequest("/api/recommendations/me", token, "GET", null, djangoBase);
      catalogSource = "Django (fallback)";
      const fallbackCatalog = recommendationData.catalog || recommendationData;
      fallbackCatalog.forEach((item) => {
        item.origin = "fallback";
      });
      recommendationData = { catalog: fallbackCatalog };
      setCatalogSourceInfo(
        `Origem do catálogo: Django (fallback do Engine). Motivo: ${engineError.message}`,
        "error"
      );
    }

    const payload = {
      machine: machineData.machine || machineData,
      diagnostics: machineData.diagnostics || initialState.diagnostics,
      route: routeData.route || routeData,
      catalog: recommendationData.catalog || recommendationData,
    };

    applyPayload(payload);
    setMessage(`Dados carregados com sucesso. Catalogo via ${catalogSource}.`, "ok");
  } catch (error) {
    if (isUnauthorizedError(error)) {
      clearAuthSession();
      showAuthScreen();
      setMessage("Sessao expirada. Faca login novamente.", "error");
      return;
    }

    if (isNetworkFetchError(error) && loadAppState()) {
      renderOverview();
      renderRoute();
      renderCatalog();
      setCatalogSourceInfo("Origem do catálogo: armazenamento local (sem conexão).", "error");
      setMessage("Backend indisponível. Dados carregados do armazenamento local.", "ok");
      return;
    }

    if (isNetworkFetchError(error)) {
      saveAppState();
      setCatalogSourceInfo("Origem do catálogo: armazenamento local (sem conexão).", "error");
      setMessage("Backend indisponível. Dados padrão salvos no navegador.", "ok");
      return;
    }

    setMessage(error.message || "Erro ao consultar API.", "error");
  } finally {
    fetchMachineBtn.disabled = false;
  }
}

async function syncCatalogFromEngineOnLoad() {
  // Sincroniza catálogo do Engine sem depender do login.
  const engineBase = sanitizeBaseUrl((engineApiBaseInput.value || getStoredEngineApiBase()).trim());
  setCatalogSourceInfo(`Sincronizando catálogo com ${engineBase}...`, "");

  try {
    const recommendationData = await fetchCatalogFromEngine(engineBase);
    state.catalog = recommendationData.catalog || recommendationData;
    catalogMeta = recommendationData.meta || {
      provider: "neo4j",
      database: "desconhecido",
      fetched_at: "",
      count: (recommendationData.catalog || []).length,
    };
    renderCatalog();
    saveAppState();
    setCatalogSourceInfo(
      `Origem: Neo4j | DB: ${catalogMeta.database} | itens: ${catalogMeta.count}`,
      "ok"
    );
  } catch (error) {
    setCatalogSourceInfo(`Origem do catálogo: local (Engine indisponível). Motivo: ${error.message}`, "error");
  }
}

// Abas do dashboard

document.querySelectorAll(".tab-btn").forEach((btn) => {
  // Controla troca de abas do painel.
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));

    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// Tabs de autenticação

document.querySelectorAll(".auth-tab-btn").forEach((btn) => {
  // Controla troca entre login e cadastro.
  btn.addEventListener("click", () => {
    clearAuthMessages();
    clearFieldValidationStates();

    document.querySelectorAll(".auth-tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".auth-form").forEach((f) => f.classList.remove("active"));

    btn.classList.add("active");
    const tabName = btn.dataset.tab;
    document.querySelector(`.auth-form[data-form="${tabName}"]`).classList.add("active");
  });
});

// Eventos principais

registerRealtimeValidation(authUsername, validateLoginUsername);
// Registra validações em tempo real.
registerRealtimeValidation(authPassword, validateLoginPassword);
registerRealtimeValidation(regUsername, validateRegisterUsername);
registerRealtimeValidation(regEmail, validateRegisterEmail);
registerRealtimeValidation(regPassword, validateRegisterPassword);
registerRealtimeValidation(regPasswordConfirm, validateRegisterPasswordConfirm);

loginForm.addEventListener("submit", handleLogin);
registerForm.addEventListener("submit", handleRegister);
fetchMachineBtn.addEventListener("click", fetchMachineFromApi);
logoutTopbarBtn.addEventListener("click", handleLogout);
newSessionBtn.addEventListener("click", () => {
  applyPayload(structuredClone(initialState));
  saveAppState();
  setMessage("Estado resetado para os dados locais do MVP.", "ok");
});

// Inicialização do app

async function initializeApp() {
  // Inicializa dados e valida sessão.
  const token = getStoredToken();
  const restoredAppState = loadAppState();

  authApiBase.value = getStoredApiBase();
  engineApiBaseInput.value = getStoredEngineApiBase();

  renderOverview();
  renderRoute();
  renderCatalog();
  setCatalogSourceInfo("Origem do catálogo: local (ainda não sincronizado).", "");

  await syncCatalogFromEngineOnLoad();

  if (!restoredAppState) {
    saveAppState();
  }

  if (token) {
    if (token.startsWith("local-")) {
      clearAuthSession();
      setSessionInfo("Sessao local antiga removida. Faca login novamente.");
      showAuthScreen();
      return;
    }

    try {
      const me = await apiRequest("/api/auth/me", token);
      if (!me.user?.username) {
        throw new Error("Sessao invalida.");
      }
    } catch (error) {
      clearAuthSession();
      if (isNetworkFetchError(error)) {
        setSessionInfo("Sem conexao com backend. Faca login quando o servidor voltar.");
      } else {
        setSessionInfo("Sessao invalida. Faca login novamente.");
      }
      showAuthScreen();
      return;
    }

    populateDashboardFromSession();
    showDashboardScreen();
  } else {
    showAuthScreen();
  }
}

initializeApp();
