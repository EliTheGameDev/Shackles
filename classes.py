import pygame, random, math
from commands import *
from values import *
from platforms import *
from groups import *
pygame.init()

screen = pygame.display.set_mode((0,0))
audio = manage_json("Config/config.json", None, mode="r")['audio']

class DecoyController:
    def rumble(self, gdgeoo, hfjopse, hhitgh):
        pass
    def get_button(self, number):
        return False
    def get_axis(self, degrees):
        return 0

joystick = DecoyController()

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
        self.detection_range = 192
        self.vision_range = (60, 50)
        self.player_in_range = False
        self.player_is_found = False
        self.direction_time = 0
        self.is_hit_by = []
        self.old_direction = 1
        
        self.real_x = self.rect.x
        self.real_y = self.rect.y
        
    def update(self):
        # base pathfinding
        self.player_is_found = player.real_x > self.real_x - self.detection_range and player.real_x < self.real_x + self.detection_range
        self.player_in_range = player.real_x > self.real_x - self.vision_range[0] and player.real_x < self.real_x + self.vision_range[0] and player.real_y > self.real_y - self.vision_range[1] and player.real_y < self.real_y + self.vision_range[1]
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
        self.direction_time = 0
        self.is_hit_by = []
        self.old_direction = 1
        self.detection_range = 192
        self.vision_range = (60, 50)
        self.player_in_range = False
        self.player_is_found = False
        self.hit_platforms = 0
        self.can_jump = True
        self.jump_time = 0
        self.jump_delay = 200
        self.jump_height = 40
        self.current_jump_height = 0
        self.jumping = False
        self.jump_slow = 0
        self.jump_speed = 7
        
        self.real_x = self.rect.x
        self.real_y = self.rect.y
        
    def update(self):
        # pathfinding
        self.player_is_found = player.real_x > self.real_x - self.detection_range and player.real_x < self.real_x + self.detection_range
        self.player_in_range = player.real_x > self.real_x - self.vision_range[0] and player.real_x < self.real_x + self.vision_range[0] and player.real_y > self.real_y - self.vision_range[1] and player.real_y < self.real_y + self.vision_range[1]
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

        if random.random() > 0.99 and self.can_jump and not self.jumping:
            self.jumping = True
            self.can_jump = False
            self.jump_time = pygame.time.get_ticks()
        
        self.rect.x = self.real_x - camera_x
        self.rect.y = self.real_y - camera_y

        if self.jumping:
            if self.jump_height > self.current_jump_height:
                self.real_y -= self.jump_speed - self.jump_slow
                self.current_jump_height += 2
                self.jump_slow += 0.1
            else:
                self.jumping = False
                self.current_jump_height = 0
                self.jump_slow = 0
                
        self.hit_platforms = pygame.sprite.spritecollide(self, plat_group, False)

        if self.hit_platforms:
            platform = self.hit_platforms[0]
            
            if not self.jumping and self.rect.bottom <= platform.rect.top + 6:
                self.can_jump = True
                self.real_y = platform.rect.top - self.rect.height
                self.rect.y = self.real_y
            else:
                self.real_y += 5
                self.can_jump = False
        
        elif not self.jumping:
            self.real_y += 5
            self.can_jump = False

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
        self.jump_height = 50
        self.current_jump_height = 0
        self.jumping = False
        self.jump_slow = 0
        self.jump_speed = 8
        self.health = self.max_health = 20
        self.lives = 3
        self.is_alive = True
        self.is_hit_by = []
        self.real_x = self.rect.x
        self.real_y = self.rect.y
        self.hit_platforms = 0
        self.climb_max = 32
        self.move_speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or joystick.get_axis(0) < -0.2:
            self.real_x -= self.move_speed
            self.direction = -1
            self.rect.x = self.real_x
            if pygame.sprite.spritecollide(self, plat_group, False):
                self.real_x += self.move_speed
        
        if keys[pygame.K_d] or joystick.get_axis(0) > 0.2:
            self.real_x += self.move_speed
            self.direction = 1
            self.rect.x = self.real_x
            if pygame.sprite.spritecollide(self, plat_group, False):
                self.real_x -= self.move_speed
        
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
        
        self.rect.x, self.rect.y = self.real_x, self.real_y

        self.hit_platforms = pygame.sprite.spritecollide(self, plat_group, False)

        if self.hit_platforms:
            plat_index = 0
            while not self.hit_platforms[plat_index].isSolid:
                plat_index += 1
            platform = self.hit_platforms[plat_index]
            
            if not self.jumping and self.rect.bottom <= platform.rect.top + self.climb_max:
                self.can_jump = True
                self.real_y = platform.rect.top - self.rect.height
                self.rect.y = self.real_y
            else:
                self.real_y += 5
                self.can_jump = False
        
        elif not self.jumping:
            self.real_y += 5
            self.can_jump = False
        
        touching = False
        for x in enemy_render_group:
            if isinstance(x, Sword) and type(x.player) != Player:
                if x.swinging:
                    touching = self.rect.colliderect(x.rect)

                if touching:
                    if x not in self.is_hit_by:
                        self.health -= x.damage
                        joystick.rumble(5, 10, 1)
                        if self.health <= 0:
                            self.lives -= 1
                            self.health = self.max_health
                        self.is_hit_by.append(x)
                else:
                    if x in self.is_hit_by:
                        self.is_hit_by.remove(x)
            if self.lives <= 0:
                lose_game(game_save)

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
class Sheath(pygame.sprite.Sprite):
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
        
        self.atk_delay = ((4 - self.swing_speed) + (self.damage/2) + (self.reach * self.max_swing // 60)) * 450
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
        self.rect.y = (self.real_y - camera_y)//8 * 8

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

class ScrollButton(pygame.sprite.Sprite):
    def __init__(self, pos, size, font, color, hover_color, game_state_occurrence, text_options, trigger_effect=None, outline_color=GREY(255), outline_thickness=3):
        super().__init__()
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(center=pos)
        self.text = text_options[0]
        self.font = font
        self.trigger_effect = trigger_effect
        self.color = color
        self.hover_color = hover_color
        self.game_state_occurrence = game_state_occurrence
        self.outline_color = outline_color
        self.outline_thickness = outline_thickness
        self.text_options = text_options
        self.index = 0
    
    def scroll(self):
        self.index += 1
        if self.index >= len(self.text_options):
            self.index = 0
        self.text = self.text_options[self.index]
    
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
        self.heart_pos = heart_pos
    def update(self):
        if player.lives >= 4 - self.heart_pos:
            if player.health < player.max_health // 2 and player.lives == 4 - self.heart_pos:
                self.image = pygame.image.load("Assets/UI & GUI/HeartHalf.png").convert_alpha()
            else:
                self.image = pygame.image.load("Assets/UI & GUI/HeartFull.png").convert_alpha()
        else:
            self.image = pygame.image.load("Assets/UI & GUI/HeartEmpty.png").convert_alpha()

class Item(pygame.sprite.Sprite):
    def __init__(self, sprite, name, description, effect, weight):
        super().__init__()
        self.spritepath = sprite
        self.image = pygame.image.load(sprite).convert_alpha()
        self.image = pygame.transform.scale(self.image, (192, 192))
        self.rect = self.image.get_rect(center=(0, 0)) # Default position, can be changed when placed in the world
        self.name = name
        self.description = description
        self.effect = effect
        self.weight = weight  # Common: 20, Uncommon: 10, Rare: 3, Legendary: 1
        self.info_box_open = False
    
    def update(self):
        mouse = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        
        info_box = InfoBox((WIDTH//2, HEIGHT//2), (WIDTH//1.5, HEIGHT//1.5), pygame.time.get_ticks() + 500)
        if self.weight == 20: noi_text_colour = (GREY(192)) # Common
        elif self.weight == 10: noi_text_colour = (GREEN) # Uncommon
        elif self.weight == 3: noi_text_colour = (RED) # Rare
        elif self.weight == 1: noi_text_colour = (YELLOW) # Legendary
        else: noi_text_colour = (BLUE) # Undefined Rarity
        noi_text = Text((WIDTH//2, HEIGHT//6), self.name, simple_font, colour=noi_text_colour)
        r_click_text = Text((WIDTH//2, HEIGHT//5), "Press ESC to Close Box", simple_font)
        item_image = DisplayObject((WIDTH//2, HEIGHT//2.5), self.spritepath, WIDTH//6)
        desc_text = Text((WIDTH//2, HEIGHT//1.75), self.description, simple_font)

        if self.rect.collidepoint(mouse[0], mouse[1]) and mouse_click[2] and not self.info_box_open:
            self.info_box_open = True
            chest_ui_group.add(info_box, noi_text, r_click_text, item_image, desc_text)
        
        if self.rect.collidepoint(mouse[0], mouse[1]) and mouse_click[0] and not self.info_box_open:
            global item_selected
            item_selected = True

        if not info_box.is_active:
            info_box.kill()
            noi_text.kill()
            item_image.kill()
            desc_text.kill()
            self.info_box_open = False

class Text(pygame.sprite.Sprite):
    def __init__(self, pos, text, font, colour=GREY(255)):
        super().__init__()
        self.font = font
        self.text = text
        self.colour = colour

        self.image = font.render(text, True, colour)
        self.rect = self.image.get_rect(center=pos)
    
    def modify_properties(self, text=None, colour=None):
        if text:
            self.text = text
        if colour:
            self.colour = text
        
        self.image = font.render(text, True, colour)
        self.rect = self.image.get_rect(center=pos)

class InfoBox(pygame.sprite.Sprite):
    def __init__(self, pos, size, wait):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(GREY(64))
        self.rect = self.image.get_rect(center=pos)
        self.is_active = True
        self.wait = wait
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_ESCAPE]:
            self.is_active = False

class DisplayObject(pygame.sprite.Sprite):
    def __init__(self, pos, sprite, scale):
        super().__init__()
        self.scale = scale

        self.image = pygame.image.load(sprite).convert_alpha()
        self.image = pygame.transform.scale(self.image, (scale, scale))
        self.rect = self.image.get_rect(center=pos)

old_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Old.png", "Handle", "Old", 1, 1, 1, 1)
old_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Old.png", "Blade", "Old", 1, 1, 1, 1)
old_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Old.png", "Foreblade", "Old", 1, 1, 1, 1)
old_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Old.png", "Sheath", "Old", 1, 1, 1, 1)
old_set = [old_handle, old_blade, old_foreblade, old_sheath]

lancing_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Lancing.png", "Handle", "Lancing", 0.7, 0.5, 3, 0.9)
lancing_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Fencing.png", "Blade", "Lancing", 0.7, 0.5, 3, 1.1)
lancing_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Lancing.png", "Foreblade", "Lancing", 0.8, 1.2, 1.4, 1.3)
lancing_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Lancing.png", "Sheath", "Lancing", 1, 1, 1, 1)
lancing_set = [lancing_blade, lancing_foreblade, lancing_handle, lancing_sheath]

brutish_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Brutish.png", "Handle", "Brutish", 0.8, 1.2, 0.9, 1.2)
brutish_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Brutish.png", "Blade", "Brutish", 1.3, 1.1, 0.7, 1.3)
brutish_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Brutish.png", "Foreblade", "Brutish", 1.05, 1, 1.05, 1.15)
brutish_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Brutish.png", "Sheath", "Brutish", 1, 1, 1, 1)
brutish_set = [brutish_blade, brutish_foreblade, brutish_handle, brutish_sheath]

classic_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Classic.png", "Handle", "Classic", 1.15, 1, 1, 1.05)
classic_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Classic.png", "Blade", "Classic", 1.2, 0.9, 1.1, 1)
classic_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Classic.png", "Foreblade", "Classic", 1.1, 1.05, 1, 1.2)
classic_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Classic.png", "Sheath", "Classic", 1, 1, 1, 1)
classic_set = [classic_handle, classic_blade, classic_foreblade, classic_sheath]

origin_point = (WIDTH / 2, 1600)

# Collectibles
ancient_key = Item("Assets/Images/Items and Blocks/Collectibles/AncientKey.png", "Ancient Key", "An old enchanted key that seems to fit in a chest's lock.", "Next chest you open will only contain artifacts", 1)
legendary_key = Item("Assets/Images/Items and Blocks/Collectibles/LegendaryKey.png", "Legendary Key", "A gold-plated key with a chest as its handle. It clearly opens a chest better than you can.", "Next chest will contain 5 items instead of 3. You may also pick an aditional item from this increased pool.", 1)
boat_coupon = Item("Assets/Images/Items and Blocks/Collectibles/BoatCoupon.png", "Boat Coupon", "A handwritten coupon for a boat ride. It's clearly been in that chest for many years.", "Next boat ride is free.", 3)
market_coupon = Item("Assets/Images/Items and Blocks/Collectibles/MarketCoupon.png", "Market Coupon", "A printed coupon for the market. It has a scratch off slot that says: Do not scratch, or coupon is invalid.", "Next market purchase has a random multiplier, usually good, but not always.", 3)
coins_10 = Item("Assets/Images/Items and Blocks/Collectibles/Coins-10.png", "10 Coins", "A handful of golden coins.", "Gain 10 coins.", 20)
coins_20 = Item("Assets/Images/Items and Blocks/Collectibles/Coins-20.png", "20 Coins", "A pile of golden coins.", "Gain 20 coins.", 10)
coins_30 = Item("Assets/Images/Items and Blocks/Collectibles/Coins-30.png", "30 Coins", "A small bag of golden coins.", "Gain 30 coins.", 3)
coins_50 = Item("Assets/Images/Items and Blocks/Collectibles/Coins-50.png", "50 Coins", "A bag filled with golden coins.", "Gain 50 coins.", 1)
coins_100 = Item("Assets/Images/Items and Blocks/Collectibles/Coins-100.png", "100 Coins", "There's so many coins in this bag that it's ripping!", "Gain 100 coins.", 1)
energy_herb = Item("Assets/Images/Items and Blocks/Collectibles/EnergyHerb.png", "Energy Herb", "A seemingly unremarkable leaf-shaped herb. It's a vibrant green and looks healthy.", "Halves your cooldowns for 90 seconds.", 10)
springy_shoes = Item("Assets/Images/Items and Blocks/Collectibles/SpringyShoes.png", "Springy Shoes", "Leather shoes with springs inspired by the Springboards on them. They won't last very long.", "Doubles your jump height for 90 seconds.", 10)
sprinting_shoes = Item("Assets/Images/Items and Blocks/Collectibles/SprintingShoes.png", "Sprinting Shoes", "Simple shoes with large lightning bolts on the side. They won't last very long.", "Increases your movement speed by 50% for 90 seconds.", 20)
feather_shoes = Item("Assets/Images/Items and Blocks/Collectibles/FeatherShoes.png", "Feather Shoes", "Utility shoes with crude feathers on them. They won't last very long.", "Reduces fall speed by 25% for 90 seconds.", 20)
shoddy_shield = Item("Assets/Images/Items and Blocks/Collectibles/ShoddyShield.png", "Shoddy Shield", "A shield that looks like the top of a tree stump. It is fairly delicate, and won't block well.", "Reduces damage taken by 33% 3 times.", 20)
modest_shield = Item("Assets/Images/Items and Blocks/Collectibles/ModestShield.png", "Modest Shield", "A shield that seems like it was carved quickly. It has a distinct ringed design. It isn't the sturdiest, and won't block well.", "Reduces damage taken by 33% 5 times.", 10)
masterful_shield = Item("Assets/Images/Items and Blocks/Collectibles/MasterfulShield.png", "Masterful Shield", "A hefty metal and wood shield that seems it was a blasksmith's pride and joy for many months. Despite being durable, it won't block well.", "Reduces damage taken by 33% 8 times.", 3)
grabby_hand = Item("Assets/Images/Items and Blocks/Collectibles/GrabbyHand.png", "Grabby Hand", "A simple device that looks as if a cartoon extendo punching glove open its hand.", "Increases reach and swing by 30% for 90 seconds.", 20)
poor_meal = Item("Assets/Images/Items and Blocks/Collectibles/PoorMeal.png", "Poor Meal", "A small bowl with cold rice, chicken, and greens. You're lucky there's no mould on it.", "Heals 5 health.", 20)
decent_meal = Item("Assets/Images/Items and Blocks/Collectibles/DecentMeal.png", "Decent Meal", "A bowl of lukewarm chicken soup that reminds you of home.", "Heals 10 health and all conditions.", 10)
medicinal_meal = Item("Assets/Images/Items and Blocks/Collectibles/MedicinalMeal.png", "Medicinal Meal", "An oddly green steamy soup. It smells of mint and basil. It's like what a dietician would recommend to a vegan.", "Heals a life and all negetive conditions.", 3)
hearty_meal = Item("Assets/Images/Items and Blocks/Collectibles/HeartyMeal.png", "Hearty Meal", "An appetising spaghetti bolognese with Swedish meatballs. It looks delicious and freshly prepared.", "Fully heals your health, but heals a life instead if 25% or less health would be healed.", 3)
enchanted_meal = Item("Assets/Images/Items and Blocks/Collectibles/EnchantedMeal.png", "Enchanted Meal", "An odd supernaturally blue soup with a blue carrot. Despite seeming radioactive, it emanantes an enchanting energy.", "Fully heals you and grants an enchanted life.", 1)

items = [ancient_key, legendary_key, boat_coupon, market_coupon, coins_10, coins_20, coins_30, coins_50, coins_100, energy_herb, springy_shoes, sprinting_shoes, feather_shoes, shoddy_shield, modest_shield, masterful_shield, grabby_hand, poor_meal, decent_meal, medicinal_meal, hearty_meal, enchanted_meal]
sets = [old_set, lancing_set, brutish_set, classic_set]
item_pool = []

for s in sets:
    for piece in s:
        for i in range(10):
            item_pool.append(piece)

for item in items:
    for i in range(item.weight):
        item_pool.append(item)

# Create player, sword, and hearts
player = Player(origin_point)
sword = Sword(player, [brutish_handle, brutish_blade, lancing_foreblade, old_sheath])
heart1 = Heart(1)
heart2 = Heart(2)
heart3 = Heart(3)

# Put them in groups
player_group.add(player)
ui_group.add(heart1, heart2, heart3)