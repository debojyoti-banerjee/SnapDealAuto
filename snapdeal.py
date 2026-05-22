import os
from datetime import datetime, timezone
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.storage.blob import BlobServiceClient


subscription_id = os.environ["SUBSCRIPTION_ID"]

threshold_minutes = int(os.environ["THRESHOLD_MINUTES"])

connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

container_name = "reports"

blob_name = "deleted_snapshots.xlsx"

excel_file = "deleted_snapshots.xlsx"

credential = DefaultAzureCredential()

compute_client = ComputeManagementClient(credential,subscription_id)

blob_service_client = (BlobServiceClient.from_connection_string(connection_string))

container_client = (blob_service_client.get_container_client(container_name))

blob_client = (container_client.get_blob_client(blob_name))

current_time = datetime.now(timezone.utc)

virtual_machines = (compute_client.virtual_machines.list_all())

deleted_snapshot_data = []

snapshots = compute_client.snapshots.list()

for snapshot in snapshots:

    snapshot_name = snapshot.name

    resource_group = snapshot.id.split("/")[4]

    creation_time = snapshot.time_created

    age_minutes = (current_time - creation_time).total_seconds() / 60

    source_disk_id = (snapshot.creation_data.source_resource_id)

    match_vm = None

    for vm in virtual_machines:

        if (vm.storage_profile.os_disk and vm.storage_profile.os_disk.managed_disk):
            os_disk_id = (vm.storage_profile.os_disk.managed_disk.id)
            if os_disk_id == source_disk_id:
                match_vm = vm
                break

    if match_vm:
        tags = match_vm.tags
        if tags:
            delete_tag = tags.get("delete_snapshot")
            if (delete_tag == "true" and age_minutes > threshold_minutes):
                delete_operation = (compute_client.snapshots.begin_delete(resource_group,snapshot_name))
                delete_operation.wait()
                print(f"{snapshot_name} deleted successfully")
                deleted_snapshot_data.append({
                    "Snapshot Name": snapshot_name,
                    "Resource Group": resource_group,
                    "VM Name": match_vm.name,
                    "Created Time": str(creation_time),
                    "Deleted Time": str(datetime.now(timezone.utc)),
                })

new_dataframe = pd.DataFrame(deleted_snapshot_data)

try:
    with open(excel_file, "wb") as download_file:
        download_stream = (blob_client.download_blob())
        download_file.write(download_stream.readall())

    old_dataframe = pd.read_excel(excel_file,engine="openpyxl")
    print("Old Excel Loaded")

except Exception:
    old_dataframe = pd.DataFrame()
    print("No Previous Excel Found")

final_dataframe = pd.concat([old_dataframe, new_dataframe],ignore_index=True)

final_dataframe.to_excel(excel_file,index=False,engine="openpyxl")

with open(excel_file, "rb") as data:
    blob_client.upload_blob(data,overwrite=True)


print("Excel Uploaded Successfully")