import json

json_data=open("ValkyrieDriveConfig.json").read()

data = json.loads(json_data)
print(data)
