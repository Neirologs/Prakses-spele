import pygame 

pygame.init()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
x = 0
y = 0
running = True
player = pygame.Rect(x, y, 100, 100)
speed = 300

while running:
    delate_time = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    key = pygame.key.get_pressed()

    if key[pygame.K_RIGHT]:
        player.x += speed * delate_time
    if key[pygame.K_LEFT]:
        player.x -= speed * delate_time
    if key[pygame.K_UP]:
        player.y -= speed * delate_time
    if key[pygame.K_DOWN]:
        player.y += speed * delate_time
    screen.fill((0, 0, 255))
    player.clamp_ip(screen.get_rect())
    pygame.draw.rect(screen, (255, 0, 0), player)
    pygame.display.flip()

pygame.quit()