#!/usr/bin/env python
# coding: utf-8

# In[1]:


try:
    import json
    from tkinter import *
    from tkinter import messagebox
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


# In[8]:


def update_firewall_rules(payload):
    # Variables
    subscription_id = FRC.SUBSCRIPTION_ID
    resource_group_name = FRC.RESOURCE_GROUP_NAME
    server_name = FRC.SERVER_NAME

    new_rule_name, ip_address, rule_name_to_remove = json.loads(payload)

    # Authenticate with Azure
    credential = InteractiveBrowserCredential()

    # Create SQL management client
    sql_client = SqlManagementClient(credential, subscription_id)

    # Retrieve the current firewall rules
    # current_firewall_rules = get_firewall_rules(sql_client, resource_group_name, server_name)
    current_firewall_rules = list(sql_client.firewall_rules.list_by_server(
        resource_group_name, server_name
    ))
    
    # Check if rule_name_to_remove is present in the current firewall rules
    rule_present = any(
        rule.name == rule_name_to_remove for rule in current_firewall_rules
    )
    
    print(rule_present)

    if not rule_present:
        rule_name_to_remove = show_firewall_rules_window(
            rule_name_to_remove, current_firewall_rules
        )

    print(rule_name_to_remove)
        
    if rule_name_to_remove != 'SD_Exit_Process':
        # Remove existing IP firewall rule
        print("removing the old firewall rule")
        removed_firewall_rule = None
        if rule_name_to_remove:
            removed_firewall_rule = sql_client.firewall_rules.get(
                resource_group_name, server_name, rule_name_to_remove
            )
            sql_client.firewall_rules.delete(
                resource_group_name, server_name, rule_name_to_remove
            )

        # Create new IP firewall rule
        print("adding the new firewall rule")
        firewall_rule_parameters = FirewallRule(
            start_ip_address=ip_address, 
            end_ip_address=ip_address
        )
        added_firewall_rule = sql_client.firewall_rules.create_or_update(
            resource_group_name,
            server_name,
            new_rule_name,
            parameters=firewall_rule_parameters,
        )

        # Get current Defender for Cloud baseline
        print("getting the baseline")
        baseline = sql_client.database_vulnerability_assessment_rule_baselines.get(
            resource_group_name=resource_group_name,
            server_name=server_name,
            database_name="master",
            vulnerability_assessment_name="VA2065",
            rule_id="VA2065",
            baseline_name="default",
        )
        
        # Filter the current baseline rules to exclude the rule we want to remove
        updated_baseline = [
            result for result in baseline.baseline_results if result.result[0] != rule_name_to_remove
        ]

        # Add the new rule to the updated_baseline list
        new_baseline_item = DatabaseVulnerabilityAssessmentRuleBaselineItem(
            result=[new_rule_name, ip_address, ip_address]
        )
        updated_baseline.append(new_baseline_item)

        # Convert DatabaseVulnerabilityAssessmentRuleBaselineItem objects to dictionaries
        updated_baseline_dicts = [item.as_dict() for item in updated_baseline]

        # Update the Defender for Cloud baseline
        print("committing the new baseline")
        sql_client.database_vulnerability_assessment_rule_baselines.create_or_update(
            resource_group_name=resource_group_name,
            server_name=server_name,
            database_name="master",
            vulnerability_assessment_name="VA2065",
            rule_id="VA2065",
            baseline_name="default",
            parameters=DatabaseVulnerabilityAssessmentRuleBaseline(
                baseline_results=updated_baseline_dicts
            ),
        )

        # Show a summary window of the actions that have been taken
        print("showing summary")
        show_summary_window(
            removed_firewall=removed_firewall_rule,
            added_firewall=added_firewall_rule
        )
    else:
        print("we were instructed to not continue. Below are runtime variables")
        print(f"{new_rule_name=}")
        print(f"{ip_address=}")
        print(f"{rule_name_to_remove=}")
        print(f"{rule_present=}")
        


# In[3]:


