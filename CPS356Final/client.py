import threading
import socket
import random
import time
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(('127.0.0.1', 59000))
except ConnectionRefusedError:
    print("Unable to connect to the server. Please check if the server is running.")
    exit()

def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                print(message)
        except:
            print('Error! Connection closed.')
            client.close()
            break

class MemoryClient:
    def __init__(self, host='127.0.0.1', port=59000):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
            print(f"Connected to the server at {host}:{port}")
        except ConnectionRefusedError:
            print("Unable to connect to the server. Please check if the server is running.")
            exit()

    def send_request(self):
        """Send a JSON-formatted memory allocation or deallocation request."""
        # Create a request packet
        action = random.choice(["allocate", "deallocate"])  # Randomly choose action
        size = random.randint(10, 100)  # Random size between 10 and 100
        request_packet = {"action": action, "size": size}

        # Convert the packet to JSON and send it
        request_json = json.dumps(request_packet)
        print(f"Sending request: {request_json}")
        self.client.send(request_json.encode('utf-8'))

        # Wait for the server's response
        response = self.client.recv(1024).decode('utf-8')
        print(f"Server response: {response}")

    def run(self, time_limit=60, interval=3):
        """
        Run the client in a loop, periodically sending requests until the time limit is reached.

        :param time_limit: Maximum duration (in seconds) the client should run.
        :param interval: Delay between consecutive requests (in seconds).
        """
        start_time = time.time()  # Record the start time

        try:
            while True:
                # Check if the time limit has been exceeded
                elapsed_time = time.time() - start_time
                if elapsed_time > time_limit:
                    print("Time limit reached. Stopping client.")
                    break

                # Send a memory allocation or deallocation request
                self.send_request()
                time.sleep(interval)  # Wait before the next request
        except KeyboardInterrupt:
            print("Client terminated.")
        finally:
            self.client.close()
            print("Connection closed.")

def client_send():
    while True:
        message = input("")
        if message:
            client.send(message.encode('utf-8'))


receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()

# Run the client
if __name__ == "__main__":
    client = MemoryClient()

    # Run the client for 60 seconds, sending requests every 5 seconds
    client.run(time_limit=60, interval=5)