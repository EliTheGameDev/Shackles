import pygame, math
from random import choice, randint, random
from commands import *
from values import *
from platforms import *
from groups import *
pygame.init()

screen = pygame.display.set_mode((0,0))
audio = manage_json("Config/config.json", None, mode="r")['audio']
item_selected = None

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
        self.image = load_image(image, (96, 96))
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
                self.direction_time = randint(15, 120)
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
    def __init__(self, pos, is_boss=False):
        super().__init__()
        if not is_boss:
            self.image = load_image("Assets/Images/Entity/Enemies/Swordsman.png", (96, 96))
        else:
            self.image = load_image("Assets/Images/Entity/Enemies/MasterSwordsman.png", (256, 256))
        self.rect = self.image.get_rect(center=pos)
        
        if not is_boss:
            self.name = "Swordsman"
            self.faction = 'enemy'
            self.weapon = None
            self.health = 8
            self.movement_speed = 2.5
            self.detection_range = 192
            self.vision_range = (60, 50)
            self.jump_delay = 200
            self.jump_height = 40
            self.current_jump_height = 0
            self.jumping = False
            self.jump_slow = 0
            self.jump_speed = 7

        else:
            self.name = "Master Swordsman"
            self.faction = 'enemy'
            self.weapon = None
            self.health = 75
            self.movement_speed = 2
            self.detection_range = 256
            self.vision_range = (160, 256)
            self.jump_delay = 500
            self.jump_height = 60
            self.current_jump_height = 0
            self.jumping = False
            self.jump_slow = 0
            self.jump_speed = 8

        self.direction = 1
        self.attacking = False
        self.direction_time = 0
        self.is_hit_by = []
        self.old_direction = 1
        self.player_in_range = False
        self.player_is_found = False
        self.hit_platforms = 0
        self.can_jump = True
        self.jump_time = 0
        self.is_boss = is_boss
        
        self.real_x = self.rect.x
        self.real_y = self.rect.y

        self.kb_duration = 0
        self.kb_speed = 0
        
    def update(self):
        # pathfinding
        self.player_is_found = player.real_x > self.real_x - self.detection_range and player.real_x < self.real_x + self.detection_range
        self.player_in_range = player.real_x > self.real_x - self.vision_range[0] and player.real_x < self.real_x + self.vision_range[0] and player.real_y > self.real_y - self.vision_range[1] and player.real_y < self.real_y + self.vision_range[1]
        if self.kb_duration <= 5:
            if not self.player_is_found and not self.player_in_range:
                if self.direction_time == 0:
                    self.direction *= -1
                    self.direction_time = randint(15, 120)
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
        else:
            self.real_x += self.kb_speed * 10
        
        if self.kb_duration > 0:
            self.kb_duration -= 1

        if random() > 0.99 and self.can_jump and not self.jumping:
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
                if self.kb_duration <= 5:
                    # First time touching this sword
                    self.health -= sword.damage
                    if not self.is_boss:
                        self.kb_duration = sword.knockback * randint(6, 10)
                        self.kb_speed = 1 * player.direction
                        self.real_x += sword.knockback * player.direction * 25
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

        if self.real_y - self.rect.height >= floor_level:
            self.kill()

