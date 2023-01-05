<h1 align="center">
Cloud Key-Value Store
</h1>

### Objective:

The project's primary goals are to evaluate various cloud storage options and implement the Memcached-lite service on public cloud VMs. The GCP cloud VMs and GCP storages are used to do this.

### Implementation:
*	Set up GCP account and API
* Create a service account key to access the GCP storages
*	Created ssh keys for Server and Client VMs
*	Launched the Server and Client VMs
*	Copied the relevant files for running the performance tests on the different storages
*	Created two storage backends – Bucket and Datastore apart from the Native storage
*	All the Storage and the VMs are shutdown and deleted after the tests

### Storage Backends:

#### Native – 
*	This storage is the one which is present in the Server-VM.
*	The type of storage is a json file and the keys and values are updated in this file by the server.

#### Bucket – 
*	This is a cloud storage and is present as one Google Cloud Storages.
*	The type of storage used is a json file created as one of the objects in the Bucket. The keys and values are updated in this object json file by the server.

#### Datastore – 
*	This is a No-SQL cloud storage and is present as one Google Cloud Storages.
*	The type of storage is in the form of entities which store in the form of keys and values. The server updates these entities by creating or updating with given key and value.

### How to run or perform the tests using the code?

The **VM.py** file is a singular code file which contains all the operations that need to be done from setting the VM & storages, perform the tests on the storages and deleting the storages and VMs.

Before running the **VM.py** file, it is necessary to add the service account key(json file) in the server_files folder else an error is invoked for no access to the GCP storages. 

Apart from running this single file, you will be prompted 3 times to run the Server VM through the command prompt as shown below:
* The server-vm has to be started by opening the command prompt and running the code: gcloud compute ssh --zone=us-central1-a server-vm
* After this, you should navigate to server_files: cd server_files/ 
* Run the command python3 server.py storage_backend(Enter either native, bucket or datastore) – Example for native: python3 server.py native

#### Code changes:

The only code changes that need to be done is for the change in the name of the service account key (json file). This name change needs to be implemented in 2 code files which are **VM.py** and **server.py**. In the below code - 

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "raghav-cskumar-fall2022-387fa080baee.json"

Instead of "raghav-cskumar-fall2022-387fa080baee.json", replace it with your service account key name (json file name).

* VM.py: Line 91
* server.py : Line 123

### Operations performed and tested:

The operation performed on the native, bucket & datastore storages are running a bunch of set and get commands by reading through the storages respectively and checking their performance. The below table showcases the number of tasks run and the average performance of each type of storage – 

![Evaluation](https://user-images.githubusercontent.com/96961381/210670813-0fdb8f21-9a49-4dcc-883a-ca2829963a9f.JPG)

The native storage was chosen so that it can act as a comparison with other cloud storages. It can be seen that it performed the best as the data is present in the same VM and not external.

The first cloud storage chosen is the Bucket. This stores data in the form of objects and for any operations done to update these objects, the object has to be overwritten resulting in more time to perform operations. This can be seen in the performance table as it took almost 2 seconds for each task.

Comparatively, the Datastore being a No-SQL storage already stores it in the form of key-value making any creation, updating or retrieval much faster than the bucket. It can be observed that although it is not better than Native, it took around 0.8 seconds which is still really good.

### Outputs: 

#### Native – 

![Native](https://user-images.githubusercontent.com/96961381/210671202-100b8d1a-ad56-41bd-96ed-fcda3583f299.jpeg)

#### Bucket –

![Bucket](https://user-images.githubusercontent.com/96961381/210671197-8877be64-b621-4974-bf71-e85e220b15ab.jpeg)

#### Datastore –

![Datastore](https://user-images.githubusercontent.com/96961381/210671199-5c027930-2ed6-4bea-b663-fadfe6ae3206.jpeg)
