import json

def GREY(brightness):
    return (brightness,) * 3

def autoloadlevel(level, level_id):
    pass

def manage_json(file_name, data, mode="w"):   
    #"w" is write mode, "r" is read mode
    if mode == "w":
        with open(file_name, mode) as file:
            json.dump(data, file, indent=4)
    elif mode == "r":
        with open(file_name, mode) as file:
            return json.load(file)
    else:
        pass