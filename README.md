# MLOps Task - Batch Pipeline

## Overview

This project implements a minimal MLOps-style batch pipeline in Python.

It demonstrates:

* Reproducibility using config + seed
* Observability using logs and metrics
* Deployment readiness using Docker

---

## Dataset

* Dataset contains ~10,000 rows (OHLCV format)
* Only the `close` column is used for calculations

---

## Run Locally

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## Run with Docker

```bash
docker build -t mlops-task .
docker run --rm mlops-task
```

---

## Success Output (metrics.json)

```json
{
  "version": "v1",
  "rows_processed": 9996,
  "metric": "signal_rate",
  "value": 0.49,
  "latency_ms": 120,
  "seed": 42,
  "status": "success"
}
```

---

## Error Output (metrics.json)

```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Missing 'close' column",
  "latency_ms": 10
}
```

---

## Processing Details

### Rolling Mean

* Computed using window from config
* First `window-1` rows are dropped (NaN handling)

### Signal Logic

* `1` if close > rolling_mean
* `0` otherwise

---

## Features

* Deterministic execution (fixed seed)
* YAML-based configuration
* Input validation:

  * Missing file
  * Invalid CSV
  * Empty dataset
  * Missing `close` column
* Structured JSON metrics output
* Logging of all processing steps
* Error handling with JSON output
* No hardcoded paths

---

## Logging (run.log)

Includes:

* Job start timestamp
* Config validation
* Rows loaded
* Processing steps
* Metrics summary
* Job end status
* Errors (if any)

---

## Exit Codes

* `0` → Success
* Non-zero → Failure

---

## Docker Notes

* Uses `python:3.9-slim`
* Includes data.csv and config.yaml
* Outputs metrics.json and run.log
* Prints metrics JSON to stdout

---

## Compliance Checklist

* ✔ CLI-based execution
* ✔ Deterministic results (seed)
* ✔ Rolling mean + signal generation
* ✔ Structured metrics (success + error)
* ✔ Logging and observability
* ✔ Dockerized pipeline
* ✔ No hardcoded paths
