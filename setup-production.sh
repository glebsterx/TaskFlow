#!/bin/bash
# Скрипт настройки TeamFlow для production

echo "🔧 TeamFlow - Настройка для production"
echo ""

# Запрос домена
read -p "Введите ваш домен (например: server.example.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "❌ Домен не может быть пустым!"
    exit 1
fi

echo ""
echo "📝 Настройка конфигурации для: $DOMAIN"
echo ""

# Обновляем .env в корне
cat > .env << EOF
# Docker Compose Environment Variables
BACKEND_PORT=8180
FRONTEND_PORT=5180
BASE_URL=https://$DOMAIN
EOF

echo "✅ Создан .env (корень)"

# Обновляем frontend/.env
cat > frontend/.env << EOF
# Frontend Environment Variables
VITE_API_URL=https://$DOMAIN:8180
EOF

echo "✅ Создан frontend/.env"

# Обновляем backend/.env если не существует
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Создан backend/.env из примера"
    echo ""
    echo "⚠️  ВАЖНО: Настройте backend/.env:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID"
    echo "   - TELEGRAM_BOT_USERNAME"
fi

# Обновляем CORS в backend/.env
echo ""
echo "📝 Обновляем CORS в backend/.env..."

# Создаём правильный CORS
CORS_LINE="BACKEND_CORS_ORIGINS=[\"https://$DOMAIN\",\"https://$DOMAIN:5180\",\"http://$DOMAIN:5180\"]"

# Удаляем старую строку CORS если есть
grep -v "^BACKEND_CORS_ORIGINS=" backend/.env > backend/.env.tmp || true
mv backend/.env.tmp backend/.env

# Добавляем новую
echo "$CORS_LINE" >> backend/.env

echo "✅ CORS обновлён"

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "📋 Конфигурация:"
echo "   Домен: https://$DOMAIN"
echo "   Backend: https://$DOMAIN:8180"
echo "   Frontend: https://$DOMAIN:5180"
echo ""
echo "🚀 Следующие шаги:"
echo "   1. Настройте backend/.env (токены Telegram)"
echo "   2. Запустите: docker-compose down"
echo "   3. Запустите: docker-compose build --no-cache"
echo "   4. Запустите: docker-compose up -d"
echo ""
