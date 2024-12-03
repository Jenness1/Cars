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
        try:
            # Send the initial welcome message
            welcome_packet = {
                "action": "system",
                "message": "Welcome! Type 'login' to log in or 'signup' to create an account:"
            }
            client.send(json.dumps(welcome_packet).encode('utf-8'))

            # Receive client's choice
            choice_packet = json.loads(client.recv(1024).decode('utf-8'))
            choice = choice_packet.get("message", "").strip().lower()

            if choice == 'login':
                # Ask for username and password
                client.send(json.dumps({"action": "system", "message": "Enter username:"}).encode('utf-8'))
                username_packet = json.loads(client.recv(1024).decode('utf-8'))
                username = username_packet.get("message", "").strip()

                client.send(json.dumps({"action": "system", "message": "Enter password:"}).encode('utf-8'))
                password_packet = json.loads(client.recv(1024).decode('utf-8'))
                password = password_packet.get("message", "").strip()

                hashed_password = hash_password(password)

                if username in user_db and user_db[username] == hashed_password:
                    client.send(json.dumps({"action": "system", "message": "Login successful!"}).encode('utf-8'))
                    return username
                else:
                    client.send(json.dumps({"action": "system", "message": "Invalid username or password. Try again."}).encode('utf-8'))

            elif choice == 'signup':
                # Ask for username and password for signup
                client.send(json.dumps({"action": "system", "message": "Select username:"}).encode('utf-8'))
                username_packet = json.loads(client.recv(1024).decode('utf-8'))
                username = username_packet.get("message", "").strip()

                if username in user_db:
                    client.send(json.dumps({"action": "system", "message": "Username already exists. Try again."}).encode('utf-8'))
                    continue

                client.send(json.dumps({"action": "system", "message": "Select password:"}).encode('utf-8'))
                password_packet = json.loads(client.recv(1024).decode('utf-8'))
                password = password_packet.get("message", "").strip()

                hashed_password = hash_password(password)
                user_db[username] = hashed_password
                save_user_db()
                client.send(json.dumps({"action": "system", "message": "Signup is complete! You can now log in."}).encode('utf-8'))
                print(f"{username}'s password has been hashed and stored in the database.")

            else:
                client.send(json.dumps({"action": "system", "message": "Invalid input. Use 'login' or 'signup'."}).encode('utf-8'))
        except Exception as e:
            print(f"Error during authentication: {e}")
            client.close()
            break



def broadcast(message, recipiant):
    recipiant.send(json.dumps({"action": "system", "message": message}).encode('utf-8'))


def handle_client(client):
    display_name = authenticate_client(client)
    display_names.append(display_name)
    clients.append(client)

    #See who the client wants to talk to 
    while True:
        allNames = ""
        for name in display_names:
            allNames = allNames + ", " + name
        client.send(json.dumps({"action": "system", "message": 'Accounts online: ' + allNames}).encode('utf-8'))
        print('\n')
        client.send(json.dumps({"action": "system", "message": "\nWho would you like to chat with?:"}).encode('utf-8'))

        recipiant = client.recv(1024).decode('utf-8').strip()
        message_dict = json.loads(recipiant)
        recipiant_name = message_dict.get("message")


        if recipiant_name not in display_names:
            client.send(json.dumps({"action": "system", "message": "Please enter a valid name "}).encode('utf-8'))
            continue
        break

    #Get the client from the display name
    i = 0
    for name in display_names:
        if name == recipiant_name:
            break
        else:
            i = i + 1
    recipiant_client = clients[i]

    client.send(json.dumps({"action": "system", "message": f"\nYou are now talking to {recipiant_name}!"}).encode('utf-8'))
        
    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            #See if action is a allocation or deallocation message
            #If it is, need to allocate memory instead of sending a message 
            message_dict = json.loads(message)
            action = message_dict.get("action")

            if action == "allocate":
                print("allocate")
            elif action == "deallocate":
                print("deallocate")
            elif action == "chat":
                broadcast(f"{display_name}: {message}".encode('utf-8'), recipiant_client)
            else:
                print("There was an error somewhere")
            
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
        thread = threading.Thread(target=handle_client, args=(client,), daemon=True)
        thread.start()




if __name__ == "__main__":
    receive()
