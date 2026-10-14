import random
import math

cell = 50
spawnTime = 10

Levels = [
    ["1S1..11.1S1..1111111",
     "11S11111S111.11..111",
     "...1.1.1.1.111.11.11",
     "111..1111S1111111111",
     "111....S.....1111111",
     "111.S111111....11111",
     "11111111111111111111"
    ],
    ["2S112..2S222S......2",
     "...111222S...2111SS2",
     "222212121..121S21S22",
     "21..1S12...2S2.21122",
     "11111111111111111112",
     "222.2222.1..11.2...2",
     ".B....B....B.......2",
     "....2....2222.211112"
    ],
    ["3333S3S....12323SSS3",
     "3333S22..333.2333S.3",
     "...33S..3S3..22.33.3",
     "B..333.S..333.22.133",
     "..3..2222.333.333333",
     "B..3333333322222.B.3",
     "..33S.33.2.22.1....3",
     ".B...333.33.33..B..3",
     "...333.222.3..3....3"
    ]
]
cubeTypes = {
    "1": {"color": (175, 35, 35), "hp": 1, "speed": 7, "size": 1},
    "2": {"color": (0, 100, 0), "hp": 2, "speed": 7, "size": 1},
    "3": {"color": (10, 190, 32), "hp": 3, "speed": 7, "size": 1},
    "S": {"color": (220, 180, 0), "hp": 5, "speed": 7, "size": 1},
    "B": {"color": (70, 0, 100), "hp": 20, "speed": 14, "size": 2}
}


class Rect:
    """Minimal replacement for pygame.Rect so this package needs no pygame."""
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
    left = property(lambda s: s.x)
    right = property(lambda s: s.x + s.w)
    top = property(lambda s: s.y)
    bottom = property(lambda s: s.y + s.h)
    centerx = property(lambda s: s.x + s.w / 2)
    centery = property(lambda s: s.y + s.h / 2)

    def colliderect(self, o):
        return self.x < o.right and o.x < self.right and self.y < o.bottom and o.y < self.bottom


def lineHitsRect(a, b, r):
    """True if the segment a->b crosses rect r (replaces Rect.clipline)."""
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    for p, q in ((-dx, a[0] - r.left), (dx, r.right - a[0]), (-dy, a[1] - r.top), (dy, r.bottom - a[1])):
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


def spawnRow(rowString, cubes, rowIndex):
    for col, char in enumerate(rowString):
        if char in cubeTypes:
            cubeType = cubeTypes[char]
            size = cell * cubeType["size"]
            cubes.append({"rect": Rect(col * cell, 0, size, size), "type": char, "hp": float(cubeType["hp"]), "speed": cubeType["speed"], "row": rowIndex})


def loadLevel(index):
    level = Levels[index]
    cubes = []
    spawnRow(level[0], cubes, 0)
    return level, cubes


def formatTime(t):
    return f"{int(t // 60):02d}:{t % 60:05.2f}"

def makeUnit(unitType, x):
    size = cell * 2 if unitType == "tank" else 24
    return {
        "type": unitType,
        "rect": Rect(int(x - size / 2), 800 - size - 12, size, size),
        "cooldown": 0.0,
        "angle": 0.0,
        "target": None
    }


def spawnFriendlyUnit(units):
    if len(units) >= 10:
        return
    unitType = "tank" if random.random() < 0.10 else "infantry"
    candidates = list(range(50, 951, 5))
    random.shuffle(candidates)
    for x in candidates:
        unit = makeUnit(unitType, x)
        if all(not unit["rect"].colliderect(existing["rect"]) for existing in units):
            units.append(unit)
            return


def chooseTarget(unit, cubes):
    if not cubes:
        return None
    if unit["type"] == "infantry":
        oldestRow = max(cube["row"] for cube in cubes)
        return random.choice([cube for cube in cubes if cube["row"] == oldestRow])
    start = (unit["rect"].centerx, unit["rect"].top)
    visible = []
    for cube in cubes:
        end = (cube["rect"].centerx, cube["rect"].centery)
        if not any(lineHitsRect(start, end, other["rect"]) for other in cubes if other is not cube):
            visible.append(cube)
    if not visible:
        return None
    strongest = max(cube["hp"] for cube in visible)
    return random.choice([cube for cube in visible if cube["hp"] == strongest])


def fireUnit(unit, cubes, projectiles, target=None):
    if target not in cubes:
        target = chooseTarget(unit, cubes)
    if target is None:
        return
    isTank = unit["type"] == "tank"
    size = 18 if isTank else 10
    damage = 4.0 if isTank else 0.5
    x = unit["rect"].centerx - size / 2
    y = unit["rect"].top - size
    dx = target["rect"].centerx - (x + size / 2)
    dy = target["rect"].centery - (y + size / 2)
    distance = max(1.0, (dx * dx + dy * dy) ** 0.5)
    speed = 1100 if isTank else 1350
    projectiles.append({"rect": Rect(x, y, size, size), "vx": dx / distance * speed, "vy": dy / distance * speed, "damage": damage, "type": unit["type"]})


