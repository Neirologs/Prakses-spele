import pygame 

pygame.init()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
x, running = 400, True
y, running = 400, True
player = pygame.Rect(400, 400, 100, 100)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        player.x += 5
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        player.x -= 5
    if pygame.key.get_pressed()[pygame.K_UP]:
        player.y -= 5
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        player.y += 5
    screen.fill((0, 0, 255))
    player.clamp_ip(screen.get_rect())
    pygame.draw.rect(screen, (255, 0, 0), player)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()