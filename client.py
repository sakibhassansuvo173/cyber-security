import socket
import json
import threading
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

def encrypt_message(message, public_key):
    e, n = public_key
    encrypted_chars = []
    for char in message:
        m = ord(char)
        c = pow(m, e, n)
        encrypted_chars.append(str(c))
    return ','.join(encrypted_chars)

def decrypt_message(encrypted_message, private_key):
    d, n = private_key
    decrypted_chars = []
    encrypted_chars = encrypted_message.split(',')
    for char in encrypted_chars:
        c = int(char)
        m = pow(c, d, n)
        decrypted_chars.append(chr(m))
    return ''.join(decrypted_chars)

class Client:
    def __init__(self, host='127.0.0.1', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.email = None
        self.public_key = None
        self.private_key = None

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if not message:
                    break
                
                data = json.loads(message)
                
                if data.get('command') == 'receive_message':
                    sender = data['from']
                    encrypted_message = data['encrypted_message']
                    key = data['key']
                    
                    # Decrypt message using received key
                    decrypted_message = decrypt_message(encrypted_message, tuple(key))
                    print(f"\nFrom: {sender}")
                    print(f"Encrypted message: {encrypted_message}")
                    print(f"Decrypted message: {decrypted_message}")
                else:
                    print(f"\nServer response: {data.get('message')}")
                    
                    # Generate keys after successful login
                    if data.get('message') == 'Login successful':
                        self.public_key, self.private_key = generate_keypair()
                        print("\nGenerated RSA keys:")
                        print(f"Public key: {self.public_key}")
                        print(f"Private key: {self.private_key}")
                
            except Exception as e:
                print(f"Error: {e}")
                break

    def start(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        while True:
            if not self.email:
                choice = input("\n1. Register\n2. Login\nChoice: ")
                email = input("Email: ")
                password = input("Password: ")
                
                if choice == '1':
                    self.client.send(json.dumps({
                        'command': 'register',
                        'email': email,
                        'password': password
                    }).encode())
                else:
                    self.client.send(json.dumps({
                        'command': 'login',
                        'email': email,
                        'password': password
                    }).encode())
                    self.email = email
            
            else:
                dest_email = input("\nEnter destination email (or 'quit' to exit): ")
                if dest_email.lower() == 'quit':
                    break
                
                message = input("Enter message: ")
                
                if self.public_key:  # Check if keys are generated
                    encrypted_message = encrypt_message(message, self.public_key)
                    
                    print(f"\nOriginal message: {message}")
                    print(f"Encrypted message: {encrypted_message}")
                    
                    self.client.send(json.dumps({
                        'command': 'send_message',
                        'dest_email': dest_email,
                        'encrypted_message': encrypted_message,
                        'key': self.private_key
                    }).encode())
                else:
                    print("Error: Keys not generated yet. Please try again.")

        self.client.close()

if __name__ == "__main__":
    client = Client()
    client.start()
