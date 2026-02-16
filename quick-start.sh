#!/bin/bash

echo "🚀 TeamFlow Quick Start"
echo ""

# Step 1: Clean up
echo "🧹 Шаг 1/4: Очистка старых контейнеров..."
docker-compose down 2>/dev/null
docker rm -f teamflow-backend teamflow-frontend 2>/dev/null
echo "✅ Очистка завершена"
echo ""

# Step 2: Check .env files
echo "📝 Шаг 2/4: Проверка конфигурации..."

# Root .env
if [ ! -f ".env" ]; then
    echo "Создаю .env в корне..."
    cp .env.example .env
fi

# Backend .env
if [ ! -f "backend/.env" ]; then
    echo "Создаю backend/.env..."
    cp backend/.env.example backend/.env
    echo ""
    echo "⚠️  ВАЖНО: Настройте backend/.env!"
    echo "   Добавьте:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID"
    echo "   - TELEGRAM_BOT_USERNAME"
    echo ""
    read -p "Открыть редактор сейчас? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} backend/.env
    else
        echo "Не забудьте настроить backend/.env перед запуском!"
        exit 1
    fi
fi

echo "✅ Конфигурация готова"
echo ""

# Step 3: Build
echo "🔨 Шаг 3/4: Сборка контейнеров..."
docker-compose build --no-cache
echo "✅ Сборка завершена"
echo ""

# Step 4: Start
echo "🚀 Шаг 4/4: Запуск..."
docker-compose up -d
echo ""

# Wait for services
echo "⏳ Ожидание запуска сервисов (30 сек)..."
sleep 30

# Check status
echo ""
echo "📊 Статус контейнеров:"
docker-compose ps
echo ""

# Show URLs
source .env 2>/dev/null || true
BACKEND_PORT=${BACKEND_PORT:-8180}
FRONTEND_PORT=${FRONTEND_PORT:-5180}
BASE_URL=${BASE_URL:-http://localhost}

echo "✅ TeamFlow запущен!"
echo ""
echo "📍 Доступ:"
echo "   Web UI:   ${BASE_URL}:${FRONTEND_PORT}"
echo "   Backend:  ${BASE_URL}:${BACKEND_PORT}"
echo "   API Docs: ${BASE_URL}:${BACKEND_PORT}/docs"
echo ""
echo "📱 Telegram Bot:"
echo "   Отправьте /start в чат"
echo ""
echo "📝 Логи:"
echo "   docker-compose logs -f"
echo ""
