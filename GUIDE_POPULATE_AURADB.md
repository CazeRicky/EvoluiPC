# 🌱 GUIDE: Popular Neo4j AuraDB com Dados de Hardware

**Objetivo:** Colocar dados de compatibilidade de hardware no Neo4j da nuvem

---

## ✅ Pré-requisitos

1. Conta Neo4j AuraDB criada (free.neo4j.com)
2. Database criado
3. Credenciais em mãos:
   - `NEO4J_URI` (ex: `neo4j+s://abc123def456.databases.neo4j.io`)
   - `NEO4J_USER` (geralmente `neo4j`)
   - `NEO4J_PASSWORD` (a senha gerada)

---

## 🚀 Opção 1: Rodar Seed Localmente Apontando para AuraDB

### Step 1: Configure as Variáveis

**No Windows PowerShell:**
```powershell
$env:NEO4J_URI = "neo4j+s://abc123def456.databases.neo4j.io"
$env:NEO4J_USER = "neo4j"
$env:NEO4J_PASSWORD = "sua-senha-aqui"
$env:NEO4J_DATABASE = "neo4j"
```

**No Mac/Linux:**
```bash
export NEO4J_URI="neo4j+s://abc123def456.databases.neo4j.io"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="sua-senha-aqui"
export NEO4J_DATABASE="neo4j"
```

### Step 2: Verifique a Conexão

```bash
cd django
python manage.py shell
```

Dentro do shell Python:
```python
from core.neo4j_store import get_driver

with get_driver() as driver:
    with driver.session() as session:
        result = session.run("RETURN 1")
        print("✅ Conectado ao AuraDB!")
```

Se der erro, a senha/URL está errada.

### Step 3: Rode o Seed

**Opção A: Usando Django (Recomendado)**
```bash
cd django
python manage.py seed_demo_users
python manage.py seed_hardware  # Se existir esse comando
```

**Opção B: Usando Script Python Direto**
```bash
cd evoluipc-engine
python seed.py
```

---

## 🚀 Opção 2: Rodar Seed via Render Deploy

Se preferir rodar tudo direto no Render (sem tocar no seu PC):

### Step 1: Editar docker-compose.production.yml

```yaml
django:
  build:
    context: ./django
    dockerfile: Dockerfile
  command: sh -c "
    python manage.py migrate &&
    python manage.py seed_demo_users &&
    python manage.py seed_hardware &&
    gunicorn evoluipc_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
  "
  environment:
    NEO4J_URI: ${NEO4J_URI}
    NEO4J_USER: ${NEO4J_USER}
    NEO4J_PASSWORD: ${NEO4J_PASSWORD}
    # ... outras variáveis
```

### Step 2: Fazer Deploy

```bash
git add docker-compose.production.yml
git commit -m "feat: adicionar seed ao deploy"
git push
```

O Render vai:
1. Fazer build da imagem
2. Rodar o seed automaticamente
3. Depois iniciar o Django normalmente

---

## ✅ Verificar se Funcionou

### No AuraDB Browser (Neo4j Aura)

```cypher
# Ver dados de CPU
MATCH (cpu:Processador) RETURN cpu.nome, cpu.soquete, cpu.tdp LIMIT 10

# Ver dados de GPU
MATCH (gpu:GPU) RETURN gpu.nome, gpu.vram, gpu.tdp LIMIT 10

# Ver placas-mãe
MATCH (mobo:PlacaMae) RETURN mobo.nome, mobo.chipset LIMIT 10

# Ver relacionamentos
MATCH ()-[rel:COMPATIVEL_COM]->() RETURN COUNT(rel) as total
```

Se retornar dados, ✅ **funcionou!**

### No Frontend do Render

1. Faça o upload de um PC
2. Clique em "Analisar"
3. Deve aparecer recomendações reais (não mais Fallback)

---

## 🐛 Troubleshooting

### Erro: "Neo4j Connection Failed"
- Verifique URL: deve começar com `neo4j+s://`
- Verifique senha: copie exatamente do AuraDB
- Teste localmente antes de fazer push

### Erro: "Timeout"
- AuraDB pode estar dormindo (free tier)
- Faça uma conexão via browser no AuraDB para ativar
- Espere 30 segundos e tente de novo

### Seed Roda mas Não Aparece Dados
- Verificar logs: `docker-compose logs django`
- Testar query no AuraDB browser
- Confirmar que `NEO4J_DATABASE` = "neo4j"

---

## 📊 Dados Que Devem Estar Lá Depois

```
Processadores:
  - Ryzen 5 5600X (Socket AM4, TDP 65W)
  - Ryzen 7 5700X3D (Socket AM4, TDP 105W)
  - Intel i5-12400 (Socket LGA1700, TDP 65W)

Placas-mãe:
  - ASUS PRIME B550M-K
  - MSI MAG B550 TOMAHAWK
  - ASRock B550 Phantom Gaming

GPUs:
  - RTX 4080 (Ada, 16GB, 320W)
  - RTX 4070 (Ada, 12GB, 200W)
  - RTX 3060 (Ampere, 12GB, 170W)

Compatibilidades:
  - RTX 4080 ← COMPATÍVEL_COM → ASUS PRIME B550M-K
  - Ryzen 7 5700X3D ← COMPATÍVEL_COM → ASRock B550 Phantom
  - etc...
```

---

## ✅ Checklist Final

- [ ] AuraDB criado e ativo
- [ ] Variáveis de ambiente configuradas (local e Render)
- [ ] Seed rodou com sucesso
- [ ] Dados aparecem nas queries
- [ ] Frontend retorna recomendações reais
- [ ] **MVP pronto na nuvem! 🚀**

---

**Tempo estimado:** 10 minutos
**Dificuldade:** Fácil
**Resultado:** Recomendações funcionando 24/7 na nuvem
