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

def load_image(sprite, size=(32, 32), transform=True):
    image = None
    try:
        if transform:
            image = pygame.transform.scale(pygame.image.load(sprite).convert_alpha(), size)
        else:
            image = pygame.image.load(sprite).convert_alpha()
    except FileNotFoundError:
        if transform:
            image = pygame.transform.scale(pygame.image.load("Assets/Images/ErrorSprite.png").convert_alpha(), size)
        else:
            image = pygame.image.load("Assets/Images/ErrorSprite.png").convert_alpha()
    except Exception:
        image = pygame.Surface(size)
    finally:
        return image

def con_ttk(text, default):
    " Converts text (like 'a' or '7') into a key. Used for keybind translation."
    text = str(text)
    if text == "`": return pygame.K_BACKQUOTE
    elif text == '1': return pygame.K_1
    elif text == '2': return pygame.K_2
    elif text == '3': return pygame.K_3
    elif text == '4': return pygame.K_4
    elif text == '5': return pygame.K_5
    elif text == '6': return pygame.K_6
    elif text == '7': return pygame.K_7
    elif text == '8': return pygame.K_8
    elif text == '9': return pygame.K_9
    elif text == '0': return pygame.K_0
    elif text == '-': return pygame.K_MINUS
    elif text == '=': return pygame.K_EQUALS
    elif text == 'bs': return pygame.K_BACKSPACE
    elif text == 'tab': return pygame.K_TAB
    elif text == 'q': return pygame.K_q
    elif text == 'w': return pygame.K_w
    elif text == 'e': return pygame.K_e
    elif text == 'r': return pygame.K_r
    elif text == 't': return pygame.K_t
    elif text == 'y': return pygame.K_y
    elif text == 'u': return pygame.K_u
    elif text == 'i': return pygame.K_i
    elif text == 'o': return pygame.K_o
    elif text == 'p': return pygame.K_p
    elif text == '[': return pygame.K_LEFTBRACKET
    elif text == ']': return pygame.K_RIGHTBRACKET
    elif text == '\\': return pygame.K_BACKSLASH
    elif text == 'caps': return pygame.K_CAPSLOCK
    elif text == 'a': return pygame.K_a
    elif text == 's': return pygame.K_s
    elif text == 'd': return pygame.K_d
    elif text == 'f': return pygame.K_f
    elif text == 'g': return pygame.K_g
    elif text == 'h': return pygame.K_h
    elif text == 'j': return pygame.K_j
    elif text == 'k': return pygame.K_k
    elif text == 'l': return pygame.K_l
    elif text == ':': return pygame.K_COLON
    elif text == "'": return pygame.K_QUOTE
    elif text == "enter": return pygame.K_RETURN
    elif text == 'lshift': return pygame.K_LSHIFT
    elif text == 'z': return pygame.K_z
    elif text == 'x': return pygame.K_x
    elif text == 'c': return pygame.K_c
    elif text == 'v': return pygame.K_v
    elif text == 'b': return pygame.K_b
    elif text == 'n': return pygame.K_n
    elif text == 'm': return pygame.K_m
    elif text == ',': return pygame.K_COMMA
    elif text == '.': return pygame.K_PERIOD
    elif text == '/': return pygame.K_SLASH
    elif text == 'rshift': return pygame.K_RSHIFT
    elif text == 'lctrl': return pygame.K_LCTRL
    elif text == 'lalt': return pygame.K_LALT
    elif text == 'space': return pygame.K_SPACE
    elif text == 'ralt': return pygame.K_RALT
    elif text == 'left': return pygame.K_LEFT
    elif text == 'up': return pygame.K_UP
    elif text == 'down': return pygame.K_DOWN
    elif text == 'right': return pygame.K_RIGHT
    elif text == 'pgup': return pygame.K_PAGEUP
    elif text == 'pgdn': return pygame.K_PAGEDOWN
    elif text == 'esc': return pygame.K_ESCAPE
    elif text == 'f1': return pygame.K_F1
    elif text == 'f2': return pygame.K_F2
    elif text == 'f3': return pygame.K_F3
    elif text == 'f4': return pygame.K_F4
    elif text == 'f5': return pygame.K_F5
    elif text == 'f6': return pygame.K_F6
    elif text == 'f7': return pygame.K_F7
    elif text == 'f8': return pygame.K_F8
    elif text == 'f9': return pygame.K_F9
    elif text == 'f10': return pygame.K_F10
    elif text == 'f11': return pygame.K_F11
    elif text == 'f12': return pygame.K_F12
    elif text == 'f13': return pygame.K_F13
    elif text == 'f14': return pygame.K_F14
    elif text == 'f15': return pygame.K_F15
    elif text == 'del': return pygame.K_DELETE
    elif text == 'pause': return pygame.K_PAUSE
    elif text == 'ins': return pygame.K_INSERT
    elif text == 'home': return pygame.K_HOME
    elif text == 'end': return pygame.K_END
    elif text == 'k1': return pygame.K_KP1
    elif text == 'k2': return pygame.K_KP2
    elif text == 'k3': return pygame.K_KP3
    elif text == 'k4': return pygame.K_KP4
    elif text == 'k5': return pygame.K_KP5
    elif text == 'k6': return pygame.K_KP6
    elif text == 'k7': return pygame.K_KP7
    elif text == 'k8': return pygame.K_KP8
    elif text == 'k9': return pygame.K_KP9
    elif text == 'k0': return pygame.K_KP0
    elif text == 'k.': return pygame.K_KP_PERIOD
    elif text == 'kenter': return pygame.K_KP_ENTER
    elif text == 'k+': return pygame.K_KP_PLUS
    elif text == 'k-': return pygame.K_KP_MINUS
    elif text == 'k*': return pygame.K_KP_MULTIPLY
    elif text == 'k/': return pygame.K_KP_DIVIDE
    elif text == 'nl': return pygame.K_NUMLOCK
    elif text == 'sl': return pygame.K_SCROLLLOCK
    else: return default

