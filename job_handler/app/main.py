import logging
import yaml
import sys
import argparse
from app.model.job_handler import JobHandler

def load_config(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Job Handler Microservice")
    parser.add_argument(
        "--config", type=str, default="config/job_handler_config.yaml",
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run in test mode (print config and exit)"
    )
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    print("=== Job Handler Microservice ===")

    config = load_config(args.config)
    print(f"Loaded config: {config}")

    if args.test:
        print("Test mode enabled. Exiting after config print.")
        return

    broker_host = config["mqtt"]["host"]
    broker_port = config["mqtt"]["port"]
    queue_manager_url = config["queue_manager"]["url"]

    handler = JobHandler(broker_host, broker_port, queue_manager_url)
    try:
        handler.start()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received, shutting down...")
        handler.stop()

if __name__ == "__main__":
    main()