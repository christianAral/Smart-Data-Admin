from typing import Any


try:
    import json
    from DotDict import DotDict as DD
    from dataclasses import dataclass
    from azure.identity import InteractiveBrowserCredential
    from azure.mgmt.sql import SqlManagementClient
    from azure.mgmt.sql.models import (
        FirewallRule,
        DatabaseVulnerabilityAssessmentRuleBaseline,
        DatabaseVulnerabilityAssessmentRuleBaselineItem,
    )
    import firewallRuleConfig as FRC
except ImportError:
    raise ImportError("This function requires azure-mgmt-sql and azure-identity. To continue, please install them with one of the commands below:\n\npip install azure-mgmt-sql azure-identity\nconda install -c conda-forge azure-mgmt-sql azure-identity")

# @dataclass
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
                baseline_name="default",
            )
        return self._curr_baseline
