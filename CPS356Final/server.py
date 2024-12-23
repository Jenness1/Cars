import threading
import socket
import json
import os
import hashlib

host = '127.0.0.1'
port = 59000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
display_names = []
action_counters = {}  # Dictionary to track client actions

USER_DB_FILE = "user_db.json"
if os.path.exists(USER_DB_FILE):
    with open(USER_DB_FILE, 'r') as file:
        user_db = json.load(file)
else:
    user_db = {}


def save_user_db():
    with open(USER_DB_FILE, 'w') as file:
        json.dump(user_db, file)


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def authenticate_client(client):
    while True:
        client.send("Welcome! Type 'login' to log in or 'signup' to create an account:".encode('utf-8'))
        choice = client.recv(1024).decode('utf-8').strip().lower()

        if choice == 'login':
            client.send("Enter username:".encode('utf-8'))
            username = client.recv(1024).decode('utf-8').strip()
            client.send("Enter password:".encode('utf-8'))
            password = client.recv(1024).decode('utf-8').strip()
            hashed_password = hash_password(password)

            if username in user_db and user_db[username] == hashed_password:
                client.send("Login successful!".encode('utf-8'))
                return username
            else:
                client.send("Invalid username or password. Try again.".encode('utf-8'))

        elif choice == 'signup':
            client.send("Select username:".encode('utf-8'))
            username = client.recv(1024).decode('utf-8').strip()
            if username in user_db:
                client.send("Username already exists. Try again.".encode('utf-8'))
                continue

            client.send("Select password:".encode('utf-8'))
            password = client.recv(1024).decode('utf-8').strip()
            hashed_password = hash_password(password)
            user_db[username] = hashed_password
            save_user_db()
            client.send("Signup is complete! You can now log in.".encode('utf-8'))
            print(f"{username}'s password has been hashed and stored in the database.")

        else:
            client.send("Invalid input. Use 'login' or 'signup'.".encode('utf-8'))


<<<<<<< Updated upstream
def broadcast(message, recipiant):
    recipiant.send(message)
=======
def broadcast(message, recipient):
    recipient.send(message)
>>>>>>> Stashed changes


def handle_client(client):
    # Authenticate the client first
    display_name = authenticate_client(client)
    display_names.append(display_name)
    clients.append(client)
    action_counters[client] = 0  # Initialize action counter for the client

<<<<<<< Updated upstream
    #broadcast(f"Server: {display_name} has joined the chat!".encode('utf-8'))
    #print(f"{display_name} has joined the chat")
    #client.send("You are now connected to the chat room!".encode('utf-8')

    #See who the client wants to talk to
    while True:
        allNames = ""
        for name in display_names:
            allNames = allNames + ", " + name
        client.send(('Accounts online: ' + allNames).encode('utf-8'))
        print('\n')
        client.send("\nWho would you like to chat with?:".encode('utf-8'))
        recipiant = client.recv(1024).decode('utf-8').strip()
        if recipiant not in display_names:
            client.send("Please enter a valid name ".encode('utf-8'))
            continue
        break

    #Get the client from the display name
    i = 0
    for name in display_names:
        if name == recipiant:
            break
        else:
            i = i + 1
    recipiant_client = clients[i]

    client.send((f"\nYou are now talking to {recipiant}!" ).encode('utf-8'))
        
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            broadcast(f"{display_name}: {message}".encode('utf-8'), recipiant_client)
=======
    client.send("You are now logged in. Memory management and chat features are available.".encode('utf-8'))

    # Main loop for post-login actions
    while True:
        try:
            if action_counters[client] >= 4:
                client.send("You have reached the maximum number of actions. Disconnecting...".encode('utf-8'))
                print(f"{display_name} has been disconnected after 4 actions.")
                clients.remove(client)
                display_names.remove(display_name)
                client.close()
                break

            client.send("\nOptions:\n1. Chat\n2. Request Memory Allocation\nEnter your choice:".encode('utf-8'))
            choice = client.recv(1024).decode('utf-8').strip()

            if choice == "1":
                # Chat functionality
                all_names = ", ".join(display_names)
                client.send((f"Accounts online: {all_names}").encode('utf-8'))
                client.send("\nWho would you like to chat with?:".encode('utf-8'))
                recipient_name = client.recv(1024).decode('utf-8').strip()

                if recipient_name not in display_names:
                    client.send("Please enter a valid name.".encode('utf-8'))
                    continue

                # Get the recipient client from the display name
                recipient_client = clients[display_names.index(recipient_name)]
                client.send((f"\nYou are now talking to {recipient_name}! Type '/exit' to stop chatting.").encode('utf-8'))

                while True:
                    message = client.recv(1024).decode('utf-8')
                    if message.lower() == "/exit":
                        client.send("Exiting chat...".encode('utf-8'))
                        break
                    broadcast(f"{display_name}: {message}".encode('utf-8'), recipient_client)
                    action_counters[client] += 1

            elif choice == "2":
                # Memory allocation functionality
                client.send("Enter memory size to allocate (in KB or MB):".encode('utf-8'))
                size = client.recv(1024).decode('utf-8').strip()

                if size.isdigit():
                    memory_request = {
                        "action": "allocate",
                        "size": int(size)
                    }
                    client.send((f"Memory allocation request sent: {memory_request}").encode('utf-8'))
                    action_counters[client] += 1
                else:
                    client.send("Invalid size. Please enter a numeric value.".encode('utf-8'))

            else:
                client.send("Invalid choice. Try again.".encode('utf-8'))

>>>>>>> Stashed changes
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            display_name = display_names[index]
            display_names.remove(display_name)
            print(f"{display_name} has disconnected.")
            break


def receive():
    while True:
        print('Server is running and listening ...')
        client, address = server.accept()
        print(f"Connection established with {str(address)}")
        thread = threading.Thread(target=handle_client, args=(client,), daemon=True)
        thread.start()



if __name__ == "__main__":
    receive()
