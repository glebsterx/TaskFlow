FROM node:20-alpine

WORKDIR /app

# Копируем package files
COPY package*.json ./
RUN npm install

# Копируем .env ПЕРЕД сборкой
COPY .env* ./

# Копируем остальное
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
