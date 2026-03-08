import pygame, random, math
from commands import *
from constants import *
pygame.init()

screen = pygame.display.set_mode((0,0))
audio = manage_json("Config/config.json", None, mode="r")['audio']
platforms = []

class DecoyController:
    def rumble(self, gdgeoo, hfjopse, hhitgh):
        pass
    def get_button(self, number):
        return False
    def get_axis(self, degrees):
        return 0

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    print(f"Controller {joystick.get_name()} connected!")
else:
    joystick = DecoyController()

class VisionBasedDetectionBox(pygame.sprite.Sprite):
    def __init__(self, mount, size):
        super().__init__()
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect()
        
        self.mount = mount
    
    def update(self):
        if self.mount.direction == 1:
            self.rect.midleft = self.mount.rect.midright
        elif self.mount.direction == -1:
            self.rect.midright = self.mount.rect.midleft
        self.image.fill(YELLOW)
        self.image.set_alpha(DETECTION_BOX_OPACITY)
        
        if self.rect.colliderect(player):
            self.mount.player_in_range = True
        else:
            self.mount.player_in_range = False

class DetectionBox(pygame.sprite.Sprite):
    def __init__(self, mount, reach):
        super().__init__()
        self.image = pygame.Surface((reach, reach))
        self.rect = self.image.get_rect()
        
        self.mount = mount
    
    def update(self):
        self.rect.center = self.mount.rect.center
        self.image.fill(BLUE)
        self.image.set_alpha(DETECTION_BOX_OPACITY)
        
        if self.rect.colliderect(player):
            self.mount.player_is_found = True
        else:
            self.mount.player_is_found = False

# Base Model For Enemies
class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, pos, image, faction, weapon, health, movement_speed):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (96, 96))
        self.rect = self.image.get_rect(center=pos)
        
        self.name = name
        self.faction = faction  # UNUSED FEATURE
        self.weapon = weapon
        self.health = health
        self.movement_speed = movement_speed
        self.direction = 1
        self.attacking = False
        self.player_in_range = False
        self.player_is_found = False
        self.direction_time = 0
        self.is_hit_by = []
        self.old_direction = 1
        
        self.real_x = self.rect.x
        self.real_y = self.rect.y
        
    def update(self):
        # pathfinding
        if not self.player_is_found and not self.player_in_range:
            if self.direction_time == 0:
                self.direction *= -1
                self.direction_time = random.randint(15, 120)
            else:
                self.real_x += self.direction * self.movement_speed
                self.direction_time -= 1
        elif self.player_is_found and not self.player_in_range:
            if self.real_x + 20 > player.rect.x:
                self.real_x -= self.movement_speed
            elif self.real_x - 20 < player.rect.x:
                self.real_x += self.movement_speed
        elif self.rect.colliderect(player.rect):
            if player.rect.x > self.real_x:
                self.direction = 1
            else:
                self.direction = -1
                
        if self.real_y + self.rect.height < floor_level:
            self.real_y += 5
        
        touching = self.rect.colliderect(sword.rect)
        
        if touching and sword.swinging:
            if sword not in self.is_hit_by:
                # First time touching this sword
                self.health -= sword.damage
                if self.health <= 0:
                    self.kill()
                    self.weapon.kill()
                self.is_hit_by.append(sword)
        else:
            # Not touching anymore → reset
            if sword in self.is_hit_by:
                self.is_hit_by.remove(sword)
        
        if self.direction == -1 and self.old_direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.direction == 1 and self.old_direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.old_direction = self.direction
        
        self.rect.x = self.real_x - camera_x
        self.rect.y = self.real_y - camera_y

