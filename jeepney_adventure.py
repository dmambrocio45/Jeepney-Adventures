"""
JEEPNEY ADVENTURE
A 2D side-scrolling Filipino-themed driving + pickup game built with Pygame.

Screens:
  - Main Menu   (PLAY / GARAGE / SETTINGS / EXIT)
  - Garage      (upgrade SPEED / FUEL / CAPACITY / BRAKE)
  - Mission Brief (shows the route + objective before a run)
  - Gameplay    (side-scrolling driving, passenger pickups, HUD)
  - Mission Complete / Mission Failed / Game Over

Controls:
  RIGHT / D  - drive forward
  LEFT  / A  - reverse / reposition
  UP    / W  - GAS (extra acceleration)
  DOWN  / S  - BRAKE
  SPACE / E  - Pick up passenger (when stopped at a stop)
  On-screen buttons work with the mouse too.

Run with:  python jeepney_adventure.py
Requires:  pip install pygame
"""

import math
import random
import sys

import pygame

# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------
pygame.init()

WIDTH, HEIGHT = 1100, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeepney Adventure")
clock = pygame.time.Clock()
FPS = 60

FONT_TITLE = pygame.font.Font(None, 64)
FONT_TITLE.set_bold(True)
FONT_XL = pygame.font.Font(None, 46)
FONT_XL.set_bold(True)
FONT_LG = pygame.font.Font(None, 34)
FONT_LG.set_bold(True)
FONT_MD = pygame.font.Font(None, 26)
FONT_MD.set_bold(True)
FONT_SM = pygame.font.Font(None, 20)

# Colors
SKY = (135, 206, 240)
SKY_EVENING = (255, 200, 140)
ROAD = (80, 80, 88)
ROAD_LINE = (230, 220, 90)
SIDEWALK = (170, 170, 165)
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
RED = (205, 40, 40)
DARK_RED = (150, 20, 20)
BLUE = (35, 60, 150)
YELLOW = (245, 195, 30)
GREEN = (60, 165, 75)
DARK_GREEN = (35, 120, 55)
GRAY = (90, 90, 95)
DARK_GRAY = (55, 55, 60)
BROWN = (120, 80, 45)
CREAM = (245, 240, 225)


def render_outline(text, font, color, outline_color, width=2):
    base = font.render(text, True, color)
    w, h = base.get_size()
    surf = pygame.Surface((w + width * 2, h + width * 2), pygame.SRCALPHA)
    outline = font.render(text, True, outline_color)
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx or dy:
                surf.blit(outline, (dx + width, dy + width))
    surf.blit(base, (width, width))
    return surf


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------
# Drawing helpers (all procedural vector art - no image assets needed)
# --------------------------------------------------------------------------

def draw_cloud(surface, x, y):
    color = (255, 255, 255)
    pygame.draw.ellipse(surface, color, (x, y, 70, 34))
    pygame.draw.ellipse(surface, color, (x + 25, y - 14, 55, 40))
    pygame.draw.ellipse(surface, color, (x + 45, y, 50, 30))


def draw_sun(surface, x, y, r=28):
    pygame.draw.circle(surface, (255, 210, 60), (x, y), r)
    pygame.draw.circle(surface, (255, 235, 140), (x, y), r - 6)


def draw_pole(surface, x, y_ground):
    pygame.draw.rect(surface, (70, 60, 50), (x, y_ground - 130, 6, 130))
    pygame.draw.line(surface, (70, 60, 50), (x - 25, y_ground - 120), (x + 31, y_ground - 120), 3)


def draw_palm_tree(surface, x, y_ground):
    pygame.draw.rect(surface, (110, 80, 45), (x, y_ground - 100, 10, 100))
    for angle in (-60, -30, 0, 30, 60):
        rad = math.radians(angle - 90)
        ex = x + 5 + math.cos(rad) * 45
        ey = y_ground - 100 + math.sin(rad) * 30
        pygame.draw.line(surface, DARK_GREEN, (x + 5, y_ground - 100), (ex, ey), 8)


