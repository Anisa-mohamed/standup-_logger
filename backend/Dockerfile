# --- Build frontend assets ---
FROM node:20-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm install
COPY frontend ./
RUN npm run build

# --- Build Python backend ---
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
RUN mkdir -p uploads

ENV FLASK_ENV=production
ENV PORT=5000
EXPOSE 5000

CMD ["gunicorn", "-k", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "run:app"]
