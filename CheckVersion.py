import requests

def CheckVersion():
    try:
        with open('version','r') as f:
            content = f.read()
        resp = requests.get('https://raw.githubusercontent.com/christianAral/Smart-Data-Admin/main/version').text
        return (content == resp)
    except:
        return True