# Function to display tkinter window for input
def get_payload():
    def submit():
        if is_valid_payload(entry.get()):
            payload.set(entry.get())
            root.destroy()
        else:
            messagebox.showerror("Error", "Please enter a valid payload.")

    root = Tk()
    root.title("Enter Payload")
    root.geometry("300x100")

    label = Label(root, text="Paste payload from Alteryx:")
    label.pack(pady=10)

    entry = Entry(root, width=30)
    entry.pack()

    payload = StringVar()
    submit_button = Button(root, text="Submit", command=submit)
    submit_button.pack(pady=10)

    root.mainloop()

    return payload.get()


# In[4]:


def is_valid_payload(s):
    try:
        data = json.loads(s)
        if isinstance(data, list) and len(data) == 3:
            return all(isinstance(item, str) for item in data)
        else:
            return False
    except ValueError:
        return False


# In[5]:


def show_firewall_rules_window(rule_name_to_remove, current_firewall_rules):
    
    # When the listbox is selected, make the delete button clickable
    def on_listbox_select(event):
        delete_button.config(state=NORMAL)

    # When the skip button is selected, exit this window and continue the workflow
    def skip():
        rules_window.destroy()
    
    # When the delete button is selected, update the value of the selected rule for deletion
    def delete():
        nonlocal selected_rule_name
        selected_rule_name = listbox.get(listbox.curselection())
        rules_window.destroy()
        
    # When the red X is selected, terminate the workflow run
    def cancel():
        nonlocal selected_rule_name
        selected_rule_name = 'SD_Exit_Process'
        rules_window.destroy()

    selected_rule_name = None
    rules_window = Tk()
    rules_window.title("Firewall Rules")
    rules_window.protocol("WM_DELETE_WINDOW", cancel)

    Label(
        rules_window,
        text=f'The provided rule name to delete ({rule_name_to_remove}) was not present.',
    ).grid(row=0, column=0, sticky=W)
    
    Label(
        rules_window, 
        text="You can either select a different rule name or skip this step"
    ).grid(row=1, column=0, sticky=W)

    Label(
        rules_window, 
        text="Current Firewall Rules:"
    ).grid(row=2, column=0, sticky=W)

    listbox = Listbox(rules_window)
    listbox.grid(row=3, column=0, sticky=NSEW)
    listbox.bind("<<ListboxSelect>>", on_listbox_select)

    for rule in current_firewall_rules:
        listbox.insert(END, f"{rule.name} ({rule.start_ip_address})")

    skip_button = Button(
        rules_window, 
        text="Skip", 
        command=skip
    )
    skip_button.grid(row=4, column=0, sticky=W)

    delete_button = Button(
        rules_window, 
        text="Delete", 
        command=delete, 
        state=DISABLED
    )
    delete_button.grid(row=4, column=0, sticky=E)

    # Configure the column weight to make the listbox expand with the window
    rules_window.columnconfigure(0, weight=1)
    rules_window.rowconfigure(2, weight=1)

    rules_window.mainloop()

    return selected_rule_name.split(" ")[0] if selected_rule_name else None


# In[6]:


def show_summary_window(removed_firewall, added_firewall):
    def close_window():
        summary_window.destroy()

    summary_window = Tk()
    summary_window.title("Summary")

    if removed_firewall.name == added_firewall.name:
        color = "#9C5700"
        text = f"Updated {removed_firewall.name}: {removed_firewall.start_ip_address} --> {added_firewall.start_ip_address}"
        Label(summary_window, text=text, fg=color).pack()
    
    if removed_firewall and removed_firewall != added_firewall:
        color = "#9C0006"
        text = F"Removed {removed_firewall.name}: {removed_firewall.start_ip_address}"
        Label(summary_window, text=text, fg=color).pack()

    if added_firewall and removed_firewall != added_firewall:
        color = "#006100"
        text = F"Added {added_firewall.name}: {added_firewall.start_ip_address}"
        Label(summary_window, text=text, fg=color).pack()

    Button(summary_window, text="Close", command=close_window).pack()

    summary_window.mainloop()


# In[9]:


if __name__ == "__main__":
    update_firewall_rules(get_payload())


# In[ ]:




