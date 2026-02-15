# Быстрое развертывание TeamFlow на VPS

## 🚀 Один скрипт для полного деплоя

### Вариант 1: Автоматический деплой (рекомендуется)

```bash
# Скопируйте и запустите эту команду на вашем VPS:
curl -sSL https://raw.githubusercontent.com/your-repo/teamflow-mvp/main/deploy.sh | bash
```

### Вариант 2: Пошаговая установка

## Требования

- **VPS:** Ubuntu 20.04/22.04 (или другой Linux)
- **RAM:** минимум 512 MB (рекомендуется 1 GB)
- **Диск:** минимум 2 GB свободного места
- **Провайдеры:** DigitalOcean, Hetzner, Linode, AWS Lightsail, любой другой

## Шаг 1: Подготовка VPS

### 1.1 Подключение к серверу

```bash
ssh root@your-vps-ip
```

### 1.2 Обновление системы

```bash
apt update && apt upgrade -y
```

### 1.3 Установка Docker (один скрипт)

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Проверка
docker --version
docker-compose --version
```

## Шаг 2: Развертывание приложения

### 2.1 Скачивание проекта

**Вариант A: Из Git репозитория**
```bash
git clone https://github.com/your-username/teamflow-mvp.git
cd teamflow-mvp
```

**Вариант B: Загрузка архива**
```bash
# На локальной машине:
scp teamflow-mvp.tar.gz root@your-vps-ip:/root/

# На VPS:
tar -xzf teamflow-mvp.tar.gz
cd teamflow-mvp
```

### 2.2 Настройка окружения

```bash
# Создать .env файл
cp backend/.env.example backend/.env

# Редактировать настройки
nano backend/.env
```

**Важные переменные в .env:**
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=-1001234567890

# Database (SQLite - уже настроен)
DATABASE_URL=sqlite+aiosqlite:///./data/teamflow.db

# Web API
API_HOST=0.0.0.0
API_PORT=8000

# CORS (добавьте IP вашего VPS)
BACKEND_CORS_ORIGINS=["http://your-vps-ip:5173","http://localhost:5173"]
```

### 2.3 Получение Telegram токенов

**Bot Token:**
1. Откройте Telegram, найдите @BotFather
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен → `TELEGRAM_BOT_TOKEN`

**Chat ID:**
```bash
# Добавьте бота в групповой чат
# Отправьте любое сообщение в чат
# Затем выполните:
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

# Найдите "chat":{"id":-1001234567890} → это ваш CHAT_ID
```

**Важно:** Отключите Privacy Mode у бота:
```
@BotFather → /mybots → выберите бота → Bot Settings → 
Group Privacy → Turn off
```

### 2.4 Запуск приложения

```bash
# Запуск
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Проверка статуса
docker-compose ps
```

## Шаг 3: Проверка работы

### 3.1 Проверка API

```bash
curl http://localhost:8000/health
# Должно вернуть: {"status":"healthy"}
```

### 3.2 Проверка бота

В Telegram чате отправьте:
```
/task
```
Бот должен ответить.

### 3.3 Проверка Web UI

Откройте в браузере:
```
http://your-vps-ip:5173
```

## Шаг 4: Настройка Nginx (опционально, для HTTPS)

### 4.1 Установка Nginx

```bash
apt install nginx -y
```

### 4.2 Конфигурация для TeamFlow

```bash
# Создать конфиг
nano /etc/nginx/sites-available/teamflow
```

**Содержимое файла:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Активировать конфиг
ln -s /etc/nginx/sites-available/teamflow /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 4.3 Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
apt install certbot python3-certbot-nginx -y

# Получение сертификата
certbot --nginx -d your-domain.com

# Автообновление (добавится автоматически)
certbot renew --dry-run
```

## Шаг 5: Автозапуск при перезагрузке

```bash
# Docker автоматически настроен на автозапуск
# Но можно добавить в systemd для надежности:

cat > /etc/systemd/system/teamflow.service <<EOF
[Unit]
Description=TeamFlow Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/root/teamflow-mvp
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl enable teamflow
systemctl start teamflow
```

## 🔧 Управление приложением

### Основные команды

```bash
# Остановить
docker-compose down

# Запустить
docker-compose up -d

# Перезапустить
docker-compose restart

# Обновить (после git pull)
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f backend
docker-compose logs -f frontend

# Зайти в контейнер
docker exec -it teamflow-backend bash

# Просмотр базы данных
docker exec -it teamflow-backend sqlite3 /app/data/teamflow.db
```

### Резервное копирование

```bash
# Бэкап базы данных
docker cp teamflow-backend:/app/data/teamflow.db ./backup-$(date +%Y%m%d).db

# Автоматический бэкап (добавить в cron)
cat > /root/backup-teamflow.sh <<EOF
#!/bin/bash
docker cp teamflow-backend:/app/data/teamflow.db /root/backups/teamflow-\$(date +\%Y\%m\%d-\%H\%M).db
# Удалить бэкапы старше 30 дней
find /root/backups -name "teamflow-*.db" -mtime +30 -delete
EOF

