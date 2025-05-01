# cyber-security
safe messaging 
This is a simple encrypted chat application built using Python's socket programming and RSA public-key cryptography. It includes both a server and a client for secure, real-time messaging between users over a local network
Features:
User Registration and Login
Users can register with an email and password, which are stored locally in a CSV file.

PublicKey Encryption -RSA
After login, each client generates a unique RSA key pair to encrypt and decrypt messages.

Message Encryption
Messages are encrypted using RSA and transmitted securely between clients via the server.

Multithreaded Server:
The server handles multiple clients concurrently using Python's threading module.
server.py — Handles user authentication, message forwarding, and client management.

client.py — Provides user interface for registration, login, and encrypted messaging.

data.csv — Stores registered users' email and password.
