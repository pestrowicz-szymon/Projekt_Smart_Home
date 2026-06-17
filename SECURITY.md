# Security Configuration & Production Readiness

This document outlines the security measures implemented in the Smart Home project and provides a checklist for transitioning from a development (local) environment to a production environment.

## 1. MQTT Communication (Mosquitto)

### Current Development State
- **Port**: 8883 (MQTTS).
- **Encryption**: TLS enabled using self-signed certificates.
- **Verification**: `tls_insecure_set(True)` is used in the backend to bypass hostname verification (allowing 'localhost' to connect even if the certificate is issued for 'mosquitto').
- **Authentication**: Certificate-based authentication is configured but not strictly enforced for all client types in dev.

### Production Requirements
- [ ] **Hostname Verification**: Set `client.tls_insecure_set(False)` in `backend/devices/mqtt_bridge.py`. Certificates must match the server's production FQDN.
- [ ] **Certificate Authority**: Use certificates from a trusted CA (e.g., Let's Encrypt) or a strictly managed private PKI.
- [ ] **Secrets Management**: Do not store `.crt` or `.key` files in the repository. Use a secure volume mount or secret provider (e.g., Docker Secrets, HashiCorp Vault).

## 2. Backend (Django / ASGI)

### Current Development State
- **Server**: Running via `uvicorn` with `--reload`.
- **SSE**: Server-Sent Events implemented using PostgreSQL `LISTEN/NOTIFY`.
- **CORS**: Configured to allow requests from `localhost:5173`.
- **Auth**: JWT tokens are used, proxied through SvelteKit.

### Production Requirements
- [ ] **DEBUG Mode**: Ensure `DEBUG=False` in `backend/.env`.
- [ ] **Secret Key**: Remove any hardcoded fallbacks for `SECRET_KEY`. It must be a unique, high-entropy string provided via environment variables.
- [ ] **Allowed Hosts**: Explicitly define `ALLOWED_HOSTS` with production domains only.
- [ ] **SSL/HTTPS**: Enable `SECURE_SSL_REDIRECT=True` and ensure the application is behind a reverse proxy (Nginx/Traefik) handling TLS termination.
- [ ] **CORS**: Restrict `CORS_ALLOWED_ORIGINS` to the specific production frontend domain.

## 3. Frontend (SvelteKit)

### Current Development State
- **Proxy**: `/api/events` proxies the backend SSE stream to bypass CORS and handle `httpOnly` cookies.
- **Environment**: Using `.env` with `API_URL=http://localhost:8000`.

### Production Requirements
- [ ] **HTTPS**: Update `API_URL` to use `https://`.
- [ ] **Secure Cookies**: Ensure session cookies are marked as `Secure` (already configured in `hooks.server.ts` but depends on HTTPS being active).

## 4. Real-Time Infrastructure

### Current Development State
- **PostgreSQL**: Standard connection strings in `.env`.
- **Notifications**: PostgreSQL `NOTIFY` payload is unencrypted in the DB log (though the connection to the DB is internal).

### Production Requirements
- [ ] **DB Encryption**: Ensure the connection between the Django ASGI workers and the PostgreSQL database uses TLS (`sslmode=verify-full`).
- [ ] **Resource Limits**: Configure Uvicorn worker limits and PostgreSQL connection pooling (e.g., PgBouncer) to handle high concurrent SSE connections.
