import json
from values import *

def GREY(brightness):
    return (brightness,) * 3

def fetch_level_data(level_id):
    level_info = manage_json(f"Levels/level_{level_id}.json", None, mode="r")
    level_data = []
    for w in range(level_info['metadata']['width']):
        level_data.append([])
        for h in range(level_info['metadata']['height']):
            level_data[w].append(level_info['blocks'][f"{w},{h}"])
    return level_data

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


def state_switcher(state_index):
    GameState.current = game_states[state_index]

def lose_game(save):
    state_switcher(4)
    manage_json(f"Saves/save{save}.json", {"difficulty": 0, "level": 0, "checkpoint": 0, "has_started": 0, "save": save})