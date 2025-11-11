# Options Pricer Server

A lightweight C++ HTTP server for Black-Scholes option pricing with Prometheus metrics. Designed for demonstration, development, or testing purposes. Runs in Docker.

## Rationale

- Serve option pricing via a simple HTTP API.
- Provide real-time Prometheus metrics for monitoring requests and a synthetic demo gauge.
- Minimal dependencies, easy to build and run in a container.
- Recommended to run in a dedicated VM if you want to avoid interfering with existing Docker containers.

## Build & Run

```bash
docker-compose up --build -d
```

- Pricer server listens on **port 8080**.
- Prometheus listens on **port 9090**.

## API Usage

### Get call and put prices

```bash
curl "http://localhost:8080/price?spot=100&strike=100&expiry=1&rate=0.05&vol=0.2"
```

Example response:

```json
{"call": 10.450583, "put": 5.573526}
```

### Prometheus Metrics

Visit `http://localhost:8080/metrics` to see:

- `requests_total` – total pricing requests
- `errors_total` – failed requests
- `request_duration_seconds` – duration of last request
- `in_flight_requests` – currently active requests
- `demo_gauge` – synthetic gauge for demo purposes

### UI (search for demo_gauge in Graph)
http://localhost:9090/

### Health Check

```bash
curl http://localhost:8080/healthz
```

Expected response:

```
ok
```

## Fuzzing / Performance Testing

The project includes a minimal fuzz/performance test setup to validate the `pricer_server` binary.  

- **Purpose:** Exercise the server with random input to catch edge-case errors and observe performance under load.  
- **Usage:**  

```bash
./fuzz_perf.sh
```