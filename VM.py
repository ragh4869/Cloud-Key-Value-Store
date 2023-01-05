# Packages
import os
import sys
import json
from threading import Thread
from multiprocessing import Process
from google.cloud import storage
from google.cloud import datastore
import time 


# Defining function to set up the Server and Client VMs
def vm_setup(project_id):
    
    # Setting firewall rules
    os.system("gcloud compute networks create default")
    os.system("gcloud compute firewall-rules create default-allow-icmp --network default --allow icmp --source-ranges 0.0.0.0/0")
    os.system("gcloud compute firewall-rules create default-allow-ssh --network default --allow tcp:22 --source-ranges 0.0.0.0/0")
    os.system("gcloud compute firewall-rules create default-allow-internal --network default --allow tcp:0-65535,udp:0-65535,icmp --source-ranges 10.128.0.0/9")
    os.system(f"gcloud compute --project={project_id} firewall-rules create default-ssh --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:22,tcp:3389 --source-ranges=0.0.0.0/0")
    os.system(f"gcloud compute --project={project_id} firewall-rules create default-internal --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=all")

    # Setting up Server VM and copying the server files into the VM
    os.system("gcloud compute instances create server-vm --zone=us-central1-a") # Start the Server VM
    os.system(f'gcloud compute ssh --zone=us-central1-a server-vm') # Get the ssh key for the Server VM
    os.system("gcloud compute scp --recurse --zone=us-central1-a server_files server-vm:") # Copy server files from local to Server VM
    os.system(f'gcloud compute ssh server-vm --zone=us-central1-a --command="sudo apt install python3-pip --assume-yes"')
    os.system(f'gcloud compute ssh server-vm --zone=us-central1-a --command="pip3 install numpy"')
    os.system(f'gcloud compute ssh server-vm --zone=us-central1-a --command="pip3 install google"')
    os.system(f'gcloud compute ssh server-vm --zone=us-central1-a --command="pip3 install google-cloud-storage"')
    os.system(f'gcloud compute ssh server-vm --zone=us-central1-a --command="pip3 install google-cloud-datastore"')
    
    # Setting up Client VM and copying the client files into the VM
    os.system("gcloud compute instances create client-vm --zone=us-central1-a") # Start the client VM
    os.system(f'gcloud compute ssh --zone=us-central1-a client-vm') # Get the ssh key for the Client VM
    os.system("gcloud compute scp --recurse --zone=us-central1-a client_files client-vm:") # Copy client files from local to Client VM
    os.system(f'gcloud compute ssh client-vm --zone=us-central1-a --command="sudo apt install python3-pip --assume-yes"')
    os.system(f'gcloud compute ssh client-vm --zone=us-central1-a --command="pip3 install numpy"')
    os.system(f'gcloud compute ssh client-vm --zone=us-central1-a --command="pip3 install google"')
    os.system(f'gcloud compute ssh client-vm --zone=us-central1-a --command="pip3 install google-cloud-storage"')
    os.system(f'gcloud compute ssh client-vm --zone=us-central1-a --command="pip3 install google-cloud-datastore"')

# Defining the function to delete the Server, Client VMs along with the google cloud storage buckets
def del_vm_gcs():

    os.system("gcloud compute instances delete server-vm --zone=us-central1-a --delete-disks=all") # Delete the Server VM
    os.system("gcloud compute instances delete client-vm --zone=us-central1-a --delete-disks=all") # Delete the Client VM

    # Delete Google Cloud Storage - Bucket
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('gcs-bucket-fall2022')
    bucket.delete(force = True)
    print("Google Cloud Storage - Bucket is deleted!")

    # Delete Google Cloud Storage - Datastore
    datastore_client = datastore.Client()
    kind = "raghav-datastore"
    query = datastore_client.query(kind=kind)
    all_keys = query.fetch()
    for key in all_keys:
        datastore_client.delete(key)
    print("Google Cloud Storage - Datastore is deleted!")

