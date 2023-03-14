import socket
import numpy as np
import pickle

# Define the server host and port
HOST = '127.0.0.1'
PORT = 65430

# Define the number of clients to create
num_clients = 10

# Create a list to store the sockets
sockets = []

# Create the sockets and connect to the server
for i in range(num_clients):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    sockets.append(s)
    print(f"Client {i+1} connected to the server.")

# Receive the global matrix and unique matrix from the server for each client
matrices = []
for s in sockets:
    data = s.recv(1024)
    matrices.append(pickle.loads(data))
    print(f"Received matrices for a client: {matrices[-1]}")

# Multiply the matrices for each client and send the result to the server
for i in range(num_clients):
    global_matrix = matrices[i]['global_matrix']
    unique_matrix = matrices[i]['unique_matrix']
    result = np.dot(global_matrix, unique_matrix)
    sockets[i].sendall(pickle.dumps(result))
    print(f"Result for client {i+1} sent to the server.")

print("All clients finished.")
