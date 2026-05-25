import pandas as pd

class StorageService:
    def __init__(self,blob_client,excel_file):
        self.blob_client=blob_client
        self.excel_file=excel_file

    def download_existing_excel(self):
        try:
            with open(excel_file, "wb") as download_file:
                download_stream = (blob_client.download_blob())
                download_file.write(download_stream.readall())
                old_dataframe = pd.read_excel(excel_file,engine="openpyxl")
                print("Old Excel Loaded")
                return old_dataframe

        except Exception:
            print(("No Previous excel found"))
            old_dataframe = pd.DataFrame()
            return old_dataframe

    def upload_excel(self,dataframe):
        dataframe.to_excel(self.excel_file,index=False,engine="openpyxl")
        with open(self.excel_file, "rb") as data:
            self.blob_client.upload_blob(data,overwrite=True)
            print("Excel file Uploaded successfully")
  

