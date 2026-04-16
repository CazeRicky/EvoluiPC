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
  token: "evoluipc.token",
  email: "evoluipc.email",
  username: "evoluipc.username",
};

const state = structuredClone(initialState);

const metricGrid = document.getElementById("metricGrid");
const diagnosticList = document.getElementById("diagnosticList");
const routeList = document.getElementById("upgradeRoute");
const catalogGrid = document.getElementById("catalogGrid");
const apiBaseInput = document.getElementById("apiBaseInput");
const emailInput = document.getElementById("emailInput");
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const authTokenInput = document.getElementById("authTokenInput");
const sessionInfo = document.getElementById("sessionInfo");
const scanMessage = document.getElementById("scanMessage");
const fetchMachineBtn = document.getElementById("fetchMachineBtn");
const registerBtn = document.getElementById("registerBtn");
const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");

function renderOverview() {
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
  routeList.innerHTML = "";
  state.route.forEach((entry) => {
    const li = document.createElement("li");
    li.className = "route-item";
    li.innerHTML = `<strong>${entry.step}: ${entry.action}</strong><span>${entry.impact}</span>`;
    routeList.appendChild(li);
  });
}

function renderCatalog() {
  catalogGrid.innerHTML = "";
  state.catalog.forEach((item) => {
    const card = document.createElement("article");
    card.className = "catalog-card";
    card.innerHTML = `
      <h3>${item.name}</h3>
      <p>${item.tag}</p>
      <p class="catalog-meta">${item.price} · ${item.source}</p>
    `;
    catalogGrid.appendChild(card);
  });
}

function applyPayload(payload) {
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
}

function setMessage(text, type) {
  scanMessage.textContent = text;
  scanMessage.className = `message ${type}`;
}

function setSessionInfo(text) {
  sessionInfo.textContent = text;
}

function sanitizeBaseUrl(url) {
  return url.replace(/\/+$/, "");
}

function saveSession() {
  localStorage.setItem(STORAGE_KEYS.apiBase, apiBaseInput.value.trim());
  localStorage.setItem(STORAGE_KEYS.token, authTokenInput.value.trim());
  localStorage.setItem(STORAGE_KEYS.email, emailInput.value.trim());
  localStorage.setItem(STORAGE_KEYS.username, usernameInput.value.trim());
}

function clearSession() {
  localStorage.removeItem(STORAGE_KEYS.apiBase);
  localStorage.removeItem(STORAGE_KEYS.token);
  localStorage.removeItem(STORAGE_KEYS.email);
  localStorage.removeItem(STORAGE_KEYS.username);
}

function restoreSession() {
  const apiBase = localStorage.getItem(STORAGE_KEYS.apiBase);
  const token = localStorage.getItem(STORAGE_KEYS.token);
  const email = localStorage.getItem(STORAGE_KEYS.email);
  const username = localStorage.getItem(STORAGE_KEYS.username);

  if (apiBase) apiBaseInput.value = apiBase;
  if (token) authTokenInput.value = token;
  if (email) emailInput.value = email;
  if (username) usernameInput.value = username;

  if (token) {
    setSessionInfo(`Sessao local detectada para ${username || "usuario"}.`);
  } else {
    setSessionInfo("Sem sessao ativa.");
  }
}

