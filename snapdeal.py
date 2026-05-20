import os
from datetime import datetime, timezone
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient


subscription_id = os.environ["SUBSCRIPTION_ID"]

threshold_days = int(
    os.environ["THRESHOLD_DAYS"]
)


credential = DefaultAzureCredential()


compute_client = ComputeManagementClient(
    credential,
    subscription_id
)


current_time = datetime.now(timezone.utc)

snapshots = compute_client.snapshots.list()

for snapshot in snapshots:

    snapshot_name = snapshot.name

    resource_group = snapshot.id.split("/")[4]

    creation_time = snapshot.time_created

    age = (current_time - creation_time).total_seconds()/60

    if age > threshold_days:

        print(f"Deleting {snapshot_name}")

        delete_operation = compute_client.snapshots.begin_delete(
            resource_group,
            snapshot_name
        )

        delete_operation.wait()
        print(f"{snapshot_name} deleted")
