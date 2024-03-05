import boto3
import json
import base64

from onetimesecret import OneTimeSecret
from Logger import Logger

class SFTPUserManager():
    def __init__(self,access_key,secret_id,config,logger:Logger=None) -> None:
        self._client = boto3.client(
            'secretsmanager',
            region_name='us-east-1',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_id
        )
        self.ots = OneTimeSecret()
        self.config = config
        self.logger = logger

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
    
    def delete_sftp_user(self,ARN:str,b64:bool=True):
        if b64:
            ARN = base64.b64decode(ARN.encode()).decode()
        resp = self._client.delete_secret(SecretId=ARN)

        if self.logger:
            self.logger.log(
                'sftpUserDeleted',
                f'ARN: {ARN}'
            )

        return resp
    
    def undelete_sftp_user(self,ARN:str,b64:bool=True):
        if b64:
            ARN = base64.b64decode(ARN.encode()).decode()
        resp = self._client.restore_secret(SecretId=ARN)

        if self.logger:
            self.logger.log(
                'sftpUserRestored',
                f'ARN: {ARN}'
            )

        return resp
    
    def get_deleted_sftp_user(self):
        delUsers = [u for u in self._list_deleted_secrets() if 'DeletedDate' in u.keys()]
        return delUsers
    
    def _list_deleted_secrets(self):
        Filters =[{
                    'Key': 'name',
                    'Values': ['SFTP']
                }]

        for page in self._client.get_paginator("list_secrets").paginate(
            Filters=Filters,
            IncludePlannedDeletion=True
            ):
            yield from page["SecretList"]
        
    
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
    
    def get_random_password(self,len:int=12):
        resp = self._client.get_random_password(
            PasswordLength=len,
            # ExcludeCharacters='string',
            # ExcludeNumbers=True|False,
            # ExcludePunctuation=True|False,
            # ExcludeUppercase=True|False,
            # ExcludeLowercase=True|False,
            # IncludeSpace=True|False,
            # RequireEachIncludedType=True|False
        )
        return {'password':resp['RandomPassword']}
    
    def create_sftp_user(self,data):
        SecretValue = {
        "Password":data['password'],
        "Role":self.config['Role'],
        "HomeDirectory":data['homedir'],
        "Policy": json.dumps({
                'Version': '2012-10-17', 
                'Statement': [
                    {
                        'Sid': 'AllowListingOfUserFolder', 
                        'Action': ['s3:ListBucket'], 
                        'Effect': 'Allow', 
                        'Resource': ['arn:aws:s3:::${transfer:HomeBucket}'], 
                        'Condition': {'StringLike': {'s3:prefix': ['${transfer:HomeFolder}/*', '${transfer:HomeFolder}']}}
                    }, {
                        'Sid': 'HomeDirObjectAccess', 
                        'Effect': 'Allow', 
                        'Action': ['s3:PutObject', 's3:GetObject', 's3:DeleteObjectVersion', 's3:DeleteObject', 's3:GetObjectVersion'], 
                        'Resource': 'arn:aws:s3:::${transfer:HomeDirectory}*'
                    }
                ]
            })
        }


        response = self._client.create_secret(
            Name=data['username'],
            SecretString=json.dumps(SecretValue),
            Description=data['homedir']
        )

        if self.logger:
            self.logger.log(
                'sftpUserCreated',
                f'Name: {data["username"]:<24} HomeDir: {data["homedir"]}'
            )
        
        return response
    
    def update_sftp_user(self,data):
        SecretId =  base64.b64decode(data['ARN_b64'].encode()).decode()
        secret = self._client.get_secret_value(SecretId=SecretId)
        secretJSON = json.loads(secret['SecretString'])

        # Update Values of the secret
        if data['password'] != '':
            secretJSON['Password'] = data['password']    
        secretJSON['HomeDirectory'] = data['homedir']

        response = self._client.update_secret(
            SecretId=SecretId,
            SecretString=json.dumps(secretJSON),
            Description=data['homedir']
        )

        if self.logger:
            self.logger.log(
                'sftpUserUpdated',
                f'Name: {data["username"]}'
            )
        
        return response