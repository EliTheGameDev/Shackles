import pygame, random, json
from commands import *
from constants import *
from classes import *
from platforms import *

pygame.init()

# --- SETUP --- #
# Game Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shackles")
clock = pygame.time.Clock()
game_state = "Title Screen"

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

# --- CREATE SPRITES --- #
group = pygame.sprite.Group()
group.add(sword, player, heart1, heart2, heart3)

foe = Swordsman((600, 400), False)
foe_sword = Sword(foe, old_set)
foe.weapon = foe_sword
radius = DetectionBox(foe, 192)
sight = VisionBasedDetectionBox(foe, (60, 50))
enemy_render_group.add(foe, foe_sword, radius, sight)

# --- PLATFORMS --- #
platforms = []

# --- MACROS --- #
def state_to_game():
    global game_state
    game_state = "Game"

# --- BUTTONS --- #
play_button = Button((WIDTH//2, HEIGHT//2), (WIDTH//4, HEIGHT//8), "PLAY GAME", pygame.font.Font("Assets/Fonts/Basic Font/NimbusRomNo9L-Reg.otf", 64), (0, 0, 0), (25, 25, 25), "Title Screen", trigger_effect=state_to_game)

# --- MAINLOOP --- #
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
    
    group.draw(screen)
    group.update()
    
    enemy_render_group.draw(screen)
    enemy_render_group.update()

    pygame.display.flip()
    clock.tick(60)

config = {
    'debug': debug,
    'audio': audio
}
manage_json("Config/config.json", config)

pygame.quit()