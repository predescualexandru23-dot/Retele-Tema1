import socket

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024

def receive_full_message(sock):
    try:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            return None

        string_data = data.decode('utf-8').strip()
        first_space = string_data.find(' ')

        if first_space == -1 or not string_data[:first_space].isdigit():
            return f"ERROR invalid response format: {string_data}"

        message_length = int(string_data[:first_space])
        full_data = string_data[first_space + 1:]
        remaining = message_length - len(full_data)

        while remaining > 0:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                return None
            chunk = data.decode('utf-8')
            full_data += chunk
            remaining -= len(chunk)

        return full_data

    except Exception as e:
        return f"ERROR {e}"

def print_help():
    print("""
Available commands:
  ADD <key> <value>    - Add a new key-value pair
  GET <key>            - Retrieve value by key
  REMOVE <key>         - Remove a key-value pair
  UPDATE <key> <value> - Update existing key's value
  POP <key>            - Get and remove a key-value pair
  LIST                 - List all key-value pairs
  COUNT                - Count total entries
  CLEAR                - Delete all entries
  QUIT                 - Close connection and exit
  help                 - Show this help message
""")

def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}. Type 'help' for available commands.")

            while True:
                try:
                    command = input('client> ').strip()
                except EOFError:
                    break

                if not command:
                    continue

                if command.lower() == 'help':
                    print_help()
                    continue

                s.sendall(command.encode('utf-8'))
                response = receive_full_message(s)

                if response is None:
                    print("[CLIENT] Server closed the connection.")
                    break

                print(f">> {response}")

                if response == "QUIT":
                    print("[CLIENT] Disconnecting.")
                    break

    except ConnectionRefusedError:
        print(f"[CLIENT] Could not connect to {HOST}:{PORT}. Is the server running?")
    except Exception as e:
        print(f"[CLIENT] Error: {e}")

if __name__ == "__main__":
    main()