# ---- Etap budowania ----
FROM node:18-bullseye as builder
WORKDIR /app

# Kopiujemy tylko package.json i tsconfig.json
COPY package.json ./

# Instalujemy wszystkie dependencies (devDependencies w tym build tools)
RUN npm install

# Kopiujemy resztę frontendu
COPY . .

#RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*
#RUN find . -type f -exec dos2unix {} \;

RUN ls -l /app/src
RUN cat /app/src/index.tsx

# Sprawdzenie obecności pliku App.tsx w katalogu /app/src
RUN if [ -f /app/src/App.tsx ]; then \
        echo "Plik App.tsx znaleziony ✅"; \
    else \
        echo "Plik App.tsx NIE ZNALEZIONY ❌"; \
        ls -l /app/src; \
        exit 1; \
    fi

ENV NODE_PATH=/app/src

# Budujemy frontend (pomijamy testy)
RUN npm run build -- --verbose

# ---- Etap produkcyjny ----
FROM nginx:stable-alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
