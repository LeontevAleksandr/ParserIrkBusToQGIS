import json

with open('irkBusPrimer.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

objs = data.get("anims", [])

print(objs[0])