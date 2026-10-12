import pygame 

pygame.init()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
x, running = 400, True

while running: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        x += 5
    screen.fill((22, 32, 46))
    pygame.draw.rect(screen, (242, 154, 74), (x, 280, 40, 40))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()