class Archer(pygame.sprite.Sprite):
    def __init__(self, pos, is_boss=False):
        super().__init__()
        if not is_boss:
            self.image = load_image("Assets/Images/Entity/Enemies/Archer.png", (128, 128))
            self.rect = self.image.get_rect(center=pos)
            self.name = "Archer"
            self.faction = 'enemy'
            self.weapon = None
            self.health = 5
            self.movement_speed = 0.5
            self.detection_range = 384
            self.vision_range = (120, 80)
            self.jump_delay = 400
            self.jump_height = 30
            self.current_jump_height = 0
            self.jumping = False
            self.jump_slow = 0
            self.jump_speed = 5
        else:
            self.image = load_image("Assets/Images/Entity/Enemies/PhantomArcher.png", (256, 256))
            self.rect = self.image.get_rect(center=pos)
            self.name = "Phantom Archer"
            self.faction = 'enemy'
            self.weapon = None
            self.health = 75
            self.movement_speed = 1
            self.detection_range = 384
            self.vision_range = (200, 200)
            self.jump_delay = 800
            self.jump_height = 50
            self.current_jump_height = 0
            self.jumping = False
            self.jump_slow = 0
            self.jump_speed = 7

        self.direction = 1
        self.attacking = False
        self.direction_time = 0
        self.is_hit_by = []
        self.old_direction = 1
        self.player_in_range = False
        self.player_is_found = False
        self.hit_platforms = 0
        self.can_jump = True
        self.jump_time = 0
        self.is_boss = is_boss
        
        self.real_x = self.rect.x
        self.real_y = self.rect.y

        self.kb_duration = 0
        self.kb_speed = 0
        
    def update(self):
        # pathfinding
        self.player_is_found = player.real_x > self.real_x - self.detection_range and player.real_x < self.real_x + self.detection_range
        self.player_in_range = player.real_x > self.real_x - self.vision_range[0] and player.real_x < self.real_x + self.vision_range[0] and player.real_y > self.real_y - self.vision_range[1] and player.real_y < self.real_y + self.vision_range[1]
        if self.kb_duration <= 5:
            if not self.player_is_found and not self.player_in_range:
                if self.direction_time == 0:
                    self.direction *= -1
                    self.direction_time = randint(15, 120)
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
        else:
            self.real_x += self.kb_speed * 10
        
        if self.kb_duration > 0:
            self.kb_duration -= 1

        if random() > 0.99 and self.can_jump and not self.jumping:
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
                if self.kb_duration <= 5:
                    # First time touching this sword
                    self.health -= sword.damage
                    if not self.is_boss:
                        self.kb_duration = sword.knockback * randint(6, 10)
                        self.kb_speed = 1 * player.direction
                        self.real_x += sword.knockback * player.direction * 25
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

        if self.real_y - self.rect.height >= floor_level:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = load_image("Assets/Images/Entity/Players/Player.png", transform=False)
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
        self.jump_power = 8
        self.base_jump_power = 8
        self.propulsion_power = 1
        self.propulsion_duration = 0
        self.propulsion_time = 0
        self.health = self.max_health = 20
        self.lives = 3
        self.is_alive = True
        self.is_hit_by = []
        self.real_x = self.rect.x
        self.real_y = self.rect.y
        self.hit_platforms = 0
        self.climb_max = 32
        self.move_speed = 5
        self.base_move_speed = 5
        self.dash_speed = 20
        self.dash_time = 0
        self.dash_delay = 4000
        self.dash_duration = 500
        self.is_dashing = False
        self.kb_duration = 0
        self.kb_speed = 0
        self.horizontal_movement = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if self.kb_duration <= 5:
            self.horizontal_movement = 0
            if keys[key_left] or joystick.get_axis(0) < -0.2:
                self.horizontal_movement = -self.move_speed
                self.direction = -1
            elif keys[key_right] or joystick.get_axis(0) > 0.2:
                self.horizontal_movement = self.move_speed
                self.direction = 1
        else:
            self.horizontal_movement = self.kb_speed * 10

        if self.horizontal_movement:
            self.real_x += self.horizontal_movement
            self.rect.x = self.real_x

            for platform in pygame.sprite.spritecollide(self, plat_group, False):
                if not platform.isSolid:
                    continue
                if self.horizontal_movement > 0:
                    self.rect.right = platform.rect.left
                else:
                    self.rect.left = platform.rect.right
                self.real_x = self.rect.x
        
        if self.kb_duration > 0:
            self.kb_duration -= 1

        if (keys[key_jump] or joystick.get_button(1)) and self.can_jump and not self.jumping:
            self.jumping = True
            self.can_jump = False
            self.jump_time = pygame.time.get_ticks()

        if self.jumping:
            if self.jump_height > self.current_jump_height:
                self.real_y -= self.jump_power - self.jump_slow
                self.current_jump_height += 2
                self.jump_slow += 0.1
            else:
                self.jumping = False
                self.current_jump_height = 0
                self.jump_slow = 0

        if keys[key_dash] and not self.is_dashing and pygame.time.get_ticks() > self.dash_time + self.dash_delay:
            self.is_dashing = True
            self.dash_time = pygame.time.get_ticks() + self.dash_duration

        if self.is_dashing and pygame.time.get_ticks() < self.dash_time:
            self.move_speed = self.dash_speed
        else:
            self.move_speed = self.base_move_speed
            self.is_dashing = False

        if keys[key_left] or keys[key_right] or abs(joystick.get_axis(0)) > 0.2:
            self.animation_key += 0.05
            if self.animation_key >= 3:
                self.animation_key = 0

        frame = load_image(self.image_set[int(self.animation_key)], transform=False)
        if self.direction == -1:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

        prev_y = self.real_y
        if not self.jumping:
            self.real_y += 5
            self.can_jump = False

        self.rect.x, self.rect.y = self.real_x, self.real_y
        self.hit_platforms = [
            platform
            for platform in pygame.sprite.spritecollide(self, plat_group, False)
            if platform.isSolid
        ]

        if self.hit_platforms:
            resolved = False
            for platform in self.hit_platforms:
                prev_top = prev_y
                prev_bottom = prev_y + self.rect.height
                new_top = self.real_y
                new_bottom = self.real_y + self.rect.height

                is_landing = (
                    not self.jumping and
                    prev_bottom <= platform.rect.top + 6 and
                    new_bottom >= platform.rect.top and
                    prev_bottom <= platform.rect.top
                )
                is_head_hit = (
                    self.jumping and
                    prev_top >= platform.rect.bottom and
                    new_top <= platform.rect.bottom and
                    new_bottom >= platform.rect.bottom
                )

                if is_landing:
                    self.can_jump = True
                    self.real_y = platform.rect.top - self.rect.height
                    self.rect.y = self.real_y
                    resolved = True
                    break
                if is_head_hit:
                    self.jumping = False
                    self.current_jump_height = 0
                    self.jump_slow = 0
                    self.real_y = platform.rect.bottom
                    self.rect.y = self.real_y
                    self.can_jump = False
                    resolved = True
                    break

            if not resolved:
                self.real_y = prev_y
                self.rect.y = self.real_y

        self.rect.x = self.real_x
        self.rect.y = self.real_y
        
        for x in enemy_render_group:
            if (isinstance(x, Sword) and type(x.player) != Player) or isinstance(x, Projectile):
                if isinstance(x, Sword):
                    touching = x.swinging and self.rect.colliderect(x.rect)
                    kb = x.knockback
                else:
                    touching = self.rect.colliderect(x.rect)
                    kb = 0

                if touching and not self.is_dashing:
                    if x not in self.is_hit_by:
                        if self.kb_duration <= 5:
                            self.health -= x.damage
                            try:
                                self.kb_duration = kb * randint(6, 10)
                                self.kb_speed = 1 * x.player.direction
                                self.real_x += kb * x.player.direction * 25
                            except AttributeError:
                                self.kb_duration = kb * randint(3, 8)
                                self.kb_speed = 1 * ((x.direction//180) * 2 - 1)
                                self.real_x += kb * ((x.direction//180) * 2 - 1)
                            joystick.rumble(5, 10, 1)
                            if self.health <= 0:
                                self.lives -= 1
                                self.health = self.max_health
                                self.real_x, self.real_y = origin_point[0], origin_point[1]
                            self.is_hit_by.append(x)
                else:
                    if x in self.is_hit_by:
                        self.is_hit_by.remove(x)
            if self.lives <= 0:
                lose_game(game_save)

class SwordPiece(pygame.sprite.Sprite):
    def __init__(self, sprite, piece, category, swn_spd_mod, max_swn_mod, reach_mod, dmg_mod, kb_mod, as_item=True, as_piece=False):
        super().__init__()
        self.image = load_image(sprite, (192, 192))
        self.rect = self.image.get_rect()
        self.spritepath = sprite
        
        self.piece = piece
        self.category = category
        self.swn_spd_mod = swn_spd_mod
        self.max_swn_mod = max_swn_mod
        self.reach_mod = reach_mod
        self.dmg_mod = dmg_mod
        self.kb_mod = kb_mod

        self.as_item = as_item
        self.as_piece = as_piece
        self.name = f"{category} {piece}"
        self.description = f"The {self.name} is a piece that fits on your sword in the {piece} slot. This specific piece is from the {category} set."
        self.effect = f"Replaces the sword piece in the {piece} slot."
        self.weight = 10  # Common: 20, Uncommon: 10, Rare: 3, Legendary: 1
        self.info_box_open = False
        self.info_box = None
        self.info_box_text = None
        self.info_box_name = None
        self.info_box_image = None
        self.info_box_description = None
    
    def update(self):
        if self.as_item:
            mouse = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if self.rect.collidepoint(mouse[0], mouse[1]) and mouse_click[2] and not self.info_box_open:
                if self.weight == 20: noi_text_colour = GREY(192) # Common
                elif self.weight == 10: noi_text_colour = GREEN # Uncommon
                elif self.weight == 3: noi_text_colour = RED # Rare
                elif self.weight == 1: noi_text_colour = YELLOW # Legendary
                else: noi_text_colour = BLUE # Undefined Rarity

                self.info_box = InfoBox((WIDTH//2, HEIGHT//2), (WIDTH//1.5, HEIGHT//1.5))
                self.info_box_name = Text((WIDTH//2, HEIGHT//5), self.name, simple_font, colour=noi_text_colour)
                self.info_box_text = Text((WIDTH//2, HEIGHT//4), "Press ESC to Close Box", simple_font)
                self.info_box_image = DisplayObject((WIDTH//2, HEIGHT//2.5), self.spritepath, WIDTH//6)
                self.info_box_description = Text((WIDTH//2, HEIGHT//1.75), self.description, simple_font)
                self.info_box_open = True
                chest_ui_group.add(
                    self.info_box,
                    self.info_box_name,
                    self.info_box_text,
                    self.info_box_image,
                    self.info_box_description,
                )
        
            if self.rect.collidepoint(mouse[0], mouse[1]) and mouse_click[0] and not self.info_box_open:
                global item_selected, GameState
                item_selected = self
                self.as_item = False
                chest_ui_group.empty()
                state_switcher(8)

            if self.info_box is not None and not self.info_box.is_active:
                self.info_box.kill()
                self.info_box_name.kill()
                self.info_box_text.kill()
                self.info_box_image.kill()
                self.info_box_description.kill()
                self.info_box = None
                self.info_box_name = None
                self.info_box_text = None
                self.info_box_image = None
                self.info_box_description = None
                self.info_box_open = False
        
        if self.as_piece:
            mouse = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

" This class is currently unused "
class Sheath(pygame.sprite.Sprite):
    def __init__(self, sprite, category, effect, set_effect):
        super().__init__()
        self.image = load_image(sprite)
        self.rect = self.image.get_rect()
        
        self.category = category
        self.effect = effect
        self.set_effect = set_effect
        
    def click_check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                pass

class Sword(pygame.sprite.Sprite):
    def __init__(self, player, pieces, is_boss=False):
        super().__init__()
        if is_boss:
            self.og_image = load_image("Assets/Images/Sword/MasterSwordsmanSword.png", (128, 128))
        else:
            self.og_image = load_image("Assets/Images/Sword/SwordStill.png", (64, 64))
        self.image = self.og_image
        self.rect = self.image.get_rect()

        # references
        self.player = player
        self.pieces = pieces
        self.is_boss = is_boss

        # swing state
        self.swinging = False
        if is_boss:
            self.swing_speed = 2     # speed at which the sword swings
            self.max_swing = 80      # how high sword swings
            self.reach = 3.5         # how far sword swings
            self.damage = 3          # how much damage the sword does
            self.knockback = 3.5     # how far an attack knocks someone back
            self.atk_delay = 1500
        
        else:
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

            self.knockback = 1              # how far an attack knocks someone back
            self.knockback *- self.pieces[0].kb_mod
            self.knockback *- self.pieces[1].kb_mod
            self.knockback *- self.pieces[1].kb_mod
            self.knockback *- self.pieces[1].kb_mod
            self.knockback = max(0.1, math.floor(self.knockback*10) / 10)
        
            self.atk_delay = ((4 - self.swing_speed) + ((self.damage + self.knockback)/3) + (self.reach * self.max_swing // 60)) * 450
        
        self.atk_time = 0
        
        self.selfX = 0
        self.selfY = 0
        self.real_x = self.rect.x
        self.real_y = self.rect.y
    
    def update(self):
        keys = pygame.key.get_pressed()
        if type(self.player) == Player:
            if (keys[key_slash] or joystick.get_button(0)) and not self.swinging and pygame.time.get_ticks() > self.atk_time + self.atk_delay:
                self.selfY += self.max_swing
                self.selfX -= math.floor(math.sqrt(self.max_swing))
                self.swinging = True
                if audio:
                    choice(sword_slashes).play()
        
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
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.mask.get_bounding_rects()[0]
            self.rect.center = self.rect.center

            # position relative to player
            self.real_x = self.player.real_x + (self.player.direction * 20 * abs(self.player.direction*2 + 1)) - 20 - (self.selfX * self.player.direction)
            self.real_y = self.player.real_y + 20 - self.selfY

        elif type(self.player) == Swordsman and not self.is_boss:
            if self.player.player_in_range and not self.swinging and pygame.time.get_ticks() > self.atk_time + self.atk_delay:
                self.selfY += self.max_swing
                self.selfX -= math.floor(math.sqrt(self.max_swing))
                self.swinging = True
                if audio:
                    choice(sword_slashes).play()
        
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

            if self.real_y - self.rect.height >= floor_level:
                self.kill()

        else:
            if self.player.player_in_range and not self.swinging and pygame.time.get_ticks() > self.atk_time + self.atk_delay:
                self.selfY += self.max_swing
                self.selfX -= math.floor(math.sqrt(self.max_swing))
                self.swinging = True
                if audio:
                    choice(sword_slashes).play()
        
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
                self.rect.center = self.player.rect.bottomright
            else:
                self.rect.center = self.player.rect.bottomleft
                
            self.real_x = self.player.real_x + (self.player.direction * 20 * abs(self.player.direction*2 + 1)) - 20 - (self.selfX * self.player.direction)
            self.real_y = self.player.real_y + 100 - self.selfY

            if self.real_y - self.rect.height >= floor_level:
                self.kill()

        self.rect.x = self.real_x - camera_x
        if self.player.jumping or self.swinging:
            self.rect.y = (self.real_y - camera_y)
        else:
            self.rect.y = (self.real_y - camera_y)//16*16
    
    def piece_interpreter(self, pieces):
        if len(pieces) < 4:
            pieces = list(pieces) + [self.pieces[0], self.pieces[1], self.pieces[2], self.pieces[3]][len(pieces):4]

        return_pieces = [None, None, None, None]
        if pieces[0] == old_handle or pieces[0] == b_old_handle:
            return_pieces[0] = "Handle - Old"
        elif pieces[0] == brutish_handle or pieces[0] == b_brutish_handle:
            return_pieces[0] = "Handle - Brutish"
        elif pieces[0] == lancing_handle or pieces[0] == b_lancing_handle:
            return_pieces[0] = "Handle - Lancing"
        elif pieces[0] == classic_handle or pieces[0] == b_classic_handle:
            return_pieces[0] = "Handle - Classic"
        
        if pieces[1] == old_blade or pieces[1] == b_old_blade:
            return_pieces[1] = "Blade - Old"
        elif pieces[1] == brutish_blade or pieces[1] == b_brutish_blade:
            return_pieces[1] = "Blade - Brutish"
        elif pieces[1] == lancing_blade or pieces[1] == b_lancing_blade:
            return_pieces[1] = "Blade - Lancing"
        elif pieces[1] == classic_blade or pieces[1] == b_classic_blade:
            return_pieces[1] = "Blade - Classic"
        
        if pieces[2] == old_foreblade or pieces[2] == b_old_foreblade:
            return_pieces[2] = "Foreblade - Old"
        elif pieces[2] == brutish_foreblade or pieces[2] == b_brutish_foreblade:
            return_pieces[2] = "Foreblade - Brutish"
        elif pieces[2] == lancing_foreblade or pieces[2] == b_lancing_foreblade:
            return_pieces[2] = "Foreblade - Lancing"
        elif pieces[2] == classic_foreblade or pieces[2] == b_classic_foreblade:
            return_pieces[2] = "Foreblade - Classic"
        
        if pieces[3] == old_sheath or pieces[3] == b_old_sheath:
            return_pieces[3] = "Sheath - Old"
        elif pieces[3] == brutish_sheath or pieces[3] == b_brutish_sheath:
            return_pieces[3] = "Sheath - Brutish"
        elif pieces[3] == lancing_sheath or pieces[3] == b_lancing_sheath:
            return_pieces[3] = "Sheath - Lancing"
        elif pieces[3] == classic_sheath or pieces[3] == b_classic_sheath:
            return_pieces[3] = "Sheath - Classic"

        for i in range(4):
            if return_pieces[i] is None:
                return_pieces[i] = self.pieces[i].name if self.pieces and hasattr(self.pieces[i], 'name') else "Handle - Old"
        return return_pieces

    def load_sword_pieces(self, sword_pieces):
        if len(sword_pieces) < 4:
            return

        if sword_pieces[0] == "Handle - Old":
            self.pieces[0] = old_handle
        elif sword_pieces[0] == "Handle - Brutish":
            self.pieces[0] = brutish_handle
        elif sword_pieces[0] == "Handle - Lancing":
            self.pieces[0] = lancing_handle
        elif sword_pieces[0] == "Handle - Classic":
            self.pieces[0] = classic_handle
        
        if sword_pieces[1] == "Blade - Old":
            self.pieces[1] = old_blade
        elif sword_pieces[1] == "Blade - Brutish":
            self.pieces[1] = brutish_blade
        elif sword_pieces[1] == "Blade - Lancing":
            self.pieces[1] = lancing_blade
        elif sword_pieces[1] == "Blade - Classic":
            self.pieces[1] = classic_blade
        
        if sword_pieces[2] == "Foreblade - Old":
            self.pieces[2] = old_foreblade
        elif sword_pieces[2] == "Foreblade - Brutish":
            self.pieces[2] = brutish_foreblade
        elif sword_pieces[2] == "Foreblade - Lancing":
            self.pieces[2] = lancing_foreblade
        elif sword_pieces[2] == "Foreblade - Classic":
            self.pieces[2] = classic_foreblade
        
        if sword_pieces[3] == "Sheath - Old":
            self.pieces[3] = old_sheath
        elif sword_pieces[3] == "Sheath - Brutish":
            self.pieces[3] = brutish_sheath
        elif sword_pieces[3] == "Sheath - Lancing":
            self.pieces[3] = lancing_sheath
        elif sword_pieces[3] == "Sheath - Classic":
            self.pieces[3] = classic_sheath

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

class Bow(pygame.sprite.Sprite):
    def __init__(self, player, is_boss=False):
        super().__init__()
        if not is_boss:
            self.og_image = load_image("Assets/Images/Other Weapons/Bow.png", (48, 48))
        else:
            self.og_image = load_image("Assets/Images/Other Weapons/Bow.png", (96, 96))
        self.image = self.og_image
        self.rect = self.image.get_rect()

        # references
        self.player = player
        self.is_boss = is_boss

        if not is_boss:
            self.atk_delay = 2000
        else:
            self.atk_delay = 1750
        
        self.atk_time = 0
        
        self.real_x = self.rect.x
        self.real_y = self.rect.y
    
    def update(self):
        # base orientation depending on player direction
        base_angle = 0
        arrow_angle = 0
        if self.player.direction == 1:      # east
            base_angle = 225
            if not self.is_boss:
                arrow_angle = choice([45, 90])
            else:
                arrow_angle = choice([45, 90, 135])
        elif self.player.direction == -1:   # west
            base_angle = 45
            if not self.is_boss:
                arrow_angle = choice([270, 315])
            else:
                arrow_angle = choice([225, 270, 315])

        # rotate sword relative to base orientation
        self.image = pygame.transform.rotate(self.og_image, base_angle)
        self.rect = self.image.get_rect(center=self.rect.center)
                
        self.real_x = self.player.real_x + (self.player.direction * 20 * abs(self.player.direction*2 + 1)) - 20 - ((self.player.direction-1) * 25)
        self.real_y = self.player.real_y + 64

        if self.real_y - self.rect.height >= floor_level:
            self.kill()

        self.rect.x = self.real_x - camera_x

        if self.player.jumping:
            self.rect.y = (self.real_y - camera_y)
        else:
            self.rect.y = (self.real_y - camera_y)//16*16
    
        if self.player.player_in_range and pygame.time.get_ticks() > self.atk_time + self.atk_delay:
                self.atk_time = pygame.time.get_ticks()
                if not self.is_boss:
                    if arrow_angle % 2 == 1:
                        enemy_render_group.add(Projectile(self.rect.center, (64, 32), "Assets/Images/Other Weapons/Arrow.png", arrow_angle, 96, 1.5, 0.8, offset_angle=90))
                    else:
                        enemy_render_group.add(Projectile(self.rect.center, (64, 32), "Assets/Images/Other Weapons/Arrow.png", arrow_angle, 48, 1.5, 0.8, gravity=0.8, offset_angle=-90))
                else:
                    if arrow_angle % 2 == 1:
                        enemy_render_group.add(Projectile(self.rect.center, (96, 48), "Assets/Images/Other Weapons/Arrow.png", arrow_angle, 120, 4, 1.5, offset_angle=90))
                    else:
                        enemy_render_group.add(Projectile(self.rect.center, (96, 48), "Assets/Images/Other Weapons/Arrow.png", arrow_angle, 64, 2.5, 1.5, gravity=0.8, offset_angle=-90))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, size, sprite, direction, velocity, damage, knockback, gravity=1, offset_angle=0):
        super().__init__()
        self.image = pygame.transform.rotate(load_image(sprite, size), offset_angle + direction)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.mask.get_bounding_rects()[0]
        self.rect.center = pos
        self.direction = direction
        self.velocity = velocity
        self.gravity = gravity * 250
        self.damage = damage
        self.knockback = knockback * 2
        self.is_falling = False
        self.hit_platforms = []

        self.duration = 0
        self.grav_val = 1
        self.real_x = pos[0]
        self.real_y = pos[1]
    
    def update(self):
        # just 8-point direction for now
        if self.direction == 0:
            self.real_y -= self.velocity
        if self.direction == 45:
            self.real_y -= self.velocity / 8
            self.real_x += self.velocity / 4
        if self.direction == 90:
            self.real_x += self.velocity
        if self.direction == 135:
            self.real_x += self.velocity / 4
            self.real_y += self.velocity / 8
        if self.direction == 180:
            self.real_y += self.velocity
        if self.direction == 225:
            self.real_y += self.velocity / 8
            self.real_x -= self.velocity / 4
        if self.direction == 270:
            self.real_x -= self.velocity
        if self.direction == 315:
            self.real_x -= self.velocity / 4
            self.real_y -= self.velocity / 8
        
        self.real_y += math.floor(self.grav_val)
        self.grav_val *= max(1.01, self.gravity / min(256, 324 - self.velocity))
        self.knockback /= 1.05
        self.velocity /= 1.05

        if self.velocity <= 8 and not self.is_falling:
            self.image = pygame.transform.rotate(self.image, -self.direction + 180)
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.mask.get_bounding_rects()[0]
            self.is_falling = True
            self.rect.center = (self.real_x, self.real_y)

        if self.real_y > floor_level:
            self.kill()
        
        self.hit_platforms = [platform for platform in pygame.sprite.spritecollide(self, plat_group, False) if platform.isSolid]

        if self.hit_platforms:
            self.kill()
        
        self.rect.x = self.real_x + camera_x
        self.rect.y = self.real_y + camera_y - 32

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

        self.scroll_cool = 300
        self.scroll_time = 0
    
    def scroll(self):
        if pygame.time.get_ticks() > self.scroll_time + self.scroll_cool:
            self.index += 1
            if self.index >= len(self.text_options):
                self.index = 0
            self.text = self.text_options[self.index]
            self.scroll_time = pygame.time.get_ticks()
    
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
        self.image = load_image("Assets/UI & GUI/HeartFull.png", (WIDTH//16, WIDTH//16))
        self.rect = self.image.get_rect()
        self.rect.x = 64 * (WIDTH // 64 + heart_pos - 4)
        self.rect.y = WIDTH//96
        self.heart_pos = heart_pos
    def update(self):
        if player.lives >= 4 - self.heart_pos:
            if player.health < player.max_health // 2 and player.lives == 4 - self.heart_pos:
                self.image = load_image("Assets/UI & GUI/HeartHalf.png", transform=False)
            else:
                self.image = load_image("Assets/UI & GUI/HeartFull.png", transform=False)
        else:
            self.image = load_image("Assets/UI & GUI/HeartEmpty.png", transform=False)

class Item(pygame.sprite.Sprite):
    def __init__(self, sprite, name, description, effect, weight):
        super().__init__()
        self.spritepath = sprite
        self.image = load_image(sprite, (192, 192))
        self.rect = self.image.get_rect(center=(0, 0)) # Default position, can be changed when placed in the world
        self.name = name
        self.description = description
        self.effect = effect
        self.weight = weight  # Common: 20, Uncommon: 10, Rare: 3, Legendary: 1
        self.info_box_open = False
        self.info_box = None
        self.info_box_text = None
        self.info_box_name = None
        self.info_box_image = None
        self.info_box_description = None
    
    def update(self):
        mouse = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if self.rect.collidepoint(mouse[0], mouse[1]) and mouse_click[2] and not self.info_box_open:
            if self.weight == 20: noi_text_colour = GREY(192) # Common
            elif self.weight == 10: noi_text_colour = GREEN # Uncommon
            elif self.weight == 3: noi_text_colour = RED # Rare
            elif self.weight == 1: noi_text_colour = YELLOW # Legendary
            else: noi_text_colour = BLUE # Undefined Rarity

            self.info_box = InfoBox((WIDTH//2, HEIGHT//2), (WIDTH//1.5, HEIGHT//1.5))
            self.info_box_name = Text((WIDTH//2, HEIGHT//5), self.name, simple_font, colour=noi_text_colour)
            self.info_box_text = Text((WIDTH//2, HEIGHT//4), "Press ESC to Close Box", simple_font)
            self.info_box_image = DisplayObject((WIDTH//2, HEIGHT//2.5), self.spritepath, WIDTH//6)
            self.info_box_description = Text((WIDTH//2, HEIGHT//1.75), self.description, simple_font)
            self.info_box_open = True
            chest_ui_group.add(
                self.info_box,
                self.info_box_name,
                self.info_box_text,
                self.info_box_image,
                self.info_box_description,
            )
        
        if self.rect.collidepoint(mouse[0], mouse[1]) and mouse_click[0] and not self.info_box_open:
                global item_selected
                item_selected = self

        if self.info_box is not None and not self.info_box.is_active:
            self.info_box.kill()
            self.info_box_name.kill()
            self.info_box_text.kill()
            self.info_box_image.kill()
            self.info_box_description.kill()
            self.info_box = None
            self.info_box_name = None
            self.info_box_text = None
            self.info_box_image = None
            self.info_box_description = None
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
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(GREY(64))
        self.rect = self.image.get_rect(center=pos)
        self.is_active = True
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_ESCAPE]:
            self.is_active = False

class DisplayObject(pygame.sprite.Sprite):
    def __init__(self, pos, sprite, scale):
        super().__init__()
        self.scale = scale

        self.image = load_image(sprite, (scale, scale))
        self.rect = self.image.get_rect(center=pos)

class SelectionCircle(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.base_image = load_image("Assets/UI & GUI/SelectionCircle.png", (size, size))
        self.angle = 0
        self.pos = list(pos)
        self.image = self.base_image
        self.rect = self.image.get_rect(center=self.pos)
    
    def update(self):
        self.angle = (self.angle + 1.5) % 360
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

class Background(pygame.sprite.Sprite):
    def __init__(self, sprite):
        super().__init__()
        self.image = load_image(sprite, (WIDTH, HEIGHT))
        self.rect = self.image.get_rect(topleft=(0, 0))

class Foreground(pygame.sprite.Sprite):
    def __init__(self, sprite, pos):
        super().__init__()
        self.image = load_image(sprite, (512, 384))
        self.rect = self.image.get_rect(topleft=pos)

old_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Old.png", "Handle", "Old", 1, 1, 1, 1, 1)
old_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Old.png", "Blade", "Old", 1, 1, 1, 1, 1)
old_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Old.png", "Foreblade", "Old", 1, 1, 1, 1, 1)
old_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Old.png", "Sheath", "Old", 1, 1, 1, 1, 1)

b_old_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Old.png", "Handle", "Old", 1, 1, 1, 1, 1, False, True)
b_old_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Old.png", "Blade", "Old", 1, 1, 1, 1, 1, False, True)
b_old_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Old.png", "Foreblade", "Old", 1, 1, 1, 1, 1, False, True)
b_old_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Old.png", "Sheath", "Old", 1, 1, 1, 1, 1, False, True)
old_set = [b_old_handle, b_old_blade, b_old_foreblade, b_old_sheath]

lancing_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Lancing.png", "Handle", "Lancing", 0.7, 0.5, 3, 0.9, 1)
lancing_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Fencing.png", "Blade", "Lancing", 0.7, 0.5, 3, 1.1, 1.6)
lancing_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Lancing.png", "Foreblade", "Lancing", 0.8, 1.2, 1.4, 1.3, 1.2)
lancing_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Lancing.png", "Sheath", "Lancing", 1, 1, 1, 1, 1)

b_lancing_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Lancing.png", "Handle", "Lancing", 0.7, 0.5, 3, 0.9, 1, False, True)
b_lancing_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Fencing.png", "Blade", "Lancing", 0.7, 0.5, 3, 1.1, 1.6, False, True)
b_lancing_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Lancing.png", "Foreblade", "Lancing", 0.8, 1.2, 1.4, 1.3, 1.2, False, True)
b_lancing_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Lancing.png", "Sheath", "Lancing", 1, 1, 1, 1, 1, False, True)
lancing_set = [b_lancing_handle, b_lancing_blade, b_lancing_foreblade, b_lancing_sheath]

brutish_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Brutish.png", "Handle", "Brutish", 0.8, 1.2, 0.9, 1.2, 1.1)
brutish_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Brutish.png", "Blade", "Brutish", 1.3, 1.1, 0.7, 1.3, 1.4)
brutish_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Brutish.png", "Foreblade", "Brutish", 1.05, 1, 1.05, 1.15, 0.95)
brutish_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Brutish.png", "Sheath", "Brutish", 1, 1, 1, 1, 1)

b_brutish_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Brutish.png", "Handle", "Brutish", 0.8, 1.2, 0.9, 1.2, 1.1, False, True)
b_brutish_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Brutish.png", "Blade", "Brutish", 1.3, 1.1, 0.7, 1.3, 1.4, False, True)
b_brutish_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Brutish.png", "Foreblade", "Brutish", 1.05, 1, 1.05, 1.15, 0.95, False, True)
b_brutish_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Brutish.png", "Sheath", "Brutish", 1, 1, 1, 1, 1, False, True)
brutish_set = [b_brutish_handle, b_brutish_blade, b_brutish_foreblade, b_brutish_sheath]

classic_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Classic.png", "Handle", "Classic", 1.15, 1, 1, 1.05, 1.05)
classic_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Classic.png", "Blade", "Classic", 1.2, 0.9, 1.1, 1, 1.05)
classic_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Classic.png", "Foreblade", "Classic", 1.1, 1.05, 1, 1.2, 1.2)
classic_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Classic.png", "Sheath", "Classic", 1, 1, 1, 1, 1)

b_classic_handle = SwordPiece("Assets/Images/Sword/Handle/Handle - Classic.png", "Handle", "Classic", 1.15, 1, 1, 1.05, 1.05, False, True)
b_classic_blade = SwordPiece("Assets/Images/Sword/Blade/Blade - Classic.png", "Blade", "Classic", 1.2, 0.9, 1.1, 1, 1.05, False, True)
b_classic_foreblade = SwordPiece("Assets/Images/Sword/Foreblade/Foreblade - Classic.png", "Foreblade", "Classic", 1.1, 1.05, 1, 1.2, 1.2, False, True)
b_classic_sheath = SwordPiece("Assets/Images/Sword/Sheath/Sheath - Classic.png", "Sheath", "Classic", 1, 1, 1, 1, 1, False, True)
classic_set = [b_classic_handle, b_classic_blade, b_classic_foreblade, b_classic_sheath]

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
sets = [old_handle, old_blade, old_foreblade, old_sheath, lancing_handle, lancing_blade, lancing_foreblade, lancing_sheath, brutish_handle, brutish_blade, brutish_foreblade, brutish_sheath, classic_handle, classic_blade, classic_foreblade, classic_sheath]
item_pool = []

piece_selection_circle = SelectionCircle((WIDTH//3, HEIGHT//2), 324)

for s in sets:
    for i in range(10):
        item_pool.append(s)

for item in items:
    for i in range(item.weight):
        item_pool.append(item)

# Create backgrounds and foregrounds
pleasant_sky = Background("Assets/Images/BG/BG-PleasantSky.png")
red_bg = Background("Assets/Images/BG/BG-Redscale.png")

grassy_sprite = "Assets/Images/BG/FG-Grassy.png"

# Create player, sword, and hearts
random_set = [choice([old_handle, lancing_handle, brutish_handle, classic_handle]), choice([old_blade, lancing_blade, brutish_blade, classic_blade]), choice([old_foreblade, lancing_foreblade, brutish_foreblade, classic_foreblade]), choice([old_sheath, lancing_sheath, brutish_sheath, classic_sheath])]
player = Player(origin_point)
sword = Sword(player, old_set)
heart1 = Heart(1)
heart2 = Heart(2)
heart3 = Heart(3)

master_swordsman = Swordsman((origin_point[0] + 200, origin_point[1]), True)
master_sword = Sword(master_swordsman, old_set, True)
master_swordsman.weapon = master_sword

phantom_archer = Archer((origin_point[0] + 200, origin_point[1]), True)
bow = Bow(phantom_archer, True)
phantom_archer.weapon = bow

# Put them in groups
player_group.add(player)
ui_group.add(heart1, heart2, heart3)
#enemy_render_group.add(master_swordsman, master_sword)
#enemy_render_group.add(phantom_archer, bow)