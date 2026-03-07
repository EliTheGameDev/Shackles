import pygame
import json
import sys
import os

# Optional file dialog
try:
    import tkinter as tk
    from tkinter import filedialog
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False

# --------------------
# Config
# --------------------
TILE_SIZE = 32
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

CATEGORY_BAR_HEIGHT = 40
HOTBAR_HEIGHT = 72

DEFAULT_SAVE_FILE = "level_data.json"

# Colors
WORLD_BORDER_COLOR = (255, 0, 0)   # thick red border
ORIGIN_HIGHLIGHT_COLOR = (255, 0, 0)

# --------------------
# Platform class + registry
# --------------------

class PlatformType:
    def __init__(self, id, color=None, sprite_path=None):
        self.id = id
        self.color = color
        self.sprite_path = sprite_path
        self.sprite = None

    def load_resources(self):
        if self.sprite_path and os.path.exists(self.sprite_path):
            img = pygame.image.load(self.sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        else:
            self.sprite = None

PLATFORMS = {}

def register_platform(platform: PlatformType):
    PLATFORMS[platform.id] = platform

def get_platform(id: str) -> PlatformType:
    return PLATFORMS.get(id, PLATFORMS["Empty"])

def register_all_platforms():
    register_platform(PlatformType("Empty",  color=(0, 0, 0)))
    register_platform(PlatformType("Eraser", color=(200, 50, 50)))

    register_platform(PlatformType("GrassB", sprite_path="Assets/Images/Platforms/Ground-Based Platforms/Base Grass Platform.png"))
    register_platform(PlatformType("GrassL", sprite_path="Assets/Images/Platforms/Ground-Based Platforms/Left Grass Platform.png"))
    register_platform(PlatformType("GrassT", sprite_path="Assets/Images/Platforms/Ground-Based Platforms/Top Grass Platform.png"))
    register_platform(PlatformType("GrassR", sprite_path="Assets/Images/Platforms/Ground-Based Platforms/Right Grass Platform.png"))

    register_platform(PlatformType("StoneB", color=(120, 120, 120)))
    register_platform(PlatformType("StoneL", color=(170, 170, 170)))

    register_platform(PlatformType("DirtB",  color=(139, 69, 19)))
    register_platform(PlatformType("DirtL",  color=(160, 90, 40)))

# --------------------
# Categories
# --------------------

PLATFORM_CATEGORIES = [
    ("Tools", ["Eraser"]),
    ("Grass", ["GrassB", "GrassL", "GrassT", "GrassR", "DirtB", "DirtL"]),
    ("Stone", ["StoneB", "StoneL"]),
]

CATEGORY_BUTTON_PADDING = 8
HOTBAR_SLOT_PADDING = 6

# --------------------
# Coordinate helpers
# --------------------

def world_to_screen(wx, wy, cam_x, cam_y):
    sx = (wx - cam_x) * TILE_SIZE + SCREEN_WIDTH // 2
    sy = (cam_y - wy) * TILE_SIZE + SCREEN_HEIGHT // 2
    return sx, sy

def screen_to_world(sx, sy, cam_x, cam_y):
    wx = (sx - SCREEN_WIDTH // 2) // TILE_SIZE + cam_x
    wy = cam_y - (sy - SCREEN_HEIGHT // 2) // TILE_SIZE
    return wx, wy

def get_visible_bounds(cam_x, cam_y):
    tiles_x = SCREEN_WIDTH // TILE_SIZE + 2
    tiles_y = SCREEN_HEIGHT // TILE_SIZE + 2
    min_x = cam_x - tiles_x // 2
    max_x = cam_x + tiles_x // 2
    min_y = cam_y - tiles_y // 2
    max_y = cam_y + tiles_y // 2
    return min_x, max_x, min_y, max_y

# --------------------
# Save / Load
# --------------------

def export_level(blocks):
    if not blocks:
        return []

    xs = [x for (x, _) in blocks.keys()]
    ys = [y for (_, y) in blocks.keys()]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    data = []
    for row_index in range(height):
        wy = min_y + row_index
        row = []
        for col_index in range(width):
            wx = min_x + col_index
            row.append(blocks.get((wx, wy), "Empty"))
        data.append(row)

    return data

def import_level(data):
    blocks = {}
    if not data:
        return blocks

    for row_index, row in enumerate(data):
        wy = row_index
        for col_index, pid in enumerate(row):
            wx = col_index
            if pid not in ("Empty", "Eraser"):
                blocks[(wx, wy)] = pid

    return blocks

def choose_save_file(initial_name):
    if not TK_AVAILABLE:
        return DEFAULT_SAVE_FILE
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.asksaveasfilename(
        title="Save level as",
        defaultextension=".json",
        initialfile=initial_name + ".json",
        filetypes=[("JSON files", "*.json")]
    )
    root.destroy()
    return filename or DEFAULT_SAVE_FILE

def choose_load_file():
    if not TK_AVAILABLE:
        return DEFAULT_SAVE_FILE
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        title="Open level",
        filetypes=[("JSON files", "*.json")]
    )
    root.destroy()
    return filename or DEFAULT_SAVE_FILE

def save_level(blocks, level_name, current_path):
    data = {"name": level_name, "tiles": export_level(blocks)}
    save_path = current_path or choose_save_file(level_name)
    with open(save_path, "w") as f:
        json.dump(data, f)
    return save_path

def load_level(current_path):
    load_path = current_path or choose_load_file()
    try:
        with open(load_path, "r") as f:
            data = json.load(f)
        return import_level(data["tiles"]), data["name"], load_path
    except:
        return {}, "Untitled", None

# --------------------
# UI drawing
# --------------------

def draw_category_bar(screen, font, selected_category_index):
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, SCREEN_WIDTH, CATEGORY_BAR_HEIGHT))
    x = CATEGORY_BUTTON_PADDING
    for i, (cat_name, _) in enumerate(PLATFORM_CATEGORIES):
        surf = font.render(cat_name, True, (255, 255, 255))
        w, h = surf.get_size()
        rect = pygame.Rect(x, 4, w + 16, CATEGORY_BAR_HEIGHT - 8)
        pygame.draw.rect(screen, (80, 80, 160) if i == selected_category_index else (60, 60, 60), rect)
        screen.blit(surf, (rect.x + 8, rect.y + (rect.height - h) // 2))
        x += rect.width + CATEGORY_BUTTON_PADDING

def get_category_at_pos(pos, font):
    x, y = pos
    if y > CATEGORY_BAR_HEIGHT:
        return None
    cx = CATEGORY_BUTTON_PADDING
    for i, (cat_name, _) in enumerate(PLATFORM_CATEGORIES):
        surf = font.render(cat_name, True, (255, 255, 255))
        w, _ = surf.get_size()
        rect = pygame.Rect(cx, 4, w + 16, CATEGORY_BAR_HEIGHT - 8)
        if rect.collidepoint(x, y):
            return i
        cx += rect.width + CATEGORY_BUTTON_PADDING
    return None

def draw_hotbar(screen, font, selected_platform_id, selected_category_index):
    y = SCREEN_HEIGHT - HOTBAR_HEIGHT
    pygame.draw.rect(screen, (30, 30, 30), (0, y, SCREEN_WIDTH, HOTBAR_HEIGHT))

    _, ids = PLATFORM_CATEGORIES[selected_category_index]
    slot_width = 64
    total_width = len(ids) * (slot_width + HOTBAR_SLOT_PADDING) + HOTBAR_SLOT_PADDING
    start_x = (SCREEN_WIDTH - total_width) // 2 + HOTBAR_SLOT_PADDING

    for idx, pid in enumerate(ids):
        rect = pygame.Rect(start_x + idx * (slot_width + HOTBAR_SLOT_PADDING), y + 8, slot_width, HOTBAR_HEIGHT - 16)
        pygame.draw.rect(screen, (200, 200, 80) if pid == selected_platform_id else (80, 80, 80), rect, border_radius=6)

        inner = rect.inflate(-16, -16)
        platform = get_platform(pid)

        if pid == "Eraser":
            pygame.draw.rect(screen, (50, 0, 0), inner)
            pygame.draw.line(screen, (255, 255, 255), inner.topleft, inner.bottomright, 3)
            pygame.draw.line(screen, (255, 255, 255), inner.topright, inner.bottomleft, 3)
        elif platform.color:
            pygame.draw.rect(screen, platform.color, inner)

        surf = font.render(pid, True, (255, 255, 255))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.bottom - 14))

