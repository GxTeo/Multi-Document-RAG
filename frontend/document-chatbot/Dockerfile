FROM node:latest

WORKDIR /app

COPY package*.json ./

RUN npm install --force

RUN npm install -g serve --force

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]