import socket
import select

HOST = '127.0.0.1'
PORT = 12345
TIMEOUT_SEC = 10
MAX_TIMEOUTS = 3

def handle_client(c, addr):
    print("client", addr, "connected")
    timeouts = 0
    try:
        while True:
            # wait for data up to TIMEOUT_SEC
            r, _, _ = select.select([c], [], [], TIMEOUT_SEC)
            if not r:
                timeouts += 1
                print("timeout from", addr, timeouts, "/", MAX_TIMEOUTS)
                if timeouts >= MAX_TIMEOUTS:
                    print("closing", addr, "after too many timeouts")
                    break
                continue

            data = c.recv(1024)
            if not data:
                # client closed
                break

            # echo-ish ack
            msg = "ack: " + data.decode()
            c.sendall(msg.encode())
            timeouts = 0  # activity, reset
    except Exception as e:
        print("client error", addr, e)
    finally:
        c.close()
        print("client", addr, "closed")

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print("listening on", HOST, PORT)

    try:
        while True:
            c, addr = s.accept()
            handle_client(c, addr)
    except KeyboardInterrupt:
        print("\nserver stopping")
    finally:
        s.close()
        print("server closed")

if __name__ == "__main__":
    main()