def get_hotbar_platform_at_pos(pos, selected_category_index):
    x, y = pos
    if y < SCREEN_HEIGHT - HOTBAR_HEIGHT:
        return None

    _, ids = PLATFORM_CATEGORIES[selected_category_index]
    slot_width = 64
    total_width = len(ids) * (slot_width + HOTBAR_SLOT_PADDING) + HOTBAR_SLOT_PADDING
    start_x = (SCREEN_WIDTH - total_width) // 2 + HOTBAR_SLOT_PADDING

    for idx, pid in enumerate(ids):
        rect = pygame.Rect(start_x + idx * (slot_width + HOTBAR_SLOT_PADDING),
                           SCREEN_HEIGHT - HOTBAR_HEIGHT + 8,
                           slot_width, HOTBAR_HEIGHT - 16)
        if rect.collidepoint(x, y):
            return pid
    return None

def draw_level_name(screen, font, name, editing):
    text = f"Level: {name}" + (" (editing)" if editing else "")
    screen.blit(font.render(text, True, (255, 255, 255)), (10, CATEGORY_BAR_HEIGHT + 8))

# --------------------
# World border
# --------------------

def draw_world_axes(screen, cam_x_int, cam_y_int):
    min_x, max_x, min_y, max_y = get_visible_bounds(cam_x_int, cam_y_int)

    if min_x <= 0 <= max_x:
        sx, _ = world_to_screen(0, 0, cam_x_int, cam_y_int)
        pygame.draw.line(screen, WORLD_BORDER_COLOR, (sx, CATEGORY_BAR_HEIGHT), (sx, SCREEN_HEIGHT - HOTBAR_HEIGHT), 6)

    if min_y <= 0 <= max_y:
        _, sy = world_to_screen(0, 0, cam_x_int, cam_y_int)
        pygame.draw.line(screen, WORLD_BORDER_COLOR, (0, sy), (SCREEN_WIDTH, sy), 6)

    if min_x <= 0 <= max_x and min_y <= 0 <= max_y:
        sx, sy = world_to_screen(0, 0, cam_x_int, cam_y_int)
        pygame.draw.rect(screen, ORIGIN_HIGHLIGHT_COLOR, pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE), 4)

