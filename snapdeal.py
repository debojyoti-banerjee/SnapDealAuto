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

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

blob_client = blob_service_client.get_blob_client(container=container_name,blob=blob_name)

try:

    with open(excel_file, "wb") as file:
        download_stream = blob_client.download_blob()
        file.write(download_stream.readall())
    print("Old Excel downloaded")
except Exception:
    print("No previous Excel found")

if os.path.exists(excel_file):
    final_dataframe = pd.read_excel(excel_file)
else:
    final_dataframe = pd.DataFrame()

current_time = datetime.now(timezone.utc)

snapshots = compute_client.snapshots.list()

deleted_snapshots = []

for snapshot in snapshots:

    snapshot_name = snapshot.name

    resource_group = snapshot.id.split("/")[4]

    creation_time = snapshot.time_created

    age_minutes = (current_time - creation_time).total_seconds() / 60

    if age_minutes > threshold_minutes:
        print(f"Deleting {snapshot_name}")
        delete_operation = compute_client.snapshots.begin_delete(resource_group,snapshot_name)
        delete_operation.wait()
        deleted_snapshots.append({
            "Snapshot Name": snapshot_name,
            "Resource Group": resource_group,
            "Creation Time": str(creation_time),
            "Deleted Time": str(datetime.now(timezone.utc))
        })
        print(f"{snapshot_name} deleted")


new_dataframe = pd.DataFrame(deleted_snapshots)

final_dataframe = pd.concat([final_dataframe, new_dataframe],ignore_index=True)

final_dataframe.to_excel(excel_file,index=False)

with open(excel_file, "rb") as data:
    blob_client.upload_blob(data,overwrite=True)

print("Excel uploaded to Blob Storage")