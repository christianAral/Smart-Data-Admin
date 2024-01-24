# Configuration

## Environment Variables
| KEY                 | VALUE                                |
|---------------------|--------------------------------------|
| AZURE_TENANT_ID     | a1b2c3d4-e5f6-g7h8-i9j0-abcdef123456 |
| AZURE_KEYVAULT_NAME | NAME-OF-KEYVAULT                     |

## Python Packages
Run one of these code blocks in a terminal depending on if your package manager is pip or conda

PIP
```
pip install flask azure-identity azure-mgmt-sql azure-keyvault-secrets
```

Conda
```
conda install -c conda-forge flask azure-identity azure-mgmt-sql azure-keyvault-secrets
```
# Usage
* On launch, Microsoft Authentication will launch in browser and a new window will also open at http://localhost:5000
* Current Firewall rules are "refreshed" every time the page reloads
* Operations include "Add", "Update", and "Delete"
* Validations
  * Two firewall rules cannot share the same name
  * IP addresses must follow the format 111.222.333.444
* "Commit Firewall Rules" will update the servers firewall rules and sync that change to Microsoft Cloud Defender Baseline