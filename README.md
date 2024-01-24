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
pip install azure-mgmt-sql azure-mgmt-keyvault azure-identity
```

Conda
```
conda install -c conda-forge azure-mgmt-sql azure-mgmt-keyvault azure-identity
```
