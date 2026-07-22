FROM node:20-alpine

WORKDIR /app

# Copy package files first (for caching)
COPY package.json package-lock.json* ./

# Install dependencies (cached layer)
RUN npm install

# Copy rest of frontend code
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
