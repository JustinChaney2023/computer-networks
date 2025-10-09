import json
import socket
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .scheduler import SCHEDULER_HOST, SCHEDULER_PORT

# Each airport runs the same Node class with a different code/port.

class Node:
    """Simple TCP peer that can accept flights and fly to other peers."""

    def __init__(
        self,
        code: str,
        listen_host: str,
        listen_port: int,
        airports: Dict[str, str],
    ) -> None:
        self.code = code.upper()
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.airports = airports
        self.running = False
        self._server_thread: Optional[threading.Thread] = None
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        self.log_path = log_dir / f"{self.code.lower()}.log"

    def start(self) -> None:
        """Start the listener and grab a flight plan from the scheduler."""
        if self.running:
            return
        self.running = True
        self._server_thread = threading.Thread(target=self._serve_forever, daemon=True)
        self._server_thread.start()
        self._log(f"Node {self.code} started on {self.listen_host}:{self.listen_port}")

        # Hop onto the scheduler in the background so main() can keep launching nodes. (gpt assist)
        threading.Thread(target=self._request_and_fly, daemon=True).start()

    def _serve_forever(self) -> None:
        """Accept inbound flights and log the details."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.listen_host, self.listen_port))
            server.listen(4)
            self._log("Ready for arrivals.")

            while self.running:
                try:
                    conn, addr = server.accept()
                except OSError:
                    break
                threading.Thread(target=self._handle_arrival, args=(conn, addr), daemon=True).start()

    def _handle_arrival(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """Handle one inbound connection until it closes."""
        with conn:
            raw = conn.recv(1024).decode("utf-8").strip()
            if not raw:
                return

            flight = self._try_parse_flight_message(raw)
            if not flight:
                self._log(f"Arrival from {addr}: {raw}")
                conn.sendall(f"ACK from {self.code}".encode("utf-8"))
                return

            legs: List[str] = flight["legs"]
            from_idx: int = flight["from_idx"]
            to_idx: int = flight["to_idx"]
            payload: str = flight["payload"]
            flight_id: str = flight["flight_id"]

            if to_idx >= len(legs) or legs[to_idx] != self.code:
                self._log(
                    f"Flight {flight_id} arrived from {legs[from_idx]} but route expected {legs[to_idx] if to_idx < len(legs) else 'unknown'}; current node {self.code}."
                )
            else:
                leg_desc = f"{legs[from_idx]} -> {self.code}"
                self._log(f"Flight {flight_id} arrived: {leg_desc} carrying {payload}")

            conn.sendall(f"ACK from {self.code}".encode("utf-8"))

            if to_idx < len(legs) - 1 and self.running:
                self._send_leg(legs, payload, flight_id, to_idx)
            elif to_idx == len(legs) - 1:
                self._log(f"Flight {flight_id} completed at {self.code}.")

    def _request_and_fly(self) -> None:
        """Keeps registering with scheduler until stopped."""
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((SCHEDULER_HOST, SCHEDULER_PORT))
                    sock.sendall(self.code.encode("utf-8"))
                    plan = sock.recv(1024).decode("utf-8").strip()
                    if not plan.startswith("FLIGHT"):
                        self._log(f"Got odd plan text: {plan}")
                        time.sleep(1.0)
                        continue

                    self._log(f"Received plan: {plan}")
                    legs, payload, flight_id = self._parse_plan(plan)
                    self._fly_route(legs, payload, flight_id)
                    sock.sendall(f"{self.code} complete".encode("utf-8"))
            except ConnectionRefusedError:
                self._log("Scheduler is offline, could not register.")
            except OSError as exc:
                self._log(f"Network error while flying: {exc}")

            if not self.running:
                break
            time.sleep(1.0)

    def _parse_plan(self, plan: str) -> Tuple[List[str], str, str]:
        """Turn 'FLIGHT A >> B >> C | cargo | id:0001' into workable goodies"""
        cleaned = plan.replace("FLIGHT", "", 1)
        sections = [segment.strip() for segment in cleaned.split("|")]
        route_part = sections[0] if sections else ""
        payload = sections[1] if len(sections) > 1 else "payload: none"
        flight_id = "0000"
        for extra in sections[2:]:
            if extra.lower().startswith("id:"):
                flight_id = extra.split(":", 1)[1].strip()
                break

        legs = [segment.strip() for segment in route_part.split(">>") if segment.strip()]
        return legs, payload, flight_id

    def _fly_route(self, legs: List[str], payload: str, flight_id: str) -> None:
        """Dispatch the first leg; downstream nodes forward the rest."""
        if len(legs) <= 1:
            self._log(f"Flight {flight_id}: no legs to fly, staying put.")
            return

        self._send_leg(legs, payload, flight_id, 0)

    def _send_leg(self, legs: List[str], payload: str, flight_id: str, from_idx: int) -> None:
        """Send the next leg in the route starting from legs[from_idx]."""
        to_idx = from_idx + 1
        if to_idx >= len(legs):
            return

        target_code = legs[to_idx]
        packet = json.dumps(
            {
                "flight_id": flight_id,
                "payload": payload,
                "legs": legs,
                "from_idx": from_idx,
                "to_idx": to_idx,
            }
        )

        try:
            host, port = self._lookup_airport(target_code)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, port))
                sock.sendall(packet.encode("utf-8"))
                ack = sock.recv(1024).decode("utf-8").strip()
                leg_desc = f"{legs[from_idx]} -> {target_code}"
                verb = "Forwarded" if from_idx > 0 else "Sent"
                self._log(f"{verb} flight {flight_id}: {leg_desc} carrying {payload} | Reply: {ack}")
        except OSError as exc:
            self._log(f"Could not reach {target_code} for flight {flight_id}: {exc}")

    def _try_parse_flight_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Attempt to decode a structured flight forwarding message."""
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        required = {"flight_id", "payload", "legs", "from_idx", "to_idx"}
        if not required.issubset(data):
            return None

        legs = data["legs"]
        if not isinstance(legs, list) or not all(isinstance(code, str) for code in legs):
            return None

        try:
            data["from_idx"] = int(data["from_idx"])
            data["to_idx"] = int(data["to_idx"])
        except (TypeError, ValueError):
            return None

        data["flight_id"] = str(data["flight_id"])
        data["payload"] = str(data["payload"])
        data["legs"] = legs
        return data

    def _lookup_airport(self, code: str) -> Tuple[str, int]:
        """Split '127.0.0.1:6003' into host/port numbers."""
        try:
            addr = self.airports[code]
            host, port_text = addr.rsplit(":", 1)
            return host, int(port_text)
        except (KeyError, ValueError) as exc:
            raise RuntimeError(f"Missing airport config for {code}") from exc

    def _log(self, text: str) -> None:
        """Append a timestamped line to the node's log file."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {text}\n"
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(line)
        print(f"[{self.code}] {text}")
