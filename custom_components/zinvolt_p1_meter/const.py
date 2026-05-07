"""Constants for the Zinvolt P1-dongle Pro integration."""

from datetime import timedelta

DOMAIN = "zinvolt_p1_dongle_pro"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = timedelta(seconds=2)
DEFAULT_WS_PATH = "/ws"
WS_HEARTBEAT = 30  # seconds
WS_RECONNECT_INITIAL = 5  # seconds before first reconnect attempt
WS_RECONNECT_MAX = 60  # seconds maximum reconnect backoff