chmod +x /root/backup-teamflow.sh

# Добавить в cron (каждый день в 2:00)
echo "0 2 * * * /root/backup-teamflow.sh" | crontab -
```

## 🚀 Быстрый деплой скрипт

Создайте файл `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 TeamFlow Quick Deploy Script"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1/5: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo -e "${GREEN}✓ Docker installed${NC}"

echo -e "${YELLOW}Step 2/5: Cloning repository...${NC}"
if [ ! -d "teamflow-mvp" ]; then
    git clone https://github.com/your-username/teamflow-mvp.git
fi
cd teamflow-mvp

echo -e "${GREEN}✓ Repository cloned${NC}"

echo -e "${YELLOW}Step 3/5: Configuring environment...${NC}"
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo ""
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your Telegram credentials:${NC}"
    echo "   nano backend/.env"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

echo -e "${GREEN}✓ Environment configured${NC}"

echo -e "${YELLOW}Step 4/5: Building containers...${NC}"
docker-compose build

echo -e "${GREEN}✓ Containers built${NC}"

echo -e "${YELLOW}Step 5/5: Starting application...${NC}"
docker-compose up -d

echo ""
echo -e "${GREEN}✅ TeamFlow deployed successfully!${NC}"
echo ""
echo "📍 Access:"
echo "   Web UI:   http://$(curl -s ifconfig.me):5173"
echo "   API:      http://$(curl -s ifconfig.me):8000"
echo "   API Docs: http://$(curl -s ifconfig.me):8000/docs"
echo ""
echo "📊 Check logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop:"
echo "   docker-compose down"
```

Сделайте скрипт исполняемым:
```bash
chmod +x deploy.sh
./deploy.sh
```

## 💰 Рекомендуемые VPS провайдеры

### Бюджетные варианты (от $5/мес):

1. **Hetzner Cloud** (рекомендуется)
   - €4.15/мес (1 vCPU, 2GB RAM)
   - Отличная производительность
   - Дата-центры в Европе

2. **DigitalOcean**
   - $6/мес (1 vCPU, 1GB RAM)
   - Простая панель управления
   - Много туториалов

3. **Linode**
   - $5/мес (1 vCPU, 1GB RAM)
   - Надежный сервис

4. **Vultr**
   - $6/мес (1 vCPU, 1GB RAM)
   - Много локаций

### Команда для создания Droplet на DigitalOcean:

```bash
# Через CLI
doctl compute droplet create teamflow \
  --region fra1 \
  --size s-1vcpu-1gb \
  --image ubuntu-22-04-x64 \
  --ssh-keys your-ssh-key-id
```

## 🔍 Troubleshooting

### Проблема: Бот не отвечает

```bash
# Проверьте логи
docker-compose logs backend | grep -i error

# Проверьте, что бот запущен
docker-compose ps

# Убедитесь, что токен правильный
cat backend/.env | grep TELEGRAM_BOT_TOKEN
```

### Проблема: База данных недоступна

```bash
# Проверьте права на папку data
docker exec teamflow-backend ls -la /app/data/

# Пересоздайте базу
docker-compose down
rm -rf backend/data/teamflow.db
docker-compose up -d
```

### Проблема: Порты заняты

```bash
# Проверьте, что порты свободны
netstat -tulpn | grep -E '5173|8000'

# Измените порты в docker-compose.yml
# Вместо "5173:5173" используйте "8080:5173"
```

### Проблема: Не хватает памяти

```bash
# Добавьте swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

## 📱 Проверка работоспособности

После деплоя выполните:

```bash
# 1. Health check API
curl http://localhost:8000/health

# 2. Проверка задач
curl http://localhost:8000/api/tasks

# 3. Проверка статистики
curl http://localhost:8000/api/stats

# 4. Telegram bot
# Отправьте в чат: /task
```

## 🔐 Безопасность

### Базовая защита:

```bash
# Настройка firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Изменить SSH порт (опционально)
nano /etc/ssh/sshd_config
# Port 22 → Port 2222
systemctl restart sshd

# Отключить root login
nano /etc/ssh/sshd_config
# PermitRootLogin no
```

### Мониторинг:

```bash
# Установить htop
apt install htop -y

# Мониторинг ресурсов
htop

# Размер базы данных
du -sh backend/data/teamflow.db
```

---

## ⚡ TL;DR - Самый быстрый способ

```bash
# На VPS:
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Загрузите teamflow-mvp.tar.gz на VPS
tar -xzf teamflow-mvp.tar.gz && cd teamflow-mvp

# Настройте .env
cp backend/.env.example backend/.env
nano backend/.env  # Добавьте TELEGRAM_BOT_TOKEN и CHAT_ID

# Запустите
docker-compose up -d --build

# Готово!
```

**Время развертывания: ~5 минут** ⏱️
