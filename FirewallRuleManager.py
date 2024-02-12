import json

from azure.core.exceptions import HttpResponseError
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.sql.models import (
    FirewallRule,
    DatabaseVulnerabilityAssessmentRuleBaseline,
    DatabaseVulnerabilityAssessmentRuleBaselineItem,
)

class FirewallRuleManager():
    def __init__(self,credential,sqlConfig,logger) -> None:
        self.RESOURCE_GROUP_NAME = sqlConfig['RESOURCE_GROUP_NAME']
        self.SERVER_NAME = sqlConfig['SERVER_NAME']
        self.curr_firewall = []
        self.curr_baseline = []
        self.logger = logger

        self.sql = SqlManagementClient(credential, sqlConfig['SUBSCRIPTION_ID'])

    def test_firewall_checksum(self):
        server_firewall = list(self.sql.firewall_rules.list_by_server(
                self.RESOURCE_GROUP_NAME, self.SERVER_NAME
            ))
        
        checksum_curr = hash("\n".join(sorted([f"{rule.name}_{rule.start_ip_address}_{rule.end_ip_address}" for rule in self.curr_firewall])))
        checksum_new  = hash("\n".join(sorted([f"{rule.name}_{rule.start_ip_address}_{rule.end_ip_address}" for rule in server_firewall])))

        if checksum_curr == checksum_new:
            status = {"synced":True}
        else:
            status = {"synced":False}

        return status

    def get_firewall_rules(self,refresh=True):
        if refresh==True or not hasattr(self,'curr_firewall'):
            self.curr_firewall = list(self.sql.firewall_rules.list_by_server(
                self.RESOURCE_GROUP_NAME, self.SERVER_NAME
            ))
        return self.curr_firewall
    
    def get_baseline_rules(self,refresh=True):
        if refresh==True or not hasattr(self,'curr_baseline'):
            self.curr_baseline = self.sql.database_vulnerability_assessment_rule_baselines.get(
                resource_group_name=self.RESOURCE_GROUP_NAME,
                server_name=self.SERVER_NAME,
                database_name="master",
                vulnerability_assessment_name="VA2065",
                rule_id="VA2065",
                baseline_name="default"
            )
            self.updated_baseline = [r for r in self.curr_baseline.baseline_results]
        
        return self.curr_baseline
    
    def check_baseline_synced(self):
        if self.curr_firewall == []:
            self.get_firewall_rules()
        if self.curr_baseline == []:
            self.get_baseline_rules()

        # Convert dictionaries to strings for comparison
        firewall_dict = [{k: v for k, v in d.__dict__.items() if k in ['name', 'start_ip_address', 'end_ip_address']} for d in self.curr_firewall]
        baseline_dict = [{'name':b.result[0],'start_ip_address':b.result[1],'end_ip_address':b.result[2]} for b in self.curr_baseline.baseline_results]

        firewall_list = [json.dumps(d, sort_keys=True) for d in firewall_dict]
        baseline_list = [json.dumps(d, sort_keys=True) for d in baseline_dict]

        # Find unique dictionaries in each list
        unique_in_firewall = [json.loads(d) for d in firewall_list if d not in baseline_list]
        unique_in_baseline = [json.loads(d) for d in baseline_list if d not in firewall_list]

        # Add "__onlyExistsIn" key to each dictionary
        for d in unique_in_firewall:
            d['__onlyExistsIn'] = 'firewall'
        for d in unique_in_baseline:
            d['__onlyExistsIn'] = 'baseline'

        # Combine the lists and return
        return unique_in_firewall + unique_in_baseline
    
    def set_baseline_rules(self):
        updateRules = [r.as_dict() for r in self.updated_baseline]
        self.curr_baseline = self.sql.database_vulnerability_assessment_rule_baselines.create_or_update(
            resource_group_name=self.RESOURCE_GROUP_NAME,
            server_name=self.SERVER_NAME,
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
            self.RESOURCE_GROUP_NAME, 
            self.SERVER_NAME,
            instr['key']
        )

        self.updated_baseline = [
            r for r in self.updated_baseline if r.result[0] != instr["key"]
        ]

    def _add_rule(self,instr):
        firewall_rule_parameters = FirewallRule(
            start_ip_address=instr['start'], 
            end_ip_address=instr['end']
        )
        self.sql.firewall_rules.create_or_update(
            self.RESOURCE_GROUP_NAME,
            self.SERVER_NAME,
            instr['name'],
            parameters=firewall_rule_parameters,
        )

        new_baseline_item = DatabaseVulnerabilityAssessmentRuleBaselineItem(
            result=[instr['name'], instr['start'], instr['end']]
        )
        self.updated_baseline.append(new_baseline_item)
    
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
                self.logger.log('firewallChange',instr)
                self._del_rule(instr)
                self._add_rule(instr)
                resp['success']['update'] += 1
            except HttpResponseError:
                resp['failure']['update'] += 1
        for instr in instructions['deletedRow']:
            try:
                self.logger.log('firewallRemove',instr)
                self._del_rule(instr)
                resp['success']['remove'] += 1
            except HttpResponseError:
                resp['failure']['remove'] += 1
        for instr in instructions['addedRow']:
            try:
                self.logger.log('firewallAdd',instr)
                self._add_rule(instr)
                resp['success']['add'] += 1
            except HttpResponseError:
                resp['failure']['add'] += 1

        self.set_baseline_rules()

        return resp