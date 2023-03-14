import pickle
import socket
import numpy as np
import threading
import queue
import random
import time


# Define the server host and port
HOST = '127.0.0.1'
PORT = 65430

# Define the number of clients and the range of the matrix dimension
num_clients = int(input("Enter the number of clients: "))
min_dim = 3
max_dim = 5

# Initialize the global matrix
matrix_dim = random.randint(min_dim, max_dim)
global_matrix = np.random.rand(matrix_dim, matrix_dim)

# Create a queue to store client matrix updates
update_queue = queue.Queue()

# tag first client
start_client_time = 0
# Define a function to handle client requests
def handle_client(conn, addr, unique_matrix):
    global start_client_time
    print(f"New connection from {addr}")
    if start_client_time == 0:
        start_client_time = time.time()
    # Send the global matrix and unique matrix to the client
    conn.sendall(pickle.dumps({'global_matrix': global_matrix, 'unique_matrix': unique_matrix}))
    while True:
        # Receive the matrix from the client
        data = conn.recv(1024)
        if not data:
            break
        # Unpickle the data and multiply the matrices
        client_matrix = pickle.loads(data)
        # Add the result to the update queue
        update_queue.put(client_matrix)
    conn.close()
    print(f"Connection from {addr} closed")

# Create a socket and bind it to the host and port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    # Create a list to store client threads
    threads = []
    # Create unique matrices for each client
    unique_matrices = [np.random.rand(matrix_dim, matrix_dim) for i in range(num_clients)]
    # Start a thread for each client
    for i in range(num_clients):
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr, unique_matrices[i]))
        threads.append(t)
        t.start()
        print(f"Started thread for client {i} with unique matrix:")
        print(unique_matrices[i])

    # Listen for client matrix updates and perform averaging
    while True:
        if not update_queue.empty():
            # Get all the matrices in the queue
            matrices = []
            while not update_queue.empty():
                matrices.append(update_queue.get())
            # Calculate the average of the matrices
            avg_matrix = np.mean(matrices, axis=0)
            # Update the global matrix
            global_matrix = avg_matrix
            print("Updated global matrix:")
            print(global_matrix)
        else:
            # If there are no more updates in the queue, break out of the loop
            break

    # Record the end time of the program
    end_time = time.time()

    # Calculate the total wall time
    total_time = end_time - start_client_time
    print(f"Total wall time: {total_time:.4f} seconds")
