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


def broadcast(message):
    for client in clients:
        client.send(message)


def handle_client(client):
    display_name = authenticate_client(client)
    display_names.append(display_name)
    clients.append(client)

    broadcast(f"Server: {display_name} has joined the chat!".encode('utf-8'))
    print(f"{display_name} has joined the chat")
    client.send("You are now connected to the chat room!".encode('utf-8'))

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            broadcast(f"{display_name}: {message}".encode('utf-8'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            display_name = display_names[index]
            broadcast(f"Server: {display_name} has left the chat!".encode('utf-8'))
            display_names.remove(display_name)
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
