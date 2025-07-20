# Observability Setup

NotebookLlaMa includes comprehensive observability features using OpenTelemetry and Jaeger for tracing and monitoring.

## Overview

The application uses:
- **OpenTelemetry** for distributed tracing
- **Jaeger** for trace collection and visualization
- **PostgreSQL** for storing trace data
- **Adminer** for database management

## Quick Start

### 1. Start Required Services

Use the service manager script to start all required services:

```bash
python tools/start_services.py
```

Or manually start Docker services:

```bash
docker compose up -d
```

### 2. Verify Services

Check that all services are running:

```bash
# Check service status
python tools/start_services.py

# Or manually check ports
curl http://localhost:16686  # Jaeger UI
curl http://localhost:4318   # OTLP Collector
curl http://localhost:5432   # PostgreSQL
curl http://localhost:8080   # Adminer
```

### 3. Access Observability Tools

- **Jaeger UI**: http://localhost:16686
- **Adminer**: http://localhost:8080
- **PostgreSQL**: localhost:5432

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Observability Configuration
ENABLE_OBSERVABILITY="true"
OTLP_ENDPOINT="http://localhost:4318/v1/traces"

# Database Configuration
pgql_db="notebookllama"
pgql_user="llama"
pgql_psw="your_password"
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_OBSERVABILITY` | `true` | Enable/disable observability features |
| `OTLP_ENDPOINT` | `http://localhost:4318/v1/traces` | OTLP collector endpoint |

## Quick Fixes

### Disable Observability (Immediate Fix)

If you're experiencing OpenTelemetry errors, quickly disable observability:

```bash
# Quick disable for current session
python tools/disable_observability.py

# Then run your application
uv run src/notebookllama/server.py
```

### Permanent Disable

Add to your `.env` file:
```bash
ENABLE_OBSERVABILITY="false"
```

## Troubleshooting

### Common Issues

#### 1. "Connection refused" errors

**Symptoms:**
```
ConnectionRefusedError: [Errno 61] Connection refused
HTTPConnectionPool(host='localhost', port=4318): Max retries exceeded
```

**Quick Fix:**
```bash
# Disable observability immediately
python tools/disable_observability.py
```

**Full Fix:**
1. Start Docker services:
   ```bash
   docker compose up -d
   ```

2. Check if Docker is running:
   ```bash
   docker version
   ```

3. Check service logs:
   ```bash
   docker compose logs jaeger
   ```

#### 2. "Overriding of current TracerProvider is not allowed"

**Symptoms:**
```
Overriding of current TracerProvider is not allowed
```

**Solution:**
The application now handles this automatically by disabling OpenTelemetry at the SDK level when `ENABLE_OBSERVABILITY=false`.

#### 3. Database connection errors

**Symptoms:**
```
Failed to connect to database
```

**Solutions:**
1. Check PostgreSQL is running:
   ```bash
   docker compose ps postgres
   ```

2. Verify database credentials in `.env`
3. Check database logs:
   ```bash
   docker compose logs postgres
   ```

### Disabling Observability

#### Method 1: Environment Variable (Recommended)
```bash
# Set in .env file
ENABLE_OBSERVABILITY="false"
```

#### Method 2: Quick Script
```bash
python tools/disable_observability.py
```

#### Method 3: Runtime Environment Variable
```bash
export ENABLE_OBSERVABILITY=false
uv run src/notebookllama/server.py
```

### Manual Service Management

#### Start individual services:

```bash
# Start Jaeger only
docker compose up -d jaeger

# Start PostgreSQL only
docker compose up -d postgres

# Start all services
docker compose up -d
```

#### Stop services:

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

#### View logs:

```bash
# All services
docker compose logs

# Specific service
docker compose logs jaeger
docker compose logs postgres
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │───▶│  Jaeger (4318)  │───▶│   PostgreSQL    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  OpenTelemetry  │    │   Jaeger UI     │    │     Adminer     │
│   Instrumentation│    │   (16686)       │    │    (8080)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## How It Works

### SDK-Level Disabling

When `ENABLE_OBSERVABILITY=false`, the application sets these environment variables:

```bash
OTEL_TRACES_SAMPLER="off"
OTEL_TRACES_EXPORTER="none"
OTEL_METRICS_EXPORTER="none"
OTEL_LOGS_EXPORTER="none"
```

This disables OpenTelemetry at the SDK level, preventing:
- Trace collection
- Export attempts
- TracerProvider conflicts
- Connection errors

### Graceful Degradation

The application includes multiple layers of error handling:
1. **SDK-level disabling** (prevents errors)
2. **Application-level error handling** (catches any remaining errors)
3. **Graceful fallbacks** (continues without observability)

## Performance Considerations

- Observability adds minimal overhead when properly configured
- Traces are sampled and buffered to reduce impact
- Database writes are asynchronous
- Graceful degradation prevents application crashes
- SDK-level disabling eliminates all overhead when disabled

## Security Notes

- Services are exposed on localhost only
- No authentication required for local development
- For production, consider:
  - Network isolation
  - Authentication for Jaeger UI
  - Database access controls
  - TLS encryption 