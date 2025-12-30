# Stage 1: Build
FROM node:18-slim as build-stage

WORKDIR /app

# Đảm bảo KHÔNG đặt NODE_ENV=production ở đây vì ta cần cài devDependencies để build
ENV NODE_ENV=development

# Copy package.json và package-lock.json
COPY package*.json ./

# Cài đặt tất cả dependencies (bao gồm cả Vite)
RUN npm install

# Sửa lỗi native binding cho Linux (nếu vẫn còn bị)
RUN npm install @rollup/rollup-linux-x64-gnu @swc/core-linux-x64-gnu

RUN npm install react-map-gl maplibre-gl

COPY . .

# Chạy build (Lúc này lệnh 'vite' đã có trong node_modules)
RUN npm run build

RUN ls -la /app
# Stage 2: Serve với Nginx
FROM nginx:stable-alpine
# Copy thư mục dist (Vite build ra dist)
COPY --from=build-stage /app/build /usr/share/nginx/html
# Copy file cấu hình nginx (tùy chọn - nếu bạn có file nginx.conf)
# COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]