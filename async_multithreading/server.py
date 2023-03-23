import asyncio
import pickle
import socket
import numpy as np
import random
import time

# Define the server host and port
HOST = '127.0.0.1'
PORT = 65420

# Define the number of clients and the range of the matrix dimension
num_clients = int(input("Enter the number of clients: "))
min_dim = 3
max_dim = 5

# Initialize the global matrix
matrix_dim = random.randint(min_dim, max_dim)
global_matrix = np.random.rand(matrix_dim, matrix_dim)

# Create a queue to store client matrix updates
update_queue = asyncio.Queue()

# Define a coroutine to handle client requests
async def handle_client(reader, writer, unique_matrix=None):
    global start_client_time
    print(f"New connection from {writer.get_extra_info('peername')}")
    # Record the start time when the first client connects
    if not hasattr(handle_client, 'start_client_time'):
        handle_client.start_client_time = time.time()
    # Send the global matrix and unique matrix to the client
    unique_matrix = np.random.rand(matrix_dim, matrix_dim)
    data = pickle.dumps({'global_matrix': global_matrix, 'unique_matrix': unique_matrix})
    writer.write(data)
    await writer.drain()
    while True:
        # Receive the matrix from the client
        data = await reader.read(1024)
        if not data:
            break
        # Unpickle the data and multiply the matrices
        client_matrix = pickle.loads(data)
        # Add the result to the update queue
        await update_queue.put(client_matrix)
    writer.close()
    print(f"Connection from {writer.get_extra_info('peername')} closed")
    # Record the end time when the last client sends its matrix
    if update_queue.qsize() == num_clients:
        handle_client.end_update_time = time.time()

# Define a coroutine to listen for client matrix updates and perform averaging
async def update_matrix():
    global global_matrix
    while True:
        # Wait for matrices to be added to the queue
        matrices = []
        for i in range(num_clients):
            matrix = await update_queue.get()
            matrices.append(matrix)
        # Average the matrices
        avg_matrix = sum(matrices) / num_clients
        # Update the global matrix
        global_matrix = avg_matrix
        # Check if all clients have sent their matrices
        if update_queue.qsize() == 0:
            break
    # Record the end time when the last matrix update is processed
    update_matrix.end_update_time = time.time()

async def main():
    # Start the server
    server = await asyncio.start_server(handle_client, HOST, PORT, family=socket.AF_INET)
    print(f"Server started on {HOST}:{PORT}")
    # Start the matrix update coroutine
    await update_matrix()
    # Calculate and print the wall time
    wall_time = update_matrix.end_update_time - handle_client.start_client_time
    print(f"Wall time between first client and last update: {wall_time:.4f} seconds")

    # Close the server
    server.close()
    await server.wait_closed()
    print("Server closed")


asyncio.run(main())