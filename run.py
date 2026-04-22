import argparse
import pandas as pd
import yaml
import json
import time
import logging
import sys
import numpy as np


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def process_data(df, window):
    df["rolling_mean"] = df["close"].rolling(window=window).mean()
    df = df.dropna()

    df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)

    signal_rate = df["signal"].mean()
    return df, signal_rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()

    start_time = time.time()

    try:
        setup_logging(args.log_file)
        logging.info("Pipeline started")

        # Load config
        config = load_config(args.config)
        window = config.get("window", 5)
        seed = config.get("seed", 42)

        np.random.seed(seed)

        # Load data
        df = pd.read_csv(args.input)

        if df.empty:
            raise ValueError("Input dataset is empty")

        if "close" not in df.columns:
            raise ValueError("Missing 'close' column")

        total_rows = len(df)  # 👈 keep original row count

        # Process data
        df_processed, signal_rate = process_data(df, window)

        latency = int((time.time() - start_time) * 1000)

        output = {
            "version": "v1",
            "rows_processed": total_rows,  # 👈 shows ~10000
            "metric": "signal_rate",
            "value": round(float(signal_rate), 4),
            "latency_ms": latency,
            "seed": seed,
            "status": "success"
        }

        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)

        logging.info(f"Total rows: {total_rows}")
        logging.info(f"Signal rate: {signal_rate}")
        logging.info("Pipeline completed successfully")

        print(json.dumps(output, indent=2))

        sys.exit(0)

    except Exception as e:
        latency = int((time.time() - start_time) * 1000)

        error_output = {
            "version": "v1",
            "status": "error",
            "error_message": str(e),
            "latency_ms": latency
        }

        with open(args.output, "w") as f:
            json.dump(error_output, f, indent=2)

        logging.error(f"Error occurred: {str(e)}")

        print(json.dumps(error_output, indent=2))

        sys.exit(1)


if __name__ == "__main__":
    main()