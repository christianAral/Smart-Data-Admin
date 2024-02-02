import boto3
import json

class SFTPUserManager():
    def __init__(self,access_key,secret_id) -> None:
        self._client = boto3.client(
            'secretsmanager',
            region_name='us-east-1',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_id
        )

    def list_secrets(self,NextToken=None):
        Filters =[{
                    'Key': 'name',
                    'Values': ['SFTP']
                }]

        if NextToken is not None:
            resp = self._client.list_secrets(
                NextToken=NextToken,
                Filters=Filters
            )
        else:
            resp = self._client.list_secrets(
                Filters=Filters
            )
        secretsList = resp['SecretList']
        if "NextToken" in resp:
            secretsList.extend(self.list_secrets(resp['NextToken']))
        
        return secretsList
    
    def get_secret_value(self,SecretId,inclPW:bool=False):
        secret = self._client.get_secret_value(SecretId=SecretId)
        secretJSON = json.loads(secret['SecretString'])
        if inclPW:
            keys = ('Password','HomeDirectory')
        else:
            keys = ('HomeDirectory',)
        filteredJSON = {k:v for k,v in secretJSON.items() if k in keys}

        metadata = self._describe_secret(SecretId=SecretId)
        filteredMetadata = {k:v for k,v in metadata.items() if k in ('Name','Description')}

        return {**filteredJSON,**filteredMetadata,"ARN":SecretId}
    
    def _describe_secret(self,SecretId):
        return self._client.describe_secret(SecretId=SecretId)