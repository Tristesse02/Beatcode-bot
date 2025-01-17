import json

# load the json file
with open('combined.json') as f:
    data = json.load(f)
    
for problem in data:
    print(problem['title'])
    
