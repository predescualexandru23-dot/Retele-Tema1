import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024

class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            if key in self.data:
                return "ERROR key already exists"
            self.data[key] = value
        return "OK - record added"

    def get(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            return f"DATA {self.data[key]}"

    def remove(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            del self.data[key]
        return "OK value deleted"

    def list_all(self):
        with self.lock:
            if not self.data:
                return "DATA|"
            pairs = ",".join(f"{k}={v}" for k, v in self.data.items())
        return f"DATA|{pairs}"

    def count(self):
        with self.lock:
            c = len(self.data)
        return f"DATA {c}"

    def clear(self):
        with self.lock:
            self.data.clear()
        return "OK all data deleted"

    def update(self, key, value):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            self.data[key] = value
        return "OK data updated"

    def pop(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            value = self.data.pop(key)
        return f"DATA {value}"

state = State()
is_running = True

def process_command(command):
    parts = command.strip().split()
    if not parts:
        return "ERROR empty command"

    cmd = parts[0].upper()

    if cmd == "ADD":
        if len(parts) < 3:
            return "ERROR usage: ADD <key> <value>"
        return state.add(parts[1], ' '.join(parts[2:]))

    elif cmd == "GET":
        if len(parts) != 2:
            return "ERROR usage: GET <key>"
        return state.get(parts[1])

    elif cmd == "REMOVE":
        if len(parts) != 2:
            return "ERROR usage: REMOVE <key>"
        return state.remove(parts[1])

    elif cmd == "LIST":
        return state.list_all()

    elif cmd == "COUNT":
        return state.count()

    elif cmd == "CLEAR":
        return state.clear()

    elif cmd == "UPDATE":
        if len(parts) < 3:
            return "ERROR usage: UPDATE <key> <new_value>"
        return state.update(parts[1], ' '.join(parts[2:]))

    elif cmd == "POP":
        if len(parts) != 2:
            return "ERROR usage: POP <key>"
        return state.pop(parts[1])

    elif cmd == "QUIT":
        return "QUIT"

    else:
        return f"ERROR unknown command '{cmd}'"

def handle_client(client_socket, addr):
    print(f"[SERVER] Handling client {addr}")
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode('utf-8').strip()
                print(f"[SERVER] Received from {addr}: {command}")

                response = process_command(command)

                response_data = f"{len(response)} {response}".encode('utf-8')
                client_socket.sendall(response_data)

                if response == "QUIT":
                    print(f"[SERVER] Client {addr} requested QUIT")
                    break

            except Exception as e:
                print(f"[SERVER] Error with client {addr}: {e}")
                try:
                    err_msg = f"ERROR {str(e)}"
                    client_socket.sendall(f"{len(err_msg)} {err_msg}".encode('utf-8'))
                except:
                    pass
                break

    print(f"[SERVER] Client {addr} disconnected")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")
        print(f"[SERVER] Commands: ADD, GET, REMOVE, LIST, COUNT, CLEAR, UPDATE, POP, QUIT")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[SERVER] Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()