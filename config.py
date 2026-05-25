import os

subscription_id = os.environ["SUBSCRIPTION_ID"]
threshold_minutes = int(os.environ["THRESHOLD_MINUTES"])
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
email_addr=os.environ["EMAIL_ADDRESS"]
email_pass=os.environ["EMAIL_PASSWORD"]
lead_email=os.environ["LEAD_EMAIL"]

container_name="reports"
blob_name = "deleted_snapshots.xlsx"
excel_file = "deleted_snapshots.xlsx"