# Packages
import socket
import sys
import time
import numpy as np

# Defing parse function to parse text file into a list of commands
def parse(filename):

    with open(filename) as f:
        lines = f.readlines()
    
    command_list = []
    i=0
    
    while i < len(lines):
        # lines[i] = lines[i].replace('\n','')
        
        if lines[i].split()[0].lower() == 'set':
            if i == len(lines)-1:
                break
            # lines[i+1] = lines[i+1].replace('\n','')
            if lines[i+1].split()[0].lower in ('set','get'):
                i += 1
                continue
            command_list.append(' '.join(lines[i:i+2]))
            i += 1
        else:
            command_list.append(lines[i])
        
        i += 1
    
    return command_list

# Defining client function
def client_program():
    
    # host = socket.gethostname() # Get hostname
    host = sys.argv[3]
    port = 4869  # Initiate port value greater than 1024
    
    # filename = 'client_input_1.txt' # Name of file
    filename = sys.argv[1] # Name of file
    storage_backend = sys.argv[2] # Type of Storage

    if storage_backend == "native":
        n = 1000
    else:
        n = 100

    performance = []

    # Running it for 10000 iterations to check performance of different storage backends
    for i in range(n+1):
        
        start = time.time()

        if i == n:
            command_list = ["END\n"]
        else:
            command_list = parse(filename) # Get the command list from the text file

        while len(command_list)!= 0:
            # Get client instance for IPv4 address and TCP connection
            client_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                client_instance.connect((host, port))  # Connect to the server
            except socket.error as se:
                print("Socket error:", str(se)) # Printing socket error 
                # continue

            comm = command_list.pop(0)  # Take command from text file
            client_instance.sendall(comm.encode())  # Send command to server

            
            # Looping and combining all the data being sent
            # msg = []
            # while True:
            #     client_data = client_instance.recv(5500) # Receive data from client
            #     # Check for empty data
            #     if not client_data:
            #         break
            #     resp = client_data.decode() # Decode the client data
            #     msg.append(resp)
            #     if '\n' in resp:
            #         break

            # response_data = "".join(msg)  # Receive response from server

            response_data = client_instance.recv(5500).decode()
            # print(response_data)  # Server Response

            client_instance.close()  # Close the connection 

        if i < n:
            time_taken = time.time() - start
            performance.append(time_taken)
            print(f"Time Taken: Iteration {i+1} - {time_taken}")

    print(f"Average time for {storage_backend} (Performance): {np.mean(performance)}")
    
 
if __name__ == '__main__':
    client_program()