def con_ktt(key, default):
    " Converts a Pygame key into the corresponding text. Used for config saving keybind and keybind displays."
    key = int(key)
    if key == pygame.K_BACKQUOTE: return "`"
    elif key == pygame.K_1: return '1'
    elif key == pygame.K_2: return '2'
    elif key == pygame.K_3: return '3'
    elif key == pygame.K_4: return '4'
    elif key == pygame.K_5: return '5'
    elif key == pygame.K_6: return '6'
    elif key == pygame.K_7: return '7'
    elif key == pygame.K_8: return '8'
    elif key == pygame.K_9: return '9'
    elif key == pygame.K_0: return '0'
    elif key == pygame.K_MINUS: return '-'
    elif key == pygame.K_EQUALS: return '='
    elif key == pygame.K_BACKSPACE: return 'bs'
    elif key == pygame.K_TAB: return 'tab'
    elif key == pygame.K_q: return 'q'
    elif key == pygame.K_w: return 'w'
    elif key == pygame.K_e: return 'e'
    elif key == pygame.K_r: return 'r'
    elif key == pygame.K_t: return 't'
    elif key == pygame.K_y: return 'y'
    elif key == pygame.K_u: return 'u'
    elif key == pygame.K_i: return 'i'
    elif key == pygame.K_o: return 'o'
    elif key == pygame.K_p: return 'p'
    elif key == pygame.K_LEFTBRACKET: return '['
    elif key == pygame.K_RIGHTBRACKET: return ']'
    elif key == pygame.K_BACKSLASH: return '\\'
    elif key == pygame.K_CAPSLOCK: return 'caps'
    elif key == pygame.K_a: return 'a'
    elif key == pygame.K_s: return 's'
    elif key == pygame.K_d: return 'd'
    elif key == pygame.K_f: return 'f'
    elif key == pygame.K_g: return 'g'
    elif key == pygame.K_h: return 'h'
    elif key == pygame.K_j: return 'j'
    elif key == pygame.K_k: return 'k'
    elif key == pygame.K_l: return 'l'
    elif key == pygame.K_COLON: return ':'
    elif key == pygame.K_QUOTE: return "'"
    elif key == pygame.K_RETURN: return 'enter'
    elif key == pygame.K_LSHIFT: return 'lshift'
    elif key == pygame.K_z: return 'z'
    elif key == pygame.K_x: return 'x'
    elif key == pygame.K_c: return 'c'
    elif key == pygame.K_v: return 'v'
    elif key == pygame.K_b: return 'b'
    elif key == pygame.K_n: return 'n'
    elif key == pygame.K_m: return 'm'
    elif key == pygame.K_COMMA: return ','
    elif key == pygame.K_PERIOD: return '.'
    elif key == pygame.K_SLASH: return '/'
    elif key == pygame.K_RSHIFT: return 'rshift'
    elif key == pygame.K_LCTRL: return 'lctrl'
    elif key == pygame.K_LALT: return 'lalt'
    elif key == pygame.K_SPACE: return 'space'
    elif key == pygame.K_RALT: return 'ralt'
    elif key == pygame.K_LEFT: return 'left'
    elif key == pygame.K_UP: return 'up'
    elif key == pygame.K_DOWN: return 'down'
    elif key == pygame.K_RIGHT: return 'right'
    elif key == pygame.K_PAGEUP: return 'pgup'
    elif key == pygame.K_PAGEDOWN: return 'pgdn'
    elif key == pygame.K_ESCAPE: return 'esc'
    elif key == pygame.K_F1: return 'f1'
    elif key == pygame.K_F2: return 'f2'
    elif key == pygame.K_F3: return 'f3'
    elif key == pygame.K_F4: return 'f4'
    elif key == pygame.K_F5: return 'f5'
    elif key == pygame.K_F6: return 'f6'
    elif key == pygame.K_F7: return 'f7'
    elif key == pygame.K_F8: return 'f8'
    elif key == pygame.K_F9: return 'f9'
    elif key == pygame.K_F10: return 'f10'
    elif key == pygame.K_F11: return 'f11'
    elif key == pygame.K_F12: return 'f12'
    elif key == pygame.K_F13: return 'f13'
    elif key == pygame.K_F14: return 'f14'
    elif key == pygame.K_F15: return 'f15'
    elif key == pygame.K_DELETE: return 'del'
    elif key == pygame.K_PAUSE: return 'pause'
    elif key == pygame.K_INSERT: return 'ins'
    elif key == pygame.K_HOME: return 'home'
    elif key == pygame.K_END: return 'end'
    elif key == pygame.K_KP1: return 'k1'
    elif key == pygame.K_KP2: return 'k2'
    elif key == pygame.K_KP3: return 'k3'
    elif key == pygame.K_KP4: return 'k4'
    elif key == pygame.K_KP5: return 'k5'
    elif key == pygame.K_KP6: return 'k6'
    elif key == pygame.K_KP7: return 'k7'
    elif key == pygame.K_KP8: return 'k8'
    elif key == pygame.K_KP9: return 'k9'
    elif key == pygame.K_KP0: return 'k0'
    elif key == pygame.K_KP_PERIOD: return 'k.'
    elif key == pygame.K_KP_ENTER: return 'kenter'
    elif key == pygame.K_KP_PLUS: return 'k+'
    elif key == pygame.K_KP_MINUS: return 'k-'
    elif key == pygame.K_KP_MULTIPLY: return 'k*'
    elif key == pygame.K_KP_DIVIDE: return 'k/'
    elif key == pygame.K_NUMLOCK: return 'nl'
    elif key == pygame.K_SCROLLLOCK: return 'sl'
    else: return default