# Defining function to create Google Cloud Storage - Bucket
def create_gcs_bucket():

    # Creating Google Cloud Storage bucket
    storage_client = storage.Client()
    bucket_name = "gcs-bucket-fall2022"
    bucket = storage_client.create_bucket(bucket_name)
    blob = bucket.blob("data.json")

    blob.upload_from_string(data=json.dumps({}),content_type='application/json')
    print("Google Cloud Storage - Bucket is created!")
    

# Defining function to run the server files in the Server VM
def run_server(storage_backend):
    # Run the server.py file
    # os.system(f'gcloud compute ssh server-vm --zone=us-central1-a --command="python3 server_files/server.py {storage_backend} {server_address}"')  
    os.system(f'gcloud compute ssh server-vm --zone=us-central1-a --command="cd server_files && python3 server.py {storage_backend} &"')  

# Defining function to automate all process and run the VM
def run_vm():

    # Set the project
    project_id = sys.argv[1]
    os.system(f"gcloud config set project {project_id}")

    # Setting Google Credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "raghav-cskumar-fall2022-387fa080baee.json"
    
    # Allow project to use the IAP
    # os.system('gcloud compute firewall-rules create allow-ssh-ingress-from-iap --direction=INGRESS --action=allow --rules=tcp:3389 --source-ranges=35.235.240.0/20')

    vm_setup(project_id) # Setup the Server and Client VM

    os.system(f'gcloud compute ssh --zone=us-central1-a client-vm') # Get the ssh key for the Client VM

    # Getting server natIP
    os.system('gcloud compute instances list --format=json > ipaddress.json') # Creating json file for running VMs
    with open('ipaddress.json') as f:
        instances = json.load(f)
        for vm_instance in instances:
            if vm_instance['name'] == 'server-vm':
                server_address = vm_instance['networkInterfaces'][0]['networkIP']
    #             # server_address = vm_instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    print(f"Server Address: {server_address}")

    # The server-vm has to be started by opening the command prompt and running the code: gcloud compute ssh --zone=us-central1-a server-vm
    # After this, you should navigate to server_files: cd server_files/ 
    # Run the command python3 server.py storage_backend(Enter either native, bucket or datastore: whichever storage is being checked)

    # Running Storage - native
    while True:
        native_server = input("Is the native server code running in server-vm (y/n): ")
        if native_server.lower() == "y":
            break
        elif native_server.lower() == "n":
            print("Run the native server code in the server-vm!")
            continue
        else:
            print("Wrong Input!")
            continue

    print("Running the native for client!")
    os.system(f'gcloud compute ssh client-vm --zone=us-central1-a --command="python3 client_files/client.py client_files/client_input_1.txt native {server_address}"') # Run the client.py file

    # Running Storage - bucket
    while True:
        native_server = input("Is the bucket server code running in server-vm (y/n): ")
        if native_server.lower() == "y":
            break
        elif native_server.lower() == "n":
            print("Run the bucket server code in the server-vm!")
            continue
        else:
            print("Wrong Input!")
            continue

    create_gcs_bucket() # Creating bucket in Google Cloud Storage

    print("Running the bucket for client!")
    os.system(f'gcloud compute ssh client-vm --zone=us-central1-a --command="python3 client_files/client.py client_files/client_input_1.txt bucket {server_address}"') # Run the client.py file

    # Running Storage - datastore
    while True:
        native_server = input("Is the datastore server code running in server-vm (y/n): ")
        if native_server.lower() == "y":
            break
        elif native_server.lower() == "n":
            print("Run the datastore server code in the server-vm!")
            continue
        else:
            print("Wrong Input!")
            continue

    print("Running the datastore for client!")
    os.system(f'gcloud compute ssh client-vm --zone=us-central1-a --command="python3 client_files/client.py client_files/client_input_1.txt datastore {server_address}"') # Run the client.py file

    del_vm_gcs() # Delete all the Server and Client VMs along with all storage backends


if __name__ == '__main__':
    run_vm()