async function apiRequest(path, token, method = "GET", payload = null) {
  const baseUrl = sanitizeBaseUrl(apiBaseInput.value.trim());
  const headers = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers.Authorization = `Token ${token}`;
  }

  const response = await fetch(`${baseUrl}${path}`, {
    method,
    headers: {
      ...headers,
    },
    body: payload ? JSON.stringify(payload) : null,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Falha ${response.status}. ${errorBody}`);
  }

  return response.json();
}

function normalizePayload(machineData, routeData, recommendationData) {
  return {
    machine: machineData.machine || machineData,
    diagnostics: machineData.diagnostics || initialState.diagnostics,
    route: routeData.route || routeData,
    catalog: recommendationData.catalog || recommendationData,
  };
}

async function fetchMachineFromApi() {
  const token = authTokenInput.value.trim();

  if (!token) {
    setMessage("Informe o token de autenticacao.", "error");
    return;
  }

  fetchMachineBtn.disabled = true;
  setMessage("Buscando dados no backend Django...", "ok");

  try {
    const [machineData, routeData, recommendationData] = await Promise.all([
      apiRequest("/api/machine/me", token),
      apiRequest("/api/upgrade-route/me", token),
      apiRequest("/api/recommendations/me", token),
    ]);

    const payload = normalizePayload(machineData, routeData, recommendationData);
    applyPayload(payload);
    saveSession();
    setMessage("Dados carregados com sucesso.", "ok");
  } catch (error) {
    setMessage(error.message || "Erro ao consultar API.", "error");
  } finally {
    fetchMachineBtn.disabled = false;
  }
}

async function handleLogin() {
  const username = usernameInput.value.trim();
  const password = passwordInput.value;

  if (!username || !password) {
    setMessage("Informe usuario e senha para login.", "error");
    return;
  }

  loginBtn.disabled = true;
  setMessage("Realizando login...", "ok");

  try {
    const loginData = await apiRequest("/api/auth/login", null, "POST", {
      username,
      password,
    });
    authTokenInput.value = loginData.token;
    saveSession();
    setSessionInfo(`Autenticado como ${loginData.user.username}.`);
    setMessage("Login realizado. Agora voce pode buscar os dados.", "ok");
    passwordInput.value = "";
  } catch (error) {
    setMessage(error.message || "Falha no login.", "error");
  } finally {
    loginBtn.disabled = false;
  }
}

async function handleRegister() {
  const username = usernameInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!username || !password) {
    setMessage("Informe usuario e senha para cadastro.", "error");
    return;
  }

  registerBtn.disabled = true;
  setMessage("Criando conta...", "ok");

  try {
    const registerData = await apiRequest("/api/auth/register", null, "POST", {
      username,
      email,
      password,
    });
    authTokenInput.value = registerData.token;
    saveSession();
    setSessionInfo(`Conta criada e autenticada como ${registerData.user.username}.`);
    setMessage("Cadastro concluido. Agora voce pode buscar os dados.", "ok");
    passwordInput.value = "";
  } catch (error) {
    setMessage(error.message || "Falha no cadastro.", "error");
  } finally {
    registerBtn.disabled = false;
  }
}

async function handleLogout() {
  const token = authTokenInput.value.trim();

  try {
    if (token) {
      await apiRequest("/api/auth/logout", token, "POST", {});
    }
  } catch {
  }

  authTokenInput.value = "";
  emailInput.value = "";
  passwordInput.value = "";
  clearSession();
  setSessionInfo("Sem sessao ativa.");
  setMessage("Sessao encerrada.", "ok");
}

async function hydrateSessionFromBackend() {
  const token = authTokenInput.value.trim();
  if (!token) return;

  try {
    const me = await apiRequest("/api/auth/me", token);
    if (me.user?.username) {
      usernameInput.value = me.user.username;
      saveSession();
      setSessionInfo(`Autenticado como ${me.user.username}.`);
    }
  } catch {
    setSessionInfo("Token local invalido. Faca login novamente.");
  }
}

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));

    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

document.getElementById("newSessionBtn").addEventListener("click", () => {
  applyPayload(structuredClone(initialState));
  setMessage("Estado resetado para os dados locais do MVP.", "ok");
});

fetchMachineBtn.addEventListener("click", fetchMachineFromApi);
loginBtn.addEventListener("click", handleLogin);
registerBtn.addEventListener("click", handleRegister);
logoutBtn.addEventListener("click", handleLogout);

renderOverview();
renderRoute();
renderCatalog();
restoreSession();
hydrateSessionFromBackend();
