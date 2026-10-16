import os
import sys

import pygame

# ----- Find project root folder -----
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from game.game import Game, Rect, LEVELS, CUBE_TYPES, format_time  # noqa: E402
from client import api_client  # noqa: E402


# ----- Convert game rectangle to pygame -----
def to_rect(r: Rect) -> pygame.Rect:
    return pygame.Rect(int(r.x), int(r.y), int(r.w), int(r.h))


# ----- Load unit pictures from disk -----
def load_unit_images() -> dict:
    images = {}
    folders = (
        os.path.join(ROOT, "assets"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"),
    )
    unit_files = (
        ("infantry", ("infantry.png",)),
        ("tank", ("tank.png", "tanks.png")),
    )
    # ----- Look for each unit image -----
    for unit_type, names in unit_files:
        paths = [os.path.join(f, n) for f in folders for n in names]
        path = next((p for p in paths if os.path.exists(p)), None)
        if path:
            images[unit_type] = pygame.image.load(path).convert_alpha()
        else:
            images[unit_type] = None
        if path is None:
            print("Image for", unit_type, "not found. Looked in:", paths)
    return images


# ----- Draw rotated unit picture -----
def draw_unit_image(screen: pygame.Surface, unit: dict,
                    images: dict) -> bool:
    sprite = images.get(unit["type"])
    if sprite is None:
        return False
    rect = to_rect(unit["rect"])
    sprite = pygame.transform.scale(sprite, rect.size)
    rotated = pygame.transform.rotate(sprite, unit["angle"])
    screen.blit(rotated, rotated.get_rect(center=rect.center))
    return True


# ----- Draw text at center point -----
def draw_text(screen: pygame.Surface, font: pygame.font.Font, text: str,
              center: tuple, color: tuple = (255, 255, 255)) -> None:
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(center=center))


# ----- Draw white button with text -----
def draw_button(screen: pygame.Surface, font: pygame.font.Font, text: str,
                rect: pygame.Rect) -> None:
    pygame.draw.rect(screen, (255, 255, 255), rect)
    label = font.render(text, True, (0, 0, 255))
    screen.blit(label, label.get_rect(center=rect.center))


# ----- Darken screen behind messages -----
def draw_overlay(screen: pygame.Surface) -> None:
    overlay = pygame.Surface((1000, 800))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))


# ----- Log in or register player -----
def authenticate(ui: dict, session: dict, game: Game,
                 register: bool) -> None:
    name = ui["name"].strip()
    if len(name) < 2:
        ui["message"] = "Name must be 2-25 characters"
        return
    if len(ui["password"]) < 3:
        ui["message"] = "Password must be at least 3 characters"
        return
    try:
        if register:
            api_client.register(name, ui["password"])
        session["token"] = api_client.login(name, ui["password"])
    except api_client.ApiError as error:
        ui["message"] = str(error)
        return
    session["name"] = name
    game.player_name = name
    ui.update(name="", password="", focus=0, message="")
    game.state = "playing"


# ----- Send score to leaderboard -----
def submit_score(game: Game, session: dict) -> tuple:
    try:
        api_client.submit_score(
            session["token"], int(round(game.total_time * 100)))
    except api_client.ApiError as error:
        if error.status == 401:
            session["token"] = None
        return "Could not save score: " + str(error), False
    return "Score saved to the leaderboard!", True


