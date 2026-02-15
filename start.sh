#!/bin/bash

echo "🚀 Starting TeamFlow..."
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp backend/.env.example backend/.env
    echo ""
    echo "📝 Please edit backend/.env and add your Telegram bot token and chat ID:"
    echo "   TELEGRAM_BOT_TOKEN=your_token_here"
    echo "   TELEGRAM_CHAT_ID=your_chat_id_here"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "📦 Building and starting containers..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "✅ TeamFlow is ready!"
echo ""
echo "📍 Access:"
echo "   Web UI:   http://localhost:5173"
echo "   API:      http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📱 Telegram Bot:"
echo "   Команды:  /task - создать задачу"
echo "             /week - недельная доска"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Stop:"
echo "   docker-compose down"
