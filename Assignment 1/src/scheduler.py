import random
import socket
import threading
from typing import Dict, List, Optional, Tuple

from config.parser import load_airports, load_routes
from scripts.name_generator import random_full_name

# Scheduler ip/port for nodes to connect to.
SCHEDULER_HOST = "127.0.0.1"
SCHEDULER_PORT = 6500

PAYLOADS = [
    lambda: f"Passenger: {random_full_name()}",
    lambda: "Cargo",
]


class Scheduler:
    """Listens for airport registrations and hands back a simple flight plan."""

    def __init__(self, airports: Dict[str, str], hubs: List[str], default_hub: Dict[str, List[str]]) -> None:
        self.airports = airports
        self.hubs = hubs
        self.default_hub = default_hub
        self._lock = threading.Lock()
        self._server_socket: Optional[socket.socket] = None
        self._flight_counter = 0

    def start(self) -> None:
        """Kick off the TCP server in its own daemon thread."""
        thread = threading.Thread(target=self._serve, daemon=True)
        thread.start()

    def _serve(self) -> None:
        """Accept incoming airport registrations forever."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((SCHEDULER_HOST, SCHEDULER_PORT))
            server.listen(8)
            self._server_socket = server
            print(f"[scheduler] listening on {SCHEDULER_HOST}:{SCHEDULER_PORT}")

            while True:
                conn, addr = server.accept()
                threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()

    def _handle_client(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """Handle a single node from register -> plan -> ack."""
        with conn:
            try:
                # First message is just the airport code (e.g. "ANC").
                raw = conn.recv(1024)
                airport_code = raw.decode("utf-8").strip().upper()
                if not airport_code:
                    return
                print(f"[scheduler] {airport_code} registered from {addr}")

                plan = self._make_plan_for(airport_code)
                conn.sendall(plan.encode("utf-8"))

                # wait for any acknowledgement so nodes can tell us they are done
                ack = conn.recv(1024).decode("utf-8").strip()
                if ack:
                    print(f"[scheduler] {airport_code} finished flight: {ack}")
            except OSError as exc:
                print(f"[scheduler] lost connection to {addr}: {exc}")

    def _make_plan_for(self, origin: str) -> str:
        """Pick a destination and optional hub, then build a tiny text message."""
        with self._lock:
            self._flight_counter += 1
            if self._flight_counter > 9999:
                self._flight_counter = 1
            flight_id = self._flight_counter
            candidates = [code for code in self.airports if code != origin]
            if not candidates:
                return f"FLIGHT {origin} | holding pattern | id:{flight_id:04d}"
            destination = random.choice(candidates)
            layover_options = self.default_hub.get(destination, [])

        # Route String
        legs = [origin]
        layover = None
        if layover_options:
            viable = [hub for hub in layover_options if hub != origin]
            if viable:
                layover = random.choice(viable)
        if layover:
            legs.append(layover)
        legs.append(destination)

        payload = random.choice(PAYLOADS)()
        route_str = " >> ".join(legs)
        message = f"FLIGHT {route_str} | {payload} | id:{flight_id:04d}"
        print(f"[scheduler] plan for {origin}: {message}")
        return message


def bootstrap_scheduler() -> Scheduler:
    """Helper for main.py. Loads config and returns a running scheduler."""
    airports = load_airports("src/airports.yaml")
    hubs, default_hub = load_routes("src/routes.yaml")
    scheduler = Scheduler(airports, hubs, default_hub)
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    # For Testing (quit doesnt work warning)
    bootstrap_scheduler()
    print("[scheduler] press Ctrl+C to quit")
    try:
        while True:
            threading.Event().wait(60)
    except KeyboardInterrupt:
        print("\n[scheduler] shutdown requested")
