# GUIA DE DEPLOYMENT - Configuração para Produção/Nuvem

## Status das Correções ✅

Todas as referências a `localhost` e `127.0.0.1` foram removidas do código.

### Mudanças Realizadas:

#### 1. **Frontend (app.js e index.html)** ✅
- ❌ Removido: Hardcoded `http://127.0.0.1:8000` e `http://127.0.0.1:8002`
- ✅ Agora usa: URLs relativas baseadas em `window.location.origin`
- ✅ Inputs agora com `placeholder` em vez de valores hardcoded

#### 2. **Docker Compose** ✅
- ❌ Removido: Healthchecks usando `127.0.0.1`
- ✅ Agora usa: Nomes de serviço Docker (neo4j, django, engine, frontend)
- ✅ Adicionado: Variáveis de ambiente para VITE_API_BASE e VITE_ENGINE_API_BASE

#### 3. **Configuração de Ambiente** ✅
- ✅ Criado: `.env.production` com template para produção
- ✅ Criar: `docker-compose.production.yml` para deploy em nuvem

---

## 🚀 COMO FAZER DEPLOY NA NUVEM

### Pré-requisitos:
1. Ter Docker e Docker Compose instalados no servidor
2. Um domínio (ex: seu-app.com)
3. Certificado SSL (recomendado usar Let's Encrypt)

### Passo 1: Preparar o Servidor

```bash
# Clone o repositório
git clone <seu-repo> evoluipc
cd evoluipc

# Criar arquivo .env para produção
cat > .env.production << EOF
DJANGO_SECRET_KEY=sua-chave-super-segreta-aleatorio-aqui
DJANGO_DEBUG=0
NEO4J_PASSWORD=sua-senha-neo4j-super-segura
DJANGO_ALLOWED_HOSTS=seu-dominio.com,api.seu-dominio.com,www.seu-dominio.com
DJANGO_CORS_ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
VITE_API_BASE=https://api.seu-dominio.com
VITE_ENGINE_API_BASE=https://engine.seu-dominio.com
EOF
```

### Passo 2: Usar Proxy Reverso (NGINX)

Crie um arquivo `nginx.conf`:

```nginx
upstream django {
    server django:8000;
}

upstream engine {
    server engine:8002;
}

upstream frontend {
    server frontend:4173;
}

server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Certificados SSL (usar certbot do Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    client_max_body_size 100M;
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API Django
    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Engine
    location /engine/ {
        proxy_pass http://engine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Passo 3: Iniciar com Docker Compose

```bash
# Usar o arquivo de produção
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# Verificar logs
docker-compose -f docker-compose.production.yml logs -f

# Parar os serviços
docker-compose -f docker-compose.production.yml down
```

### Passo 4: Configurar SSL com Let's Encrypt

```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com

# Renovar automaticamente
sudo certbot renew --quiet --no-eff-email --agree-tos --email seu-email@example.com
```

---

## ✅ Checklist de Produção

- [ ] Gerar SECRET_KEY forte: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- [ ] Definir DJANGO_DEBUG=0
- [ ] Configurar ALLOWED_HOSTS com seu domínio
- [ ] Configurar CORS_ALLOWED_ORIGINS apenas com seu domínio
- [ ] Usar senhas fortes para NEO4J_PASSWORD
- [ ] Habilitar HTTPS/SSL
- [ ] Verificar backups do Neo4j
- [ ] Monitorar logs e performance
- [ ] Usar Gunicorn em vez de `runserver` (já configurado em `.production.yml`)

---

## 📝 Comandos Úteis

```bash
# Ver status dos containers
docker-compose ps

# Executar migrate
docker-compose exec django python manage.py migrate

# Criar superusuário
docker-compose exec django python manage.py createsuperuser

# Ver logs em tempo real
docker-compose logs -f django

# Limpar volumes (cuidado!)
docker-compose down -v
```

---

## 🔧 Próximas Melhorias Recomendadas

1. Adicionar Redis para cache
2. Implementar rate limiting
3. Adicionar monitoramento (Prometheus + Grafana)
4. Backup automático do Neo4j
5. CI/CD com GitHub Actions ou GitLab CI
6. WAF (Web Application Firewall)
