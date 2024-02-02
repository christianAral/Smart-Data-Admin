import os
import json

from Logger import Logger
from FirewallRuleManager import FirewallRuleManager
import CheckRequirements

from azure.identity import InteractiveBrowserCredential
from azure.keyvault.secrets import SecretClient

class SmartDataAdmin():
    def __init__(self) -> None:
        
        # Create Anon classes for sub-process configs
        self.globalConfig = type("", (), {})()
        self.kvConfig = type("", (), {})()

    # def _checkEnvironVariables(self):
        self.globalConfig.tenantid = os.environ.get('AZURE_TENANT_ID')
        self.kvConfig.kvname = os.environ.get('AZURE_KEYVAULT_NAME')
        
        if self.globalConfig.tenantid is None \
        or self.kvConfig.kvname is None:
            raise EnvironmentError("The Smart Data Admin Class requires two environment variables, 'AZURE_TENANT_ID' and 'AZURE_KEYVAULT_NAME'. "
                                   "Please add these to your environment variables and try again.")

    # def _login(self):    
        self._credential = InteractiveBrowserCredential(
            tenant_id=self.globalConfig.tenantid, 
            allow_multitenant_authentication=True
        )
        self._credential.authenticate()
    
    # def _setupKeyvaultClient(self):
        self.kv = SecretClient(
            vault_url=f"https://{self.kvConfig.kvname}.vault.azure.net/", 
            credential=self._credential
        )

        logConfig = json.loads(self.kv.get_secret('blobLogConfig').value)
        self.logger = Logger(self._credential,logConfig)

        sqlConfig = json.loads(self.kv.get_secret('firewallRuleManagerConfig').value)
        self.firewallMGR = FirewallRuleManager(self._credential,sqlConfig,self.logger)
