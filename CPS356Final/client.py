import socket
import json
import threading

# Initialize the client socket and connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59000))

def process_server_message(message):
    """
    Process server messages dynamically and respond based on the type of request.
    """
    if "Welcome! Type 'login' to log in or 'signup'" in message:
        # Handle login/signup
        print(f"Server: {message}")
        response = input().strip()  # User provides login/signup input
        client.send(response.encode('utf-8'))
    elif "Enter username" in message or "Enter password" in message:
        # Handle login/signup credentials
        print(f"Server: {message}")
        response = input().strip()
        client.send(response.encode('utf-8'))
    elif "Enter memory size" in message:
        # Handle memory allocation request
        print(f"Server: {message}")
        size = input().strip()
        if size.isdigit():  # Validate numeric input
            request = {
                "action": "allocate",
                "size": int(size)
            }
            client.send(json.dumps(request).encode('utf-8'))
        else:
            print("Invalid input. Please enter a numeric value.")
            client.send("Invalid input".encode('utf-8'))
    else:
        # Handle any other server messages
        print(f"Server: {message}")

def handle_server_communication():
    """
    Continuously listen for messages from the server and respond appropriately.
    """
    while True:
        try:
            # Receive messages from the server
            message = client.recv(1024).decode('utf-8')
            if message:
                process_server_message(message)
        except Exception as e:
            print(f"Error: {e}")
            client.close()
            break

def user_input():
    """
    Handle user input after login.
    """
    while True:
        message = input().strip()  # Allow user to input messages
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    try:
        # Start listening for and responding to server messages
        receive_thread = threading.Thread(target=handle_server_communication)
        receive_thread.start()

        # Start handling user input after authentication
        user_input_thread = threading.Thread(target=user_input)
        user_input_thread.start()
    except KeyboardInterrupt:
        print("\nClient disconnected.")
        client.close()
