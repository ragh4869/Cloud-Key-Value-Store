# Packages
import os
import socket
import json
import sys
import time
from multiprocessing import Process
from google.cloud import storage
from google.cloud import datastore
from threading import Thread

# Defining Get function
def get_data(client_data, storage_backend, conn):
    
    if storage_backend == "native":
        with open('data.json') as f: # Open json file to read 
            data = json.load(f) # Convert json object to a dictionary
    elif storage_backend == "bucket":
        storage_client = storage.Client()
        bucket = storage_client.get_bucket('gcs-bucket-fall2022')
        blob = bucket.get_blob('data.json')
        data = json.loads(blob.download_as_string(client=None))
    elif storage_backend == "datastore":
        datastore_client = datastore.Client()
        kind = "raghav-datastore"
        task_key = datastore_client.key(kind, client_data[1])
        data = datastore_client.get(task_key)

    # Checking for required number of inputs
    if len(client_data) != 2:
        conn.sendall('Invalid command inputs. Try Again!\r\nEND'.encode())
        return
    
    # Get Key value
    key_val = client_data[1]

    # Sending the key, value and bit count in required format
    if storage_backend == "datastore":
        if bool(data):
            bit_val = data['Bits']
            data_val = data['Data']
            output_val = f'VALUE {key_val} {bit_val} \r\n{data_val}\r\nEND\r\n'
            conn.sendall(output_val.encode())
        else:
            conn.sendall('Key value not available\r\nEND'.encode())
    else:
        if key_val in data.keys():
            bit_val = data[key_val]['Bits']
            data_val = data[key_val]['Data']
            output_val = f'VALUE {key_val} {bit_val} \r\n{data_val}\r\nEND\r\n'
            conn.sendall(output_val.encode())
        else:
            conn.sendall('Key value not available\r\nEND'.encode())


# Defining Set function
def set_data(client_data, storage_backend, conn):
    
    if storage_backend == "native":
        with open('data.json') as f: # Open json file to read
            data = json.load(f) # Convert json object to a dictionary
    elif storage_backend == "bucket":
        storage_client = storage.Client()
        bucket = storage_client.bucket("gcs-bucket-fall2022")
        blob = bucket.get_blob('data.json')
        data = json.loads(blob.download_as_string(client=None))
    
    # Checking for required number of inputs
    if len(client_data) != 4:
        conn.sendall('NOT-STORED\r\nInvalid command inputs. Try Again!\r\n'.encode())
        return
    
    # Get Key value
    key_val = client_data[1]

    # Checking for correct bit value input
    try:
        bit_value = int(client_data[2])
    except:
        conn.sendall('NOT-STORED\r\nBit value is not an integer. Try Again!\r\n'.encode())
        return

    if bit_value == len(client_data[3]):
        pass
    else:
        conn.sendall('NOT-STORED\r\nBit value not specified correctly. Try Again!\r\n'.encode())
        return
    
    # Checking if the data is getting STORED or NOT-STORED
    try:
        
        if storage_backend == "native":
            data[key_val] = {'Bits':bit_value, 'Data':client_data[3]}
            with open('data.json', 'w') as f: # Open json file to write
                json.dump(data, f, indent=2) # Update the data in the json file
        elif storage_backend == "bucket":
            data[key_val] = {'Bits':bit_value, 'Data':client_data[3]}
            storage_client = storage.Client()
            bucket = storage_client.get_bucket('gcs-bucket-fall2022')
            blob = bucket.get_blob('data.json')
            blob.upload_from_string(data=json.dumps(data),content_type='application/json')
        elif storage_backend == "datastore":
            datastore_client = datastore.Client()
            kind = "raghav-datastore"
            task_key = datastore_client.key(kind, key_val)
            task = datastore.Entity(key=task_key)
            task.update({
                "Bits": bit_value,
                "Data": client_data[3]
            })
            datastore_client.put(task)

        conn.sendall('STORED\r\n'.encode())
    except:
        conn.sendall('NOT-STORED\r\n'.encode())


# Defining server program
def server_program():
    
    storage_backend = sys.argv[1]

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "raghav-cskumar-fall2022-387fa080baee.json"

    # host = socket.gethostname() # Get hostname
    host = '0.0.0.0'
    port = 4869  # Initiate port value greater than 1024

    # Get server instance for IPv4 address and TCP connection
    server_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    try:
        server_instance.bind((host, port))  # Binding host address and port to the server socket
    except socket.error as se:
        print(str(se)) # Printing socket error

    server_instance.listen() # Instance of server listening to clients 
    
    # act = True
    while True:
        conn, address = server_instance.accept()  # Accepting a new connection
        print("Connection from: " + str(address))
        msg = []
        while True:
            client_data = conn.recv(5500) # Receive data from client
            # Check for empty data
            if not client_data:
                break
            try:
                response_data = client_data.decode() # Decode the client data
            except:
                try:
                    response_data = client_data.decode('latin-1') # Decode the client data with latin-1
                except:
                    response_data = client_data.decode('utf-8') # Decode the client data with utf-8 
            msg.append(response_data)
            if '\n' in response_data:
                break

        resp = "".join(msg)
        resp = resp.replace('\n','')

        # print(f'Command: {resp}') 

        cl_data = resp.split(maxsplit=3) 
        
        # Run the commands using Process 
        # if cl_data[0].lower() == 'set':
        #     # Start Set function process
        #     client_process = Process(target=set_data, args=(cl_data,conn,))
        #     client_process.start()
        # elif cl_data[0].lower() == 'get':
        #     # Start Get function process
        #     client_process = Process(target=get_data, args=(cl_data,conn,))
        #     client_process.start()
        # else:
        #     conn.sendall('Wrong Command. Try Again!\r\n'.encode())


        # Run the commands using Thread
        if cl_data[0].lower() == 'set':
            # Start Set function process
            client_thread = Thread(target=set_data, args=(cl_data,storage_backend,conn,))
            client_thread.start()
        elif cl_data[0].lower() == 'get':
            # Start Get function process
            client_thread = Thread(target=get_data, args=(cl_data,storage_backend,conn,))
            client_thread.start()
        elif cl_data[0] == "END":
            conn.sendall('Closing Server!\r\n'.encode())
            break
        else:
            conn.sendall('Wrong Command. Try Again!\r\n'.encode())


    print(f"{storage_backend} is complete!")

    conn.close()

if __name__ == '__main__':
    server_program()