# --------------------
# Main
# --------------------

def main():
    pygame.init()
    register_all_platforms()
    for p in PLATFORMS.values():
        p.load_resources()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    blocks = {}
    cam_x, cam_y = 0, 0

    level_name = "Untitled"
    level_file_path = None

    selected_category = 1
    current_platform = PLATFORM_CATEGORIES[selected_category][1][0]
    editing_name = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if editing_name:
                    if event.key == pygame.K_RETURN:
                        editing_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        level_name = level_name[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        editing_name = False
                    else:
                        if event.unicode.isprintable():
                            level_name += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_F2:
                        editing_name = True
                    if event.key == pygame.K_e:
                        selected_category = 0
                        current_platform = "Eraser"
                    if event.key == pygame.K_s:
                        level_file_path = save_level(blocks, level_name, level_file_path)
                    if event.key == pygame.K_l:
                        blocks, level_name, level_file_path = load_level(level_file_path)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                cat = get_category_at_pos((mx, my), font)
                if cat is not None:
                    selected_category = cat
                    current_platform = PLATFORM_CATEGORIES[cat][1][0]
                    continue

                hot = get_hotbar_platform_at_pos((mx, my), selected_category)
                if hot:
                    current_platform = hot
                    continue

                if CATEGORY_BAR_HEIGHT < my < SCREEN_HEIGHT - HOTBAR_HEIGHT:
                    wx, wy = screen_to_world(mx, my, cam_x, cam_y)
                    wx, wy = int(wx), int(wy)

                    if wx < 0 or wy < 0:
                        continue

                    if event.button == 1:
                        if current_platform in ("Eraser", "Empty"):
                            blocks.pop((wx, wy), None)
                        else:
                            blocks[(wx, wy)] = current_platform

                    elif event.button == 3:
                        blocks.pop((wx, wy), None)

        keys = pygame.key.get_pressed()
        if not editing_name:
            speed = 10 * dt
            if keys[pygame.K_LEFT]:
                cam_x -= speed
            if keys[pygame.K_RIGHT]:
                cam_x += speed
            if keys[pygame.K_UP]:
                cam_y += speed
            if keys[pygame.K_DOWN]:
                cam_y -= speed

        cam_x = max(cam_x, -1)
        cam_y = max(cam_y, -1)

        cam_x_int = int(round(cam_x))
        cam_y_int = int(round(cam_y))

        screen.fill((0, 0, 0))

        min_x, max_x, min_y, max_y = get_visible_bounds(cam_x_int, cam_y_int)
        for wx in range(max(min_x, 0), max_x + 1):
            for wy in range(max(min_y, 0), max_y + 1):
                sx, sy = world_to_screen(wx, wy, cam_x_int, cam_y_int)
                rect = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)

                if rect.bottom < CATEGORY_BAR_HEIGHT or rect.top > SCREEN_HEIGHT - HOTBAR_HEIGHT:
                    continue

                pid = blocks.get((wx, wy), "Empty")
                plat = get_platform(pid)

                if plat.sprite:
                    screen.blit(plat.sprite, rect)
                else:
                    if pid not in ("Empty", "Eraser"):
                        pygame.draw.rect(screen, plat.color, rect)
                    else:
                        pygame.draw.rect(screen, (40, 40, 40), rect, 1)

        draw_world_axes(screen, cam_x_int, cam_y_int)
        draw_category_bar(screen, font, selected_category)
        draw_hotbar(screen, font, current_platform, selected_category)
        draw_level_name(screen, font, level_name, editing_name)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()