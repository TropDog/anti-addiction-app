# Stage 1: build React app
FROM node:20-alpine AS builder
WORKDIR /app

# Build-time env
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: nginx
FROM nginx:alpine

# Usuń domyślne pliki
RUN rm -rf /usr/share/nginx/html/*

# Skopiuj build React i szablon configu Nginx
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/conf.d/nginx.conf.template

# Expose port
EXPOSE 80

# CMD – zamień zmienną BACKEND_HOST i uruchom nginx
CMD envsubst '$BACKEND_HOST' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/default.conf && \
    nginx -g 'daemon off;'
