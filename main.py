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

def load_save_file(save):
    global game_save
    game_save = save['save']
    state_switcher(2)
    create_level(save['level'])
    plat_to_group()

def save_and_quit():
    config = {
        'debug': debug,
        'audio': audio
    }
    manage_json("Config/config.json", config)
    state_switcher(0)

def att_spawn_enemy(pos):
    if random.uniform(0, 1000) < 0.01:
        new_foe = Swordsman(pos, False)
        new_foe_sword = Sword(new_foe, old_set)
        new_foe.weapon = new_foe_sword
        enemy_render_group.add(new_foe, new_foe_sword)

# --------------- #
# --- BUTTONS --- #
# --------------- #

# Title Screen
play_button = Button((WIDTH//2, HEIGHT//2), (WIDTH//4, HEIGHT//8), "PLAY GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: state_switcher(1))
exit_button = Button((WIDTH//2, HEIGHT//4*3), (WIDTH//4, HEIGHT//8), "EXIT GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=lambda: pygame.quit())

# Save Selection
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

# Pause Menu
resume_button = Button((WIDTH//2, HEIGHT//8*3), (WIDTH//4, HEIGHT//8), "Resume Game", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: state_switcher(2))
quit_button = Button((WIDTH//2, HEIGHT//8*7), (WIDTH//4, HEIGHT//8), "Save and Quit", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Pause", trigger_effect=lambda: save_and_quit())

# Game Over
main_menu_button = Button((WIDTH//2, HEIGHT//4*3), (WIDTH//2, HEIGHT//8), "Go Back to Main Menu", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Game Over", trigger_effect=lambda: state_switcher(0))

# ---------------- #
# --- MAINLOOP --- #
# ---------------- #

while running:
    if GameState.current == "Title Screen":
        try:
            for event in pygame.event.get():
                if event.type ==pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
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
                if event.key == pygame.K_ESCAPE:
                    running = False
            save_button_1.check_button_click(event, GameState.current)
            save_button_2.check_button_click(event, GameState.current)
            save_button_3.check_button_click(event, GameState.current)
        screen.fill((0, 0, 0))
        for button in save_buttons:
            button.draw(screen, GameState.current)
            button.update()

        clock.tick(30)
        pygame.display.flip()

    if GameState.current == "Pause":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            resume_button.check_button_click(event, GameState.current)
            quit_button.check_button_click(event, GameState.current)
    
        screen.fill(GREY(15))

        resume_button.draw(screen, GameState.current)
        resume_button.update()
        quit_button.draw(screen, GameState.current)
        quit_button.update()

        pause_text = title_font.render("PAUSED", True, GREY(255))
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//64*3))

        clock.tick(30)
        pygame.display.flip()
    
    if GameState.current == "Game Over":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill((0, 0, 0))

        game_over_text = title_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - game_over_text.get_height()//2))
        main_menu_button.draw(screen, GameState.current)
        main_menu_button.update()

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
        
        # ui
        for sprite in ui_group:
            screen.blit(sprite.image, sprite.rect)
            sprite.update()
        healthtext = simple_font.render(f"Health: {player.health}", True, GREY(255))
        screen.blit(healthtext, (0, 3))

        pygame.display.flip()
        clock.tick(60)

pygame.quit()