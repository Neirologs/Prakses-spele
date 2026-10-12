import pygame 

def processInput(player, playerSpeed, deltaTime):
    key = pygame.key.get_pressed()
    if key[pygame.K_RIGHT]:
        player.x += playerSpeed * deltaTime
    if key[pygame.K_LEFT]:
        player.x -= playerSpeed * deltaTime

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    clock = pygame.time.Clock()
    running = True
    player = pygame.Rect(500, 600, 120, 20)
    playerSpeed = 550

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