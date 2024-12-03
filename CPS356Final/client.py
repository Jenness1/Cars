import threading
import socket
import random
import time
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 59000))

#Recieving Messages
def client_receive():
    while True:
        try:
            response = client.recv(1024).decode('utf-8')
            message_dict = json.loads(response)
            message = message_dict.get("message")
            if message:
                print(message)
        except:
            print('Error! Connection closed.')
            client.close()
            break

#Sending messages
def client_send():
    while True:
        message = input("")
        message_packet = {"action": "chat", "size": 100, "message": message}
        message_json = json.dumps(message_packet)
        if message_json:
            client.send(message_json.encode('utf-8'))

#Request for allocating or deallocating memory
def allocate_deallocate():
    while True:
        # Randomly choose action (allocate or deallocate)
        action = random.choice(["allocate", "deallocate"])
        size = random.randint(10, 100)  # Random size
        request_packet = {"action": action, "size": size, "message": ""}

        # Convert the packet to JSON and send it
        request_json = json.dumps(request_packet)
        print(f"Sending request: {request_json}")
        client.send(request_json.encode('utf-8'))

        time.sleep(10) 


#Recieve Thread
receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

#Send Thread
send_thread = threading.Thread(target=client_send)
send_thread.start()

#Allocation/deallocation Thread
receive_thread = threading.Thread(target=allocate_deallocate)
receive_thread.start()