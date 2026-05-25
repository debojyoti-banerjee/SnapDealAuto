from datetime import datetime, timezone


class SnapshotService:
    def __init__(self,compute_client,threshold_minutes):
        self.compute_client = compute_client
        self.threshold_minutes = threshold_minutes

    def get_deleted_snapshots_data(self,virtual_machines,email_service,lead_email):
        current_time = datetime.now(timezone.utc)
        deleted_snapshot_data = []
        snapshots = self.compute_client.snapshots.list()
        for snapshot in snapshots:
            snapshot_name = snapshot.name
            resource_group = snapshot.id.split("/")[4]
            creation_time =snapshot.time_created
            age_minutes = (current_time - creation_time).total_seconds() / 60
            source_disk_id = snapshot.creation_data.source_resource_id
            match_vm = None
            for vm in virtual_machines:
                if (vm.storage_profile.os_disk and vm.storage_profile.os_disk.managed_disk):
                    os_disk_id =vm.storage_profile.os_disk.managed_disk.id
                    if (os_disk_id == source_disk_id):
                        match_vm = vm
                        break
            if match_vm:
                tags = match_vm.tags
                if tags:
                    delete_tag = tags.get("delete_snapshot")
                    if (delete_tag == "true" and age_minutes > self.threshold_minutes):
                        delete_operation = self.compute_client.snapshots.begin_delete(
                                resource_group,
                                snapshot_name
                            )
                        delete_operation.wait()
                        print(f"{snapshot_name}deleted successfully")
                        email_service.send_email(
                            lead_email,
                            snapshot_name,
                            match_vm.name,
                            resource_group
                        )
                        deleted_snapshot_data.append({

                            "Snapshot Name": snapshot_name,
                            "Resource Group": resource_group,
                            "VM Name": match_vm.name,
                            "Created Time": str(creation_time),
                            "Deleted Time": str(current_time),
                        })
        return deleted_snapshot_data