class Swordsman(pygame.sprite.Sprite):
    def __init__(self, pos, is_boss):
        super().__init__()
        self.image = pygame.image.load("Assets/Images/Entity/Enemies/Swordsman.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (96, 96))
        self.rect = self.image.get_rect(center=pos)
        
        self.name = "Swordsman"
        self.faction = 'enemy'
        self.weapon = None
        self.health = 8
        self.movement_speed = 2.5
        self.direction = 1
        self.attacking = False
        self.player_in_range = False
        self.player_is_found = False
        self.direction_time = 0
        self.is_hit_by = []
        self.old_direction = 1
        
        self.real_x = self.rect.x
        self.real_y = self.rect.y
        
    def update(self):
        # pathfinding
        if not self.player_is_found and not self.player_in_range:
            if self.direction_time == 0:
                self.direction *= -1
                self.direction_time = random.randint(15, 120)
            else:
                self.real_x += self.direction * self.movement_speed
                self.direction_time -= 1
        elif self.player_is_found and not self.player_in_range:
            if self.real_x + 20 > player.rect.x:
                self.real_x -= self.movement_speed
            elif self.real_x - 20 < player.rect.x:
                self.real_x += self.movement_speed
        elif self.rect.colliderect(player.rect):
            if player.rect.x > self.real_x:
                self.direction = 1
            else:
                self.direction = -1
                
        if self.real_y + self.rect.height < floor_level:
            self.real_y += 5
        
        touching = self.rect.colliderect(sword.rect)
        
        if touching and sword.swinging:
            if sword not in self.is_hit_by:
                # First time touching this sword
                self.health -= sword.damage
                if self.health <= 0:
                    self.kill()
                    self.weapon.kill()
                self.is_hit_by.append(sword)
        else:
            # Not touching anymore → reset
            if sword in self.is_hit_by:
                self.is_hit_by.remove(sword)
        
        if self.direction == -1 and self.old_direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.direction == 1 and self.old_direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.old_direction = self.direction
        
        self.rect.x = self.real_x - camera_x
        self.rect.y = self.real_y - camera_y

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("Assets/Images/Entity/Players/Player.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.can_jump = True
        self.image_set = [
            "Assets/Images/Entity/Players/Player.png",
            "Assets/Images/Entity/Players/Player1.png",
            "Assets/Images/Entity/Players/Player2.png",
        ]
        self.animation_key = 0
        self.direction = 1
        self.jump_time = 0
        self.jump_delay = 200
        self.jump_height = 40
        self.current_jump_height = 0
        self.jumping = False
        self.jump_slow = 0
        self.jump_speed = 8
        self.health = 20
        self.lives = 3
        self.is_alive = True
        self.is_hit_by = []
        self.real_x = self.rect.x
        self.real_y = self.rect.y

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or joystick.get_axis(0) < -0.2:
            self.real_x -= 4
            self.direction = -1
        if keys[pygame.K_d] or joystick.get_axis(0) > 0.2:
            self.real_x += 4
            self.direction = 1
        if (keys[pygame.K_SPACE] or joystick.get_button(1)) and self.can_jump and not self.jumping:
            self.jumping = True
            self.can_jump = False
            self.jump_time = pygame.time.get_ticks()
            
        if self.jumping:
            if self.jump_height > self.current_jump_height:
                self.real_y -= self.jump_speed - self.jump_slow
                self.current_jump_height += 2
                self.jump_slow += 0.1
            else:
                self.jumping = False
                self.current_jump_height = 0
                self.jump_slow = 0

        if keys[pygame.K_a] or keys[pygame.K_d] or abs(joystick.get_axis(0)) > 0.2:
            self.animation_key += 0.05
            if self.animation_key >= 3: 
                self.animation_key = 0

        frame = pygame.image.load(self.image_set[int(self.animation_key)]).convert_alpha()
        if self.direction == -1:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame
        
        if pygame.time.get_ticks() - self.jump_time > self.jump_delay and not self.jumping:
            if any(self.rect.colliderect(platform.rect) for lists in platforms for platform in lists):
                self.real_y += 5
            else:
                self.can_jump = True  # Reset jump when on the ground
        
        touching = False
        for x in enemy_render_group:
            if isinstance(x, Sword) and type(x.player) != Player:
                if x.swinging:
                    touching = self.rect.colliderect(x.rect)

                if touching:
                    if x not in self.is_hit_by:
                            # First time touching this sword
                        self.health -= x.damage
                        joystick.rumble(5, 10, 1)
                        if self.health <= 0:
                            running = False
                        self.is_hit_by.append(x)
                else:
                    # Not touching anymore → reset
                    if x in self.is_hit_by:
                        self.is_hit_by.remove(x)
                        
        self.rect.x = self.real_x - camera_x
        self.rect.y = self.real_y - camera_y

class SwordPiece(pygame.sprite.Sprite):
    def __init__(self, sprite, piece, category, swn_spd_mod, max_swn_mod, reach_mod, dmg_mod):
        super().__init__()
        self.image = pygame.image.load(sprite).convert_alpha()
        self.rect = self.image.get_rect()
        
        self.piece = piece
        self.category = category
        self.swn_spd_mod = swn_spd_mod
        self.max_swn_mod = max_swn_mod
        self.reach_mod = reach_mod
        self.dmg_mod = dmg_mod
        
    def click_check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                pass

" This class is currently unused "
class Sheith(pygame.sprite.Sprite):
    def __init__(self, sprite, category, special_effect1, special_effect2):
        super().__init__()
        self.image = pygame.image.load(sprite).convert_alpha()
        self.rect = self.image.get_rect()
        
        self.category = category
        self.special_effect1 = special_effect1
        self.special_effect2 = special_effect2
        
    def click_check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                pass

class Sword(pygame.sprite.Sprite):
    def __init__(self, player, pieces):
        super().__init__()
        self.og_image = pygame.image.load("Assets/Images/Sword/SwordStill.png").convert_alpha()
        self.image = self.og_image
        self.rect = self.image.get_rect()

        # references
        self.player = player
        self.pieces = pieces

        # swing state
        self.swinging = False
        
        self.swing_speed = 3     # speed at which the sword swings
        self.swing_speed *= self.pieces[0].swn_spd_mod
        self.swing_speed *= self.pieces[1].swn_spd_mod
        self.swing_speed *= self.pieces[2].swn_spd_mod
        self.swing_speed *= self.pieces[3].swn_spd_mod
        self.swing_speed = math.floor(self.swing_speed*10) / 10
        
        self.max_swing = 40       # how high sword swings
        self.max_swing *= self.pieces[0].max_swn_mod
        self.max_swing *= self.pieces[1].max_swn_mod
        self.max_swing *= self.pieces[2].max_swn_mod
        self.max_swing *= self.pieces[3].max_swn_mod
        self.max_swing = math.floor(self.max_swing*10) / 10
        
        self.reach = 1.5                     # how far sword swings
        self.reach *= self.pieces[0].reach_mod
        self.reach *= self.pieces[1].reach_mod
        self.reach *= self.pieces[2].reach_mod
        self.reach *= self.pieces[3].reach_mod
        self.reach = math.floor(self.reach*10) / 10
        
        self.damage = 1                  # how much damage the sword does
        self.damage *= self.pieces[0].dmg_mod
        self.damage *= self.pieces[1].dmg_mod
        self.damage *= self.pieces[2].dmg_mod
        self.damage *= self.pieces[3].dmg_mod
        self.damage = math.floor(self.damage*10) / 10
        
        self.atk_delay = (4 - self.swing_speed) * 800
        self.atk_time = 0
        
        self.selfX = 0
        self.selfY = 0
        self.real_x = self.rect.x
        self.real_y = self.rect.y
    
    def update(self):
        keys = pygame.key.get_pressed()
        if type(self.player) == Player:
            if (keys[pygame.K_w] or joystick.get_button(0)) and not self.swinging and pygame.time.get_ticks() > self.atk_time + self.atk_delay:
                self.selfY += self.max_swing
                self.selfX -= math.floor(math.sqrt(self.max_swing))
                self.swinging = True
                if audio:
                    random.choice(sword_slashes).play()
        
            if self.swinging:
                # keep moving until we reach the limit
                if 0 - self.selfY < self.max_swing//2:
                    self.selfY -= self.swing_speed   # slowly bring sword back down
                    if self.selfY < 0:
                        self.selfX += self.reach
                    else:
                        self.selfX -= self.reach
                else:
                    # reset when finished
                    self.selfY = 0
                    self.selfX = 0
                    self.swinging = False
                    self.atk_time = pygame.time.get_ticks()
            
            # base orientation depending on player direction
            base_angle = 0
            if self.player.direction == 1:      # east
                base_angle = 315
            elif self.player.direction == -1:   # west
                base_angle = 135

            # rotate sword relative to base orientation
            self.image = pygame.transform.rotate(self.og_image, base_angle)
            self.rect = self.image.get_rect(center=self.rect.center)

            # position relative to player
            self.real_x = self.player.real_x + (self.player.direction * 20 * abs(self.player.direction*2 + 1)) - 20 - (self.selfX * self.player.direction)
            self.real_y = self.player.real_y + 20 - self.selfY
                    
        else:
            if self.player.player_in_range and not self.swinging and pygame.time.get_ticks() > self.atk_time + self.atk_delay:
                self.selfY += self.max_swing
                self.selfX -= math.floor(math.sqrt(self.max_swing))
                self.swinging = True
                if audio:
                    random.choice(sword_slashes).play()
        
            if self.swinging:
                # keep moving until we reach the limit
                if 0 - self.selfY < self.max_swing//2:
                    self.selfY -= self.swing_speed   # slowly bring sword back down
                    if self.selfY < 0:
                        self.selfX += self.reach
                    else:
                        self.selfX -= self.reach
                else:
                    # reset when finished
                    self.selfY = 0
                    self.selfX = 0
                    self.swinging = False
                    self.atk_time = pygame.time.get_ticks()
            
            # base orientation depending on player direction
            base_angle = 0
            if self.player.direction == 1:      # east
                base_angle = 315
            elif self.player.direction == -1:   # west
                base_angle = 135

            # rotate sword relative to base orientation
            self.image = pygame.transform.rotate(self.og_image, base_angle)
            self.rect = self.image.get_rect(center=self.rect.center)

            # position relative to player
            if bool(self.player.direction + 1):
                self.rect.center = self.player.rect.midright
            else:
                self.rect.center = self.player.rect.midleft
                
            self.real_x = self.player.real_x + (self.player.direction * 20 * abs(self.player.direction*2 + 1)) - 20 - (self.selfX * self.player.direction)
            self.real_y = self.player.real_y + 20 - self.selfY

        self.rect.x = self.real_x - camera_x
        self.rect.y = self.real_y - camera_y

class Button(pygame.sprite.Sprite):
    def __init__(self, pos, size, text, font, color, hover_color, game_state_occurrence, trigger_effect=None, outline_color=GREY(255), outline_thickness=3):
        super().__init__()
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(center=pos)
        self.text = text
        self.font = font
        self.trigger_effect = trigger_effect
        self.color = color
        self.hover_color = hover_color
        self.game_state_occurrence = game_state_occurrence
        self.outline_color = outline_color
        self.outline_thickness = outline_thickness

    def draw(self, screen, current_state):
        # Only draw if we're in the right game state
        if current_state == self.game_state_occurrence:
            mouse_pos = pygame.mouse.get_pos()

            # Fill color changes on hover
            fill_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
            pygame.draw.rect(screen, fill_color, self.rect)

            # Draw outline (border)
            pygame.draw.rect(screen, self.outline_color, self.rect, self.outline_thickness)

            # Render text
            text_surface = self.font.render(self.text, True, GREY(255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def check_button_click(self, event, current_state):
        if current_state == self.game_state_occurrence:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos) and self.trigger_effect:
                    self.trigger_effect()

class Heart(pygame.sprite.Sprite):
    def __init__(self, heart_pos):
        super().__init__()
        self.image = pygame.image.load("Assets/UI & GUI/HeartFull.png").convert_alpha()
        pygame.transform.scale(self.image, (WIDTH//16, WIDTH//16))
        self.rect = self.image.get_rect()
        self.rect.x = 64 * (WIDTH // 64 + heart_pos - 4)
        self.rect.y = WIDTH//96

old_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Old.png", "Handle", "Old", 1, 1, 1, 1)
old_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Old.png", "Blade", "Old", 1, 1, 1, 1)
old_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Old.png", "Foreblade", "Old", 1, 1, 1, 1)
old_sheith = SwordPiece("Assets/Images/Sword/Sheith/Sheith - Old.png", "Sheith", "Old", 1, 1, 1, 1)
old_set = [old_handle, old_blade, old_foreblade, old_sheith]

lancing_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Lancing.png", "Handle", "Lancing", 0.7, 0.5, 3, 0.9)
lancing_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Fencing.png", "Blade", "Lancing", 0.7, 0.5, 3, 1.1)
lancing_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Lancing.png", "Foreblade", "Lancing", 0.8, 1.2, 1.4, 1.3)
lancing_sheith = SwordPiece("Assets/Images/Sword/Sheith/Sheith - Lancing.png", "Sheith", "Lancing", 1, 1, 1, 1)
lancing_set = [lancing_blade, lancing_foreblade, lancing_handle, lancing_sheith]

player = Player((WIDTH / 2, HEIGHT / 2))
sword = Sword(player, lancing_set)
heart1 = Heart(1)
heart2 = Heart(2)
heart3 = Heart(3)