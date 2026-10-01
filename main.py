import pygame, json
import classes
from math import *
from commands import *
import values
from classes import *
from platforms import *
from groups import *

pygame.init()

# --- SETUP --- #
# Game Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shackles - Early Dev v5")
clock = pygame.time.Clock()

# Joystick Setup
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    print(f"Controller {joystick.get_name()} connected!")
else:
    joystick = DecoyController()

# Config
running = True
config = manage_json("Config/config.json", None, mode="r")
debug = config['debug']
audio = config['audio']
key_slash = con_ttk(config['keybinds']['slash'], pygame.K_w)
key_left = con_ttk(config['keybinds']['left'], pygame.K_a)
key_right = con_ttk(config['keybinds']['right'], pygame.K_d)
key_jump = con_ttk(config['keybinds']['jump'], pygame.K_SPACE)
key_pause = con_ttk(config['keybinds']['pause'], pygame.K_s)
key_dash = con_ttk(config['keybinds']['dash'], pygame.K_q)
key_interact = con_ttk(config['keybinds']['interact'], pygame.K_e)
key_debug = con_ttk(config['keybinds']['debug'], pygame.K_TAB)

# --- EFFECTS --- #
class Effect:
    def __init__(self, name, target, severity):
        self.name = name
        self.target = target
        self.severity = severity

# --- MACROS --- #

def load_save_file(save_num):
    global game_save, player, sword
    save = manage_json(f"Saves/save{save_num}.json", None, mode="r")
    game_save = save_num
    state_switcher(2)
    create_level(save['level'])
    plat_to_group()
    player.health = save['player_data']['health']
    player.max_health = save['player_data']['max_health']
    player.lives = save['player_data']['lives']
    sword.handle = save['sword_data']['handle']
    sword.blade = save['sword_data']['blade']
    sword.foreblade = save['sword_data']['foreblade']
    sword.sheath = save['sword_data']['sheath']

def save_and_quit():
    config = {
        "debug": True,
        "audio": True,
        "keybinds": {
            "left": con_ktt(key_left, 'a'),
            "right": con_ktt(key_right, 'd'),
            "slash": con_ktt(key_slash, 'w'),
            "jump": con_ktt(key_jump, 'space'),
            "pause": con_ktt(key_pause, 's'),
            "dash": con_ktt(key_dash, 'q'),
            "interact": con_ktt(key_interact, 'e'),
            "debug": con_ktt(key_debug, 'tab')
        }
    }
    manage_json("Config/config.json", config)
    state_switcher(0)

def att_spawn_enemy(pos):
    active_enemy_count = sum(isinstance(sprite, Swordsman) for sprite in enemy_render_group) + sum(isinstance(sprite, Archer) for sprite in enemy_render_group)
    if active_enemy_count >= 8 or random() >= 0.00001:
        return False

    if randint(1, 5) <= 3:
        new_foe = Swordsman(pos, False)
        new_foe_sword = Sword(new_foe, old_set)
        new_foe.weapon = new_foe_sword
        enemy_render_group.add(new_foe, new_foe_sword)
    else:
        new_foe = Archer(pos)
        new_foe_bow = Bow(new_foe)
        new_foe.weapon = new_foe_bow
        enemy_render_group.add(new_foe, new_foe_bow)
    return True

def force_off():
    global running
    running = False

def open_save_creator(save_num):
    state_switcher(6)
    global game_save
    game_save = save_num

def create_save(save_num, difficulty):
    manage_json(f"Saves/save{save_num}.json", {"difficulty": difficulty, "level": 0, "checkpoint": 0, "has_started": 1, "save": save_num, "player_data": {"health": 20, "max_health": 20, "lives": 3}, "sword_data": {"handle": "Handle - Old", "blade": "Blade - Old", "foreblade": "Foreblade - Old", "sheath": "Sheath - Old"}}, mode="w")
    load_save_file(save_num)

