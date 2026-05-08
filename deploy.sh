#!/bin/bash
# SCRIPT DE DEPLOY - Para facilitar o processo

set -e

echo "🚀 EvoluiPC - Deploy Helper"
echo "================================"
echo ""

# Menu
echo "Escolha a opção:"
echo "1) Testar localmente (desenvolvimento)"
echo "2) Preparar para produção"
echo "3) Ver status das mudanças"
echo ""
read -p "Opção (1-3): " opcao

case $opcao in
  1)
    echo ""
    echo "📦 Inicializando ambiente de desenvolvimento..."
    docker-compose down -v 2>/dev/null || true
    docker-compose up -d --build
    echo ""
    echo "✅ Ambiente iniciado!"
    echo "📱 Frontend: http://localhost:4173"
    echo "📡 Django API: http://localhost:8000"
    echo "⚙️  Engine API: http://localhost:8002"
    echo "🗄️  Neo4j UI: http://localhost:7474"
    echo ""
    echo "Ver logs: docker-compose logs -f"
    ;;
  
  2)
    echo ""
    echo "🌐 Preparação para produção..."
    echo ""
    echo "IMPORTANTE: Configure seu domínio e senhas!"
    echo ""
    echo "1. Gerar SECRET_KEY forte:"
    python3 -c "import secrets; print('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(50))"
    echo ""
    echo "2. Editar .env com seus valores:"
    echo "   - DJANGO_SECRET_KEY (copie acima)"
    echo "   - DJANGO_ALLOWED_HOSTS"
    echo "   - NEO4J_PASSWORD"
    echo "   - DJANGO_CORS_ALLOWED_ORIGINS"
    echo ""
    echo "3. Depois execute:"
    echo "   docker-compose -f docker-compose.production.yml --env-file .env up -d"
    echo ""
    echo "📖 Ver DEPLOYMENT_GUIDE.md para instruções detalhadas"
    ;;
  
  3)
    echo ""
    echo "📊 Status das mudanças:"
    git status
    echo ""
    echo "📝 Mudanças em arquivos:"
    git diff --name-only
    ;;
  
  *)
    echo "❌ Opção inválida"
    exit 1
    ;;
esac
