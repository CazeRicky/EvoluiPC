# Guia de Configuração - EvoluiPC Frontend + Django Backend

## 🚀 Início Rápido

### 1. **Obter o IP do seu computador**

#### Windows:
```powershell
ipconfig
```
Procure pela seção "IPv4 Address" (geralmente algo como `192.168.x.x` ou `10.0.x.x`)

#### Mac/Linux:
```bash
ifconfig
```
Procure pelo "inet" address na sua interface de rede ativa (wifi/eth).

### 2. **Configurar o arquivo `.env.local`**

Abra o arquivo `frontend/.env.local` e substitua o IP:

```env
VITE_API_BASE_URL=http://SEU_IP_AQUI:8000/api
```

**Exemplo:**
```env
VITE_API_BASE_URL=http://192.168.1.15:8000/api
```

### 3. **Iniciar o Backend Django**

No terminal da pasta `backend-django`:
```bash
python manage.py runserver 0.0.0.0:8000
```

⚠️ **IMPORTANTE:** Use `0.0.0.0:8000` para aceitar conexões de todos os IPs da rede local, não apenas localhost.

### 4. **Iniciar o Frontend (Web)**

No terminal da pasta `frontend`:
```bash
npm run dev
```

O app estará disponível em `http://localhost:5173`

### 5. **Testar a Conexão**

1. Abra http://localhost:5173 no seu navegador
2. Faça login com um usuário da seed do Django
3. Se os dados carregarem corretamente → ✅ Conexão funcionando!

---

## 📱 Compilar para Mobile (Android/iOS)

### Android:
```bash
npm run cap:android
```

### iOS:
```bash
npm run cap:ios
```

> **Nota:** Ao compilar para mobile, o IP precisa ser o da sua máquina na rede local (Wi-Fi).

---

## 🔍 Troubleshooting

### "Erro 401 - Unauthorized"
- Verifique se o token foi salvo corretamente
- Tente fazer logout e login novamente

### "Erro de conexão ao backend"
- ✅ Confirme que o IP está correto em `.env.local`
- ✅ Verifique se o Django está rodando em `0.0.0.0:8000`
- ✅ Teste com `curl`: `curl http://SEU_IP:8000/api/machine/me/`

### "CORS Error"
- Verifique se o Django tem `CORS_ALLOWED_ORIGINS` configurado corretamente em `settings.py`
- Adicione `http://SEU_IP_LOCAL:5173` (ou da máquina cliente) se necessário

---

## 📝 Endpoints Esperados

O frontend espera estes endpoints do Django:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login` | Login do usuário |
| POST | `/api/auth/register` | Registrar novo usuário |
| GET | `/api/auth/me` | Info do usuário atual |
| GET | `/api/machine/me` | Dados do setup + diagnósticos |
| GET | `/api/upgrade-route/me` | Rota de upgrade |
| GET | `/api/recommendations/me` | Catálogo de produtos |

---

## 💾 Componentes Principais

### `LoadingSpinner.tsx`
Componente reutilizável para estados de carregamento:
```tsx
import { LoadingSpinner } from '../components/LoadingSpinner';

<LoadingSpinner message="Carregando..." size="md" fullScreen={true} />
```

### `apiService`
Centralizador de requisições:
```typescript
await apiService.getMachineData()
await apiService.getUpgradeRoute()
await apiService.getCatalog()
```

---

## ✨ Próximas Melhorias Sugeridas

- [ ] Adicionar retry automático em caso de falha
- [ ] Implementar refresh de dados a cada 30s
- [ ] Adicionar cache local (IndexedDB)
- [ ] Criar sistema de notificações em tempo real
- [ ] Implementar PWA para suportar offline
