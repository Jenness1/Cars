import socket
import threading
import json
import random
import time
import select

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client.connect(('127.0.0.1', 59000))

def client_receive():
    """Handle incoming messages from the server."""
    while True:
        # Use select to check if data is available to read from the socket
        readable, _, _ = select.select([client], [], [], 0.1)
        if readable:
            try:
                message = client.recv(1024).decode('utf-8')
                if message:
                    print(message)
            except:
                print('Error! Connection closed.')
                client.close()
                break

def authenticate():
    """Handle login or signup process, waiting for the server's prompt."""
    while True:
        # Wait for the server's prompt for login or signup
        response = client.recv(1024).decode('utf-8')
        print(response)

        if 'login' in response or 'signup' in response:
            choice = input("Enter 'login' to log in or 'signup' to create an account: ").strip().lower()
            client.send(choice.encode('utf-8'))

            if choice == 'login' or choice == 'signup':
                # Handle username and password input after the server's prompt
                username_prompt = client.recv(1024).decode('utf-8')
                print(username_prompt)
                username = input("Enter username: ").strip()
                client.send(username.encode('utf-8'))

                password_prompt = client.recv(1024).decode('utf-8')
                print(password_prompt)
                password = input("Enter password: ").strip()
                client.send(password.encode('utf-8'))

                # Wait for server's response
                response = client.recv(1024).decode('utf-8')
                print(response)

                # If login/signup is successful, break the loop
                if 'successful' in response:
                    break
        else:
            print("Invalid choice, please try again.")

def MemoryClient():
    """Send a JSON-formatted memory allocation or deallocation request."""
    while True:
        # Randomly choose action (allocate or deallocate)
        action = random.choice(["allocate", "deallocate"])
        size = random.randint(10, 100)  # Random size
        request_packet = {"action": action, "size": size}

        # Convert the packet to JSON and send it
        request_json = json.dumps(request_packet)
        print(f"Sending request: {request_json}")
        client.send(request_json.encode('utf-8'))

        # Wait for server's response
        response = client.recv(1024).decode('utf-8')
        print(f"Server response: {response}")
        time.sleep(3)  # Wait before sending the next request

# Start receiving messages from the server
receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

# Authenticate user
authenticate()

# Wait for the "You can now perform memory operations." message
response = client.recv(1024).decode('utf-8')
if "perform memory operations" in response:
    print("Authentication successful. You can now begin memory operations.")

    # Start sending memory allocation/deallocation requests
    MemoryClient()

# Run the client
if __name__ == "__main__":
    client = MemoryClient()

    # Run the client for 60 seconds, sending requests every 5 seconds
    client.run(time_limit=60, interval=5)