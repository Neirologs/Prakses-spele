import math
import random
from typing import Optional

# ----- Size of one grid cell -----
CELL = 50
# ----- Seconds between new rows -----
SPAWN_TIME = 8

# ----- All level layouts -----
LEVELS = [
    [
        "1S1..11.1S1..1111111",
        "11S11111S111.11..111",
        "...1.1.1.1.111.11.11",
        "111..1111S1111111111",
        "111....S.....1111111",
        "111.S111111....11111",
        "11111111111111111111",
    ],
    [
        "2S112..2S222S......2",
        "...111222S...2111SS2",
        "222212121..121S21S22",
        "21..1S12...2S2.21122",
        "11111111111111111112",
        "222.2222.1..11.2...2",
        ".B....B....B.......2",
        "....2....2222.211112",
    ],
    [
        "3333S3S....123233SS3",
        "3S33S22..333.2333S.3",
        "...33S..3S3..22.33.3",
        "B..333.S..333.22.133",
        "..3..2222.333.333333",
        "B..3333333333333.B.3",
        "..33S.33.2.22.1....3",
        ".B...333.33.33..B..3",
        "...333.222.3..3....3",
    ],
]

# ----- Stats for each cube type -----
CUBE_TYPES = {
    "1": {"color": (175, 35, 35), "hp": 1, "speed": 1000, "size": 1},
    "2": {"color": (0, 100, 0), "hp": 2, "speed": 8, "size": 1},
    "3": {"color": (10, 190, 32), "hp": 3, "speed": 8, "size": 1},
    "S": {"color": (220, 180, 0), "hp": 5, "speed": 8, "size": 1},
    "B": {"color": (70, 0, 100), "hp": 20, "speed": 10, "size": 2},
}


# ----- Simple rectangle without pygame -----
class Rect:
    """Minimal replacement for pygame.Rect so this package needs no pygame."""

    # ----- Create rectangle from numbers -----
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.x, self.y, self.w, self.h = x, y, w, h

    # ----- Edges and center of rectangle -----
    left = property(lambda s: s.x)
    right = property(lambda s: s.x + s.w)
    top = property(lambda s: s.y)
    bottom = property(lambda s: s.y + s.h)
    centerx = property(lambda s: s.x + s.w / 2)
    centery = property(lambda s: s.y + s.h / 2)

    # ----- Check if two rectangles overlap -----
    def colliderect(self, o: "Rect") -> bool:
        return (self.x < o.right and o.x < self.right
                and self.y < o.bottom and o.y < self.bottom)


# ----- Check if line crosses rectangle -----
def line_hits_rect(a: tuple, b: tuple, r: Rect) -> bool:
    """True if the segment a->b crosses rect r (replaces Rect.clipline)."""
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    checks = (
        (-dx, a[0] - r.left),
        (dx, r.right - a[0]),
        (-dy, a[1] - r.top),
        (dy, r.bottom - a[1]),
    )
    # ----- Test line against each edge -----
    for p, q in checks:
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                if t > t1:
                    return False
                t0 = max(t0, t)
            else:
                if t < t0:
                    return False
                t1 = min(t1, t)
    return True


# ----- Add one row of cubes -----
def spawn_row(row_string: str, cubes: list, row_index: int) -> None:
    # ----- Go through each row character -----
    for col, char in enumerate(row_string):
        if char in CUBE_TYPES:
            cube_type = CUBE_TYPES[char]
            size = CELL * cube_type["size"]
            cubes.append({
                "rect": Rect(col * CELL, CELL - size, size, size),
                "type": char,
                "hp": float(cube_type["hp"]),
                "speed": cube_type["speed"],
                "row": row_index,
            })


# ----- Load a level's first row -----
def load_level(index: int) -> tuple:
    level = LEVELS[index]
    cubes = []
    spawn_row(level[0], cubes, 0)
    return level, cubes


# ----- Turn seconds into mm:ss.xx -----
def format_time(t: float) -> str:
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


# ----- Build a new friendly unit -----
def make_unit(unit_type: str, x: int) -> dict:
    size = CELL * 2 if unit_type == "tank" else 24
    return {
        "type": unit_type,
        "rect": Rect(int(x - size / 2), 800 - size - 12, size, size),
        "cooldown": 0.0,
        "angle": 0.0,
        "target": None,
    }


# ----- Add a unit if space -----
def spawn_friendly_unit(units: list) -> None:
    if len(units) >= 10:
        return
    unit_type = "tank" if random.random() < 0.25 else "infantry"
    candidates = list(range(50, 951, 5))
    random.shuffle(candidates)
    # ----- Find a free spot -----
    for x in candidates:
        unit = make_unit(unit_type, x)
        if all(not unit["rect"].colliderect(existing["rect"])
               for existing in units):
            units.append(unit)
            return


