# Pod-Siksha: Production Deployment Guide

## 1. Live Public Deployment Reference
Pod-Siksha is deployed and publicly accessible over secure HTTPS:

- **Public Application URL:** [https://fairly-private-supported-killing.trycloudflare.com](https://fairly-private-supported-killing.trycloudflare.com)
- **Teacher Observatory URL:** [https://fairly-private-supported-killing.trycloudflare.com/teacher](https://fairly-private-supported-killing.trycloudflare.com/teacher)
- **Health Check Endpoint:** [https://fairly-private-supported-killing.trycloudflare.com/api/health](https://fairly-private-supported-killing.trycloudflare.com/api/health)
- **Deployment Strategy:** Cloudflare Managed Edge Tunnel with SSL/TLS termination, QUIC protocol, zero open inbound firewall ports, and persistent SQLite storage.

---

## 2. Infrastructure & Environment Architecture

```
                                  [ Internet / Judges ]
                                            |
                                            v (HTTPS / TLS 1.3)
                         [ Cloudflare Edge Network (QUIC) ]
                                            |
                                            v (Encrypted Tunnel)
                         [ Local Host / Pod-Siksha Service ]
                               +------------+------------+
                               |                         |
                               v                         v
                       [ FastAPI Backend ]       [ SQLite Database ]
                         (Uvicorn :8008)           (pod_siksha.db)
                               |
                +--------------+---------------+
                |                              |
                v                              v
      [ Live Gnani AI APIs ]         [ Live Google Gemini ]
      - Prisma STT v3.0              - gemini-3.5-flash-lite
      - Timbre TTS v3.0 (Shivani/Yashraj)
```

---

## 3. Required Environment Variables

All secrets are maintained strictly on the server:

| Variable | Description | Example / Allowed Value |
|---|---|---|
| `GNANI_API_KEY` | Authentication token for Gnani Prisma STT & Timbre TTS | Configured in `.env` |
| `GEMINI_API_KEY` | Authentication token for Google Gemini GenAI SDK | Configured in `.env` |
| `GNANI_STT_URL` | Endpoint for Prisma STT v3 API | `https://api.vachana.ai/stt/v3` |
| `GNANI_TTS_URL` | Endpoint for Timbre TTS v3 inference API | `https://api.vachana.ai/api/v1/tts/inference` |
| `GNANI_VOICE_A` | Voice model for Host A & oral quiz questions | `Shivani` |
| `GNANI_VOICE_B` | Voice model for Host B | `Yashraj` |
| `LLM_MODEL` | Google Gemini model identifier | `gemini-3.5-flash-lite` |
| `DATABASE_PATH` | Path to persistent SQLite database | `./pod_siksha.db` |
| `PORT` | Listening port for FastAPI / Uvicorn | `8008` |

---

## 4. Container & Alternative Cloud Deployments (Docker / Railway / Render)

### Dockerfile (`Dockerfile`)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8008

CMD ["python", "server.py"]
```

### Persistent Volume Configuration (Important Rule)
If migrating to Render or Railway:
- **Render**: Render Web Services use ephemeral disks on the free tier. To prevent wiping `pod_siksha.db` on restart, a persistent Render Disk must be attached and `DATABASE_PATH` set to `/data/pod_siksha.db`.
- **Railway**: Add a Volume mount pointing to `/app/pod_siksha.db`.

---

## 5. Production Health Monitoring
A dedicated health endpoint (`/api/health`) provides status telemetry:
```bash
curl https://fairly-private-supported-killing.trycloudflare.com/api/health
```
Response:
```json
{
  "status": "healthy",
  "service": "Pod-Siksha",
  "version": "2.0.0",
  "environment": "production",
  "database": "connected",
  "gnani_stt": "configured",
  "gnani_tts": "configured",
  "gemini_api": "configured",
  "timestamp": "2026-11-09T16:07:13.891877"
}
```
