import smtplib
from email.mime.text import MIMEText

class EmailService:
    def __init__(self,email_address,email_password):
        self.email_address=email_address
        self.email_password=email_password

    def send_email(self,lead_email,snapshot_name,vm_name,resource_group):
        subject=f"Snapshot deletion: {snapshot_name}"
        body=f"""
        Snapshot Cleanup Alert
        Snapshot Name: {snapshot_name}
        VM Name: {vm_name}
        Resource Group: {resource_group}
        Status: Snapshot Deleted successfully
        """
        message=MIMEText(body)
        message["Subject"]=subject
        message["From"]=self.email_address
        message["To"]=lead_email
        with smtplib.SMTP("smtp.gmail.com",587) as server:
            server.starttls()
            server.login(self.email_address,self.email_password)
            server.send_message(message)
            Print("Messaged send Successfully")