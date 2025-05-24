import pygame
import pytmx
import time
import random
import sys

pygame.init()

# Fenêtre
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maison Jeu")

# Musique (exemple)
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Charger la carte
tmx_data = pytmx.load_pygame('map/maison.tmx')

# Charger les collisions
collision_rects = []
for obj in tmx_data.objects:
    if hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'width') and hasattr(obj, 'height'):
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        collision_rects.append(rect)

# Caractéristiques du joueur
player_width = 15
player_height = 15
player_x = 100
player_y = 100
player_speed = 3.5

# Coordonnées des lumières
lights_positions = [
    (215.5, 82.5), (513.0, 163.0), (569.0, 142.0), (544.5, 110.5),
    (642.5, 145.5), (730.0, 145.5), (810.5, 82.5), (880.5, 121.0),
    (810.5, 54.5), (765.0, 348.5), (838.5, 390.5), (765.0, 404.5),
    (842.0, 523.5), (702.0, 537.5), (425.5, 555.0), (467.5, 327.5),
    (184.0, 341.5), (86.0, 334.5)
]

# Image de la lumière
light_img = pygame.image.load('map/light.png').convert_alpha()
light_img = pygame.transform.scale(light_img, (35, 35))

# Fonts
font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Comic Sans MS", 40)

# Fonctions utilitaires
def draw_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, width, height)

    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, rect)
        if click[0] and action:
            pygame.time.delay(200)
            action()
    else:
        pygame.draw.rect(screen, color, rect)

    text_surf = font.render(text, True, (255, 255, 255))
    screen.blit(text_surf, (x + (width - text_surf.get_width()) // 2,
                            y + (height - text_surf.get_height()) // 2))

def rules_screen():
    running = True
    while running:
        screen.fill((30, 30, 30))
        rules = [
            "But du jeu : éteindre les lumières allumées dans la maison.",
            "Déplacez-vous avec les flèches directionnelles.",
            "Appuyez sur ESPACE quand vous êtes sur une lumière pour l’éteindre.",
            "Vous avez 60 secondes pour éteindre un maximum de lumières.",
            "",
            "Appuyez sur ÉCHAP pour revenir au menu."
        ]
        for i, line in enumerate(rules):
            rendered = font.render(line, True, (255, 255, 255))
            screen.blit(rendered, (50, 100 + i * 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        pygame.display.flip()

def options_screen():
    running = True
    volume = pygame.mixer.music.get_volume()

    while running:
        screen.fill((50, 50, 50))
        title = big_font.render("Options", True, (255, 255, 255))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))

        vol_text = font.render(f"Volume musique : {int(volume * 100)}%", True, (255, 255, 255))
        screen.blit(vol_text, (WIDTH // 2 - 100, 200))

        draw_button("-", WIDTH // 2 - 80, 240, 40, 40, (100, 100, 100), (150, 150, 150),
                    lambda: change_volume(-0.1))
        draw_button("+", WIDTH // 2 + 40, 240, 40, 40, (100, 100, 100), (150, 150, 150),
                    lambda: change_volume(0.1))
        draw_button("Retour", WIDTH // 2 - 60, 320, 120, 40, (100, 0, 0), (150, 0, 0),
                    lambda: exit_screen())

        volume = pygame.mixer.music.get_volume()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        pygame.display.flip()

def change_volume(amount):
    volume = pygame.mixer.music.get_volume()
    volume = max(0.0, min(1.0, volume + amount))
    pygame.mixer.music.set_volume(volume)

def exit_screen():
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))

# Écran principal du menu
def show_main_menu():
    background = pygame.image.load("background.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    menu_running = True

    while menu_running:
        screen.blit(background, (0, 0))
        title = big_font.render("Jeu des Lumières", True, (255, 255, 255))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 80))

        draw_button("Jouer", 400, 200, 200, 50, (0, 100, 0), (0, 150, 0), lambda: exit_screen())
        draw_button("Règles du jeu", 400, 270, 200, 50, (0, 0, 100), (0, 0, 150), rules_screen)
        draw_button("Options", 400, 340, 200, 50, (100, 100, 0), (150, 150, 0), options_screen)
        draw_button("Quitter", 400, 410, 200, 50, (100, 0, 0), (150, 0, 0), lambda: pygame.quit() or sys.exit())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu_running = False

        pygame.display.flip()

# Lancer le menu
show_main_menu()

# Variables du jeu
lights_on = []
light_timers = {}
lights_turned_off = 0
current_light = None
start_time = time.time()
game_duration = 60
game_over = False
result_text = ""

# Boucle principale du jeu
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60)
    screen.fill((0, 0, 0))
    current_time = time.time()
    elapsed_time = int(current_time - start_time)
    time_left = max(0, game_duration - elapsed_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]: dx -= player_speed
    if keys[pygame.K_RIGHT]: dx += player_speed
    if keys[pygame.K_UP]: dy -= player_speed
    if keys[pygame.K_DOWN]: dy += player_speed

    # Déplacement avec collisions
    next_rect = pygame.Rect(player_x + dx, player_y + dy, player_width, player_height)
    if not any(next_rect.colliderect(block) for block in collision_rects):
        player_x += dx
        player_y += dy

    # Éteindre la lumière
    if keys[pygame.K_SPACE] and current_light:
        light_rect = pygame.Rect(current_light[0], current_light[1], 35, 35)
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        if light_rect.colliderect(player_rect):
            lights_on.remove(current_light)
            del light_timers[current_light]
            current_light = None
            lights_turned_off += 1
            time.sleep(0.2)

    # Timer d’extinction auto
    for light in lights_on[:]:
        if time.time() - light_timers.get(light, 0) >= 6:
            lights_on.remove(light)
            if light == current_light:
                current_light = None
            del light_timers[light]

    # Nouvelle lumière
    if not current_light and not game_over:
        available = [l for l in lights_positions if l not in lights_on]
        if available:
            new_light = random.choice(available)
            lights_on.append(new_light)
            light_timers[new_light] = time.time()
            current_light = new_light

    # Affichage carte
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    # Ombres + lumières
    darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, 180))
    for light in lights_on:
        pygame.draw.circle(darkness, (0, 0, 0, 0), (int(light[0]) + 17, int(light[1]) + 17), 70)
        screen.blit(light_img, (light[0], light[1]))
    screen.blit(darkness, (0, 0))

    # Joueur
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    pygame.draw.rect(screen, (245, 222, 179), player_rect)
    pygame.draw.rect(screen, (139, 69, 19), (player_x, player_y, player_width, player_height // 3))
    eye_y = player_y + player_height // 2
    pygame.draw.circle(screen, (255, 255, 255), (int(player_x + 3), eye_y), 2)
    pygame.draw.circle(screen, (255, 255, 255), (int(player_x + player_width - 3), eye_y), 2)

    # Infos
    screen.blit(font.render(f"Lumières éteintes : {lights_turned_off}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Temps restant : {time_left}s", True, (255, 255, 255)), (WIDTH - 180, 10))

    if time_left <= 0 and not game_over:
        game_over = True
        result_text = "Victoire !" if lights_turned_off >= 10 else "Défaite..."
        result_rendered = font.render(f"{result_text} Score final : {lights_turned_off}", True, (255, 255, 0))

    if game_over:
        screen.blit(result_rendered, ((WIDTH - result_rendered.get_width()) // 2, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()
