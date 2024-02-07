import requests
from pathlib import Path

def CheckVersion():
    _VERSION_PATH = Path(__file__).with_name("version")
    with open(_VERSION_PATH,'r') as f:
        content = f.read()
    resp = requests.get('https://raw.githubusercontent.com/christianAral/Smart-Data-Admin/main/version').text
    return (content == resp)
