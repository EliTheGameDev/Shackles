import pygame
import json
import sys
import os
import tkinter as tk
from tkinter import filedialog

# 1. INITIALIZE PYGAME FIRST
pygame.init()

# Ensure the Levels directory exists
if not os.path.exists("Levels"):
    os.makedirs("Levels")

# --------------------
# Config
# --------------------
TILE_SIZE = 32
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

CATEGORY_BAR_HEIGHT = 40
HOTBAR_HEIGHT = 72

# Colors
GRID_COLOR = (40, 40, 40)
UI_BG = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
INPUT_INACTIVE = (60, 60, 60)
INPUT_ACTIVE = (100, 100, 150)

# 2. SETUP DISPLAY BEFORE LOADING IMAGES
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shackles - Level Editor")

# --------------------
# Platform class + registry
# --------------------
class PlatformType:
    def __init__(self, id, color=None, sprite_path=None):
        self.id = id
        self.color = color if color else (255, 0, 255) # Missing texture fallback
        self.sprite_path = sprite_path
        self.sprite = None

    def load_resources(self):
        if self.sprite_path and os.path.exists(self.sprite_path):
            img = pygame.image.load(self.sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        else:
            self.sprite = None

platform_registry = {}

def register_platform(plat):
    plat.load_resources()
    platform_registry[plat.id] = plat

def get_platform(pid):
    return platform_registry.get(pid, platform_registry.get("Empty"))

# Register default tools
register_platform(PlatformType("Empty", color=(0, 0, 0)))
register_platform(PlatformType("Eraser", color=(255, 100, 100)))

# ==========================================
# AUTOMATIC PLATFORM GENERATION (18 Total)
# ==========================================
platform_types = ["Brick", "Dirt", "Grass"]
platform_prefixes = ["Base", "Bottom Left", "Bottom Right", "Left", "Right", "Top"]

for p_type in platform_types:
    for prefix in platform_prefixes:
        plat_name = f"{prefix} {p_type}" 
        plat_path = f"Assets/Images/Platforms/Ground-Based Platforms/{plat_name} Platform.png"
        
        fallback_color = (50 + (len(p_type)*20) % 200, 100, 50 + (len(prefix)*20) % 200)
        register_platform(PlatformType(plat_name, color=fallback_color, sprite_path=plat_path))

# --------------------
# Helper Functions
# --------------------
def world_to_screen(wx, wy, cam_x, cam_y):
    sx = (wx * TILE_SIZE) - int(cam_x * TILE_SIZE)
    sy = (wy * TILE_SIZE) - int(cam_y * TILE_SIZE) + CATEGORY_BAR_HEIGHT
    return sx, sy

def screen_to_world(sx, sy, cam_x, cam_y):
    wx = (sx + int(cam_x * TILE_SIZE)) // TILE_SIZE
    wy = (sy - CATEGORY_BAR_HEIGHT + int(cam_y * TILE_SIZE)) // TILE_SIZE
    return wx, wy

def save_level_dialog(blocks, map_w, map_h):
    # Hide the main tkinter window, we only want the dialog box
    root = tk.Tk()
    root.withdraw() 
    filepath = filedialog.asksaveasfilename(
        initialdir=os.path.join(os.getcwd(), "Levels"),
        title="Save Level As...",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    root.destroy()

    if not filepath:
        print("Save cancelled.")
        return

    # Create dictionary with EVERY single coordinate
    all_blocks = {}
    for y in range(map_h):
        for x in range(map_w):
            # If a block exists there, save it. Otherwise, save "Empty"
            all_blocks[f"{x},{y}"] = blocks.get((x, y), "Empty")

    save_data = {
        "metadata": {"width": map_w, "height": map_h},
        "blocks": all_blocks
    }
    with open(filepath, "w") as f:
        json.dump(save_data, f, indent=4)
    print(f"Level saved to {filepath}")

def load_level_dialog():
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        initialdir=os.path.join(os.getcwd(), "Levels"),
        title="Load Level JSON",
        filetypes=[("JSON files", "*.json")]
    )
    root.destroy()

    blocks = {}
    map_w, map_h = 50, 50 # Defaults
    
    if filepath and os.path.exists(filepath):
        with open(filepath, "r") as f:
            save_data = json.load(f)
            
            if "metadata" in save_data:
                map_w = save_data["metadata"].get("width", 50)
                map_h = save_data["metadata"].get("height", 50)
                block_data = save_data["blocks"]
            else:
                block_data = save_data
            
            for key, pid in block_data.items():
                # We only need to load non-empty blocks into our active dictionary to save memory
                if pid != "Empty":
                    x, y = map(int, key.split(","))
                    blocks[(x, y)] = pid
        print(f"Level loaded from {filepath}")
    else:
        print("No file selected. Starting fresh.")
        
    return blocks, map_w, map_h

# --------------------
# Main Loop
# --------------------
def main():
    clock = pygame.time.Clock()
    ui_font = pygame.font.SysFont(None, 24)

    # Prompt user to load a file on startup
    blocks, map_width, map_height = load_level_dialog()
    
    available_platforms = [p for p in platform_registry.keys() if p not in ["Empty", "Eraser"]]
    current_selection_idx = 0 

    # Calculate view size in tiles
    view_w_tiles = SCREEN_WIDTH / TILE_SIZE
    view_h_tiles = (SCREEN_HEIGHT - CATEGORY_BAR_HEIGHT - HOTBAR_HEIGHT) / TILE_SIZE

    # Start camera at bottom-left of the map
    cam_x = 0.0
    cam_y = max(0.0, map_height - view_h_tiles)
    speed = 0.5
    
    # Text Input UI setup
    input_w_rect = pygame.Rect(100, 7, 50, 26)
    input_h_rect = pygame.Rect(230, 7, 50, 26)
    active_w = False
    active_h = False
    text_w = str(map_width)
    text_h = str(map_height)

    running = True
    while running:
        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_w_rect.collidepoint(event.pos):
                    active_w = True
                    active_h = False
                elif input_h_rect.collidepoint(event.pos):
                    active_h = True
                    active_w = False
                else:
                    active_w = False
                    active_h = False
                    if text_w.isdigit() and int(text_w) > 0: map_width = int(text_w)
                    if text_h.isdigit() and int(text_h) > 0: map_height = int(text_h)

            if event.type == pygame.KEYDOWN:
                if active_w:
                    if event.key == pygame.K_RETURN:
                        active_w = False
                        if text_w.isdigit() and int(text_w) > 0: map_width = int(text_w)
                    elif event.key == pygame.K_BACKSPACE:
                        text_w = text_w[:-1]
                    elif event.unicode.isdigit():
                        text_w += event.unicode
                elif active_h:
                    if event.key == pygame.K_RETURN:
                        active_h = False
                        if text_h.isdigit() and int(text_h) > 0: map_height = int(text_h)
                    elif event.key == pygame.K_BACKSPACE:
                        text_h = text_h[:-1]
                    elif event.unicode.isdigit():
                        text_h += event.unicode
                else:
                    # Save Level Trigger
                    if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        # Release keys so we don't get stuck holding Ctrl after the window closes
                        pygame.event.clear() 
                        save_level_dialog(blocks, map_width, map_height)
                        
                    if event.key == pygame.K_e:
                        current_selection_idx = (current_selection_idx + 1) % len(available_platforms)
                    if event.key == pygame.K_q:
                        current_selection_idx = (current_selection_idx - 1) % len(available_platforms)

        # --- Input for Camera ---
        keys = pygame.key.get_pressed()
        if not (active_w or active_h):
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                cam_x -= speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                cam_x += speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                cam_y -= speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s] and not (pygame.key.get_mods() & pygame.KMOD_CTRL):
                cam_y += speed

        # Clamp camera
        max_cam_x = max(0.0, map_width - view_w_tiles)
        max_cam_y = max(0.0, map_height - view_h_tiles)
        cam_x = max(0.0, min(cam_x, max_cam_x))
        cam_y = max(0.0, min(cam_y, max_cam_y))

        # --- Placing / Erasing ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if CATEGORY_BAR_HEIGHT < mouse_y < SCREEN_HEIGHT - HOTBAR_HEIGHT:
            wx, wy = screen_to_world(mouse_x, mouse_y, cam_x, cam_y)
            mouse_btns = pygame.mouse.get_pressed()
            
            if 0 <= wx < map_width and 0 <= wy < map_height:
                if mouse_btns[0]:
                    blocks[(wx, wy)] = available_platforms[current_selection_idx]
                if mouse_btns[2]:
                    if (wx, wy) in blocks:
                        del blocks[(wx, wy)]

        # --- Drawing ---
        screen.fill((0, 0, 0))

        min_x = max(0, int(cam_x))
        max_x = min(map_width - 1, int(cam_x) + int(view_w_tiles) + 1)
        min_y = max(0, int(cam_y))
        max_y = min(map_height - 1, int(cam_y) + int(view_h_tiles) + 1)

        for wx in range(min_x, max_x + 1):
            for wy in range(min_y, max_y + 1):
                sx, sy = world_to_screen(wx, wy, cam_x, cam_y)
                rect = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)

                if rect.bottom < CATEGORY_BAR_HEIGHT or rect.top > SCREEN_HEIGHT - HOTBAR_HEIGHT:
                    continue

                pygame.draw.rect(screen, GRID_COLOR, rect, 1)

                pid = blocks.get((wx, wy), "Empty")
                if pid != "Empty":
                    plat = get_platform(pid)
                    if plat.sprite:
                        screen.blit(plat.sprite, rect)
                    else:
                        pygame.draw.rect(screen, plat.color, rect)

        # Draw UI
        pygame.draw.rect(screen, UI_BG, (0, 0, SCREEN_WIDTH, CATEGORY_BAR_HEIGHT))
        pygame.draw.rect(screen, UI_BG, (0, SCREEN_HEIGHT - HOTBAR_HEIGHT, SCREEN_WIDTH, HOTBAR_HEIGHT))
        
        selected_text = ui_font.render(f"Selected: {available_platforms[current_selection_idx]} (Q/E to switch)", True, TEXT_COLOR)
        screen.blit(selected_text, (20, SCREEN_HEIGHT - HOTBAR_HEIGHT + 25))
        
        lbl_w = ui_font.render("Width:", True, TEXT_COLOR)
        screen.blit(lbl_w, (40, 12))
        pygame.draw.rect(screen, INPUT_ACTIVE if active_w else INPUT_INACTIVE, input_w_rect)
        pygame.draw.rect(screen, TEXT_COLOR, input_w_rect, 2)
        txt_w_surf = ui_font.render(text_w, True, TEXT_COLOR)
        screen.blit(txt_w_surf, (input_w_rect.x + 5, input_w_rect.y + 5))

        lbl_h = ui_font.render("Height:", True, TEXT_COLOR)
        screen.blit(lbl_h, (165, 12))
        pygame.draw.rect(screen, INPUT_ACTIVE if active_h else INPUT_INACTIVE, input_h_rect)
        pygame.draw.rect(screen, TEXT_COLOR, input_h_rect, 2)
        txt_h_surf = ui_font.render(text_h, True, TEXT_COLOR)
        screen.blit(txt_h_surf, (input_h_rect.x + 5, input_h_rect.y + 5))

        info_text = ui_font.render("WASD/Arrows: Move | L-Click: Place | R-Click: Erase | Ctrl+S: Save", True, (150, 150, 150))
        screen.blit(info_text, (350, 12))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()