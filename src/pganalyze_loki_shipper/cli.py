from urllib.parse import quote_plus

from websockets.sync.client import connect
import os
import json
import logging
import socket
from logging.handlers import SysLogHandler

LOKI_HOST = os.getenv("LOKI_HOST", None)
LOKI_X_TOKEN = os.getenv("LOKI_TOKEN", None)
LOKI_QUERY = os.getenv("LOKI_QUERY", None)

logger = logging.getLogger(__name__)

def parse_logs(logs: dict):
    result: list[tuple[int, str]] = []
    for log in logs["streams"]:
        for entry in log["values"]:
            result.append((int(entry[0]), entry[1]))

    sorted_result = sorted(result, key=lambda x: x[0])
    yield from [entry[1] for entry in sorted_result]


def stream_logs():
    query = quote_plus(LOKI_QUERY)
    url = f"wss://{LOKI_HOST}/loki/api/v1/tail?query={query}"

    while True:
        try:
            with connect(
                url,
                additional_headers={"X-Token": LOKI_X_TOKEN, "X-Datasource": "product"},
            ) as websocket:
                logger.info(f"Connected to {url}")
                for message in websocket:
                    parsed_message = json.loads(message)
                    yield from parse_logs(parsed_message)
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.exception(e)
            continue


def run_syslog(host: str, port: int):
    syslogger = logging.getLogger("MyLogger")
    syslogger.addHandler(
        SysLogHandler(address=(host, port), socktype=socket.SOCK_STREAM)
    )
    log_count = 0
    for log_message in stream_logs():
        syslogger.info(log_message)
        log_count += 1
        if log_count % 1000 == 0:
            logger.info(f"Sent {log_count} logs to syslog")


def run_stdout():
    for log_message in stream_logs():
        logger.info(log_message)


def main():
    if not LOKI_X_TOKEN:
        raise ValueError("LOKI_TOKEN environment variable is not set")

    if not LOKI_QUERY:
        raise ValueError("LOKI_QUERY environment variable is not set")

    if not LOKI_HOST:
        raise ValueError("LOKI_HOST environment variable is not set")

    pganalyze_syslog = os.getenv("PGANALYZE_SYSLOG", None)
    if pganalyze_syslog:
        logger.info(f"Sending logs to syslog: {pganalyze_syslog}")
        host, port = pganalyze_syslog.split(":")
        run_syslog(host, int(port))
    else:
        logger.info("Sending logs to stdout")
        run_stdout()
