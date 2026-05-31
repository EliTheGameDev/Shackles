import pygame, random, json
from math import *
from commands import *
from values import *
from classes import *
from platforms import *
from groups import *

pygame.init()

# --- SETUP --- #
# Game Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shackles - Early Dev V4")
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

# --- EFFECTS --- #
class Effect:
    def __init__(self, name, target, severity):
        self.name = name
        self.target = target
        self.severity = severity

# --- MACROS --- #

def load_save_file(save_num):
    global game_save
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
        'debug': debug,
        'audio': audio
    }
    manage_json("Config/config.json", config)
    state_switcher(0)

def att_spawn_enemy(pos):
    if random.uniform(0, 1000) < 0.005:
        new_foe = Swordsman(pos, False)
        new_foe_sword = Sword(new_foe, old_set)
        new_foe.weapon = new_foe_sword
        enemy_render_group.add(new_foe, new_foe_sword)

def force_off():
    global running
    running = False

def open_save_creator(save_num):
    state_switcher(6)
    global game_save
    game_save = save_num

def create_save(save_num, difficulty):
    manage_json(f"Saves/save{save_num}.json", {"difficulty": difficulty, "level": 0, "checkpoint": 0, "has_started": 1, "save": save_num})
    load_save_file(save_num)

# --------------- #
# --- BUTTONS --- #
# --------------- #

