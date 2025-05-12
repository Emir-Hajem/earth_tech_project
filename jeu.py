import pygame
import pytmx
import time
import random

pygame.init()

# Fenêtre
screen = pygame.display.set_mode((1000, 650))
pygame.display.set_caption("Maison Jeu")

# Charger la carte
tmx_data = pytmx.load_pygame('map/maison.tmx')

# Charger les collisions
collision_rects = []
for obj in tmx_data.objects:
    if hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'width') and hasattr(obj, 'height'):
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        collision_rects.append(rect)

# Caractéristiques du joueur
player_color = (0, 255, 0)
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

# Gestion des lumières
lights_on = []
light_timers = {}  # Nouveau : pour stocker l'heure d'allumage
lights_turned_off = 0
current_light = None

# Minuteur
font = pygame.font.SysFont("Arial", 20)
start_time = time.time()
game_duration = 60
game_over = False
result_text = ""

# Ajouter une page d'introduction
def show_intro_screen():
    intro_font = pygame.font.SysFont("Comic Sans MS", 40)  # Utilisation d'une belle police
    instructions_font = pygame.font.SysFont("Arial", 24)

    # Charger une image de fond pour l'introduction (modifier l'image selon ton choix)
    intro_background = pygame.image.load("background.png")  # Remplacer par ton image de fond
    intro_background = pygame.transform.scale(intro_background, (1000, 650))

    screen.blit(intro_background, (0, 0))

    # Texte principal
    title_text = intro_font.render("Bienvenue dans le Jeu des Lumières!", True, (255, 255, 255))
    screen.blit(title_text, ((screen.get_width() - title_text.get_width()) // 2, screen.get_height() // 4))

    # Explication du jeu
    instructions_text = instructions_font.render(
        "But du jeu : éteindre les lumières allumées dans la maison", True, (255, 255, 255))
    screen.blit(instructions_text, ((screen.get_width() - instructions_text.get_width()) // 2, screen.get_height() // 2))

    # Instructions supplémentaires
    more_instructions_text = instructions_font.render(
        "Utilisez les flèches pour vous déplacer et la barre espace pour éteindre les lumières.", True, (255, 255, 255))
    screen.blit(more_instructions_text, ((screen.get_width() - more_instructions_text.get_width()) // 2, screen.get_height() // 2 + 40))

    # Appuyer sur une touche pour commencer
    start_text = instructions_font.render("Appuyez sur une touche pour commencer...", True, (255, 255, 255))
    screen.blit(start_text, ((screen.get_width() - start_text.get_width()) // 2, screen.get_height() // 1.5))

    pygame.display.flip()

    # Attendre que l'utilisateur appuie sur une touche
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Lancer l'écran d'introduction avant de commencer le jeu
show_intro_screen()

# Boucle principale
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
    if keys[pygame.K_LEFT]:
        dx -= player_speed
    if keys[pygame.K_RIGHT]:
        dx += player_speed
    if keys[pygame.K_UP]:
        dy -= player_speed
    if keys[pygame.K_DOWN]:
        dy += player_speed

    # Test de collision
    next_rect = pygame.Rect(player_x + dx, player_y + dy, player_width, player_height)
    can_move = True
    for block in collision_rects:
        if next_rect.colliderect(block):
            can_move = False
            break

    if can_move:
        player_x += dx
        player_y += dy

    # Éteindre la lumière si joueur appuie sur espace et est dessus
    if keys[pygame.K_SPACE] and current_light:
        light_rect = pygame.Rect(current_light[0], current_light[1], 35, 35)
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        if light_rect.colliderect(player_rect):
            lights_on.remove(current_light)
            del light_timers[current_light]
            current_light = None
            lights_turned_off += 1
            time.sleep(0.2)

    # Éteindre automatiquement les lumières après 6 secondes
    for light in lights_on[:]:  # copie pour pouvoir modifier la liste
        if time.time() - light_timers.get(light, 0) >= 6:
            lights_on.remove(light)
            if light == current_light:
                current_light = None
            del light_timers[light]

    # Allumer une nouvelle lumière si aucune active
    if not current_light and not game_over:
        available = [l for l in lights_positions if l not in lights_on]
        if available:
            new_light = random.choice(available)
            lights_on.append(new_light)
            light_timers[new_light] = time.time()
            current_light = new_light

    # Afficher la carte
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    # Ombre
    darkness = pygame.Surface((1000, 650), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, 180))
    for light in lights_on:
        pygame.draw.circle(darkness, (0, 0, 0, 0), (int(light[0]) + 17, int(light[1]) + 17), 70)
    screen.blit(darkness, (0, 0))

    # Lumières
    for light in lights_on:
        screen.blit(light_img, (light[0], light[1]))

        # Joueur (corps beige, cheveux marrons, yeux blancs)
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    pygame.draw.rect(screen, (245, 222, 179), player_rect)  # Corps beige (Wheat)

    # Cheveux marron
    hair_height = player_height // 3
    pygame.draw.rect(screen, (139, 69, 19), (player_x, player_y, player_width, hair_height))

    # Yeux blancs
    eye_radius = 2
    eye_offset_x = 3
    eye_y = player_y + player_height // 2
    pygame.draw.circle(screen, (255, 255, 255), (int(player_x + eye_offset_x), eye_y), eye_radius)
    pygame.draw.circle(screen, (255, 255, 255), (int(player_x + player_width - eye_offset_x), eye_y), eye_radius)

    # Coordonnées joueur
    coords_text = font.render(f"Coordonnées: ({player_x:.1f}, {player_y:.1f})", True, (255, 255, 255))
    screen.blit(coords_text, (10, screen.get_height() - 30))

    # Score et temps
    score_text = font.render(f"Lumières éteintes : {lights_turned_off}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    timer_text = font.render(f"Temps restant : {time_left}s", True, (255, 255, 255))
    screen.blit(timer_text, (screen.get_width() - timer_text.get_width() - 10, 10))

    # Fin de partie
    if time_left <= 0 and not game_over:
        game_over = True
        if lights_turned_off >= 10:
            result_text = "Victoire !"
        else:
            result_text = "Défaite..."
        result_rendered = font.render(f"{result_text} Score final : {lights_turned_off}", True, (255, 255, 0))

    if game_over:
        screen.blit(result_rendered, (
            (screen.get_width() - result_rendered.get_width()) // 2,
            (screen.get_height() - result_rendered.get_height()) // 2
        ))

    pygame.display.flip()

pygame.quit()
