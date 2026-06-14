# Multi-stage Next.js build. Production uses the standalone output;
# dev uses `next dev` with source mounted as a volume (see docker-compose.dev.yml).

FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# --- Production stage (default target) ---
FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Standalone output includes only what's needed to run, much smaller image
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]

# --- Dev stage (selected via `target: dev` in docker-compose.dev.yml) ---
# Carries node_modules from `deps` so `next dev` can start immediately; the
# actual source code is mounted as a volume so edits hot-reload.
FROM node:20-slim AS dev
WORKDIR /app
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1
# Polling-based file watcher — required for Next.js HMR to detect host file
# changes through Docker for Mac's bind mount.
ENV WATCHPACK_POLLING=true
COPY --from=deps /app/node_modules ./node_modules
# Source code will arrive via the bind mount in docker-compose.dev.yml.
EXPOSE 3000
CMD ["npm", "run", "dev"]
