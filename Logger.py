import datetime
import base64
from azure.storage.blob import BlobServiceClient

class Logger():
    def __init__(self,credential,logConfig,UPN) -> None:
        self.config = logConfig
        self.upn = UPN
        self.blob_service_client = BlobServiceClient(
            account_url=f"https://{self.config['storageAccount']}.blob.core.windows.net", 
            credential=credential
        )
        self.container_client = self.blob_service_client.get_container_client(
            container=self.config['container']
        )

    def log(self,type:str,message:str):
        timestamp = datetime.datetime.utcnow().isoformat(timespec='seconds')
        if isinstance(message,dict):
            message = str(message)
        msg_tab_escaped = message.replace('\t','    ')
        bMessage = (f"{timestamp}\t{type}\t{self.upn}\t{msg_tab_escaped}\n").encode()
        
        log_blob = self.blob_service_client.get_blob_client(
            self.config['container'], 
            f"SDAdmin/SDAdmin_{timestamp[:10]}.log"
        )
        if not log_blob.exists():
            log_blob.create_append_blob()
            headers = '\t'.join(['timestamp','type','user','message']) + '\n'
            log_blob.append_block(headers.encode())

        log_blob.append_block(bMessage)

    def _tsv2dict(self,tsv:str) -> dict:
        lines = tsv.split('\n')
        header = lines[0].split('\t')
        data_lines = lines[1:-1]

        result = []
        for line in data_lines:
            columns = line.split('\t')
            row_dict = {header[i] if i < len(header) else f'Field{i}': col for i, col in enumerate(columns)}
            result.append(row_dict)

        return result
    
    def list_log_file_names(self,b64:bool=True):
        filenames = [b for b in self.container_client.list_blob_names(name_starts_with='SDAdmin/SDAdmin',)]
        
        if b64:
            return [base64.b64encode(fname.encode()).decode() for fname in filenames]
        else:
            return filenames 
    
    def get_log_file(self,filename,b64:bool=True):
        if b64:
            filename = base64.b64decode(filename.encode()).decode()
        blobClient = self.container_client.get_blob_client(filename)
        blobStr = blobClient.download_blob().readall().decode('utf-8')
        blobDict = self._tsv2dict(blobStr)
        return blobDict