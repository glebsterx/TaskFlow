# TeamFlow v0.3.0 - Production Ready

## 🚀 Быстрый старт

```bash
./quick-start.sh
```

## 📋 Настройка

1. **Корневой .env:**
   ```bash
   cp .env.example .env
   ```

2. **Backend .env:**
   ```bash
   cp backend/.env.example backend/.env
   nano backend/.env  # Добавьте токены
   ```

3. **Запуск:**
   ```bash
   docker-compose up --build -d
   ```

## 📱 Доступ

- Web UI: http://localhost:5180
- API: http://localhost:8180

## 🔧 Порты

Настраиваются в `.env`:
```env
BACKEND_PORT=8180
FRONTEND_PORT=5180
BASE_URL=http://localhost
```

## 🐛 Ошибка ContainerConfig?

```bash
./clean-all.sh
docker-compose up --build -d
```

---

MIT License
