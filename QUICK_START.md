# ⚡ Quick Start - EvoluiPC

## 🚀 Começar em 5 minutos

### Passo 1: Obter IP Local
```powershell
# Windows
ipconfig

# Mac/Linux
ifconfig
```
Procure por algo como: `192.168.1.15` ou `10.0.0.XX`

### Passo 2: Editar `.env.local`
```bash
cd frontend
nano .env.local  # ou abra em seu editor favorito
```

Mude esta linha:
```env
VITE_API_BASE_URL=http://SEU_IP_AQUI:8000/api
```

Exemplo:
```env
VITE_API_BASE_URL=http://192.168.1.15:8000/api
```

### Passo 3: Iniciar Backend
```bash
cd backend-django
python manage.py runserver 0.0.0.0:8000
```

### Passo 4: Iniciar Frontend
```bash
cd frontend
npm install  # primeira vez only
npm run dev
```

### Passo 5: Abrir no Navegador
```
http://localhost:5173
```

---

## ✅ Checklist

- [ ] IP local obtido
- [ ] `.env.local` atualizado com IP correto
- [ ] Backend Django rodando em `0.0.0.0:8000`
- [ ] Frontend rodando em `localhost:5173`
- [ ] Conseguir fazer login
- [ ] Dados carregando corretamente

---

## 🔧 Se não funcionar

### ❌ "Erro de conexão"
```
Solução: 
1. Confirme que o IP está correto em .env.local
2. Verifique se Django está rodando: http://SEU_IP:8000/
3. Teste firewall: ping SEU_IP
```

### ❌ "401 - Unauthorized"
```
Solução:
1. Faça logout (limpar localStorage)
2. Faça login novamente
3. Confirme usuário/senha da seed do Django
```

### ❌ "CORS Error"
```
Solução: Adicionar em backend Django settings.py:
CORS_ALLOWED_ORIGINS = [
    "http://SEU_IP_LOCAL:5173",
    "http://localhost:5173",
]
```

---

## 📱 Compilar para Mobile

### Android
```bash
cd frontend
npm run cap:android
```

### iOS
```bash
cd frontend
npm run cap:ios
```

---

## 📊 Arquivos Criados para Integração

| Arquivo | Propósito |
|---------|-----------|
| `.env.local` | Config do backend IP |
| `setup-backend.js` | Script auto-config |
| `src/app/components/LoadingSpinner.tsx` | Componente loading |
| `SETUP_BACKEND_INTEGRATION.md` | Docs completas |
| `INTEGRATION_SUMMARY.md` | Resumo executivo |

---

## 💡 Dicas

1. **Não commitr `.env.local`** - Já está em `.gitignore` ✅
2. **Use `0.0.0.0` no Django** - Para aceitar conexões Wi-Fi
3. **Teste endpoints com curl:**
   ```bash
   curl http://192.168.1.15:8000/api/
   ```
4. **Se mudar de rede** - Atualize `.env.local` com novo IP

---

## 🎯 Próximo Passo

```bash
npm run dev
# Abrir http://localhost:5173
# Fazer login
# Ver dados carregando em tempo real!
```

---

**Tudo pronto!** Qualquer dúvida, consulte `SETUP_BACKEND_INTEGRATION.md` 📖
