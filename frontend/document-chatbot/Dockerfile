FROM node:latest

WORKDIR /app

COPY package*.json ./

RUN npm install --force

COPY . .

RUN npm install -g serve --force

# RUN npm run build

EXPOSE 3000

# CMD ["serve", "-s", "build", "-l", "3000"]
ENV PORT=3000
CMD ["npm", "run", "start"]