import json
  

print('hej')
# Data to be written
dictionary ={
    "constants" : {
        'test' : 1,
        'tmp' : 12
    }
}
  
# Serializing json 
json_object = json.dumps(dictionary, indent = 4)
  
# Writing to sample.json
with open("../config.json", "w") as outfile:
    outfile.write(json_object)
