import json

json_data=open("TestSaveFile.txt").read()

data = json.loads(json_data)
print(data)

print(data["packet"][0]["data_id"])
print(data["packet"][0]["data"][1]["input"])