import pygame 

cell = 50

Levels = [
    ["111..11.111..111111"
     "11S11111S111.11..11"
     "...1.1.1.1.111.11.1"
     "111..1111S111111111"
     "111..........111111"
     "111.S111111....1111"
     "1111111111111111111"
    ],
    ["21112..22222S......"
     "...111222S...2111SS"
     "222S12121..121S21S2"
     "21..1S12...222.2112"
     "1111111111111111111"
     "222.2222.1..11.2..."
     "......B............"
     "....2....2222.21111"
    ],
    ["3333331....12323SSS"
     "3333222..333.2333S."
     "...33S..333..22.33."
     "B..333.S..333.22.13"
     "..3..2222.333.33333"
     "..SS3333S3332223..."
     "..SSS.33.2.22.1...3"
     ".B...333.S3.33..B.."
     "...333.222.3..3...."
    ]
]

CubeTypes = {
    "1": {"color": (255,255,0), "hp": 1, "speed": 40, "size":1},
    "2": {"color": (0,176,153), "hp": 2, "speed": 40, "size":1},
    "3": {"color": (120,32,44), "hp": 3, "speed": 40, "size":1},
    "S": {"color": (255,255,255), "hp": 5, "speed": 40, "size":1},
    "B": {"color": (2,5,100), "hp": 25, "speed": 80, "size":2},
}

def spawnRow(rowString, cubes)

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

    while running:
        deltaTime = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        processInput(player, playerSpeed, deltaTime)

        screen.fill((0, 0, 255))
        player.clamp_ip(screen.get_rect())
        pygame.draw.rect(screen, (255, 0, 0), player)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()