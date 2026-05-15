# ETAPA 1: Construcción (Build)
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# ETAPA 2: Servidor (Nginx)
FROM nginx:alpine
# Copiamos la configuración de Nginx con el proxy configurado
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copiamos los archivos estáticos generados por Angular
# Para Angular 17+ el output suele estar en dist/frontend/browser
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
