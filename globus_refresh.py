import argparse
import os
from datetime import datetime
import time
import hashlib
import globus_sdk
from globus_sdk.scopes import TransferScopes
from utils_folder import filehash
from utils_folder import compute_dir_index
from utils_folder import compute_diff
import getpass
import os
import shutil



#get client ID from globus online you need this to be able to access globus transfer
CLIENT_ID = "8641b548-8e95-4708-af68-6af6212931b2"
auth_client = globus_sdk.NativeAppAuthClient(CLIENT_ID)


# we will need to do the login flow potentially twice, so define it as a
# function
#
# we default to using the Transfer "all" scope, but it is settable here
# look at the ConsentRequired handler below for how this is used
def login_and_get_transfer_client(*, scopes=TransferScopes.all):
    auth_client.oauth2_start_flow(requested_scopes=scopes)
    authorize_url = auth_client.oauth2_get_authorize_url()
    print(f"Please go to this URL and login:\n\n{authorize_url}\n")

    auth_code = input("Please enter the code here: ").strip()
    tokens = auth_client.oauth2_exchange_code_for_tokens(auth_code)
    transfer_tokens = tokens.by_resource_server["transfer.api.globus.org"]

    # return the TransferClient object, as the result of doing a login
    return globus_sdk.TransferClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(transfer_tokens["access_token"])
    )


# define the submission step -- we will use it twice below
def do_submit(client):
    task_doc = client.submit_transfer(task_data)
    task_id = task_doc["task_id"]
    print(f"submitted transfer, task_id={task_id}")



# get an initial client to try with, which requires a login flow
transfer_client = login_and_get_transfer_client()


TRANSFER_FOLDER = 'C:/Users/rfratus/Documents/oct/transfer' 

#local path
path = 'C:/Users/rfratus/Documents/oct/Test' 
files = []
subdirs = []

for root, dirs, filenames in os.walk(path):
    for subdir in dirs:
        subdirs.append(os.path.relpath(os.path.join(root, subdir), path))

    for f in filenames:
        files.append(os.path.relpath(os.path.join(root, f), path))


index = {}
for f in files:
    index[f] = os.path.getmtime(os.path.join(path, files[0]))

diff = compute_dir_index(path)


#here is a loop that watches a folder for changes to send a transfer request when a change is detected, then automatically deletes transferred files
flag1 = 0
print("watching for file changes")
while(1):


    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith((".oct", ".tiff", ".raw", ".tif")):
                destss = shutil.move(root + '/' + name, TRANSFER_FOLDER)
                print(destss)

    #here detects when a change occured, functions are in utils folder
    diff2 = compute_dir_index(TRANSFER_FOLDER)
    data = compute_diff(diff2, diff)


    #this triggers if files are created or updated in the folder
    if(bool(data.get('created')) == True or bool(data.get('updated')) == True):
        
        # create a Transfer task consisting of one or more items
        task_data = globus_sdk.TransferData(
            source_endpoint="b192e704-5d64-11ee-8775-1dc3121de006", destination_endpoint="33fdf1d5-7b1c-4a21-8d3b-dd4b48d60dfa"
        )


        task_data.add_item(
            "/C/Users/rfratus/Documents/oct/Test",  # source
            "/project/jonccal/ecocoat/data/oct/Test",
            recursive=True
        )
            
        diff = diff2
        print("change found")
        print(data)
        try:
            task_doc = transfer_client.submit_transfer(task_data)
            task_id = task_doc["task_id"]
            print(f"submitted transfer, task_id={task_id}")
        except globus_sdk.TransferAPIError as err:
            # if the error is something other than consent_required, reraise it,
            # exiting the script with an error message
            if not err.info.consent_required:
                raise

            # we now know that the error is a ConsentRequired
            # print an explanatory message and do the login flow again
            print(
                "Encountered a ConsentRequired error.\n"
                "You must login a second time to grant consents.\n\n"
            )
            transfer_client = login_and_get_transfer_client(
                scopes=err.info.consent_required.required_scopes
            )

            # finally, try the submission a second time, this time with no error
            # handling
            task_doc = transfer_client.submit_transfer(task_data)
            task_id = task_doc["task_id"]
            print(f"submitted transfer, task_id={task_id}")



        start_time = time.time()
        #this watches the submitted job to wait for completion so avoid a double transfer request
        while not transfer_client.task_wait(task_id, timeout=60):
            print(f"Job ID: {task_id} minute of transferring")
        print("Transfer Complete")
        print("--- %s seconds ---" % (time.time() - start_time))


        #transfer is complete deleting files
        root_dir = TRANSFER_FOLDER
        file_set = set()

        for dir_, _, files in os.walk(root_dir):
            for file_name in files:
                rel_dir = os.path.relpath(dir_, root_dir)
                rel_file = os.path.join(rel_dir, file_name)
                file_set.add(rel_file)
            
        print(file_set)

        for f in file_set:
            f = f.replace("\\\\", "\\")
            print(f)
            os.remove('C:\\Users\\rfratus\\Documents\\oct\\transfer' + f)


        for f in os.walk(TRANSFER_FOLDER,topdown=False):

            rdir = f[0]
            rdir = rdir.replace("\\\\", "\\")
            print(rdir)

            if rdir != TRANSFER_FOLDER:
                os.rmdir('C:' + rdir)

    
