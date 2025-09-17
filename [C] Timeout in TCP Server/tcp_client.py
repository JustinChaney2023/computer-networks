import socket
import select

HOST = '127.0.0.1'
PORT = 12345
TIMEOUT_SEC = 10
MAX_TIMEOUTS = 3

def main():
    # connect with a 10s timeout just for the connect step
    s = socket.create_connection((HOST, PORT), timeout=TIMEOUT_SEC)
    # put back into blocking mode (we'll do timeouts via select)
    s.setblocking(True)
    print("connected to", HOST, PORT)

    timeouts = 0

    try:
        while True:
            msg = input("msg ('.' to quit): ")
            if msg == '.':
                break

            # send all (blocking ok here)
            s.sendall(msg.encode())

            # wait up to TIMEOUT_SEC for a response
            r, _, _ = select.select([s], [], [], TIMEOUT_SEC)
            if not r:
                timeouts += 1
                print("timeout", timeouts, "/", MAX_TIMEOUTS)
                if timeouts >= MAX_TIMEOUTS:
                    print("too many timeouts, closing")
                    break
                continue

            data = s.recv(1024)
            if not data:
                print("server closed")
                break

            print("recv:", data.decode())
            timeouts = 0  # got data, reset

    except Exception as e:
        print("client error:", e)
    finally:
        s.close()
        print("client closed")

if __name__ == "__main__":
    main()
