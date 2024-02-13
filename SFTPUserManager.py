import boto3
import json
import base64

from onetimesecret import OneTimeSecret

class SFTPUserManager():
    def __init__(self,access_key,secret_id) -> None:
        self._client = boto3.client(
            'secretsmanager',
            region_name='us-east-1',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_id
        )
        self.ots = OneTimeSecret()

    def get_sftp_user_info(self):
        allSecrets = self._batch_get_secret_value()
        secretList = []
        for secret in allSecrets:
            thisSecret = {k:v for k,v in secret.items() if k in ('ARN','Name')}
            thisSecret['HomeDirectory'] = json.loads(secret['SecretString'])['HomeDirectory']
            secretList.append(thisSecret)
        return secretList

    def get_sftp_user_password(self,ARN:str,b64:bool=True,asLink:bool=True,passphrase:str=None):
        if b64:
            ARN = base64.b64decode(ARN.encode()).decode()
        sftpUserInfo = self._get_secret_value(ARN,True)
        
        if asLink: # Feed this through OneTimeSecret
            ots = self.ots.share(sftpUserInfo['Password'],passphrase)
            return {'secret_url':ots['secret_url']}
        else:
            return {'Password':sftpUserInfo['Password']}
    
    def _batch_get_secret_value(self,NextToken=None):
        Filters =[{
                    'Key': 'name',
                    'Values': ['SFTP']
                }]

        if NextToken is not None:
            resp = self._client.batch_get_secret_value(
                NextToken=NextToken,
                Filters=Filters
            )
        else:
            resp = self._client.batch_get_secret_value(
                Filters=Filters
            )
        secretsList = resp['SecretValues']
        if "NextToken" in resp:
            secretsList.extend(self._batch_get_secret_value(resp['NextToken']))
        
        return secretsList
    
    def _get_secret_value(self,SecretId,inclPW:bool=False):
        secret = self._client.get_secret_value(SecretId=SecretId)
        secretJSON = json.loads(secret['SecretString'])
        if inclPW:
            keys = ('Password','HomeDirectory')
        else:
            keys = ('HomeDirectory',)
        filteredJSON = {k:v for k,v in secretJSON.items() if k in keys}

        metadata = self._describe_secret(SecretId=SecretId)
        filteredMetadata = {k:v for k,v in metadata.items() if k in ('Name')}

        return {**filteredJSON,**filteredMetadata,"ARN":SecretId}
    
    def _describe_secret(self,SecretId):
        return self._client.describe_secret(SecretId=SecretId)