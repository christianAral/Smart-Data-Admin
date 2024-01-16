from typing import Any


try:
    from azure.identity import InteractiveBrowserCredential
    from azure.core.exceptions import HttpResponseError
    from azure.mgmt.sql import SqlManagementClient
    from azure.mgmt.sql.models import (
        FirewallRule,
        DatabaseVulnerabilityAssessmentRuleBaseline,
        DatabaseVulnerabilityAssessmentRuleBaselineItem,
    )
    import firewallRuleConfig as FRC
except ImportError:
    raise ImportError("This function requires azure-mgmt-sql and azure-identity. To continue, please install them with one of the commands below:\n\npip install azure-mgmt-sql azure-identity\nconda install -c conda-forge azure-mgmt-sql azure-identity")

class FirewallRuleManager(InteractiveBrowserCredential):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.authenticate()
        self._subscription_id = FRC.SUBSCRIPTION_ID
        self._resource_group_name = FRC.RESOURCE_GROUP_NAME
        self._server_name = FRC.SERVER_NAME
        self._sql_client = SqlManagementClient(self, self._subscription_id)
        self._curr_firewall = []
        self._curr_baseline = []

    def get_firewall_rules(self,refresh=True):
        if refresh==True or not hasattr(self,'_curr_firewall'):
            self._curr_firewall = list(self._sql_client.firewall_rules.list_by_server(
                self._resource_group_name, self._server_name
            ))
        return self._curr_firewall
    
    def get_baseline_rules(self,refresh=True):
        if refresh==True or not hasattr(self,'_curr_baseline'):
            self._curr_baseline = self._sql_client.database_vulnerability_assessment_rule_baselines.get(
                resource_group_name=self._resource_group_name,
                server_name=self._server_name,
                database_name="master",
                vulnerability_assessment_name="VA2065",
                rule_id="VA2065",
                baseline_name="default"
            )
            self._updated_baseline = [r for r in self._curr_baseline.baseline_results]
        
        return self._curr_baseline
    
    def set_baseline_rules(self):
        updateRules = [r.as_dict() for r in self._updated_baseline]
        self._curr_baseline = self._sql_client.database_vulnerability_assessment_rule_baselines.create_or_update(
            resource_group_name=self._resource_group_name,
            server_name=self._server_name,
            database_name="master",
            vulnerability_assessment_name="VA2065",
            rule_id="VA2065",
            baseline_name="default",
                        parameters=DatabaseVulnerabilityAssessmentRuleBaseline(
                baseline_results=updateRules
            )
        )

    def _del_rule(self,instr):
        self._sql_client.firewall_rules.delete(
            self._resource_group_name, 
            self._server_name,
            instr['key']
        )

        self._updated_baseline = [
            r for r in self._updated_baseline if r.result[0] != instr["key"]
        ]

    def _add_rule(self,instr):
        firewall_rule_parameters = FirewallRule(
            start_ip_address=instr['start'], 
            end_ip_address=instr['end']
        )
        self._sql_client.firewall_rules.create_or_update(
            self._resource_group_name,
            self._server_name,
            instr['name'],
            parameters=firewall_rule_parameters,
        )

        new_baseline_item = DatabaseVulnerabilityAssessmentRuleBaselineItem(
            result=[instr['name'], instr['start'], instr['end']]
        )
        self._updated_baseline.append(new_baseline_item)
    
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

        for instr in instructions['deletedRow']:
            try:
                print(f'deleting the {instr["key"]} rule!')
                self._del_rule(instr)
                resp['success']['remove'] += 1
            except HttpResponseError:
                resp['failure']['remove'] += 1

        for instr in instructions['addedRow']:
            try:
                print(f'adding the {instr["key"]} rule!')
                self._add_rule(instr)
                resp['success']['add'] += 1
            except HttpResponseError:
                resp['failure']['add'] += 1

        for instr in instructions['changedRow']:
            try:
                print(f'updating the {instr["key"]} rule!')
                self._del_rule(instr)
                self._add_rule(instr)
                resp['success']['update'] += 1
            except HttpResponseError:
                resp['failure']['update'] += 1

        print('setting baseline')
        self.set_baseline_rules()
        print('baseline set successfully')

        return resp
