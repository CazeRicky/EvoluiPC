# EvoluiPC - RESUMO DAS MUDANÇAS PARA PRODUÇÃO/NUVEM

## 🎯 Problema Identificado

O código estava **hardcoded com `localhost` e `127.0.0.1`**, o que causa falhas quando rodando:
- Em máquinas remotas (Mac, Linux)
- Em ambientes Docker
- Em nuvem (AWS, Azure, etc.)

David reportou: **"não apareceu nada"** → Era porque o frontend tentava acessar `127.0.0.1:8000` que não existe em outros ambientes.

---

## ✅ CORREÇÕES REALIZADAS

### 1. **Frontend (app.js)**
```javascript
// ❌ ANTES
localStorage.setItem(STORAGE_KEYS.engineApiBase, "http://127.0.0.1:8002");
return localStorage.getItem(STORAGE_KEYS.apiBase) || "http://127.0.0.1:8000";

// ✅ DEPOIS
const engineBase = window.EVOLUIPC_ENGINE_API_BASE || (window.location.origin + '/engine');
return localStorage.getItem(STORAGE_KEYS.apiBase) || (window.location.origin + '/api');
```

**O que muda:**
- Usa URL relativa baseada no domínio atual
- Funciona em qualquer servidor/nuvem
- Pode ser sobrescrito por variáveis de ambiente

---

### 2. **Frontend (index.html)**
```html
<!-- ❌ ANTES -->
<input id="apiBaseInput" type="text" value="http://127.0.0.1:8000" />

<!-- ✅ DEPOIS -->
<input id="apiBaseInput" type="text" placeholder="Deixe em branco para autodetectar" />
```

---

### 3. **Docker Compose**
```yaml
# ❌ ANTES (não funciona em Docker porque 127.0.0.1 é local ao container)
healthcheck:
  test: ["CMD", "python", "-c", "urllib.request.urlopen('http://127.0.0.1:8002')"]

# ✅ DEPOIS (usa nome de serviço Docker)
healthcheck:
  test: ["CMD", "python", "-c", "urllib.request.urlopen('http://engine:8002')"]
```

**Serviços Docker agora se comunicam via:**
- `neo4j:7687` (banco de dados)
- `django:8000` (backend)
- `engine:8002` (motor de IA)
- `frontend:4173` (frontend)

---

### 4. **Novos Arquivos Criados**

#### `.env.production` 
Template com variáveis para produção

#### `docker-compose.production.yml`
Versão otimizada para nuvem com:
- Gunicorn em vez de runserver
- Memory management para Neo4j
- Restart policies = always
- Network isolada
- Validação de variáveis obrigatórias

#### `DEPLOYMENT_GUIDE.md`
Guia completo de deploy na nuvem

---

## 🚀 COMO TESTAR LOCALMENTE

```bash
# Reconstruir e iniciar
docker-compose up -d --build

# Verificar se tudo subiu
docker-compose ps

# Acessar
- Frontend: http://localhost:4173
- Django: http://localhost:8000
- Engine: http://localhost:8002
- Neo4j: http://localhost:7474
```

---

## 🌐 PRÓXIMOS PASSOS PARA NUVEM

1. **Gerar SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

2. **Preparar servidor (AWS/Azure/Heroku):**
   - Docker e Docker Compose instalados
   - Domínio DNS configurado
   - Certificado SSL (Let's Encrypt)

3. **Fazer deploy:**
   ```bash
   docker-compose -f docker-compose.production.yml --env-file .env.production up -d
   ```

4. **Configurar NGINX como proxy reverso** (ver DEPLOYMENT_GUIDE.md)

---

## 📋 MUDANÇAS POR ARQUIVO

| Arquivo | Mudanças |
|---------|----------|
| `frontend/app.js` | URLs relativas, remove hardcoded localhost |
| `frontend/index.html` | Inputs sem valores padrão |
| `docker-compose.yml` | Healthchecks com nomes de serviço |
| `docker-compose.production.yml` | ✨ Novo arquivo otimizado |
| `django/.env.example` | URLs atualizadas |
| `django/.env.production` | ✨ Novo arquivo para produção |
| `DEPLOYMENT_GUIDE.md` | ✨ Novo guia completo |

---

## ✨ RESULTADO

Agora o EvoluiPC pode rodar em **qualquer lugar**:
- ✅ Localhost (desenvolvimento)
- ✅ Docker local
- ✅ Servidor remoto
- ✅ AWS/Azure/GCP
- ✅ Heroku
- ✅ DigitalOcean

Sem alterar uma linha de código! 🎉
