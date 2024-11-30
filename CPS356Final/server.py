import threading
import socket
import json
import os

host = '127.0.0.1'
port = 59000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
aliases = []

# Load or initialize user database
USER_DB_FILE = "user_db.json"
if os.path.exists(USER_DB_FILE):
    with open(USER_DB_FILE, 'r') as file:
        user_db = json.load(file)
else:
    user_db = {}


def save_user_db():
    with open(USER_DB_FILE, 'w') as file:
        json.dump(user_db, file)


def broadcast(message):
    for client in clients:
        client.send(message)


def authenticate_client(client):
    while True:
        client.send("Welcome! Type 'login' to log in or 'signup' to create a new account:".encode('utf-8'))
        choice = client.recv(1024).decode('utf-8').strip().lower()

        if choice == 'login':
            client.send("Enter username:".encode('utf-8'))
            username = client.recv(1024).decode('utf-8').strip()
            client.send("Enter password:".encode('utf-8'))
            password = client.recv(1024).decode('utf-8').strip()

            if username in user_db and user_db[username] == password:
                client.send("Login successful!".encode('utf-8'))
                return username
            else:
                client.send("Invalid username or password. Try again.".encode('utf-8'))

        elif choice == 'signup':
            client.send("Choose a username:".encode('utf-8'))
            username = client.recv(1024).decode('utf-8').strip()
            if username in user_db:
                client.send("Username already exists. Try again.".encode('utf-8'))
                continue

            client.send("Choose a password:".encode('utf-8'))
            password = client.recv(1024).decode('utf-8').strip()
            user_db[username] = password
            save_user_db()
            client.send("Signup successful! You can now log in.".encode('utf-8'))

        else:
            client.send("Invalid option. Please type 'login' or 'signup'.".encode('utf-8'))


def handle_client(client):
    alias = authenticate_client(client)
    aliases.append(alias)
    clients.append(client)

    broadcast(f"Server: {alias} has joined the chat!".encode('utf-8'))
    client.send("You are now connected to the chat room!".encode('utf-8'))

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            broadcast(f"{alias}: {message}".encode('utf-8'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            alias = aliases[index]
            broadcast(f"Server: {alias} has left the chat!".encode('utf-8'))
            aliases.remove(alias)
            break


def receive():
    while True:
        print('Server is running and listening ...')
        client, address = server.accept()
        print(f"Connection established with {str(address)}")
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


if __name__ == "__main__":
    receive()
