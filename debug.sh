#!/bin/bash
echo "=== Диагностика TeamFlow ==="
echo ""

echo "1. Статус контейнеров:"
docker ps | grep teamflow
echo ""

echo "2. Порты:"
docker port teamflow-backend
docker port teamflow-frontend
echo ""

echo "3. Curl к backend (localhost):"
curl -s http://localhost:8180/health
echo ""

echo "4. Curl к backend (0.0.0.0):"
curl -s http://0.0.0.0:8180/health
echo ""

echo "5. Curl к API tasks:"
curl -s http://localhost:8180/api/tasks
echo ""

echo "6. Netstat - что слушает:"
ss -tlnp | grep 8180
echo ""

echo "7. Логи backend (последние 20 строк):"
docker logs teamflow-backend --tail 20
echo ""

echo "8. IP контейнера backend:"
docker inspect teamflow-backend | grep '"IPAddress"'
