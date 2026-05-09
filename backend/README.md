This backend exposes a JWT-protected REST API for users, homes, devices, sensor readings, and device actions.

## Database

The backend uses PostgreSQL by default. Set these environment variables before running the server:

- `POSTGRES_DB` - database name, for example `smarthome_db`
- `POSTGRES_USER` - database user, for example `postgres`
- `POSTGRES_PASSWORD` - database password
- `POSTGRES_HOST` - database host, for example `localhost`
- `POSTGRES_PORT` - database port, for example `5432`

Example local setup:

```powershell
$env:POSTGRES_DB = "smarthome_db"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "your_password"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
```
Swagger UI is available at:

`http://localhost:8000/api/docs/`