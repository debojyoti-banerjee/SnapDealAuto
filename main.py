import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.storage.blob import BlobServiceClient
from config import *
from email_service import EmailService
from storage_services import StorageService
from snapshot_manager import SnapshotService 


credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential,subscription_id)
blob_service_client = (BlobServiceClient.from_connection_string(connection_string))
container_client = (blob_service_client.get_container_client(container_name))
blob_client = (container_client.get_blob_client(blob_name))



virtual_machines = (compute_client.virtual_machines.list_all())



email_service=EmailService(email_addr,email_pass)
storage_service=StorageService(blob_client,excel_file)
snapshot_service=SnapshotService(compute_client,threshold_minutes)



old_dataframe=storage_service.download_existing_excel()
deleted_snapshot_data=snapshot_service.get_deleted_snapshots_data(virtual_machines,email_service,lead_email)
new_dataframe=pd.DataFrame(deleted_snapshot_data)
final_dataframe = pd.concat([old_dataframe, new_dataframe],ignore_index=True)
storage_service.upload_excel(final_dataframe)