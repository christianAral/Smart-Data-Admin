import os
import json

from Logger import Logger
from FirewallRuleManager import FirewallRuleManager

try:
    from azure.identity import InteractiveBrowserCredential
    from azure.keyvault.secrets import SecretClient
    from azure.core.exceptions import HttpResponseError
    from azure.mgmt.sql import SqlManagementClient
    from azure.mgmt.sql.models import (
        FirewallRule,
        DatabaseVulnerabilityAssessmentRuleBaseline,
        DatabaseVulnerabilityAssessmentRuleBaselineItem,
    )
    from azure.storage.blob import BlobServiceClient
except ImportError:
    with open('requirements.txt','r', encoding='utf-16') as reqs:
        reqd_pkgs = [req.split('==')[0] for req in reqs.read().split('\n')]

    raise ImportError(f"This function requires {', '.join(reqd_pkgs)}. "
                      "To continue, please install them with one of the commands below:\n\n"
                      f"  pip install {' '.join(reqd_pkgs)}\n"
                      f"  conda install -c conda-forge {' '.join(reqd_pkgs)}")


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
