import pygame, random, json
from commands import *
from constants import *
from classes import *
from platforms import *
from groups import *

pygame.init()

# --- SETUP --- #
# Game Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shackles")
clock = pygame.time.Clock()
game_state = game_states[0]

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

# --- PLATFORMS --- #
platforms = []

# --- MACROS --- #
def state_switcher(state_index):
    global game_state
    game_state = game_states[state_index]

def create_level(level):
    global platforms
    plat_list_val = -1
    for plat_list in fetch_level_data(level):
        platforms.append([])
        plat_list_val += 1
        plat_val = -1
        for plat in plat_list:
            plat_val += 1
            if plat != 'Empty':
                platforms[plat_list_val].append(Platform((plat_list_val*32, plat_val*32), f"Assets/Images/Platforms/Ground-Based Platforms/{plat} Platform.png"))

def load_save_file(save):
    state_switcher(2)
    create_level(save['level'])

# --- BUTTONS --- #
play_button = Button((WIDTH//2, HEIGHT//2), (WIDTH//4, HEIGHT//8), "PLAY GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: state_switcher(1))

if bool(manage_json("Saves/save1.json", None, mode="r")['has_started']):
    save_button_1 = Button((WIDTH//2, HEIGHT//5 * 2), (WIDTH//4, HEIGHT//8), f"SAVE 1 - Lv.{manage_json('Saves/save1.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(manage_json("Saves/save1.json", None, mode="r")))
else:
    save_button_1 = Button((WIDTH//2, HEIGHT//5 * 2), (WIDTH//4, HEIGHT//8), "SAVE 1", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: state_switcher(2))
if bool(manage_json("Saves/save2.json", None, mode="r")['has_started']):
    save_button_2 = Button((WIDTH//2, HEIGHT//5 * 3), (WIDTH//4, HEIGHT//8), f"SAVE 2 - Lv.{manage_json('Saves/save2.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(manage_json("Saves/save2.json", None, mode="r")))
else:
    save_button_2 = Button((WIDTH//2, HEIGHT//5 * 3), (WIDTH//4, HEIGHT//8), "SAVE 2", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: state_switcher(2))
if bool(manage_json("Saves/save3.json", None, mode="r")['has_started']):
    save_button_3 = Button((WIDTH//2, HEIGHT//5 * 4), (WIDTH//4, HEIGHT//8), f"SAVE 3 - Lv.{manage_json('Saves/save3.json', None, mode='r')['level']}", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: load_save_file(manage_json("Saves/save3.json", None, mode="r")))
else:
    save_button_3 = Button((WIDTH//2, HEIGHT//5 * 4), (WIDTH//4, HEIGHT//8), "SAVE 3", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Saves", trigger_effect=lambda: state_switcher(2))
save_buttons = [save_button_1, save_button_2, save_button_3]

# ---------------- #
# --- MAINLOOP --- #
# ---------------- #

while running and game_state == "Title Screen":
    for event in pygame.event.get():
        if event.type ==pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        play_button.check_button_click(event, game_state)
    
    screen.fill((0, 0, 0))
    
    title = title_font.render("SHACKLES", True, GREY(255))
    screen.blit(title, (225, 100))
    
    play_button.draw(screen, game_state)
    
    clock.tick(30)
    pygame.display.flip()
while running and game_state == "Saves":
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        save_button_1.check_button_click(event, game_state)
        save_button_2.check_button_click(event, game_state)
        save_button_3.check_button_click(event, game_state)
    screen.fill((0, 0, 0))
    for button in save_buttons:
        button.draw(screen, game_state)
        button.update()

    clock.tick(30)
    pygame.display.flip()

while running and game_state == "Game":
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_TAB:
                debug = not debug
        if event.type == pygame.JOYBUTTONDOWN:
            if joystick.get_button(2):
                debug = not debug

    screen.fill(GREY(0))
    
    camera_x = player.real_x - WIDTH // 2
    camera_y = player.real_y - HEIGHT // 2
    
    healthtext = simple_font.render(f"Health: {player.health}", True, GREY(255))
    screen.blit(healthtext, (0, 3))
    
    if debug:
        statstext = simple_font.render("Sword Stats-", True, GREY(255))
        screen.blit(statstext, (0, 24))
        swingtext = simple_font.render(f"Swing Speed: {sword.swing_speed}", True, GREY(255))
        screen.blit(swingtext, (0, 48))
        reachtext = simple_font.render(f"Vertical Reach: {sword.max_swing}", True, GREY(255))
        screen.blit(reachtext, (0, 72))
        dmgtext = simple_font.render(f"Damage: {sword.damage}", True, GREY(255))
        screen.blit(dmgtext, (0, 96))
        sword_time = pygame.time.get_ticks() - sword.atk_time if (pygame.time.get_ticks() - sword.atk_time) < sword.atk_delay else sword.atk_delay
        cooldowntext = simple_font.render(f"Attack Cooldown Remaining: {sword_time} / {sword.atk_delay} ms", True, GREY(255))
        screen.blit(cooldowntext, (0, 120))
        DETECTION_BOX_OPACITY = 80
    else:
        DETECTION_BOX_OPACITY = 0
    
    screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))
    player.update()
    screen.blit(sword.image, (sword.rect.x - camera_x, sword.rect.y - camera_y))
    sword.update()

    for sprite in enemy_render_group:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y))
        sprite.update()
    for sprite in ui_group:
        screen.blit(sprite.image, sprite.rect)
        sprite.update()
    for lists in platforms:
        for plat in lists:
            screen.blit(plat.image, (plat.rect.x - camera_x, plat.rect.y - camera_y))
            plat.update()


    pygame.display.flip()
    clock.tick(60)

config = {
    'debug': debug,
    'audio': audio
}
manage_json("Config/config.json", config)

pygame.quit()