#!/bin/bash
# Полная очистка Docker перед запуском

echo "🧹 Полная очистка Docker..."

# Остановка всех контейнеров
docker-compose down 2>/dev/null

# Удаление контейнеров
docker rm -f teamflow-backend teamflow-frontend 2>/dev/null

# Удаление образов
docker rmi teamflow_backend teamflow_frontend 2>/dev/null

# Очистка неиспользуемых образов
docker image prune -f

echo "✅ Очистка завершена!"
echo ""
echo "Теперь запустите:"
echo "  docker-compose up --build -d"