# ----- Pick which cube to shoot -----
def choose_target(unit: dict, cubes: list) -> Optional[dict]:
    if not cubes:
        return None
    if unit["type"] == "infantry":
        oldest_row = min(cube["row"] for cube in cubes)
        return random.choice(
            [cube for cube in cubes if cube["row"] == oldest_row])
    start = (unit["rect"].centerx, unit["rect"].top)
    visible = []
    # ----- Keep cubes tank can see -----
    for cube in cubes:
        end = (cube["rect"].centerx, cube["rect"].centery)
        if not any(line_hits_rect(start, end, other["rect"])
                   for other in cubes if other is not cube):
            visible.append(cube)
    if not visible:
        return None
    strongest = max(cube["hp"] for cube in visible)
    return random.choice(
        [cube for cube in visible if cube["hp"] == strongest])


# ----- Shoot a projectile at target -----
def fire_unit(unit: dict, cubes: list, projectiles: list,
              target: Optional[dict] = None) -> None:
    if target not in cubes:
        target = choose_target(unit, cubes)
    if target is None:
        return
    is_tank = unit["type"] == "tank"
    size = 18 if is_tank else 10
    damage = 8.0 if is_tank else 0.5
    x = unit["rect"].centerx - size / 2
    y = unit["rect"].top - size
    dx = target["rect"].centerx - (x + size / 2)
    dy = target["rect"].centery - (y + size / 2)
    distance = max(1.0, (dx * dx + dy * dy) ** 0.5)
    speed = 1100 if is_tank else 1350
    projectiles.append({
        "rect": Rect(x, y, size, size),
        "vx": dx / distance * speed,
        "vy": dy / distance * speed,
        "damage": damage,
        "type": unit["type"],
    })


