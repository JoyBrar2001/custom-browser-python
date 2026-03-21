import json

def read_file(path):
    with open(path, "r") as f:
        return json.load(f)

def write_file(path, update_fn):
    data = read_file(path)
    
    new_data = update_fn(data)
    
    with open(path, "w") as f:
        json.dump(new_data, f, indent=4)
        
    return new_data