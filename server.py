import socket
import threading
import csv
import json
from datetime import datetime
import math
import random

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def generate_prime():
    while True:
        num = random.randint(100, 1000)
        if is_prime(num):
            return num

def generate_keypair():
    p = generate_prime()
    q = generate_prime()
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Choose public key e
    e = 65537  # Commonly used value
    while math.gcd(e, phi) != 1:
        e = random.randrange(1, phi)
    
    # Calculate private key d
    d = pow(e, -1, phi)
    
    return ((e, n), (d, n))

def save_user(email, password):
    with open('data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email, password])

def check_user(email, password):
    try:
        with open('data.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == email and row[1] == password:
                    return True
    except FileNotFoundError:
        with open('data.csv', 'w', newline='') as file:
            pass
    return False

def check_user_exists(email):
    try:
        with open('data.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == email:
                    return True
    except FileNotFoundError:
        return False
    return False

class Server:
    def __init__(self, host='127.0.0.1', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = {}
        print(f"Server running on {host}:{port}")

    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def handle_client(self, client, address):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    break
                
                data = json.loads(message)
                command = data.get('command')
                
                if command == 'register':
                    email = data['email']
                    password = data['password']
                    if not check_user_exists(email):
                        save_user(email, password)
                        client.send(json.dumps({'status': 'success', 'message': 'Registration successful'}).encode())
                    else:
                        client.send(json.dumps({'status': 'error', 'message': 'User already exists'}).encode())
                
                elif command == 'login':
                    email = data['email']
                    password = data['password']
                    if check_user(email, password):
                        self.clients[client] = email
                        client.send(json.dumps({'status': 'success', 'message': 'Login successful'}).encode())
                    else:
                        client.send(json.dumps({'status': 'error', 'message': 'Invalid credentials'}).encode())
                
                elif command == 'send_message':
                    dest_email = data['dest_email']
                    encrypted_message = data['encrypted_message']
                    key = data['key']
                    
                    # Find destination client
                    dest_client = None
                    for c, email in self.clients.items():
                        if email == dest_email:
                            dest_client = c
                            break
                    
                    if dest_client:
                        message_data = {
                            'command': 'receive_message',
                            'from': self.clients[client],
                            'encrypted_message': encrypted_message,
                            'key': key
                        }
                        dest_client.send(json.dumps(message_data).encode())
                    else:
                        client.send(json.dumps({
                            'status': 'error',
                            'message': 'User not found'
                        }).encode())
                
            except Exception as e:
                print(f"Error: {e}")
                break
        
        self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            del self.clients[client]
        client.close()

    def start(self):
        while True:
            client, address = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(client, address))
            thread.start()

if __name__ == "__main__":
    server = Server()
    server.start()
