import os
import sys
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from game import Game, Levels, cubeTypes, formatTime


def toRect(r):
    return pygame.Rect(int(r.x), int(r.y), int(r.w), int(r.h))


def load_unit_images():
    images = {}
    folders = (os.path.join(ROOT, "assets"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"))
    for unit_type, names in (("infantry", ("infantry.png",)), ("tank", ("tank.png", "tanks.png"))):
        paths = [os.path.join(f, n) for f in folders for n in names]
        path = next((p for p in paths if os.path.exists(p)), None)
        images[unit_type] = pygame.image.load(path).convert_alpha() if path else None
        if path is None:
            print("Image for", unit_type, "not found. Looked in:", paths)
    return images


def draw_unit_image(screen, unit, images):
    sprite = images.get(unit["type"])
    if sprite is None:
        return False
    rect = toRect(unit["rect"])
    sprite = pygame.transform.scale(sprite, rect.size)
    rotated = pygame.transform.rotate(sprite, unit["angle"])
    screen.blit(rotated, rotated.get_rect(center=rect.center))
    return True


def drawText(screen, font, text, center, color=(255, 255, 255)):
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(center=center))


def drawButton(screen, font, text, rect):
    pygame.draw.rect(screen, (255, 255, 255), rect)
    label = font.render(text, True, (0, 0, 255))
    screen.blit(label, label.get_rect(center=rect.center))


def drawOverlay(screen):
    overlay = pygame.Surface((1000, 800))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("War Breakout")
    unitImages = load_unit_images()
    game = Game()
    clock = pygame.time.Clock()
    running = True
    overlayDrawn = False
    titleFont = pygame.font.SysFont(None, 120)
    font = pygame.font.SysFont(None, 70)
    smallFont = pygame.font.SysFont(None, 40)
    tinyFont = pygame.font.SysFont(None, 27)
    startButton = pygame.Rect(350, 450, 300, 70)
    aboutButton = pygame.Rect(350, 540, 300, 70)
    nextButton = pygame.Rect(350, 480, 300, 70)
    retryButton = pygame.Rect(350, 480, 300, 70)
    menuButton = pygame.Rect(350, 650, 300, 70)
    nameBox = pygame.Rect(150, 360, 700, 70)

    while running:
        deltaTime = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            clicked = event.type == pygame.MOUSEBUTTONDOWN
            if game.state == "menu":
                if clicked and startButton.collidepoint(event.pos):
                    game.state = "name"
                elif clicked and aboutButton.collidepoint(event.pos):
                    game.state = "about"
            elif game.state == "name":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(game.playerName.strip()) >= 2:
                        game.playerName = game.playerName.strip()
                        game.state = "playing"
                    elif event.key == pygame.K_BACKSPACE:
                        game.playerName = game.playerName[:-1]
                    elif event.unicode and event.unicode.isprintable() and len(game.playerName) < 25:
                        game.playerName += event.unicode
            elif game.state == "playing":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game.launch()
            elif game.state == "victory":
                if clicked and nextButton.collidepoint(event.pos):
                    game.nextLevel()
            elif game.state == "gameover":
                if clicked and retryButton.collidepoint(event.pos):
                    game.retry()
            elif game.state == "about":
                if clicked and menuButton.collidepoint(event.pos):
                    game.state = "menu"
            elif game.state == "final":
                if clicked and menuButton.collidepoint(event.pos):
                    game.toMenu()

        if game.state == "menu":
            screen.fill((0, 0, 255))
            drawText(screen, titleFont, "War Breakout", (500, 250))
            drawButton(screen, smallFont, "Start Game", startButton)
            drawButton(screen, smallFont, "About", aboutButton)
            pygame.display.flip()
            continue
        if game.state == "name":
            screen.fill((0, 0, 255))
            drawText(screen, font, "Enter your name (2-25 characters)", (500, 280))
            pygame.draw.rect(screen, (255, 255, 255), nameBox, 3)
            drawText(screen, smallFont, game.playerName, nameBox.center)
            drawText(screen, smallFont, "Press Enter to start", (500, 480))
            pygame.display.flip()
            continue
        if game.state == "about":
            screen.fill((0, 0, 255))
            drawText(screen, font, "About", (500, 150))
            drawText(screen, smallFont, "War Breakout takes breakout games to the next level!", (500, 280))
            drawText(screen, smallFont, "Fight against cubes with infantry and tanks.", (500, 360))
            drawText(screen, smallFont, "Defeat them in the fastest time possible!", (500, 400))
            drawText(screen, smallFont, "Made by: Neirologs 2026", (500, 450))
            drawButton(screen, smallFont, "Back", menuButton)
            pygame.display.flip()
            continue
        if game.state in ("gameover", "victory", "final"):
            if not overlayDrawn:
                drawOverlay(screen)
                if game.state == "gameover":
                    drawText(screen, font, "Defenses breached, you lost!", (500, 400), (255, 0, 0))
                    drawButton(screen, smallFont, "Try Again", retryButton)
                elif game.state == "victory":
                    drawText(screen, font, "You defended against the enemies!", (500, 350))
                    drawText(screen, smallFont, "Time: " + formatTime(game.totalTime), (500, 430))
                    drawButton(screen, smallFont, "Next Level", nextButton)
                else:
                    drawText(screen, font, "Congratulations, you won!", (500, 250))
                    drawText(screen, smallFont, "Player: " + game.playerName, (500, 350))
                    drawText(screen, smallFont, "Total time: " + formatTime(game.totalTime), (500, 400))
                    for i, t in enumerate(game.levelTimes):
                        drawText(screen, smallFont, "Level " + str(i + 1) + ": " + formatTime(t), (500, 470 + i * 45))
                    drawButton(screen, smallFont, "Main Menu", menuButton)
                pygame.display.flip()
                overlayDrawn = True
            continue

        overlayDrawn = False
        key = pygame.key.get_pressed()
        direction = (key[pygame.K_RIGHT] or key[pygame.K_d]) - (key[pygame.K_LEFT] or key[pygame.K_a])
        game.update(deltaTime, direction)

        screen.fill((0, 0, 255))
        pygame.draw.rect(screen, (255, 0, 0), toRect(game.player))
        pygame.draw.circle(screen, (255, 255, 255), (int(game.ballX), int(game.ballY)), game.ballRadius)
        for cube in game.cubes:
            pygame.draw.rect(screen, cubeTypes[cube["type"]]["color"], toRect(cube["rect"]).inflate(-6, -6))
            if cube["hp"] > 1 and cube["type"] not in ("B", "S"):
                drawText(screen, tinyFont, str(int(cube["hp"]) if cube["hp"].is_integer() else cube["hp"]), toRect(cube["rect"]).center)
        for powerup in game.powerups:
            pygame.draw.rect(screen, (255, 255, 255), toRect(powerup["rect"]))
            pygame.draw.rect(screen, (0, 220, 255), toRect(powerup["rect"]).inflate(-6, -6))
        for unit in game.units:
            if not draw_unit_image(screen, unit, unitImages):
                color = (25, 85, 35) if unit["type"] == "tank" else (70, 115, 70)
                pygame.draw.rect(screen, color, toRect(unit["rect"]))
        for projectile in game.projectiles:
            if projectile["type"] == "tank":
                pygame.draw.rect(screen, (255, 245, 80), toRect(projectile["rect"]))
                pygame.draw.rect(screen, (255, 115, 0), toRect(projectile["rect"]), 3)
            else:
                pygame.draw.rect(screen, (30, 255, 255), toRect(projectile["rect"]))
        timerText = smallFont.render(formatTime(game.totalTime), True, (255, 255, 255))
        screen.blit(timerText, timerText.get_rect(topright=(990, 10)))
        infantryCount = sum(u["type"] == "infantry" for u in game.units)
        tankCount = sum(u["type"] == "tank" for u in game.units)
        unitText = tinyFont.render(f"Level: {game.levelIndex + 1}/{len(Levels)}   Infantry: {infantryCount}   Tanks: {tankCount}", True, (255, 255, 255))
        screen.blit(unitText, (10, 10))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()