# ----- Holds all game state and rules -----
class Game:
    PLAYER_SPEED = 550
    BALL_RADIUS = 10
    BALL_SPEED = 400

    # ----- Set up a new game -----
    def __init__(self) -> None:
        self.player_name = ""
        self.player = Rect(440, 600, 120, 20)
        self.retry()
        self.state = "menu"

    # ----- Reset everything for a level -----
    def start_level(self) -> None:
        self.level, self.cubes = load_level(self.level_index)
        self.next_row = 1
        self.spawn_timer = 0.0
        self.ball_x = self.player.centerx
        self.ball_y = self.player.top - self.BALL_RADIUS
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.launched = False
        self.started = False
        self.powerups = []
        self.units = []
        self.projectiles = []
        self.state = "playing"

    # ----- Restart from level one -----
    def retry(self) -> None:
        self.level_index = 0
        self.total_time = 0.0
        self.level_start = 0.0
        self.level_times = []
        self.start_level()

    # ----- Move on to next level -----
    def next_level(self) -> None:
        self.level_index = min(self.level_index + 1, len(LEVELS) - 1)
        self.start_level()

    # ----- Go back to main menu -----
    def to_menu(self) -> None:
        self.player_name = ""
        self.retry()
        self.state = "menu"

    # ----- Shoot the ball upward -----
    def launch(self) -> None:
        if not self.launched:
            self.launched = True
            self.started = True
            self.ball_vx = random.choice((-1, 1)) * random.uniform(100, 300)
            self.ball_vy = -self.BALL_SPEED

    # ----- Hurt a cube, maybe destroy -----
    def damage_cube(self, cube: dict, amount: float) -> None:
        cube["hp"] -= amount
        if cube["hp"] <= 0:
            if cube["type"] == "S":
                self.powerups.append({
                    "rect": Rect(cube["rect"].centerx - 10,
                                 cube["rect"].centery, 20, 20),
                    "speed": 240,
                })
            if cube in self.cubes:
                self.cubes.remove(cube)

    # ----- Run one frame of game -----
    def update(self, delta_time: float, direction: int) -> None:
        """direction: -1 left, 0 none, 1 right."""
        if self.state != "playing":
            return
        player, cubes, r = self.player, self.cubes, self.BALL_RADIUS
        # ----- Move paddle left or right -----
        player.x = max(0, min(1000 - player.w,
                              player.x + self.PLAYER_SPEED * direction
                              * delta_time))

        # ----- Move ball or hold it -----
        if not self.launched:
            self.ball_x = player.centerx
            self.ball_y = player.top - r
        else:
            self.ball_x += self.ball_vx * delta_time
            self.ball_y += self.ball_vy * delta_time
            # ----- Bounce ball off walls -----
            if self.ball_x - r <= 0:
                self.ball_x = r
                self.ball_vx = abs(self.ball_vx)
            if self.ball_x + r >= 1000:
                self.ball_x = 1000 - r
                self.ball_vx = -abs(self.ball_vx)
            if self.ball_y - r <= 0:
                self.ball_y = r
                self.ball_vy = abs(self.ball_vy)
            if self.ball_y - r > 800:
                self.launched = False
            ball_rect = Rect(self.ball_x - r, self.ball_y - r, r * 2, r * 2)
            # ----- Bounce ball off paddle -----
            if (ball_rect.colliderect(player) and self.ball_vy > 0
                    and self.ball_y <= player.top):
                self.ball_y = player.top - r
                self.ball_vy = -abs(self.ball_vy)
                self.ball_vx = ((self.ball_x - player.centerx)
                                / (player.w / 2) * 300)
            # ----- Check ball hitting cubes -----
            for cube in cubes:
                if ball_rect.colliderect(cube["rect"]):
                    c = cube["rect"]
                    overlap_left = ball_rect.right - c.left
                    overlap_right = c.right - ball_rect.left
                    overlap_top = ball_rect.bottom - c.top
                    overlap_bottom = c.bottom - ball_rect.top
                    smallest = min(overlap_left, overlap_right,
                                   overlap_top, overlap_bottom)
                    # ----- Bounce away from hit side -----
                    if smallest == overlap_left:
                        self.ball_x -= overlap_left
                        self.ball_vx = -abs(self.ball_vx)
                    elif smallest == overlap_right:
                        self.ball_x += overlap_right
                        self.ball_vx = abs(self.ball_vx)
                    elif smallest == overlap_top:
                        self.ball_y -= overlap_top
                        self.ball_vy = -abs(self.ball_vy)
                    else:
                        self.ball_y += overlap_bottom
                        self.ball_vy = abs(self.ball_vy)
                    self.damage_cube(cube, 1)
                    break

        if not self.started:
            return
        # ----- Update timers and spawn rows -----
        self.total_time += delta_time
        self.spawn_timer += delta_time
        if self.spawn_timer >= SPAWN_TIME and self.next_row < len(self.level):
            spawn_row(self.level[self.next_row], cubes, self.next_row)
            self.next_row += 1
            self.spawn_timer = 0.0

        # ----- Move cubes down, check loss -----
        for cube in cubes:
            cube["rect"].y += cube["speed"] * delta_time
            if cube["rect"].bottom >= player.top:
                self.state = "gameover"

        # ----- Move and collect powerups -----
        for powerup in self.powerups[:]:
            powerup["rect"].y += powerup["speed"] * delta_time
            if powerup["rect"].colliderect(player):
                spawn_friendly_unit(self.units)
                self.powerups.remove(powerup)
            elif powerup["rect"].top > 800:
                self.powerups.remove(powerup)

        # ----- Aim and fire each unit -----
        for unit in self.units:
            if unit["target"] not in cubes:
                unit["target"] = choose_target(unit, cubes)
            target = unit["target"]
            if target is not None:
                dx = target["rect"].centerx - unit["rect"].centerx
                dy = target["rect"].centery - unit["rect"].centery
                if dx != 0 or dy != 0:
                    unit["angle"] = -90.0 - math.degrees(math.atan2(dy, dx))
            unit["cooldown"] -= delta_time
            if unit["cooldown"] <= 0:
                fire_unit(unit, cubes, self.projectiles, unit["target"])
                unit["cooldown"] = 5.0 if unit["type"] == "tank" else 1.0

        # ----- Move projectiles, check hits -----
        for projectile in self.projectiles[:]:
            pr = projectile["rect"]
            pr.x += projectile["vx"] * delta_time
            pr.y += projectile["vy"] * delta_time
            if pr.bottom < 0 or pr.top > 800 or pr.right < 0 or pr.left > 1000:
                self.projectiles.remove(projectile)
                continue
            # ----- Damage cube a shot hits -----
            for cube in cubes:
                if pr.colliderect(cube["rect"]):
                    self.damage_cube(cube, projectile["damage"])
                    self.projectiles.remove(projectile)
                    break

        # ----- Check if level is won -----
        if (self.state == "playing" and not cubes
                and self.next_row >= len(self.level)):
            self.level_times.append(self.total_time - self.level_start)
            self.level_start = self.total_time
            if self.level_index == len(LEVELS) - 1:
                self.state = "final"
            else:
                self.state = "victory"