# Title Screen
play_button = Button((WIDTH//2, HEIGHT//2), (WIDTH//4, HEIGHT//8), "PLAY GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: state_switcher(1))
exit_button = Button((WIDTH//2, HEIGHT//4*3), (WIDTH//4, HEIGHT//8), "EXIT GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: force_off())

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
difficulty_button = ScrollButton((WIDTH//2, HEIGHT//2.5), (WIDTH//4, HEIGHT//8), difficulties, pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Save Creator")
difficulty_button.trigger_effect = difficulty_button.scroll
create_save_button = Button((WIDTH//2, HEIGHT//1.66), (WIDTH//4, HEIGHT//8), "Create Save", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Save Creator", trigger_effect=lambda: create_save(game_save, difficulty_button.index))

# Pause Menu
resume_button = Button((WIDTH//2, HEIGHT//8*3), (WIDTH//4, HEIGHT//8), "Resume Game", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(2))
quit_button = Button((WIDTH//2, HEIGHT//8*7), (WIDTH//4, HEIGHT//8), "Save and Quit", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: save_and_quit())
settings_button = Button((WIDTH//2, HEIGHT//8*5), (WIDTH//4, HEIGHT//8), "Settings", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(5))

# Game Over
main_menu_button = Button((WIDTH//2, HEIGHT//4*3), (WIDTH//2, HEIGHT//8), "Go Back to Main Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Game Over", trigger_effect=lambda: back_to_main_menu())

# Settings
back_to_pause = Button((WIDTH//2, HEIGHT//8*3), (WIDTH//2.5, HEIGHT//8), "Return to Pause Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Settings", trigger_effect=lambda: state_switcher(3))

def reload_buttons():
    global play_button, exit_button, save_button_1, save_button_2, save_button_2, save_button_3, save_buttons, resume_button, quit_button, settings_button, main_menu_button, back_to_pause, difficulty_button, create_save_button
    play_button = Button((WIDTH//2, HEIGHT//2), (WIDTH//4, HEIGHT//8), "PLAY GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: state_switcher(1))
    exit_button = Button((WIDTH//2, HEIGHT//4*3), (WIDTH//4, HEIGHT//8), "EXIT GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: force_off())
    if bool(manage_json("Saves/save1.json", None, mode="r")['has_started']): save_button_1 = Button((WIDTH//2, HEIGHT//5 * 2), (WIDTH//4, HEIGHT//8), f"SAVE 1 - Lv.{manage_json('Saves/save1.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(1))
    else: save_button_1 = Button((WIDTH//2, HEIGHT//5 * 2), (WIDTH//4, HEIGHT//8), "SAVE 1", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: state_switcher(2))
    if bool(manage_json("Saves/save2.json", None, mode="r")['has_started']): save_button_2 = Button((WIDTH//2, HEIGHT//5 * 3), (WIDTH//4, HEIGHT//8), f"SAVE 2 - Lv.{manage_json('Saves/save2.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(2))
    else: save_button_2 = Button((WIDTH//2, HEIGHT//5 * 3), (WIDTH//4, HEIGHT//8), "SAVE 2", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: state_switcher(2))
    if bool(manage_json("Saves/save3.json", None, mode="r")['has_started']): save_button_3 = Button((WIDTH//2, HEIGHT//5 * 4), (WIDTH//4, HEIGHT//8), f"SAVE 3 - Lv.{manage_json('Saves/save3.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(3))
    else: save_button_3 = Button((WIDTH//2, HEIGHT//5 * 4), (WIDTH//4, HEIGHT//8), "SAVE 3", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: state_switcher(2))
    save_buttons = [save_button_1, save_button_2, save_button_3]
    resume_button = Button((WIDTH//2, HEIGHT//8*3), (WIDTH//4, HEIGHT//8), "Resume Game", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(2))
    quit_button = Button((WIDTH//2, HEIGHT//8*7), (WIDTH//4, HEIGHT//8), "Save and Quit", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: save_and_quit())
    settings_button = Button((WIDTH//2, HEIGHT//8*5), (WIDTH//4, HEIGHT//8), "Settings", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(5))
    main_menu_button = Button((WIDTH//2, HEIGHT//4*3), (WIDTH//2, HEIGHT//8), "Go Back to Main Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Game Over", trigger_effect=lambda: back_to_main_menu())
    back_to_pause = Button((WIDTH//2, HEIGHT//8*3), (WIDTH//2.5, HEIGHT//8), "Return to Pause Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Settings", trigger_effect=lambda: state_switcher(3))
    difficulty_button = ScrollButton((WIDTH//2, HEIGHT//2.5), (WIDTH//4, HEIGHT//8), difficulties, pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Save Creator")
    difficulty_button.trigger_effect = difficulty_button.scroll
    create_save_button = Button((WIDTH//2, HEIGHT//1.66), (WIDTH//4, HEIGHT//8), "Create Save", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Save Creator", trigger_effect=lambda: create_save(game_save, difficulty_button.index))


def back_to_main_menu():
    state_switcher(0)
    reload_buttons()

def open_chest():
    for sprite in range(3):
        added_item = random.choice(item_pool)
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
                exit_button.check_button_click(event, GameState.current)
        
            screen.fill((0, 0, 0))
    
            title = title_font.render("SHACKLES", True, GREY(255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
            play_button.draw(screen, GameState.current)
            play_button.update()
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

        game_over_text = title_font.render("GAME OVER", True, RED)
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
        
        screen.fill((0, 0, 0))

        settings_text = title_font.render("SETTINGS", True, GREY(255))
        screen.blit(settings_text, (WIDTH//2 - settings_text.get_width()//2, HEIGHT//64*3))
        back_to_pause.draw(screen, "Settings")
        back_to_pause.update()

        clock.tick(30)
        pygame.display.flip()

    if GameState.current == "Chest UI":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pass
                    
        if item_selected:
            state_switcher(2)
            chest_ui_group.empty()
    
        screen.fill((0, 0, 0))

        chest_ui_text = title_font.render("Select One:", True, GREY(255))
        screen.blit(chest_ui_text, (WIDTH//2 - chest_ui_text.get_width()//2, HEIGHT//64*3))

        chest_ui_group.draw(screen)
        chest_ui_group.update()

        clock.tick(30)
        pygame.display.flip()

    if GameState.current == "Game":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_TAB:
                    debug = not debug
                if event.key == pygame.K_s:
                    state_switcher(3)
            if event.type == pygame.JOYBUTTONDOWN:
                if joystick.get_button(2):
                    debug = not debug

        item_rolled = False
        screen.fill(GREY(0))
    
        camera_x = player.rect.centerx - (WIDTH // 2)
        camera_y = player.rect.centery - (HEIGHT // 2)

        if player.real_y > floor_level:
            player.real_x = origin_point[0]
            player.real_y = origin_point[1]
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
                screen.blit(plat.image, (plat.rect.x - camera_x, plat.rect.y - camera_y))
                plat.update()
                att_spawn_enemy((plat.rect.x, plat.rect.y+128))
                if plat.isCheckPoint and player.rect.x >= plat.rect.x - 128 and player.rect.x <= plat.rect.x + 128 and player.rect.y >= plat.rect.y - 128 and player.rect.y <= plat.rect.y + 64:
                    data = manage_json(f"Saves/save{game_save}.json", '', 'r')
                    data['checkpoint'] = plat.isCheckPoint
                    manage_json(f"Saves/save{game_save}.json", data)
                if plat.isChest and player.rect.x >= plat.rect.x - 128 and player.rect.x <= plat.rect.x + 128 and player.rect.y >= plat.rect.y - 128 and player.rect.y <= plat.rect.y + 64:
                    open_chest_text = simple_font.render("Press [E] to open Chest", True, GREY(255))
                    screen.blit(open_chest_text, (WIDTH//2 - open_chest_text.get_width()//2, 8))
                    if pygame.key.get_pressed()[pygame.K_e]:
                        open_chest()
                if plat.bouncer > 0 and player.rect.x >= plat.rect.x - 40 and player.rect.x <= plat.rect.x + 40 and player.rect.y >= plat.rect.y - 64 and player.rect.y <= plat.rect.y + 64:
                    player.jumping = True
                    player.real_y += plat.bouncer * 16
                if plat.isExit and player.rect.colliderect(plat.rect):
                    platforms.clear()
                    player.real_x = origin_point[0]
                    player.real_y = origin_point[1]
                    camera_x = 0
                    camera_y = 0
                    create_level(1)
        # ui
        for sprite in ui_group:
            screen.blit(sprite.image, sprite.rect)
            sprite.update()
        healthtext = simple_font.render(f"Health: {player.health}", True, GREY(255))
        screen.blit(healthtext, (0, 3))

        # debug
        if debug:
            screen.blit(simple_font.render(f"Damage: {sword.damage}", True, GREY(255)), (0, 32))
            screen.blit(simple_font.render(f"Cooldown: {floor(min(sword.atk_delay, pygame.time.get_ticks() - sword.atk_time))} / {floor(sword.atk_delay)}", True, GREY(255)), (0, 64))

        pygame.display.flip()
        clock.tick(60)

pygame.quit()