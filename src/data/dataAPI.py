import json
from collections import namedtuple
from json import JSONEncoder
def save(data_dict):
        jsonString = json.dumps(data_dict, default=lambda o: o.__dict__, indent=4)
        print(jsonString)
        with open("data/data.json", 'w') as outfile:
            outfile.write(jsonString)
            outfile.close()

def read():
    with open("data/data.json", 'r') as data_file:
        objs = json.loads(data_file.read())
        data_file.close()
        return objs




