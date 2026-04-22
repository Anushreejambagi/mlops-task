import argparse
import pandas as pd
import numpy as np
import yaml
import logging
import json
import time
import sys
import os


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError("Config file not found")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    required_keys = ["seed", "window", "version"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")

    return config


def load_data(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError("Input file not found")

    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("CSV file is empty")

    if "close" not in df.columns:
        raise ValueError("Missing 'close' column")

    return df


def compute_signal(df, window):
    logging.info("Starting rolling mean computation")

    df["rolling_mean"] = df["close"].rolling(window=window).mean()

    # Handle first window-1 rows by dropping NaNs
    df = df.dropna().reset_index(drop=True)

    logging.info("Generating signals")

    df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()

    setup_logging(args.log_file)

    start_time = time.time()

    try:
        logging.info("Job started")

        config = load_config(args.config)
        np.random.seed(config["seed"])

        logging.info(f"Config loaded: {config}")

        df = load_data(args.input)
        logging.info(f"Rows loaded: {len(df)}")

        df = compute_signal(df, config["window"])

        signal_rate = df["signal"].mean()
        rows_processed = len(df)
        latency_ms = int((time.time() - start_time) * 1000)

        logging.info(f"Signal rate: {signal_rate}")
        logging.info(f"Latency: {latency_ms} ms")

        metrics = {
            "version": config["version"],
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(float(signal_rate), 4),
            "latency_ms": latency_ms,
            "seed": config["seed"],
            "status": "success"
        }

        with open(args.output, "w") as f:
            json.dump(metrics, f, indent=4)

        logging.info(f"Metrics: {metrics}")
        logging.info("Job completed successfully")

        print(json.dumps(metrics, indent=4))
        sys.exit(0)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        error_output = {
            "version": "v1",
            "status": "error",
            "error_message": str(e),
            "latency_ms": latency_ms
        }

        with open(args.output, "w") as f:
            json.dump(error_output, f, indent=4)

        logging.error(f"Error: {str(e)}")
        print(json.dumps(error_output, indent=4))

        sys.exit(1)


if __name__ == "__main__":
    main()