import pygame 

cell = 50
spawnTime = 5

Levels = [
    ["111..11.111..111111",
     "11S11111S111.11..11",
     "...1.1.1.1.111.11.1",
     "111..1111S111111111",
     "111..........111111",
     "111.S111111....1111",
     "1111111111111111111"
    ],
    ["21112..22222S......",
     "...111222S...2111SS",
     "222S12121..121S21S2",
     "21..1S12...222.2112",
     "1111111111111111111",
     "222.2222.1..11.2...",
     "......B............",
     "....2....2222.21111"
    ],
    ["3333331....12323SSS",
     "3333222..333.2333S.",
     "...33S..333..22.33.",
     "B..333.S..333.22.13",
     "..3..2222.333.33333",
     "..SS3333S3332223...",
     "..SSS.33.2.22.1...3",
     ".B...333.S3.33..B..",
     "...333.222.3..3...."
    ]
]

cubeTypes = {
    "1": {"color": (220,30,30),  "hp": 1,  "speed": 5000, "size":1},
    "2": {"color": (255,220,0),  "hp": 2,  "speed": 7, "size":1},
    "3": {"color": (40,200,60),  "hp": 3,  "speed": 7, "size":1},
    "S": {"color": (212,175,55), "hp": 5,  "speed": 7, "size":1},
    "B": {"color": (15,10,25),   "hp": 25, "speed": 14, "size":2},
}

def spawnRow(rowString, cubes):
    for col, char in enumerate(rowString):
        if char in cubeTypes:
            cubeType = cubeTypes[char]
            cube = pygame.Rect(col * cell, 0, cell * cubeType["size"], cell * cubeType["size"])
            cubes.append({"rect": cube, "y": 0.0, "type": char, "hp": cubeType["hp"], "speed": cubeType["speed"]})


def processInput(player, playerSpeed, deltaTime):
    key = pygame.key.get_pressed()
    if key[pygame.K_RIGHT]:
        player.x += playerSpeed * deltaTime
    if key[pygame.K_LEFT]:
        player.x -= playerSpeed * deltaTime

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    player = pygame.Rect(500, 600, 120, 20)
    playerSpeed = 550
    clock = pygame.time.Clock()
    running = True

    cubes = []
    spawnTimer = 0
    level = Levels[0]
    spawnRow(level[0], cubes)
    nextRow = 1

    ballRadius = 10
    ballSpeed = 400
    ballX = player.centerx
    ballY = player.top - ballRadius
    ballVX = 0
    ballVY = 0
    launched = False

    started = False
    gameOver = False
    gameOverDrawn = False
    font = pygame.font.SysFont(None, 80)

    while running:
        deltaTime = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not launched:
                launched = True
                started = True
                ballVX = 200
                ballVY = -ballSpeed

        if gameOver:
            if not gameOverDrawn:
                overlay = pygame.Surface((1000, 800))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                text = font.render("Defenses breached, you lost!", True, (255, 0, 0))
                screen.blit(text, text.get_rect(center=(500, 400)))
                pygame.display.flip()
                gameOverDrawn = True
            continue

        processInput(player, playerSpeed, deltaTime)

        if not launched:
            ballX = player.centerx
            ballY = player.top - ballRadius
        else:
            ballX += ballVX * deltaTime
            ballY += ballVY * deltaTime

        if launched:
            # walls
            if ballX - ballRadius <= 0:
                ballX = ballRadius
                ballVX = abs(ballVX)
            if ballX + ballRadius >= 1000:
                ballX = 1000 - ballRadius
                ballVX = -abs(ballVX)
            if ballY - ballRadius <= 0:
                ballY = ballRadius
                ballVY = abs(ballVY)
            if ballY - ballRadius > 800:
                launched = False

            ballRect = pygame.Rect(ballX - ballRadius, ballY - ballRadius, ballRadius * 2, ballRadius * 2)

            # paddle
            if ballRect.colliderect(player) and ballVY > 0:
                ballY = player.top - ballRadius
                ballVY = -abs(ballVY)
                ballVX = (ballX - player.centerx) / (player.width / 2) * 300

            # cubes
            for cube in cubes:
                r = cube["rect"]
                if ballRect.colliderect(r):
                    overlapLeft = ballRect.right - r.left
                    overlapRight = r.right - ballRect.left
                    overlapTop = ballRect.bottom - r.top
                    overlapBottom = r.bottom - ballRect.top
                    smallest = min(overlapLeft, overlapRight, overlapTop, overlapBottom)

                    if smallest == overlapLeft:
                        ballVX = -abs(ballVX)
                    elif smallest == overlapRight:
                        ballVX = abs(ballVX)
                    elif smallest == overlapTop:
                        ballVY = -abs(ballVY)
                    else:
                        ballVY = abs(ballVY)

                    cube["hp"] -= 1
                    if cube["hp"] <= 0:
                        cubes.remove(cube)
                    break

        if started:       
            spawnTimer += deltaTime
            if spawnTimer >= spawnTime and nextRow < len(level):
                spawnRow(level[nextRow], cubes)
                nextRow += 1
                spawnTimer = 0
            for cube in cubes:
                cube['y'] += cube['speed'] * deltaTime
                cube['rect'].y = int(cube['y'])
                if cube['rect'].bottom >= player.top:
                    gameOver = True

        screen.fill((0, 0, 255))
        player.clamp_ip(screen.get_rect())
        pygame.draw.rect(screen, (255, 0, 0), player)
        pygame.draw.circle(screen, (255, 255, 255), (int(ballX), int(ballY)), ballRadius)
        for cube in cubes:
            pygame.draw.rect(screen, cubeTypes[cube["type"]]["color"], cube["rect"].inflate(-6, -6))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()