# EvoluiPC - Mobile Dashboard

## 🎨 Identidade Visual

- **Background Principal:** `#f3efe6` (Creme suave)
- **Texto/Botões Primários:** `#121212` (Preto sólido)
- **Acento (Sustentabilidade):** `#0b7a75` (Verde escuro)
- **Fontes:** Space Grotesk (UI) e IBM Plex Mono (Dados técnicos)

## 📱 Estrutura de Rotas

### Autenticação
- `/` - **Splash Screen**: Logo animado com redirecionamento automático
- `/login` - **Login**: Autenticação de usuário
- `/register` - **Cadastro**: Criação de nova conta

### Fluxo Principal (com Bottom Navigation)
- `/home` - **Home/Meu Setup**: Visão geral do hardware atual
- `/diagnostics` - **Diagnóstico**: Análise de gargalos e compatibilidade
- `/route` - **Rota de Upgrade**: Árvore de evolução com passos recomendados
- `/marketplace` - **Marketplace**: Catálogo de peças com links de afiliados
- `/details/:stepId` - **Detalhes do Upgrade**: Informações específicas de cada passo

## 🗂️ Estrutura de Dados (Mock - Baseada no Django Backend)

### Interfaces Principais

```typescript
// Machine Snapshot
{
  cpu: string
  gpu: string
  ram: string
  motherboard: string
  storage: string
  psu: string
  performance_score: number
  compatibility_score: number
}

// Diagnostic
{
  id: string
  message: string
  severity: 'info' | 'warning' | 'critical'
  component: string
}

// Upgrade Step
{
  step: number
  action: string
  component: string
  impact: string
  impact_percentage: number
  estimated_cost: number
  priority: 'high' | 'medium' | 'low'
}

// Catalog Item
{
  id: string
  name: string
  type: 'cpu' | 'gpu' | 'ram' | 'storage' | 'psu' | 'motherboard'
  price: number
  source: string
  affiliate_link: string
  tag: string
  compatibility: number
  performance_gain: number
}
```

## 🔌 Integração com Backend Django

### Endpoints Esperados

```typescript
// Autenticação
POST /api/auth/login
POST /api/auth/register

// Dados do Usuário
GET /api/machine/me        // MachineSnapshot
GET /api/diagnostics/me    // Diagnostic[]
GET /api/upgrade-route/me  // UpgradeStep[]
GET /api/catalog/me        // CatalogItem[]
```

### Headers Obrigatórios
```
Authorization: Token <seu_token>
```

## 📦 Componentes Principais

- `StatCard` - Cards de estatísticas (Performance, Compatibilidade, etc.)
- `ChartCard` - Container para gráficos Recharts
- `QuickAction` - Botões de ação rápida
- `TransactionItem` - Items de lista (usado para upgrades)
- `BottomNav` - Navegação inferior com 4 tabs

## 🎯 Bottom Navigation

1. **Home** - Visão geral do setup
2. **Diagnóstico** - Análise de gargalos
3. **Rota** - Caminho de upgrade
4. **Loja** - Marketplace de peças

## 🚀 Próximos Passos para Integração

1. Substituir funções mock em `mockData.ts` por chamadas reais à API
2. Implementar gerenciamento de estado global (Context API ou Zustand)
3. Adicionar tratamento de erros e loading states
4. Implementar cache de dados offline
5. Adicionar refresh de dados com pull-to-refresh

## 📝 Notas de Desenvolvimento

- O sistema de rotas usa `react-router` v7
- Animações implementadas com `motion/react` (Framer Motion)
- Gráficos criados com `recharts`
- Design system baseado em Tailwind CSS v4
- Todas as fontes são carregadas via Google Fonts