def draw_building(surface, x, y_ground, color):
    h = 130
    w = 110
    top = y_ground - h
    pygame.draw.rect(surface, color, (x, top, w, h))
    pygame.draw.rect(surface, BLACK, (x, top, w, h), 2)
    for row in range(3):
        for col in range(3):
            wx = x + 12 + col * 32
            wy = top + 15 + row * 35
            pygame.draw.rect(surface, (170, 210, 235), (wx, wy, 20, 22))
            pygame.draw.rect(surface, BLACK, (wx, wy, 20, 22), 1)


def draw_store(surface, x, y_ground):
    h = 95
    w = 120
    top = y_ground - h
    pygame.draw.rect(surface, CREAM, (x, top + 15, w, h - 15))
    pygame.draw.rect(surface, BLACK, (x, top + 15, w, h - 15), 2)
    # awning
    stripes = 6
    stripe_w = w // stripes
    for i in range(stripes):
        color = RED if i % 2 == 0 else WHITE
        pygame.draw.rect(surface, color, (x + i * stripe_w, top - 5, stripe_w, 18))
    pygame.draw.rect(surface, BLACK, (x, top - 5, w, 18), 2)
    label = FONT_SM.render("SARI-SARI", True, DARK_RED)
    surface.blit(label, (x + w // 2 - label.get_width() // 2, top + 25))
    pygame.draw.rect(surface, (90, 60, 30), (x + w // 2 - 15, top + h - 45, 30, 45))


def draw_person(surface, x, y_ground, color):
    pygame.draw.circle(surface, (255, 210, 170), (x, y_ground - 46), 8)
    pygame.draw.rect(surface, color, (x - 7, y_ground - 38, 14, 24), border_radius=3)
    pygame.draw.line(surface, (60, 60, 60), (x - 4, y_ground - 14), (x - 6, y_ground), 4)
    pygame.draw.line(surface, (60, 60, 60), (x + 4, y_ground - 14), (x + 6, y_ground), 4)


def draw_heart(surface, cx, cy, size, color):
    r = size // 2
    pygame.draw.circle(surface, color, (cx - r // 2, cy - r // 4), r // 2)
    pygame.draw.circle(surface, color, (cx + r // 2, cy - r // 4), r // 2)
    points = [(cx - r, cy - r // 5), (cx, cy + r), (cx + r, cy - r // 5)]
    pygame.draw.polygon(surface, color, points)


def star_points(cx, cy, r_out, r_in, rotation=-90):
    pts = []
    for i in range(10):
        ang = math.radians(rotation + i * 36)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def draw_star(surface, cx, cy, r_out, color, outline=BLACK):
    pts = star_points(cx, cy, r_out, r_out * 0.45)
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.polygon(surface, outline, pts, 2)


def draw_coin(surface, cx, cy, r, color=YELLOW):
    pygame.draw.circle(surface, color, (cx, cy), r)
    pygame.draw.circle(surface, BLACK, (cx, cy), r, 2)
    s = FONT_SM.render("$", True, DARK_RED)
    surface.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))


def draw_jeepney(surface, x, y, scale=1.0, onboard=0, capacity=1, bob=0):
    w, h = int(230 * scale), int(95 * scale)
    top = y - h + bob

    pygame.draw.rect(surface, RED, (x, top, w, h), border_radius=14)
    pygame.draw.rect(surface, BLUE, (x, top + h * 0.55, w, h * 0.45), border_radius=10)
    pygame.draw.rect(surface, YELLOW, (x + w * 0.05, top - 14, w * 0.9, 18), border_radius=6)
    pygame.draw.rect(surface, BLACK, (x, top - 14, w, h + 14), 2, border_radius=14)

    # windshield + side windows with passengers
    n_windows = 4
    win_w = (w - 30) / n_windows - 8
    for i in range(n_windows):
        wx = x + 15 + i * ((w - 30) / n_windows)
        win_rect = pygame.Rect(int(wx), int(top + 10), int(win_w), int(h * 0.42))
        pygame.draw.rect(surface, (200, 232, 255), win_rect, border_radius=4)
        pygame.draw.rect(surface, BLACK, win_rect, 2, border_radius=4)
        if i < onboard:
            pygame.draw.circle(surface, (90, 60, 40), win_rect.center, 6)

    # stripes
    pygame.draw.rect(surface, YELLOW, (x, top + h * 0.5, w, 6))
    for i in range(3):
        dx = x + 20 + i * (w - 40) / 2
        pygame.draw.polygon(
            surface, (255, 255, 255),
            [(dx, top + h - 8), (dx + 14, top + h - 8), (dx + 7, top + h - 20)],
        )

    # wheels
    wheel_y = top + h
    for wx in (x + 42 * scale, x + w - 42 * scale):
        pygame.draw.circle(surface, BLACK, (int(wx), int(wheel_y)), int(19 * scale))
        pygame.draw.circle(surface, (150, 150, 150), (int(wx), int(wheel_y)), int(8 * scale))

    return pygame.Rect(x, top - 14, w, h + 14)


def draw_stop_sign(surface, x, y_ground, picked, waiting=2):
    pole_x = x
    pygame.draw.rect(surface, (90, 90, 90), (pole_x, y_ground - 90, 6, 90))
    color = (140, 140, 140) if picked else YELLOW
    pygame.draw.circle(surface, color, (pole_x + 3, y_ground - 95), 22)
    pygame.draw.circle(surface, BLACK, (pole_x + 3, y_ground - 95), 22, 2)
    label = FONT_SM.render("PARA", True, BLACK)
    surface.blit(label, (pole_x + 3 - label.get_width() // 2, y_ground - 102))
    if not picked:
        for i in range(waiting):
            draw_person(surface, x - 20 - i * 18, y_ground, (60, 120, 190) if i % 2 else (190, 90, 130))


def draw_pothole(surface, x, y_ground):
    pygame.draw.ellipse(surface, (35, 30, 25), (x - 22, y_ground - 8, 44, 16))
    pygame.draw.ellipse(surface, (15, 12, 10), (x - 16, y_ground - 6, 32, 10))


def draw_stat_bar(surface, x, y, level, max_level=5, seg_w=32, seg_h=22, gap=5):
    for i in range(max_level):
        rect = pygame.Rect(x + i * (seg_w + gap), y, seg_w, seg_h)
        color = YELLOW if i < level else DARK_GRAY
        pygame.draw.rect(surface, color, rect, border_radius=4)
        pygame.draw.rect(surface, BLACK, rect, 2, border_radius=4)


def draw_tiled(surface, draw_fn, spacing, parallax, y, world_offset):
    off = (world_offset * parallax) % spacing
    first_n = int(-((world_offset * parallax) // spacing)) - 1
    x = -off - spacing
    n = first_n
    while x < WIDTH + spacing:
        draw_fn(surface, int(x), y, n)
        x += spacing
        n += 1


class Button:
    def __init__(self, rect, text, base_color, hover_color, text_color=WHITE, font=None, radius=12):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font or FONT_MD
        self.radius = radius

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = self.hover_color if hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, BLACK, self.rect, 3, border_radius=self.radius)
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# --------------------------------------------------------------------------
# Game state
# --------------------------------------------------------------------------

def new_game_state():
    return {
        "money": 250,
        "stars": 12,
        "hearts": 3,
        "max_hearts": 3,
        "stats": {"speed": 2, "fuel": 2, "capacity": 2, "brake": 2},
        "max_level": 5,
        "upgrade_cost": 100,
    }


def new_mission():
    return {"target": 5, "picked_up": 0, "time_left": 150.0, "route": ["BARANGAY", "SCHOOL", "MARKET"]}


def new_world():
    stops = []
    wx = 500
    names = ["BARANGAY", "SCHOOL", "MARKET", "PLAZA", "CHURCH", "TERMINAL"]
    for i in range(6):
        stops.append({"world_x": wx, "name": names[i], "picked": False, "waiting": random.randint(1, 3)})
        wx += random.randint(650, 950)
    potholes = []
    px = 900
    for _ in range(7):
        potholes.append({"world_x": px, "hit": False})
        px += random.randint(500, 900)
    return stops, potholes


def new_runtime():
    stops, potholes = new_world()
    return {
        "world_offset": 0.0,
        "speed": 0.0,
        "fuel": 100.0,
        "onboard": 0,
        "stops": stops,
        "potholes": potholes,
        "message": "",
        "message_timer": 0.0,
        "gas_held": False,
        "brake_held": False,
        "left_held": False,
        "right_held": False,
    }


game = new_game_state()
mission = new_mission()
rt = new_runtime()

JEEP_SCREEN_X = 160
GROUND_Y = 520


# --------------------------------------------------------------------------
# Background scenery (shared by gameplay + mission brief)
# --------------------------------------------------------------------------

def scenery_item(surface, x, y, n):
    kind = n % 4
    if kind == 0:
        draw_building(surface, x, y, (230, 220, 195))
    elif kind == 1:
        draw_store(surface, x, y)
    elif kind == 2:
        draw_building(surface, x, y, (205, 222, 235))
    else:
        draw_palm_tree(surface, x, y)


def draw_sky_and_road(surface, world_offset):
    surface.fill(SKY)
    draw_tiled(surface, lambda s, x, y, n: draw_cloud(s, x, y + (n % 3) * 12), 340, 0.15, 60, world_offset)
    draw_tiled(surface, lambda s, x, y, n: draw_pole(s, x, y), 230, 0.55, GROUND_Y, world_offset)
    draw_tiled(surface, scenery_item, 260, 0.5, GROUND_Y, world_offset)
    pygame.draw.rect(surface, SIDEWALK, (0, GROUND_Y, WIDTH, 14))
    pygame.draw.rect(surface, ROAD, (0, GROUND_Y + 14, WIDTH, HEIGHT - GROUND_Y - 14))
    draw_tiled(
        surface,
        lambda s, x, y, n: pygame.draw.rect(s, ROAD_LINE, (x, y, 45, 6)),
        90, 1.0, GROUND_Y + 55, world_offset,
    )


# --------------------------------------------------------------------------
# Gameplay update
# --------------------------------------------------------------------------

def update_gameplay(dt, keys):
    stats = game["stats"]
    max_speed = 3.2 + stats["speed"] * 1.5
    accel = 0.10 + stats["speed"] * 0.025
    decel = 0.22 + stats["brake"] * 0.12
    friction = 0.06
    capacity_max = 2 + stats["capacity"]

    if rt["fuel"] <= 0:
        max_speed = min(max_speed, 1.3)

    gas = keys[pygame.K_UP] or keys[pygame.K_w] or rt["gas_held"]
    brake = keys[pygame.K_DOWN] or keys[pygame.K_s] or rt["brake_held"]
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d] or rt["right_held"]
    left = keys[pygame.K_LEFT] or keys[pygame.K_a] or rt["left_held"]

    if brake:
        if rt["speed"] > 0:
            rt["speed"] = max(0.0, rt["speed"] - decel)
        else:
            rt["speed"] = min(0.0, rt["speed"] + decel)
    elif gas:
        rt["speed"] = min(max_speed, rt["speed"] + accel * 1.6)
    elif right:
        rt["speed"] = min(max_speed, rt["speed"] + accel)
    elif left:
        rt["speed"] = max(-max_speed * 0.4, rt["speed"] - accel * 0.9)
    else:
        if rt["speed"] > 0:
            rt["speed"] = max(0.0, rt["speed"] - friction)
        elif rt["speed"] < 0:
            rt["speed"] = min(0.0, rt["speed"] + friction)

    if rt["speed"] > 0 and (gas or right):
        rt["fuel"] = max(0.0, rt["fuel"] - 0.05)

    rt["world_offset"] = max(0.0, rt["world_offset"] + rt["speed"])

    if mission["picked_up"] < mission["target"]:
        mission["time_left"] = max(0.0, mission["time_left"] - dt)

    jeep_world_x = rt["world_offset"] + JEEP_SCREEN_X

    for stop in rt["stops"]:
        if not stop["picked"] and abs(jeep_world_x - stop["world_x"]) < 55:
            stop["_near"] = True
        else:
            stop["_near"] = False

    for hole in rt["potholes"]:
        if not hole["hit"] and abs(jeep_world_x - hole["world_x"]) < 26:
            hole["hit"] = True
            game["hearts"] = max(0, game["hearts"] - 1)
            rt["message"] = "Ouch! Hit a pothole! -1 heart"
            rt["message_timer"] = 2.0

    if rt["message_timer"] > 0:
        rt["message_timer"] -= dt
        if rt["message_timer"] <= 0:
            rt["message"] = ""


def try_pickup():
    stats = game["stats"]
    capacity_max = 2 + stats["capacity"]
    if mission["picked_up"] >= mission["target"]:
        return
    for stop in rt["stops"]:
        if stop.get("_near") and not stop["picked"]:
            if rt["onboard"] >= capacity_max:
                rt["message"] = "Jeepney is full! Drop off before picking up more."
                rt["message_timer"] = 2.0
                return
            stop["picked"] = True
            rt["onboard"] = min(capacity_max, rt["onboard"] + 1)
            mission["picked_up"] += 1
            game["money"] += 30
            game["stars"] += 1
            rt["fuel"] = min(100.0, rt["fuel"] + 20)
            rt["message"] = f"Picked up passenger at {stop['name']}! +P30"
            rt["message_timer"] = 2.0
            return


# --------------------------------------------------------------------------
# Draw screens
# --------------------------------------------------------------------------

def draw_hud(surface):
    draw_coin(surface, 34, 32, 18)
    surface.blit(render_outline(str(game["money"]), FONT_LG, WHITE, BLACK, 2), (56, 16))

    draw_star(surface, 190, 32, 16, YELLOW)
    surface.blit(render_outline(str(game["stars"]), FONT_LG, WHITE, BLACK, 2), (212, 16))

    for i in range(game["max_hearts"]):
        color = RED if i < game["hearts"] else (90, 90, 90)
        draw_heart(surface, WIDTH - 30 - i * 40, 30, 26, color)

    bar_w = 160
    fx, fy = WIDTH // 2 - bar_w // 2, 14
    pygame.draw.rect(surface, DARK_GRAY, (fx, fy, bar_w, 14), border_radius=6)
    fw = int(bar_w * rt["fuel"] / 100)
    fuel_color = GREEN if rt["fuel"] > 30 else RED
    pygame.draw.rect(surface, fuel_color, (fx, fy, fw, 14), border_radius=6)
    pygame.draw.rect(surface, BLACK, (fx, fy, bar_w, 14), 2, border_radius=6)
    surface.blit(FONT_SM.render("FUEL", True, BLACK), (fx, fy + 16))

    mins = int(mission["time_left"]) // 60
    secs = int(mission["time_left"]) % 60
    timer_txt = f"{mins:02d}:{secs:02d}"
    surface.blit(render_outline(timer_txt, FONT_LG, WHITE, BLACK, 2), (WIDTH // 2 - 40, 34))

    mtxt = FONT_MD.render(f"Passengers: {mission['picked_up']}/{mission['target']}", True, WHITE)
    shadow = FONT_MD.render(f"Passengers: {mission['picked_up']}/{mission['target']}", True, BLACK)
    surface.blit(shadow, (22, 62))
    surface.blit(mtxt, (20, 60))

    if rt["message"]:
        msg = FONT_MD.render(rt["message"], True, BLACK)
        box = pygame.Surface((msg.get_width() + 24, msg.get_height() + 14), pygame.SRCALPHA)
        box.fill((255, 255, 255, 220))
        surface.blit(box, (WIDTH // 2 - box.get_width() // 2, 90))
        surface.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 97))


def draw_gameplay(surface):
    draw_sky_and_road(surface, rt["world_offset"])
    jeep_world_x = rt["world_offset"] + JEEP_SCREEN_X

    for hole in rt["potholes"]:
        sx = hole["world_x"] - rt["world_offset"] + JEEP_SCREEN_X
        if -40 < sx < WIDTH + 40 and not hole["hit"]:
            draw_pothole(surface, int(sx), GROUND_Y + 34)

    for stop in rt["stops"]:
        sx = stop["world_x"] - rt["world_offset"] + JEEP_SCREEN_X
        if -60 < sx < WIDTH + 60:
            draw_stop_sign(surface, int(sx), GROUND_Y, stop["picked"], stop["waiting"])

    stats = game["stats"]
    capacity_max = 2 + stats["capacity"]
    bob = int(math.sin(pygame.time.get_ticks() * 0.01) * 2) if abs(rt["speed"]) > 0.3 else 0
    draw_jeepney(surface, JEEP_SCREEN_X, GROUND_Y + 14, 1.0, rt["onboard"], capacity_max, bob)

    draw_hud(surface)

    near_any = any(s.get("_near") and not s["picked"] for s in rt["stops"])
    pickup_color = GREEN if near_any else (110, 130, 110)
    btn_pickup.base_color = pickup_color
    btn_pickup.hover_color = (80, 190, 100) if near_any else (110, 130, 110)
    btn_pickup.draw(surface)
    btn_left.draw(surface)
    btn_right.draw(surface)
    btn_brake.draw(surface)
    btn_gas.draw(surface)


def draw_menu(surface):
    draw_sky_and_road(surface, 0)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 90))
    surface.blit(overlay, (0, 0))

    draw_sun(surface, 90, 90)
    draw_sun(surface, WIDTH - 90, 90)

    title1 = render_outline("JEEPNEY", FONT_TITLE, RED, BLACK, 3)
    title2 = render_outline("ADVENTURE", FONT_TITLE, YELLOW, BLACK, 3)
    surface.blit(title1, (WIDTH // 2 - title1.get_width() // 2, 60))
    surface.blit(title2, (WIDTH // 2 - title2.get_width() // 2, 125))

    for b in (btn_play, btn_garage, btn_settings, btn_exit):
        b.draw(surface)


def draw_garage(surface):
    surface.fill((45, 40, 42))
    for i in range(6):
        pygame.draw.line(surface, (60, 55, 58), (i * (WIDTH // 6), 0), (i * (WIDTH // 6), HEIGHT), 2)

    title = render_outline("GARAGE", FONT_XL, YELLOW, BLACK, 2)
    surface.blit(title, (60, 30))

    draw_jeepney(surface, 60, 330, 1.3, 0, 5)

    stats = game["stats"]
    labels = [("SPEED", "speed"), ("FUEL", "fuel"), ("CAPACITY", "capacity"), ("BRAKE", "brake")]
    y0 = 110
    for i, (label, key) in enumerate(labels):
        y = y0 + i * 70
        txt = FONT_MD.render(label, True, WHITE)
        surface.blit(txt, (560, y))
        draw_stat_bar(surface, 700, y - 4, stats[key], game["max_level"])
        upgrade_buttons[key].rect.topleft = (700 + 5 * 37 + 15, y - 6)
        upgrade_buttons[key].draw(surface)

    money_txt = render_outline(f"P {game['money']}", FONT_LG, WHITE, BLACK, 2)
    surface.blit(money_txt, (WIDTH - money_txt.get_width() - 40, 40))

    btn_back_garage.draw(surface)

    if rt["message"] and rt["message_timer"] > 0:
        msg = FONT_MD.render(rt["message"], True, YELLOW)
        surface.blit(msg, (560, y0 + 4 * 70 + 10))


def draw_mission_brief(surface):
    draw_sky_and_road(surface, 0)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 20, 150))
    surface.blit(overlay, (0, 0))

    panel = pygame.Rect(90, 70, WIDTH - 180, HEIGHT - 170)
    pygame.draw.rect(surface, (250, 248, 240), panel, border_radius=16)
    pygame.draw.rect(surface, BLACK, panel, 3, border_radius=16)

    mtxt = FONT_XL.render("MISSION: PICK UP 5 PASSENGERS", True, DARK_RED)
    surface.blit(mtxt, (panel.x + 30, panel.y + 25))

    route = ["BARANGAY", "SCHOOL", "MARKET"]
    rx = panel.x + 60
    ry = panel.y + 110
    for i, name in enumerate(route):
        pygame.draw.circle(surface, YELLOW, (rx, ry), 26)
        pygame.draw.circle(surface, BLACK, (rx, ry), 26, 2)
        lbl = FONT_SM.render(name[:3], True, BLACK)
        surface.blit(lbl, (rx - lbl.get_width() // 2, ry - 8))
        name_txt = FONT_SM.render(name, True, BLACK)
        surface.blit(name_txt, (rx - name_txt.get_width() // 2, ry + 32))
        if i < len(route) - 1:
            pygame.draw.line(surface, BLACK, (rx + 30, ry), (rx + 170, ry), 3)
        rx += 200

    info_y = panel.y + 190
    surface.blit(FONT_MD.render(f"Passengers needed: {mission['target']}", True, BLACK), (panel.x + 30, info_y))
    surface.blit(FONT_MD.render(f"Money: P {game['money']}", True, BLACK), (panel.x + 30, info_y + 35))
    surface.blit(FONT_MD.render("Time limit: 02:30", True, BLACK), (panel.x + 30, info_y + 70))

    tip = FONT_SM.render(
        "Tip: drive up to a PARA stop, stop, then press SPACE or PICK UP to board a passenger.",
        True, (80, 80, 80),
    )
    surface.blit(tip, (panel.x + 30, info_y + 115))

    btn_start_mission.draw(surface)
    btn_back_from_brief.draw(surface)


def draw_end_screen(surface, title, subtitle, color):
    surface.fill((25, 25, 30))
    t = render_outline(title, FONT_TITLE, color, BLACK, 3)
    surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 180))
    s = FONT_LG.render(subtitle, True, WHITE)
    surface.blit(s, (WIDTH // 2 - s.get_width() // 2, 260))
    stats_txt = FONT_MD.render(
        f"Passengers picked up: {mission['picked_up']}/{mission['target']}   |   Money: P {game['money']}   |   Stars: {game['stars']}",
        True, (220, 220, 220),
    )
    surface.blit(stats_txt, (WIDTH // 2 - stats_txt.get_width() // 2, 320))
    btn_end_continue.draw(surface)


# --------------------------------------------------------------------------
# Buttons
# --------------------------------------------------------------------------

btn_play = Button((WIDTH // 2 - 130, 260, 260, 55), "PLAY", GREEN, (90, 200, 110), font=FONT_LG)
btn_garage = Button((WIDTH // 2 - 130, 325, 260, 55), "GARAGE", BLUE, (70, 100, 190), font=FONT_LG)
btn_settings = Button((WIDTH // 2 - 130, 390, 260, 55), "SETTINGS", YELLOW, (255, 215, 80), BLACK, font=FONT_LG)
btn_exit = Button((WIDTH // 2 - 130, 455, 260, 55), "EXIT", RED, (230, 70, 70), font=FONT_LG)

btn_back_garage = Button((40, HEIGHT - 80, 160, 50), "BACK", GRAY, (130, 130, 135), font=FONT_MD)

upgrade_buttons = {
    key: Button((0, 0, 130, 34), f"UPGRADE P{game['upgrade_cost']}", GREEN, (90, 200, 110), font=FONT_SM)
    for key in ("speed", "fuel", "capacity", "brake")
}

btn_start_mission = Button((WIDTH // 2 - 260, HEIGHT - 130, 220, 55), "START", GREEN, (90, 200, 110), font=FONT_LG)
btn_back_from_brief = Button((WIDTH // 2 + 40, HEIGHT - 130, 220, 55), "BACK", GRAY, (130, 130, 135), font=FONT_LG)

btn_left = Button((30, HEIGHT - 90, 70, 55), "<-", (200, 200, 200), (230, 230, 230), BLACK, font=FONT_LG)
btn_right = Button((110, HEIGHT - 90, 70, 55), "->", (200, 200, 200), (230, 230, 230), BLACK, font=FONT_LG)
btn_pickup = Button((WIDTH // 2 - 100, HEIGHT - 90, 200, 55), "PICK UP", GREEN, (90, 200, 110), font=FONT_MD)
btn_brake = Button((WIDTH - 220, HEIGHT - 90, 90, 55), "BRAKE", RED, (230, 80, 80), font=FONT_MD)
btn_gas = Button((WIDTH - 120, HEIGHT - 90, 90, 55), "GAS", GREEN, (90, 200, 110), font=FONT_MD)

btn_end_continue = Button((WIDTH // 2 - 120, 400, 240, 55), "BACK TO MENU", BLUE, (70, 100, 190), font=FONT_LG)


# --------------------------------------------------------------------------
# Main loop
# --------------------------------------------------------------------------

def main():
    global mission, rt

    state = "MENU"
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "MENU":
                if btn_play.clicked(event):
                    state = "MISSION_BRIEF"
                elif btn_garage.clicked(event):
                    state = "GARAGE"
                elif btn_exit.clicked(event):
                    running = False
                elif btn_settings.clicked(event):
                    pass

            elif state == "GARAGE":
                if btn_back_garage.clicked(event):
                    state = "MENU"
                for key, b in upgrade_buttons.items():
                    if b.clicked(event):
                        level = game["stats"][key]
                        cost = game["upgrade_cost"]
                        if level >= game["max_level"]:
                            rt["message"] = f"{key.upper()} is already maxed!"
                            rt["message_timer"] = 2.0
                        elif game["money"] < cost:
                            rt["message"] = "Not enough money!"
                            rt["message_timer"] = 2.0
                        else:
                            game["money"] -= cost
                            game["stats"][key] += 1
                            rt["message"] = f"{key.upper()} upgraded!"
                            rt["message_timer"] = 2.0

            elif state == "MISSION_BRIEF":
                if btn_start_mission.clicked(event):
                    mission = new_mission()
                    rt = new_runtime()
                    game["hearts"] = game["max_hearts"]
                    state = "PLAY"
                elif btn_back_from_brief.clicked(event):
                    state = "MENU"

            elif state == "PLAY":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_e):
                    try_pickup()
                if btn_pickup.clicked(event):
                    try_pickup()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_left.rect.collidepoint(event.pos):
                        rt["left_held"] = True
                    if btn_right.rect.collidepoint(event.pos):
                        rt["right_held"] = True
                    if btn_brake.rect.collidepoint(event.pos):
                        rt["brake_held"] = True
                    if btn_gas.rect.collidepoint(event.pos):
                        rt["gas_held"] = True
                if event.type == pygame.MOUSEBUTTONUP:
                    rt["left_held"] = False
                    rt["right_held"] = False
                    rt["brake_held"] = False
                    rt["gas_held"] = False

            elif state in ("MISSION_COMPLETE", "MISSION_FAILED", "GAMEOVER"):
                if btn_end_continue.clicked(event):
                    state = "MENU"

        # ---- updates ----
        if state == "PLAY":
            update_gameplay(dt, keys)
            if game["hearts"] <= 0:
                state = "GAMEOVER"
            elif mission["picked_up"] >= mission["target"]:
                game["money"] += 100
                game["stars"] += 5
                state = "MISSION_COMPLETE"
            elif mission["time_left"] <= 0:
                state = "MISSION_FAILED"

        # ---- draw ----
        if state == "MENU":
            draw_menu(screen)
        elif state == "GARAGE":
            draw_garage(screen)
        elif state == "MISSION_BRIEF":
            draw_mission_brief(screen)
        elif state == "PLAY":
            draw_gameplay(screen)
        elif state == "MISSION_COMPLETE":
            draw_end_screen(screen, "MISSION COMPLETE!", "Great driving, Pasahero Hero!", GREEN)
        elif state == "MISSION_FAILED":
            draw_end_screen(screen, "TIME'S UP", "Try again to finish the route.", YELLOW)
        elif state == "GAMEOVER":
            draw_end_screen(screen, "GAME OVER", "Your jeepney took too much damage.", RED)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