class Game:
    playerSpeed = 550
    ballRadius = 10
    ballSpeed = 400

    def __init__(self):
        self.playerName = ""
        self.player = Rect(440, 600, 120, 20)
        self.retry()
        self.state = "menu"

    def startLevel(self):
        self.level, self.cubes = loadLevel(self.levelIndex)
        self.nextRow = 1
        self.spawnTimer = 0.0
        self.ballX = self.player.centerx
        self.ballY = self.player.top - self.ballRadius
        self.ballVX = 0.0
        self.ballVY = 0.0
        self.launched = False
        self.started = False
        self.powerups = []
        self.units = []
        self.projectiles = []
        self.state = "playing"

    def retry(self):
        self.levelIndex = 0
        self.totalTime = 0.0
        self.levelStart = 0.0
        self.levelTimes = []
        self.startLevel()

    def nextLevel(self):
        self.levelIndex = min(self.levelIndex + 1, len(Levels) - 1)
        self.startLevel()

    def toMenu(self):
        self.playerName = ""
        self.retry()
        self.state = "menu"

    def launch(self):
        if not self.launched:
            self.launched = True
            self.started = True
            self.ballVX = random.choice((-1, 1)) * random.uniform(100, 300)
            self.ballVY = -self.ballSpeed

    def damageCube(self, cube, amount):
        cube["hp"] -= amount
        if cube["hp"] <= 0:
            if cube["type"] == "S":
                self.powerups.append({"rect": Rect(cube["rect"].centerx - 10, cube["rect"].centery, 20, 20), "speed": 240})
            if cube in self.cubes:
                self.cubes.remove(cube)

    def update(self, deltaTime, direction):
        """direction: -1 left, 0 none, 1 right."""
        if self.state != "playing":
            return
        player, cubes, r = self.player, self.cubes, self.ballRadius
        player.x = max(0, min(1000 - player.w, player.x + self.playerSpeed * direction * deltaTime))

        if not self.launched:
            self.ballX = player.centerx
            self.ballY = player.top - r
        else:
            self.ballX += self.ballVX * deltaTime
            self.ballY += self.ballVY * deltaTime
            if self.ballX - r <= 0:
                self.ballX = r
                self.ballVX = abs(self.ballVX)
            if self.ballX + r >= 1000:
                self.ballX = 1000 - r
                self.ballVX = -abs(self.ballVX)
            if self.ballY - r <= 0:
                self.ballY = r
                self.ballVY = abs(self.ballVY)
            if self.ballY - r > 800:
                self.launched = False
            ballRect = Rect(self.ballX - r, self.ballY - r, r * 2, r * 2)
            if ballRect.colliderect(player) and self.ballVY > 0 and self.ballY <= player.top:
                self.ballY = player.top - r
                self.ballVY = -abs(self.ballVY)
                self.ballVX = (self.ballX - player.centerx) / (player.w / 2) * 300
            for cube in cubes:
                if ballRect.colliderect(cube["rect"]):
                    c = cube["rect"]
                    overlapLeft = ballRect.right - c.left
                    overlapRight = c.right - ballRect.left
                    overlapTop = ballRect.bottom - c.top
                    overlapBottom = c.bottom - ballRect.top
                    smallest = min(overlapLeft, overlapRight, overlapTop, overlapBottom)
                    if smallest == overlapLeft:
                        self.ballX -= overlapLeft
                        self.ballVX = -abs(self.ballVX)
                    elif smallest == overlapRight:
                        self.ballX += overlapRight
                        self.ballVX = abs(self.ballVX)
                    elif smallest == overlapTop:
                        self.ballY -= overlapTop
                        self.ballVY = -abs(self.ballVY)
                    else:
                        self.ballY += overlapBottom
                        self.ballVY = abs(self.ballVY)
                    self.damageCube(cube, 1)
                    break

        if not self.started:
            return
        self.totalTime += deltaTime
        self.spawnTimer += deltaTime
        if self.spawnTimer >= spawnTime and self.nextRow < len(self.level):
            spawnRow(self.level[self.nextRow], cubes, self.nextRow)
            self.nextRow += 1
            self.spawnTimer = 0.0

        for cube in cubes:
            cube["rect"].y += cube["speed"] * deltaTime
            if cube["rect"].bottom >= player.top:
                self.state = "gameover"

        for powerup in self.powerups[:]:
            powerup["rect"].y += powerup["speed"] * deltaTime
            if powerup["rect"].colliderect(player):
                spawnFriendlyUnit(self.units)
                self.powerups.remove(powerup)
            elif powerup["rect"].top > 800:
                self.powerups.remove(powerup)

        for unit in self.units:
            if unit["target"] not in cubes:
                unit["target"] = chooseTarget(unit, cubes)
            target = unit["target"]
            if target is not None:
                dx = target["rect"].centerx - unit["rect"].centerx
                dy = target["rect"].centery - unit["rect"].centery
                if dx != 0 or dy != 0:
                    unit["angle"] = -90.0 - math.degrees(math.atan2(dy, dx))
            unit["cooldown"] -= deltaTime
            if unit["cooldown"] <= 0:
                fireUnit(unit, cubes, self.projectiles, unit["target"])
                unit["cooldown"] = 5.0 if unit["type"] == "tank" else 1.0

        for projectile in self.projectiles[:]:
            pr = projectile["rect"]
            pr.x += projectile["vx"] * deltaTime
            pr.y += projectile["vy"] * deltaTime
            if pr.bottom < 0 or pr.top > 800 or pr.right < 0 or pr.left > 1000:
                self.projectiles.remove(projectile)
                continue
            for cube in cubes:
                if pr.colliderect(cube["rect"]):
                    self.damageCube(cube, projectile["damage"])
                    self.projectiles.remove(projectile)
                    break

        if self.state == "playing" and not cubes and self.nextRow >= len(self.level):
            self.levelTimes.append(self.totalTime - self.levelStart)
            self.levelStart = self.totalTime
            if self.levelIndex == len(Levels) - 1:
                self.state = "final"
            else:
                self.state = "victory"