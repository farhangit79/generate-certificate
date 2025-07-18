import requests
import json

# FortiGate info
FGT_IP = "https://192.168.1.99"
API_TOKEN = "nNrtk4Nfzd8hgmrgccs19Qrq6tzhnr"  # or use Basic Auth user/pass

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# Firewall rule data example (adjust as needed)
rule_data = {
    "json": {
        "name": "jenkins_rule",
        "srcintf": [{"name": "vlan10"}],
        "dstintf": [{"name": "internal"}],
        "srcaddr": [{"name": "all"}],
        "dstaddr": [{"name": "all"}],
        "action": "accept",
        "schedule": "always",
        "service": [{"name": "ALL"}],
        "logtraffic": "all",
        "status": "enable",
        "comments": "Created from Jenkins"
    }
}

url = f"{FGT_IP}/api/v2/cmdb/firewall/policy/"

response = requests.post(url, headers=headers, json=rule_data)

if response.status_code == 200 or response.status_code == 201:
    print("Firewall rule created successfully")
else:
    print(f"Failed to create rule: {response.status_code} {response.text}")
