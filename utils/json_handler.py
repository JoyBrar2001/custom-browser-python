import json

def read_file(path):
    with open(path, "r") as f:
        return json.load(f)

def write_file(path, update_fn=None, data=None):
    if update_fn is not None:
        current_data = read_file(path)
        new_data = update_fn(current_data)
    
    elif data is not None:
        new_data = data
    
    else:
        raise ValueError("Either update_fn or data must be provided")
    
    with open(path, "w") as f:
        json.dump(new_data, f, indent=4)
        
    return new_data