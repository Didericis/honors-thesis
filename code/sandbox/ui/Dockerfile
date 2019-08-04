FROM node:12

RUN mkdir -p /code

COPY package.json package-lock.json /tmp/
RUN cd /tmp && npm install
RUN cd /code && ln -s /tmp/node_modules

WORKDIR /code

COPY . .

EXPOSE 3000

ARG API_URL

RUN npm run build
RUN npm install -g serve
