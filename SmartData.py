from typing import Any
import os
import json
import requests
import datetime
import base64

try:
    from azure.identity import InteractiveBrowserCredential
    from azure.core.exceptions import HttpResponseError
    from azure.mgmt.sql import SqlManagementClient
    from azure.mgmt.sql.models import (
        FirewallRule,
        DatabaseVulnerabilityAssessmentRuleBaseline,
        DatabaseVulnerabilityAssessmentRuleBaselineItem,
    )
    from azure.keyvault.secrets import SecretClient
    from azure.storage.blob import BlobServiceClient
except ImportError:
    reqd_pkgs = ['azure-mgmt-sql','azure-keyvault-secrets','azure-identity','azure-storage-blob']

    raise ImportError(f"This function requires {', '.join(reqd_pkgs)}. "
                      "To continue, please install them with one of the commands below:\n\n"
                      "pip install {' '.join(reqd_pkgs)}\n"
                      "conda install -c conda-forge {' '.join(reqd_pkgs)}")


class SmartDataAdmin():
    def __init__(self, **kwargs: Any) -> None:
        
        # Create Anon classes for sub-process configs
        self.globalConfig = type("", (), {})()
        self.kvConfig = type("", (), {})()
        self.sqlConfig = type("", (), {})()
        self.logger = type("", (), {})()

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

        # get logged in user
        try:
            # Get the access token
            token = self._credential.get_token('https://graph.microsoft.com/.default')

            # Call Microsoft Graph API to get the user's details
            headers = {'Authorization': 'Bearer ' + token.token}
            response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)

            # Get the user's UPN
            self.upn = response.json()['userPrincipalName']
        except:
            self.upn = 'noUser@local.local'
    
    # def _setupKeyvaultClient(self):
        self.kv = SecretClient(
            vault_url=f"https://{self.kvConfig.kvname}.vault.azure.net/", 
            credential=self._credential
        )

    # def _setupBlobLogClient(self):
        logConfig = json.loads(self.kv.get_secret('blobLogConfig').value)
        self.logger.config = logConfig
        self.logger.blob_service_client = BlobServiceClient(
            account_url=f"https://{self.logger.config['storageAccount']}.blob.core.windows.net", 
            credential=self._credential
        )
        self.logger.container_client = self.logger.blob_service_client.get_container_client(
            container=self.logger.config['container']
        )

    # def _setupSQLClient(self):
        sqlConfig = json.loads(self.kv.get_secret('firewallRuleManagerConfig').value)
        SUBSCRIPTION_ID = sqlConfig['SUBSCRIPTION_ID']
        self.sqlConfig.RESOURCE_GROUP_NAME = sqlConfig['RESOURCE_GROUP_NAME']
        self.sqlConfig.SERVER_NAME = sqlConfig['SERVER_NAME']
        self.sqlConfig.curr_firewall = []
        self.sqlConfig.curr_baseline = []

        self.sql = SqlManagementClient(self._credential, SUBSCRIPTION_ID)

    def log(self,type:str,message:str):
        timestamp = datetime.datetime.utcnow().isoformat(timespec='seconds')
        if isinstance(message,dict):
            message = str(message)
        msg_tab_escaped = message.replace('\t','    ')
        bMessage = (f"{timestamp}\t{type}\t{self.upn}\t{msg_tab_escaped}\n").encode()
        
        log_blob = self.logger.blob_service_client.get_blob_client(
            self.logger.config['container'], 
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
        filenames = [b for b in self.logger.container_client.list_blob_names(name_starts_with='SDAdmin/SDAdmin',)]
        
        if b64:
            return [base64.b64encode(fname.encode()).decode() for fname in filenames]
        else:
            return filenames 
    
    def get_log_file(self,filename,b64:bool=True):
        if b64:
            filename = base64.b64decode(filename.encode()).decode()

        print(f'filename: {filename}')
        blobClient = self.logger.container_client.get_blob_client(filename)
        print(f'blobClient exists: {blobClient.exists()}')
        blobStr = blobClient.download_blob().readall().decode('utf-8')
        blobDict = self._tsv2dict(blobStr)
        return blobDict

    def get_firewall_rules(self,refresh=True):
        if refresh==True or not hasattr(self.sqlConfig,'curr_firewall'):
            self.sqlConfig.curr_firewall = list(self.sql.firewall_rules.list_by_server(
                self.sqlConfig.RESOURCE_GROUP_NAME, self.sqlConfig.SERVER_NAME
            ))
        return self.sqlConfig.curr_firewall
    
    def get_baseline_rules(self,refresh=True):
        if refresh==True or not hasattr(self.sqlConfig,'curr_baseline'):
            self.sqlConfig.curr_baseline = self.sql.database_vulnerability_assessment_rule_baselines.get(
                resource_group_name=self.sqlConfig.RESOURCE_GROUP_NAME,
                server_name=self.sqlConfig.SERVER_NAME,
                database_name="master",
                vulnerability_assessment_name="VA2065",
                rule_id="VA2065",
                baseline_name="default"
            )
            self.sqlConfig.updated_baseline = [r for r in self.sqlConfig.curr_baseline.baseline_results]
        
        return self.sqlConfig.curr_baseline
    
    def set_baseline_rules(self):
        updateRules = [r.as_dict() for r in self.sqlConfig.updated_baseline]
        self.sqlConfig.curr_baseline = self.sql.database_vulnerability_assessment_rule_baselines.create_or_update(
            resource_group_name=self.sqlConfig.RESOURCE_GROUP_NAME,
            server_name=self.sqlConfig.SERVER_NAME,
            database_name="master",
            vulnerability_assessment_name="VA2065",
            rule_id="VA2065",
            baseline_name="default",
                        parameters=DatabaseVulnerabilityAssessmentRuleBaseline(
                baseline_results=updateRules
            )
        )

    def _del_rule(self,instr):
        self.sql.firewall_rules.delete(
            self.sqlConfig.RESOURCE_GROUP_NAME, 
            self.sqlConfig.SERVER_NAME,
            instr['key']
        )

        self.sqlConfig.updated_baseline = [
            r for r in self.sqlConfig.updated_baseline if r.result[0] != instr["key"]
        ]

    def _add_rule(self,instr):
        firewall_rule_parameters = FirewallRule(
            start_ip_address=instr['start'], 
            end_ip_address=instr['end']
        )
        self.sql.firewall_rules.create_or_update(
            self.sqlConfig.RESOURCE_GROUP_NAME,
            self.sqlConfig.SERVER_NAME,
            instr['name'],
            parameters=firewall_rule_parameters,
        )

        new_baseline_item = DatabaseVulnerabilityAssessmentRuleBaselineItem(
            result=[instr['name'], instr['start'], instr['end']]
        )
        self.sqlConfig.updated_baseline.append(new_baseline_item)
    
    def update_rules(self,instructions):
        self.get_baseline_rules(True)
        resp = {
            'instructions': {
                'add':len(instructions['addedRow']),
                'update':len(instructions['changedRow']),
                'remove':len(instructions['deletedRow'])
            },
            'success': {
                'add':0,
                'update':0,
                'remove':0
            },
            'failure': {
                'add':0,
                'update':0,
                'remove':0
            }
        }

        for instr in instructions['changedRow']:
            try:
                self.log('firewallChange',instr)
                self._del_rule(instr)
                self._add_rule(instr)
                resp['success']['update'] += 1
            except HttpResponseError:
                resp['failure']['update'] += 1
        for instr in instructions['deletedRow']:
            try:
                self.log('firewallRemove',instr)
                self._del_rule(instr)
                resp['success']['remove'] += 1
            except HttpResponseError:
                resp['failure']['remove'] += 1
        for instr in instructions['addedRow']:
            try:
                self.log('firewallAdd',instr)
                self._add_rule(instr)
                resp['success']['add'] += 1
            except HttpResponseError:
                resp['failure']['add'] += 1

        print('setting baseline')
        self.set_baseline_rules()
        print('baseline set successfully')

        return resp