def return_new_pieces(piece):
    if piece is None or not isinstance(piece, SwordPiece):
        return [sword.handle, sword.blade, sword.foreblade, sword.sheath]

    if piece.piece == "Handle":
        return [piece, sword.blade, sword.foreblade, sword.sheath]
    elif piece.piece == "Blade":
        return [sword.handle, piece, sword.foreblade, sword.sheath]
    elif piece.piece == "Foreblade":
        return [sword.handle, sword.blade, piece, sword.sheath]
    elif piece.piece == "Sheath":
        return [sword.handle, sword.blade, sword.foreblade, piece]
    else:
        return [sword.handle, sword.blade, sword.foreblade, sword.sheath]

def sword_ui_swap():
    global sword, piece_selection_circle
    selected = classes.item_selected
    if selected is None or not isinstance(selected, SwordPiece):
        return

    swap_pieces = return_new_pieces(selected)
    if len(swap_pieces) < 4:
        swap_pieces = [sword.handle, sword.blade, sword.foreblade, sword.sheath]

    sword.load_sword_pieces(sword.piece_interpreter(swap_pieces))
    if piece_selection_circle.pos[0] <= WIDTH//2:
        piece_selection_circle.pos = [WIDTH//3*2, HEIGHT//2]
    else:
        piece_selection_circle.pos = [WIDTH//3, HEIGHT//2]

# --------------- #
# --- BUTTONS --- #
# --------------- #

# Title Screen
play_button = Button((WIDTH//2, HEIGHT//2), (WIDTH//4, HEIGHT//8), "PLAY GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: state_switcher(1))
title_settings_button = Button((WIDTH//2, HEIGHT//16*11), (WIDTH//4, HEIGHT//8), "SETTINGS", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: state_switcher(5))
exit_button = Button((WIDTH//2, HEIGHT//8*7), (WIDTH//4, HEIGHT//8), "EXIT GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: force_off())

# Save Selection
if bool(manage_json("Saves/save1.json", None, mode="r")['has_started']):
    save_button_1 = Button((WIDTH//2, HEIGHT//2.5), (WIDTH//4, HEIGHT//8), f"SAVE 1 - Lv.{manage_json('Saves/save1.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(1))
else:
    save_button_1 = Button((WIDTH//2, HEIGHT//2.5), (WIDTH//4, HEIGHT//8), "SAVE 1", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: open_save_creator(1))
if bool(manage_json("Saves/save2.json", None, mode="r")['has_started']):
    save_button_2 = Button((WIDTH//2, HEIGHT//1.66), (WIDTH//4, HEIGHT//8), f"SAVE 2 - Lv.{manage_json('Saves/save2.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(2))
else:
    save_button_2 = Button((WIDTH//2, HEIGHT//1.66), (WIDTH//4, HEIGHT//8), "SAVE 2", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: open_save_creator(2))
if bool(manage_json("Saves/save3.json", None, mode="r")['has_started']):
    save_button_3 = Button((WIDTH//2, HEIGHT//1.25), (WIDTH//4, HEIGHT//8), f"SAVE 3 - Lv.{manage_json('Saves/save3.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(3))
else:
    save_button_3 = Button((WIDTH//2, HEIGHT//1.25), (WIDTH//4, HEIGHT//8), "SAVE 3", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: open_save_creator(3))
save_buttons = [save_button_1, save_button_2, save_button_3]

# Save Creator
difficulty_button = ScrollButton((WIDTH//2, HEIGHT//2.5), (WIDTH//4, HEIGHT//8), pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Save Creator", difficulties)
difficulty_button.trigger_effect = difficulty_button.scroll
create_save_button = Button((WIDTH//2, HEIGHT//1.66), (WIDTH//4, HEIGHT//8), "Create Save", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Save Creator", trigger_effect=lambda: create_save(game_save, difficulty_button.index))

# Pause Menu
resume_button = Button((WIDTH//2, HEIGHT//8*3), (WIDTH//4, HEIGHT//8), "Resume Game", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(2))
quit_button = Button((WIDTH//2, HEIGHT//8*7), (WIDTH//4, HEIGHT//8), "Save and Quit", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: save_and_quit())
settings_button = Button((WIDTH//2, HEIGHT//8*5), (WIDTH//4, HEIGHT//8), "Settings", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(5))

# Game Over
main_menu_button = Button((WIDTH//2, HEIGHT//4*3), (WIDTH//2, HEIGHT//8), "Go Back to Main Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Game Over", trigger_effect=lambda: back_to_main_menu())

# Settings
back_to_pause = Button((WIDTH//4, HEIGHT//8*3), (WIDTH//2.5, HEIGHT//8), "Return to Pause Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Settings", trigger_effect=lambda: state_switcher(3))
back_to_title = Button((WIDTH//4*3, HEIGHT//8*3), (WIDTH//2.5, HEIGHT//8), "Return to Title Screen", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Settings", trigger_effect=lambda: back_to_main_menu())

# Sword UI
swap_button = Button((WIDTH//2, HEIGHT//1.5), (WIDTH//4, HEIGHT//8), "Swap Pieces", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Sword UI", trigger_effect=lambda: sword_ui_swap())

def reload_buttons():
    global play_button, exit_button, save_button_1, save_button_2, save_button_2, save_button_3, save_buttons, resume_button, quit_button, settings_button, main_menu_button, back_to_pause, difficulty_button, create_save_button
    play_button = Button((WIDTH//2, HEIGHT//2), (WIDTH//4, HEIGHT//8), "PLAY GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: state_switcher(1))
    title_settings_button = Button((WIDTH//2, HEIGHT//16*11), (WIDTH//4, HEIGHT//8), "SETTINGS", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: state_switcher(5))
    exit_button = Button((WIDTH//2, HEIGHT//8*7), (WIDTH//4, HEIGHT//8), "EXIT GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: force_off())
    if bool(manage_json("Saves/save1.json", None, mode="r")['has_started']): save_button_1 = Button((WIDTH//2, HEIGHT//2.5), (WIDTH//4, HEIGHT//8), f"SAVE 1 - Lv.{manage_json('Saves/save1.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(1))
    else: save_button_1 = Button((WIDTH//2, HEIGHT//2.5), (WIDTH//4, HEIGHT//8), "SAVE 1", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: open_save_creator(1))
    if bool(manage_json("Saves/save2.json", None, mode="r")['has_started']): save_button_2 = Button((WIDTH//2, HEIGHT//1.66), (WIDTH//4, HEIGHT//8), f"SAVE 2 - Lv.{manage_json('Saves/save2.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(2))
    else: save_button_2 = Button((WIDTH//2, HEIGHT//1.66), (WIDTH//4, HEIGHT//8), "SAVE 2", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: open_save_creator(2))
    if bool(manage_json("Saves/save3.json", None, mode="r")['has_started']): save_button_3 = Button((WIDTH//2, HEIGHT//1.25), (WIDTH//4, HEIGHT//8), f"SAVE 3 - Lv.{manage_json('Saves/save3.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(3))
    else: save_button_3 = Button((WIDTH//2, HEIGHT//1.25), (WIDTH//4, HEIGHT//8), "SAVE 3", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: open_save_creator(3))
    save_buttons = [save_button_1, save_button_2, save_button_3]
    difficulty_button = ScrollButton((WIDTH//2, HEIGHT//2.5), (WIDTH//4, HEIGHT//8), pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Save Creator", difficulties)
    difficulty_button.trigger_effect = difficulty_button.scroll
    create_save_button = Button((WIDTH//2, HEIGHT//1.66), (WIDTH//4, HEIGHT//8), "Create Save", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Save Creator", trigger_effect=lambda: create_save(game_save, difficulty_button.index))
    resume_button = Button((WIDTH//2, HEIGHT//8*3), (WIDTH//4, HEIGHT//8), "Resume Game", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(2))
    quit_button = Button((WIDTH//2, HEIGHT//8*7), (WIDTH//4, HEIGHT//8), "Save and Quit", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: save_and_quit())
    settings_button = Button((WIDTH//2, HEIGHT//8*5), (WIDTH//4, HEIGHT//8), "Settings", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(5))
    main_menu_button = Button((WIDTH//2, HEIGHT//4*3), (WIDTH//2, HEIGHT//8), "Go Back to Main Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Game Over", trigger_effect=lambda: back_to_main_menu())
    back_to_pause = Button((WIDTH//4, HEIGHT//8*3), (WIDTH//2.5, HEIGHT//8), "Return to Pause Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Settings", trigger_effect=lambda: state_switcher(3))
    back_to_title = Button((WIDTH//4*3, HEIGHT//8*3), (WIDTH//2.5, HEIGHT//8), "Return to Title Screen", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Settings", trigger_effect=lambda: back_to_main_menu())
    swap_button = Button((WIDTH//2, HEIGHT//1.5), (WIDTH//4, HEIGHT//8), "Swap Pieces", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Sword UI", trigger_effect=lambda: sword_ui_swap())

def back_to_main_menu():
    state_switcher(0)
    reload_buttons()

def open_chest():
    for sprite in range(3):
        added_item = choice(item_pool)
        added_item.rect.center = (WIDTH//4 * (sprite+1), HEIGHT//1.5)
        chest_ui_group.add(added_item)
    state_switcher(7)

# ---------------- #
# --- MAINLOOP --- #
# ---------------- #

while running:
    if GameState.current == "Title Screen":
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    pass
                play_button.check_button_click(event, GameState.current)
                title_settings_button.check_button_click(event, GameState.current)
                exit_button.check_button_click(event, GameState.current)
        
            screen.fill((0, 0, 0))
    
            title = title_font.render("SHACKLES", True, GREY(255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            platforms.clear()
            plat_group.empty()
    
            play_button.draw(screen, GameState.current)
            play_button.update()
            title_settings_button.draw(screen, GameState.current)
            title_settings_button.update()
            exit_button.draw(screen, GameState.current)
            exit_button.update()
    
            clock.tick(30)
            pygame.display.flip()
        except pygame.error:
            pass

    if GameState.current == "Saves":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pass
            save_button_1.check_button_click(event, GameState.current)
            save_button_2.check_button_click(event, GameState.current)
            save_button_3.check_button_click(event, GameState.current)
        screen.fill((0, 0, 0))
        for button in save_buttons:
            button.draw(screen, GameState.current)
            button.update()

        clock.tick(30)
        pygame.display.flip()

    if GameState.current == "Save Creator":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        difficulty_button.check_button_click(event, GameState.current)
        create_save_button.check_button_click(event, GameState.current)

        screen.fill((0, 0, 0))
        save_creator_text = subtitle_font.render("CREATE NEW SAVE", True, GREY(255))
        screen.blit(save_creator_text, (WIDTH//2 - save_creator_text.get_width()//2, HEIGHT//64*3))
        difficulty_button.draw(screen, GameState.current)
        create_save_button.draw(screen, GameState.current)

        clock.tick(30)
        pygame.display.flip()

    if GameState.current == "Pause":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pass
            resume_button.check_button_click(event, GameState.current)
            quit_button.check_button_click(event, GameState.current)
            settings_button.check_button_click(event, GameState.current)
    
        screen.fill(GREY(15))

        resume_button.draw(screen, GameState.current)
        resume_button.update()
        quit_button.draw(screen, GameState.current)
        quit_button.update()
        settings_button.draw(screen, GameState.current)
        settings_button.update()

        pause_text = title_font.render("PAUSED", True, GREY(255))
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//64*3))

        clock.tick(30)
        pygame.display.flip()
    
    if GameState.current == "Game Over":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pass
        main_menu_button.check_button_click(event, GameState.current)
        
        screen.fill((0, 0, 0))

        game_over_text = title_font.render("GAME OVER", True, values.RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - game_over_text.get_height()//2))
        main_menu_button.draw(screen, GameState.current)
        main_menu_button.update()

        clock.tick(30)
        pygame.display.flip()
    
    if GameState.current == "Settings":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            back_to_pause.check_button_click(event, "Settings")
            back_to_title.check_button_click(event, "Settings")
        
        screen.fill((0, 0, 0))

        settings_text = title_font.render("SETTINGS", True, GREY(255))
        screen.blit(settings_text, (WIDTH//2 - settings_text.get_width()//2, HEIGHT//64*3))

        back_to_pause.draw(screen, "Settings")
        back_to_pause.update()
        back_to_title.draw(screen, "Settings")
        back_to_title.update()

        clock.tick(30)
        pygame.display.flip()

    if GameState.current == "Chest UI":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pass
                    
        screen.fill((0, 0, 0))

        chest_ui_text = title_font.render("Select One:", True, GREY(255))
        screen.blit(chest_ui_text, (WIDTH//2 - chest_ui_text.get_width()//2, HEIGHT//64*3))

        chest_ui_group.draw(screen)
        chest_ui_group.update()

        if classes.item_selected:
            if isinstance(classes.item_selected, SwordPiece):
                piece_selection_circle.center = (WIDTH//3, HEIGHT//2)
                state_switcher(8)
            else:
                state_switcher(2)
                classes.item_selected = None
                chest_ui_group.empty()

        clock.tick(30)
        pygame.display.flip()
    
    if GameState.current == "Sword UI":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    piece_selection_circle.rect.x = WIDTH//3
                    state_switcher(2)
                    classes.item_selected = None
                    sword_ui_group.empty()
                    sword_ui_list.clear()
            swap_button.check_button_click(event, GameState.current)
                    
        screen.fill((0, 0, 0))

        sword_ui_text = common_simple_font.render("Press ESC to exit", True, GREY(255))
        screen.blit(sword_ui_text, (WIDTH//2 - sword_ui_text.get_width()//2, HEIGHT//64*3))

        swap_button.draw(screen, GameState.current)

        if classes.item_selected is not None and isinstance(classes.item_selected, SwordPiece):
            sword_ui_group.empty()
            if classes.item_selected.piece == "Handle":
                sword_ui_group.add(sword.pieces[0], classes.item_selected)
                sword_ui_list = [sword.pieces[0], classes.item_selected]
            elif classes.item_selected.piece == "Blade":
                sword_ui_group.add(sword.pieces[1], classes.item_selected)
                sword_ui_list = [sword.pieces[1], classes.item_selected]
            elif classes.item_selected.piece == "Foreblade":
                sword_ui_group.add(sword.pieces[2], classes.item_selected)
                sword_ui_list = [sword.pieces[2], classes.item_selected]
            elif classes.item_selected.piece == "Sheath":
                sword_ui_group.add(sword.pieces[3], classes.item_selected)
                sword_ui_list = [sword.pieces[3], classes.item_selected]
            
            sword_ui_list[0].rect.center = (WIDTH//3, HEIGHT//2)
            sword_ui_list[1].rect.center = (WIDTH//3*2, HEIGHT//2)

        sword_ui_group.update()
        sword_ui_group.draw(screen)

        piece_selection_circle.update()
        screen.blit(piece_selection_circle.image, piece_selection_circle.rect)

        swap_button.draw(screen, GameState.current)
        swap_button.update()

        clock.tick(30)
        pygame.display.flip()

    if GameState.current == "Game":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    # pass
                if event.key == key_debug:
                    debug = not debug
                if event.key == key_pause:
                    state_switcher(3)
            if event.type == pygame.JOYBUTTONDOWN:
                if joystick.get_button(2):
                    debug = not debug

        item_rolled = False
        screen.fill(GREY(0))
        timer = pygame.time.get_ticks()

        pleasant_sky.rect.topleft = (0, 0)
        screen.blit(pleasant_sky.image, pleasant_sky.rect)
    
        camera_x = player.rect.centerx - (WIDTH // 2)
        camera_y = player.rect.centery - (HEIGHT // 2)

        if player.real_y > values.floor_level:
            player.real_x = values.origin_point[0]
            player.real_y = values.origin_point[1]
            player.lives -= 1
            player.health = player.max_health

        # ----------------- #
        # --- RENDERING --- #
        # ----------------- #

        # player and sword
        screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))
        player.update()
        screen.blit(sword.image, (sword.rect.x - camera_x, sword.rect.y - camera_y))
        sword.update()

        # enemies
        for sprite in enemy_render_group:
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y))
            sprite.update()
        
        # platforms
        for lists in platforms:
            for plat in lists:
                if (camera_x - plat.rect.width <= plat.rect.x <= camera_x + WIDTH and
                        camera_y - plat.rect.height <= plat.rect.y <= camera_y + HEIGHT):
                    screen.blit(plat.image, (plat.rect.x - camera_x, plat.rect.y - camera_y))
                plat.update()
                if (
                    not plat.enemy_spawned
                    and abs(plat.rect.centerx - player.rect.centerx) < WIDTH + 256
                    and abs(plat.rect.centery - player.rect.centery) < HEIGHT + 256
                    and att_spawn_enemy((plat.rect.x, plat.rect.y - 128))
                ):
                    plat.enemy_spawned = True
                if plat.isCheckPoint and player.rect.x >= plat.rect.x - 128 and player.rect.x <= plat.rect.x + 128 and player.rect.y >= plat.rect.y - 128 and player.rect.y <= plat.rect.y + 64:
                    data = manage_json(f"Saves/save{game_save}.json", '', 'r')
                    if data['checkpoint'] != plat.isCheckPoint:
                        data['checkpoint'] = plat.isCheckPoint
                        manage_json(f"Saves/save{game_save}.json", data)
                if plat.isChest and player.rect.x >= plat.rect.x - 128 and player.rect.x <= plat.rect.x + 128 and player.rect.y >= plat.rect.y - 128 and player.rect.y <= plat.rect.y + 64:
                    open_chest_text = simple_font.render("Press [E] to open Chest", True, GREY(255))
                    screen.blit(open_chest_text, (WIDTH//2 - open_chest_text.get_width()//2, 8))
                    if pygame.key.get_pressed()[key_interact]:
                        plat.image = load_image("Assets/Images/Items and Blocks/Chest1.png", size=(64, 64))
                        plat.isChest = False
                        open_chest()
                if plat.bouncer > 0 and player.rect.x >= plat.rect.x - 40 and player.rect.x <= plat.rect.x + 40 and player.rect.y >= plat.rect.y - 64 and player.rect.y <= plat.rect.y + 64:
                    player.jumping = True
                    player.real_y += plat.bouncer * 16
                if plat.isExit and player.rect.colliderect(plat.rect):
                    camera_x = 0
                    camera_y = 0
                    create_level(1)
                    player.real_x = values.origin_point[0]
                    player.real_y = values.origin_point[1]
                if plat.text and player.rect.x >= plat.rect.x - 128 and player.rect.x <= plat.rect.x + 128 and player.rect.y >= plat.rect.y - 128 and player.rect.y <= plat.rect.y + 128:
                    bubble_text = simple_font.render(f"Text: {plat.text}", True, GREY(0))
                    screen.blit(bubble_text, (WIDTH//2 - bubble_text.get_width()//2, 8))

        fg = None
        for w in range(WIDTH//512):
            fg = Foreground(grassy_sprite, (w * 512, HEIGHT - 384))
            screen.blit(fg.image, fg.rect)

        # ui
        for sprite in ui_group:
            screen.blit(sprite.image, sprite.rect)
            sprite.update()
        healthtext = simple_font.render(f"Health: {player.health}", True, GREY(0))
        screen.blit(healthtext, (0, 3))

        # debug
        if debug:
            screen.blit(simple_font.render(f"Damage: {sword.damage}", True, GREY(0)), (0, 32))
            screen.blit(simple_font.render(f"Cooldown: {floor(min(sword.atk_delay, pygame.time.get_ticks() - sword.atk_time))} / {floor(sword.atk_delay)}ms", True, GREY(0)), (0, 64))
            screen.blit(simple_font.render(f"FPS: {floor(clock.get_fps()*10)/10}", True, GREY(0)), (0, 96))

        pygame.display.flip()
        clock.tick(90)

pygame.quit()