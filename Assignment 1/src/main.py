# C:\...\Assignment 1> python -m src.main 

import signal
import time
from typing import Dict, List, Tuple

from config.parser import load_airports, load_routes
from .node import Node
from .scheduler import Scheduler

"""
Assignment:
    - Scheduler hands out routes like ANC >> SEA.
    - Each airport runs as both a server (listens for arrivals) and a client (flies to another airport).
"""

def _split_address(addr: str) -> Tuple[str, int]:
    """Turn '127.0.0.1:6001' into ('127.0.0.1', 6001)."""
    host, port_text = addr.rsplit(":", 1)
    return host.strip(), int(port_text)

def _start_nodes(airports: Dict[str, str]) -> List[Node]:
    """Create and start a Node per airport."""
    nodes: List[Node] = []
    for code, addr in airports.items():
        host, port = _split_address(addr)
        node = Node(code, host, port, airports)
        node.start()
        nodes.append(node)
        time.sleep(0.1)  # small stagger so not everything talks at once
    return nodes

def main() -> None:
    airports = load_airports("src/airports.yaml")
    hubs, default_hub = load_routes("src/routes.yaml")

    scheduler = Scheduler(airports, hubs, default_hub)
    scheduler.start()
    time.sleep(0.5)  # give the scheduler a moment to bind its socket

    nodes = _start_nodes(airports)
    print("[main] All nodes launched. Press Ctrl+C to stop.")

    # Keep the process around until the user stops it.
    # I think this is like super bad practice but whatever.
    stop = False

    def _handle_sigint(signum, frame):
        nonlocal stop
        stop = True
        print("\n[main] Shutdown signal received, wrapping up...")

    signal.signal(signal.SIGINT, _handle_sigint)

    while not stop:
        time.sleep(1)

    # Give nodes a sec to finish logging. So we do not forcefully close sockets.
    time.sleep(1)
    print("[main] Shutdown complete.")

if __name__ == "__main__":
    main()
