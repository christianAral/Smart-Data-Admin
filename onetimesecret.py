import requests

class NoSecretProvidedException(Exception):
    pass

class OneTimeSecret():
    def __init__(self,USERNAME:str=None,APITOKEN:str=None,APIVERSION:str=None) -> None:
        version = 'v1' if APIVERSION is None else APIVERSION
        self.baseurl = 'https://onetimesecret.com'
        self.apiurl = f'{self.baseurl}/api/{version}'
        self.secreturl = f'{self.baseurl}/secret/'
        if USERNAME != None and APITOKEN != None:
            self.auth = requests.auth.HTTPBasicAuth(USERNAME,APITOKEN)
        else:
            self.auth = None

    '''
    Current status of the system.

    Parameters
        None
    '''
    @property
    def status(self):
        resp = requests.get(
            self.apiurl + '/status',
            auth=self.auth    
        )
        try:
            return resp.json()
        except:
            return resp.text
        

    '''
    Use this method to store a secret value.

    Query Params
        secret: the secret value which is encrypted before being stored. There is a maximum length based on your plan that is enforced (1k-10k).
        passphrase: a string that the recipient must know to view the secret. This value is also used to encrypt the secret and is bcrypted before being stored so we only have this value in transit.
        ttl: the maximum amount of time, in seconds, that the secret should survive (i.e. time-to-live). Once this time expires, the secret will be deleted and not recoverable.
        recipient: an email address. We will send a friendly email containing the secret link (NOT the secret itself).
    Attributes
        custid: this is you :]
        metadata_key: the unique key for the metadata. DO NOT share this.
        secret_key: the unique key for the secret you create. This is key that you can share.
        ttl: The time-to-live (in seconds) that was specified (i.e. not the time remaining)
        metadata_ttl: The remaining time (in seconds) that the metadata has left to live.
        secret_ttl: The remaining time (in seconds) that the secret has left to live.
        recipient: if a recipient was specified, this is an obfuscated version of the email address.
        created: Time the secret was created in unix time (UTC)
        updated: ditto, but the time it was last updated.
        passphrase_required: If a passphrase was provided when the secret was created, this will be true. Otherwise false, obviously.
    '''
    # def share(self,secret:str,passphrase:str=None,ttl:int=None,recipient:str=None) -> dict:
    def share(self,secret:str,passphrase:str=None,ttl:int=None,recipient:str=None) -> dict:
        if secret in (None,''):
            raise NoSecretProvidedException('No secret text was provided!')

        data = {'secret':secret.encode('utf-8'),'ttl':3600*24 if ttl == None else ttl}

        if passphrase not in (None,''):
            data.update({"passphrase":passphrase.encode("utf-8")})
        if recipient not in (None,''):
            data.update({"recipient":recipient.encode("utf-8")})

        resp = requests.post(
            url=self.apiurl + '/share',
            auth=self.auth,
            data=data
        )
        try:
            secreturl = self.secreturl + resp.json()['secret_key']
            return {**resp.json(),"secret_url":secreturl}
        except:
            return resp.text 
    
    '''
    Generate a short, unique secret. This is useful for temporary passwords, one-time pads, salts, etc.

    Query Params
        passphrase: a string that the recipient must know to view the secret. This value is also used to encrypt the secret and is bcrypted before being stored so we only have this value in transit.
        ttl: the maximum amount of time, in seconds, that the secret should survive (i.e. time-to-live). Once this time expires, the secret will be deleted and not recoverable.
        recipient: an email address. We will send a friendly email containing the secret link (NOT the secret itself).
    '''
    # def generate(self,passphrase:str=None,ttl:int=None,recipient:str=None) -> dict:
    def generate(self,passphrase:str=None,ttl:int=None,recipient:str=None) -> dict:
        data = {'ttl':3600*24 if ttl == None else ttl}

        if passphrase not in (None,''):
            data.update({"passphrase":passphrase.encode("utf-8")})
        if recipient not in (None,''):
            data.update({"recipient":recipient.encode("utf-8")})

        resp = requests.post(
            url=self.apiurl + '/generate',
            auth=self.auth,
            data=data
        )
        try:
            secreturl = self.secreturl + resp.json()['secret_key']
            return {**resp.json(),"secret_url":secreturl}
        except:
            return resp.text 
        



