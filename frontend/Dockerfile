FROM node:20-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./
RUN npm install

# Копируем всё остальное (включая .env)
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
