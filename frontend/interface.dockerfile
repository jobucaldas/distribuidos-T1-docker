FROM node:22

WORKDIR /app

ADD meet .

RUN npm install

CMD ["npm", "run", "start"]