# ----- Run the whole game -----
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("War Breakout")
    unit_images = load_unit_images()
    game = Game()
    clock = pygame.time.Clock()
    running = True
    overlay_drawn = False
    session = {"name": "", "token": None}
    ui = {"name": "", "password": "", "focus": 0, "message": ""}
    final_message = ""
    final_ok = False
    title_font = pygame.font.SysFont(None, 120)
    font = pygame.font.SysFont(None, 70)
    small_font = pygame.font.SysFont(None, 40)
    tiny_font = pygame.font.SysFont(None, 27)
    start_button = pygame.Rect(350, 450, 300, 70)
    about_button = pygame.Rect(350, 540, 300, 70)
    next_button = pygame.Rect(350, 480, 300, 70)
    retry_button = pygame.Rect(350, 480, 300, 70)
    menu_button = pygame.Rect(350, 650, 300, 70)
    name_box = pygame.Rect(150, 250, 700, 70)
    pass_box = pygame.Rect(150, 380, 700, 70)
    login_button = pygame.Rect(150, 490, 330, 70)
    register_button = pygame.Rect(520, 490, 330, 70)

    # ----- Main loop runs every frame -----
    while running:
        delta_time = clock.tick(60) / 1000.0
        delta_time = min(delta_time, 0.05)
        # ----- Handle mouse and keyboard events -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            clicked = event.type == pygame.MOUSEBUTTONDOWN
            # ----- Menu screen clicks -----
            if game.state == "menu":
                if clicked and start_button.collidepoint(event.pos):
                    if session["token"]:
                        game.player_name = session["name"]
                        game.state = "playing"
                    else:
                        game.state = "login"
                elif clicked and about_button.collidepoint(event.pos):
                    game.state = "about"
            # ----- Login screen input -----
            elif game.state == "login":
                # ----- Typing into login boxes -----
                if event.type == pygame.KEYDOWN:
                    field = "name" if ui["focus"] == 0 else "password"
                    if event.key == pygame.K_TAB:
                        ui["focus"] = 1 - ui["focus"]
                    elif event.key == pygame.K_RETURN:
                        if ui["focus"] == 0:
                            ui["focus"] = 1
                        else:
                            authenticate(ui, session, game, False)
                    elif event.key == pygame.K_BACKSPACE:
                        ui[field] = ui[field][:-1]
                    elif (event.unicode and event.unicode.isprintable()
                            and len(ui[field]) < 25):
                        ui[field] += event.unicode
                # ----- Clicking login screen buttons -----
                elif clicked:
                    if name_box.collidepoint(event.pos):
                        ui["focus"] = 0
                    elif pass_box.collidepoint(event.pos):
                        ui["focus"] = 1
                    elif login_button.collidepoint(event.pos):
                        authenticate(ui, session, game, False)
                    elif register_button.collidepoint(event.pos):
                        authenticate(ui, session, game, True)
                    elif menu_button.collidepoint(event.pos):
                        ui["message"] = ""
                        game.state = "menu"
            # ----- Press space to launch -----
            elif game.state == "playing":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game.launch()
            # ----- Victory screen next button -----
            elif game.state == "victory":
                if clicked and next_button.collidepoint(event.pos):
                    game.next_level()
            # ----- Game over retry button -----
            elif game.state == "gameover":
                if clicked and retry_button.collidepoint(event.pos):
                    game.retry()
            # ----- About screen back button -----
            elif game.state == "about":
                if clicked and menu_button.collidepoint(event.pos):
                    game.state = "menu"
            # ----- Final screen menu button -----
            elif game.state == "final":
                if clicked and menu_button.collidepoint(event.pos):
                    game.to_menu()
                    game.player_name = session["name"]

        # ----- Draw menu screen -----
        if game.state == "menu":
            screen.fill((0, 0, 255))
            draw_text(screen, title_font, "War Breakout", (500, 250))
            draw_button(screen, small_font, "Start Game", start_button)
            draw_button(screen, small_font, "About", about_button)
            pygame.display.flip()
            continue
        # ----- Draw login screen -----
        if game.state == "login":
            screen.fill((0, 0, 255))
            draw_text(screen, font, "Log in or register", (500, 130))
            screen.blit(
                small_font.render("Name (2-25 characters)", True,
                                  (255, 255, 255)),
                (150, 215))
            screen.blit(
                small_font.render("Password (3+ characters)", True,
                                  (255, 255, 255)),
                (150, 345))
            name_color = (255, 255, 255) if ui["focus"] == 0 else (120, 120, 200)
            pass_color = (255, 255, 255) if ui["focus"] == 1 else (120, 120, 200)
            pygame.draw.rect(screen, name_color, name_box, 3)
            pygame.draw.rect(screen, pass_color, pass_box, 3)
            draw_text(screen, small_font, ui["name"], name_box.center)
            draw_text(screen, small_font, "*" * len(ui["password"]),
                      pass_box.center)
            draw_button(screen, small_font, "Log in", login_button)
            draw_button(screen, small_font, "Register", register_button)
            draw_text(screen, small_font, ui["message"], (500, 610),
                      (255, 130, 130))
            draw_button(screen, small_font, "Back", menu_button)
            pygame.display.flip()
            continue
        # ----- Draw about screen -----
        if game.state == "about":
            screen.fill((0, 0, 255))
            draw_text(screen, font, "About", (500, 150))
            draw_text(screen, small_font,
                      "War Breakout takes breakout games to the next level!",
                      (500, 280))
            draw_text(screen, small_font,
                      "Fight against cubes with infantry and tanks.",
                      (500, 360))
            draw_text(screen, small_font,
                      "Defeat them in the fastest time possible!", (500, 400))
            draw_text(screen, small_font, "Made by: Neirologs 2026",
                      (500, 450))
            draw_button(screen, small_font, "Back", menu_button)
            pygame.display.flip()
            continue
        # ----- Draw end of level screens -----
        if game.state in ("gameover", "victory", "final"):
            if not overlay_drawn:
                if game.state == "final":
                    final_message, final_ok = submit_score(game, session)
                draw_overlay(screen)
                if game.state == "gameover":
                    draw_text(screen, font, "Defenses breached, you lost!",
                              (500, 400), (255, 0, 0))
                    draw_button(screen, small_font, "Try Again", retry_button)
                elif game.state == "victory":
                    draw_text(screen, font,
                              "You defended against the enemies!", (500, 350))
                    draw_text(screen, small_font,
                              "Time: " + format_time(game.total_time),
                              (500, 430))
                    draw_button(screen, small_font, "Next Level", next_button)
                else:
                    draw_text(screen, font, "Congratulations, you won!",
                              (500, 250))
                    draw_text(screen, small_font,
                              "Player: " + game.player_name, (500, 350))
                    draw_text(screen, small_font,
                              "Total time: " + format_time(game.total_time),
                              (500, 400))
                    # ----- Show time for each level -----
                    for i, t in enumerate(game.level_times):
                        draw_text(screen, small_font,
                                  "Level " + str(i + 1) + ": "
                                  + format_time(t),
                                  (500, 470 + i * 45))
                    message_color = (120, 255, 120) if final_ok else (255, 130, 130)
                    draw_text(screen, tiny_font, final_message, (500, 615),
                              message_color)
                    draw_button(screen, small_font, "Main Menu", menu_button)
                pygame.display.flip()
                overlay_drawn = True
            continue

        # ----- Update game each frame -----
        overlay_drawn = False
        key = pygame.key.get_pressed()
        direction = key[pygame.K_RIGHT] - key[pygame.K_LEFT]
        game.update(delta_time, direction)

        # ----- Draw paddle and ball -----
        screen.fill((0, 0, 255))
        pygame.draw.rect(screen, (255, 0, 0), to_rect(game.player))
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(game.ball_x), int(game.ball_y)),
                           game.BALL_RADIUS)
        # ----- Draw every cube -----
        for cube in game.cubes:
            pygame.draw.rect(screen, CUBE_TYPES[cube["type"]]["color"],
                             to_rect(cube["rect"]).inflate(-6, -6))
        # ----- Draw every powerup -----
        for powerup in game.powerups:
            pygame.draw.rect(screen, (255, 255, 255),
                             to_rect(powerup["rect"]))
            pygame.draw.rect(screen, (0, 220, 255),
                             to_rect(powerup["rect"]).inflate(-6, -6))
        # ----- Draw every friendly unit -----
        for unit in game.units:
            if not draw_unit_image(screen, unit, unit_images):
                if unit["type"] == "tank":
                    color = (25, 85, 35)
                else:
                    color = (70, 115, 70)
                pygame.draw.rect(screen, color, to_rect(unit["rect"]))
        # ----- Draw every projectile -----
        for projectile in game.projectiles:
            if projectile["type"] == "tank":
                pygame.draw.rect(screen, (255, 245, 80),
                                 to_rect(projectile["rect"]))
                pygame.draw.rect(screen, (255, 115, 0),
                                 to_rect(projectile["rect"]), 3)
            else:
                pygame.draw.rect(screen, (30, 255, 255),
                                 to_rect(projectile["rect"]))
        # ----- Draw timer and unit counts -----
        timer_text = small_font.render(format_time(game.total_time), True,
                                       (255, 255, 255))
        screen.blit(timer_text, timer_text.get_rect(topright=(990, 10)))
        infantry_count = sum(u["type"] == "infantry" for u in game.units)
        tank_count = sum(u["type"] == "tank" for u in game.units)
        unit_text = tiny_font.render(
            f"Level: {game.level_index + 1}/{len(LEVELS)}   "
            f"Infantry: {infantry_count}   Tanks: {tank_count}",
            True, (255, 255, 255))
        screen.blit(unit_text, (10, 10))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()