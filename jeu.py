import pygame
clock = pygame.time.Clock()
import pytmx
import time
import random
import sys
import math
pygame.init()
volume = 0.5  # Valeur par défaut du volume (50%)
child_font = pygame.font.SysFont("Comic Sans MS", 20, bold=True)
font = pygame.font.SysFont("Arial", 28)

# Fenêtre
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maison Jeu")

background_img = pygame.image.load("background.png").convert()

# Musique (exemple)
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

is_paused = False  # Le jeu n'est pas en pause à l'initialisation.


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
    rules_running = True

    # Polices
    title_font = pygame.font.SysFont("Segoe UI", 50, bold=True)
    text_font = pygame.font.SysFont("Segoe UI", 22)
    bold_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
    subtitle_font = pygame.font.SysFont("Segoe UI", 32, italic=True)

    # Couleurs sobres
    bg_color = (245, 245, 245)       # gris très clair
    text_color = (40, 40, 40)        # gris foncé
    highlight_color = (70, 130, 180) # bleu acier

    while rules_running:
        screen.fill(bg_color)

        # Titre (sans soulignement)
        title_text = "Règles du jeu"
        title = title_font.render(title_text, True, text_color)
        title_x = (WIDTH - title.get_width()) // 2
        screen.blit(title, (title_x, 40))

        # Règles du jeu (avec mots importants en gras)
        rules = [
            [("But du jeu :", True), (" éteins les lumières inutiles pour économiser l’énergie.", False)],
            [("Déplace-toi", True), (" avec les flèches du clavier.", False)],
            [("Quand une lumière est allumée,", False), (" place-toi dessus et appuie sur ESPACE pour l’éteindre.", True)],
            [("Tu disposes de 60 secondes", True), (" pour éteindre un maximum de lumières.", False)],
            [("Chaque geste compte", True), (" pour protéger la planète.", False)],
            [("Au bout de 10 lumières éteintes,", False), (" tu as gagné, mais ne t’arrête pas là !", True)],
        ]

        y_start = 100
        line_spacing = 55
        for i, line_parts in enumerate(rules):
            x = (WIDTH - 800) // 2  # centrage approximatif
            current_x = x
            for text, is_bold in line_parts:
                font_to_use = bold_font if is_bold else text_font
                rendered_text = font_to_use.render(text, True, text_color)
                screen.blit(rendered_text, (current_x, y_start + i * line_spacing))
                current_x += rendered_text.get_width()

        # Texte d’instruction pour revenir au menu
        tip = subtitle_font.render("Appuie sur ÉCHAP pour revenir au menu", True, highlight_color)
        screen.blit(tip, ((WIDTH - tip.get_width()) // 2, HEIGHT - 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                rules_running = False

        pygame.display.flip()


def close_options():
    global current_screen
    current_screen = "menu"
    return False  # pour couper la boucle

def draw_text_centered(text, y, size=28, color=(255, 255, 255)):
    font_local = pygame.font.SysFont("Arial", size)
    text_surface = font_local.render(text, True, color)
    x = (WIDTH - text_surface.get_width()) // 2
    screen.blit(text_surface, (x, y))


def options_screen():
    global volume
    global options_running
    options_running = True
    dragging = False
    slider_rect = pygame.Rect(300, 250, 200, 20)

    while options_running:
        screen.fill((30, 30, 60))
        draw_text_centered("Options", 100, size=40, color=(255, 255, 0))
        draw_text_centered(f"Volume: {int(volume * 100)}%", 200)

        # Slider
        draw_volume_slider(slider_rect.x, slider_rect.y, slider_rect.width, slider_rect.height, volume)

        # Gestion slider
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if click[0] and slider_rect.collidepoint(mouse):
            dragging = True
        if not click[0]:
            dragging = False
        if dragging:
            new_vol = (mouse[0] - slider_rect.x) / slider_rect.width
            volume = max(0.0, min(1.0, new_vol))
            pygame.mixer.music.set_volume(volume)

        # Bouton retour
        draw_rounded_button("Retour", 330, 350, 140, 50,
                            color=(100, 100, 255),
                            hover_color=(150, 150, 255),
                            action=lambda: setattr(sys.modules[__name__], 'options_running', False))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(60)

def draw_text(text, x, y, size=28, color=(255, 255, 255)):
    font_local = pygame.font.SysFont("Arial", size)
    text_surface = font_local.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_rounded_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, width, height)

    is_hovered = rect.collidepoint(mouse)
    pygame.draw.rect(screen, (0, 0, 0), rect.move(4, 4), border_radius=15)  # ombre
    pygame.draw.rect(screen, hover_color if is_hovered else color, rect, border_radius=15)

    text_surf = font.render(text, True, (255, 255, 255))
    screen.blit(text_surf, (x + (width - text_surf.get_width()) // 2,
                            y + (height - text_surf.get_height()) // 2))

    if is_hovered and click[0]:
        pygame.time.delay(200)
        if action:
            action()

def draw_volume_slider(x, y, width, height, volume):
    pygame.draw.rect(screen, (150, 150, 150), (x, y, width, height), border_radius=10)
    fill_width = int(volume * width)
    pygame.draw.rect(screen, (100, 200, 100), (x, y, fill_width, height), border_radius=10)
    pygame.draw.circle(screen, (255, 255, 255), (x + fill_width, y + height // 2), height // 2)

def exit_options():
    global current_screen
    current_screen = "menu"


def change_volume(amount):
    global volume
    volume = max(0.0, min(1.0, volume + amount))
    pygame.mixer.music.set_volume(volume)


def exit_screen():
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))

def show_main_menu():
    background = pygame.image.load("background.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    menu_running = True

    # Variables pour animation titre
    title_base_size = 40
    title_anim_time = 0

    # Pour gérer le délai entre clics (anti double clic)
    click_cooldown = 300  # ms
    last_click_time = 0

    while menu_running:
        dt = clock.tick(60)
        title_anim_time += dt / 1000  # secondes

        screen.blit(background, (0, 0))

        # Animation légère sur la taille du titre
        anim_scale = 1 + 0.05 * math.sin(title_anim_time * 3)  # oscillation sinusoïdale
        title_font_size = int(title_base_size * anim_scale)
        title_font = pygame.font.SysFont("Comic Sans MS", title_font_size, bold=True)
        title = title_font.render("Jeu des Lumières", True, (255, 255, 255))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 80))

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        # Liste de boutons : (texte, y, couleur normale, couleur survol, fonction)
        buttons = [
            ("Jouer", 200, (0, 100, 0), (0, 180, 0), lambda: exit_screen()),
            ("Règles du jeu", 270, (0, 0, 100), (0, 0, 180), rules_screen),
            ("Options", 340, (100, 100, 0), (180, 180, 0), options_screen),
            ("Quitter", 410, (150, 0, 0), (220, 0, 0), lambda: pygame.quit() or sys.exit())
        ]

        # Dessin boutons avec agrandissement au survol
        for text, y, color, hover_color, action in buttons:
            text_surf = font.render(text, True, (255, 255, 255))
            width, height = 220, 55
            x = (WIDTH - width) // 2
            rect = pygame.Rect(x, y, width, height)
            is_hovered = rect.collidepoint(mouse)

            # Effet agrandissement sur hover
            scale = 1.1 if is_hovered else 1.0
            scaled_width = int(width * scale)
            scaled_height = int(height * scale)
            scaled_x = x - (scaled_width - width) // 2
            scaled_y = y - (scaled_height - height) // 2
            scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)

            # Ombre
            pygame.draw.rect(screen, (0, 0, 0), scaled_rect.move(4, 4), border_radius=15)
            # Bouton
            pygame.draw.rect(screen, hover_color if is_hovered else color, scaled_rect, border_radius=15)

            # Texte centré sur bouton (avec scaling inversé pour ne pas agrandir le texte)
            text_pos = (scaled_x + (scaled_width - text_surf.get_width()) // 2,
                        scaled_y + (scaled_height - text_surf.get_height()) // 2)
            screen.blit(text_surf, text_pos)

            # Détecter clic avec cooldown
            current_time = pygame.time.get_ticks()
            if is_hovered and click[0] and current_time - last_click_time > click_cooldown:
                last_click_time = current_time
                pygame.time.delay(150)
                action()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu_running = False

        pygame.display.flip()

def draw_pause_menu():
    # Affiche un fond transparent sombre
    pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pause_overlay.fill((0, 0, 0, 180))  # Fond semi-transparent
    screen.blit(pause_overlay, (0, 0))

    # Dessine "Pause" au centre
    pause_font = pygame.font.SysFont("Segoe UI", 50, bold=True)
    pause_text = pause_font.render("Pause", True, (255, 255, 255))
    screen.blit(pause_text, ((WIDTH - pause_text.get_width()) // 2, HEIGHT // 3))

    # Dessin des boutons
    button_width, button_height = 200, 50
    button_x = (WIDTH - button_width) // 2
    button_y_start = HEIGHT // 2

    # Boutons
    buttons = [
        ("Reprendre", lambda: toggle_pause()),
        ("Paramètres", options_screen),
        ("Quitter", lambda: pygame.quit() or sys.exit())
    ]

    for i, (text, action) in enumerate(buttons):
        # Position des boutons en colonne
        button_y = button_y_start + (i * (button_height + 10))
        rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Détecter survol et clic
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 100, 255), rect, border_radius=15)
            if mouse_click[0]:
                pygame.time.delay(200)
                action()  # Exécute l'action liée au bouton
        else:
            pygame.draw.rect(screen, (70, 70, 150), rect, border_radius=15)

        # Texte du bouton
        text_font = pygame.font.SysFont("Arial", 30)
        text_surface = text_font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2,
                                   rect.y + (rect.height - text_surface.get_height()) // 2))

def draw_text_with_background(text, font, fg_color, bg_color, pos, screen):
    text_surface = font.render(text, True, fg_color)
    shadow_surface = font.render(text, True, (0, 0, 0))

    x, y = pos
    padding = 3  # Reduced padding from 5 to 3
    rect = text_surface.get_rect(topleft=(x - padding, y - padding))
    rect.inflate_ip(padding * 2, padding * 2)
    pygame.draw.rect(screen, bg_color, rect, border_radius=10) # Maybe reduce border_radius too

    screen.blit(shadow_surface, (x + 1, y + 1)) # Adjusted shadow offset
    screen.blit(text_surface, (x, y))

def toggle_pause():
    global is_paused
    is_paused = not is_paused


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

running = True
clock = pygame.time.Clock()
#boucle du jeu

for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            is_paused = not is_paused  # Bascule entre pause et actif


while running:
    dt = clock.tick(60)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Appui sur ECHAP
                toggle_pause()

    # Si le jeu est en pause, afficher le menu pause
    if is_paused:
        draw_pause_menu()
        pygame.display.flip()
        continue  # Passer le reste de la boucle pour garder le jeu en pause

    # Si le jeu n'est pas terminé et actif
    if not game_over:
        screen.fill((0, 0, 0))  # Effacer l'écran

        # Temps écoulé
        current_time = time.time()
        elapsed_time = int(current_time - start_time)
        time_left = max(0, game_duration - elapsed_time)

        # Vérifier si le temps est écoulé
        if time_left == 0:
            game_over = True

        # Gestion des touches (déplacement joueur)
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx -= player_speed
        if keys[pygame.K_RIGHT]: dx += player_speed
        if keys[pygame.K_UP]: dy -= player_speed
        if keys[pygame.K_DOWN]: dy += player_speed

        # Déplacement avec gestion des collisions
        next_rect = pygame.Rect(player_x + dx, player_y + dy, player_width, player_height)
        if not any(next_rect.colliderect(block) for block in collision_rects):
            player_x += dx
            player_y += dy

        # Gestion des lumières
        if keys[pygame.K_SPACE] and current_light:
            light_rect = pygame.Rect(current_light[0], current_light[1], 35, 35)
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            if light_rect.colliderect(player_rect):
                lights_on.remove(current_light)
                del light_timers[current_light]
                current_light = None
                lights_turned_off += 1
                time.sleep(0.2)

        # Timer extinction automatique
        for light in lights_on[:]:
            if time.time() - light_timers.get(light, 0) >= 6:
                lights_on.remove(light)
                lights_turned_off -= 1
                if light == current_light:
                    current_light = None
                del light_timers[light]

        # Nouveau courant lumineux
        if not current_light:
            available = [l for l in lights_positions if l not in lights_on]
            if available:
                new_light = random.choice(available)
                lights_on.append(new_light)
                light_timers[new_light] = time.time()
                current_light = new_light

        # Affichage des graphiques (carte, lumières, joueur, etc.)
        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

        # Ombres et lumières
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

        # Affichage des informations
        draw_text_with_background(f"Lumières éteintes : {lights_turned_off}", child_font, (255, 255, 255),
                                  (255, 140, 0),
                                  (10, 10), screen)
        draw_text_with_background(f"Temps restant : {time_left}s", child_font, (255, 255, 255), (255, 140, 0),
                                  (700, 10),
                                  screen)
    else:
        # Affiche fond
        screen.blit(background_img, (1000, 650))

        # Polices
        big_font = pygame.font.SysFont("impact", 40, bold=False)
        score_font = pygame.font.SysFont("comicsansms", 60, italic=True)
        message_font = pygame.font.SysFont("arial", 35, italic=True)
        button_font = pygame.font.SysFont("arial", 30, bold=True)

        # Texte selon victoire ou défaite
        if lights_turned_off >= 10:
            title_text = "V I C T O I R E !"
            title_color = (0, 255, 0)  # vert vif
            message_text = "Bravo, tu as éteint toutes les lumières !"
        else:
            title_text = "D É F A I T E"
            title_color = (255, 0, 0)  # rouge vif
            message_text = "Essaie encore, tu peux mieux faire !"

        # Rendu textes
        title_surface = big_font.render(title_text, True, title_color)
        score_surface = score_font.render(f"Score : {lights_turned_off}", True, (0, 0, 255))  # bleu
        message_surface = message_font.render(message_text, True, (255, 255, 255))  # blanc

        # Position
        center_x = WIDTH // 2
        title_rect = title_surface.get_rect(center=(center_x, HEIGHT // 3))
        score_rect = score_surface.get_rect(center=(center_x, HEIGHT // 3 + 90))
        message_rect = message_surface.get_rect(center=(center_x, HEIGHT // 3 + 150))

        # Blit textes
        screen.blit(title_surface, title_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(message_surface, message_rect)

        # Bouton Quitter
        button_text = "Quitter"
        button_color = (200, 0, 0)
        button_hover_color = (255, 50, 50)
        button_rect = pygame.Rect(center_x - 70, HEIGHT // 3 + 220, 140, 50)

        # Souris
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Change couleur si survol
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, button_hover_color, button_rect)
            if mouse_pressed[0]:
                running = False  # Quitte le jeu si clique
        else:
            pygame.draw.rect(screen, button_color, button_rect)

        # Texte bouton centré
        button_surface = button_font.render(button_text, True, (255, 255, 255))
        button_text_rect = button_surface.get_rect(center=button_rect.center)
        screen.blit(button_surface, button_text_rect)

    pygame.display.flip()

pygame.quit()
