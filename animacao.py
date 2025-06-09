def show_jarvis_loading(duration=3):
    """Animação de loading futurista estilo J.A.R.V.I.S."""
    width, height = 800, 400
    screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
    pygame.display.set_caption(f"{ASSISTANT_NAME} - Inicialização")
    
    bg_color = (2, 4, 15)
    primary_color = (0, 200, 255)
    secondary_color = (0, 120, 200)
    pulse_color = (0, 255, 255)
    text_color = (150, 230, 255)
    
    try:
        font_large = pygame.font.Font(None, 52)
        font_medium = pygame.font.Font(None, 28)
    except:
        font_large = pygame.font.SysFont('consolas', 52)
        font_medium = pygame.font.SysFont('consolas', 28)
    
    try:
        pygame.mixer.music.load("startup_sound.mp3")
        pygame.mixer.music.play()
    except:
        pass

    start_time = time.time()
    center_x, center_y = width // 2, height // 2
    radius = 110

    particles = []  # Lista de partículas
    running = True

    while running:
        current_time = time.time() - start_time
        progress = min(1.0, current_time / duration)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        screen.fill(bg_color)

        # === Fundo com linhas circulares ===
        for i in range(0, 360, 15):
            angle = math.radians(i)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            pygame.draw.line(screen, (0, 80, 120), (center_x, center_y), (x, y), 1)

        # === Anel de progresso com camada dupla ===
        progress_angle = -math.pi/2 + 2 * math.pi * progress
        pygame.draw.circle(screen, (0, 80, 100), (center_x, center_y), radius + 15, 1)
        pygame.draw.arc(screen, primary_color,
                        (center_x - radius, center_y - radius, radius * 2, radius * 2),
                        -math.pi/2, progress_angle, 6)

        pygame.draw.arc(screen, secondary_color,
                        (center_x - radius - 10, center_y - radius - 10, (radius + 10) * 2, (radius + 10) * 2),
                        -math.pi/2, progress_angle, 2)

        # === Partículas circulando ===
        if progress < 1:
            for _ in range(2):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.5, 1.5)
                particles.append({
                    'angle': angle,
                    'radius': radius,
                    'speed': speed,
                    'size': random.randint(2, 4)
                })

        new_particles = []
        for p in particles:
            p['angle'] += p['speed'] * 0.01
            x = center_x + p['radius'] * math.cos(p['angle'])
            y = center_y + p['radius'] * math.sin(p['angle'])
            pygame.draw.circle(screen, pulse_color, (int(x), int(y)), p['size'])
            if 0 < x < width and 0 < y < height:
                new_particles.append(p)
        particles = new_particles

        # === Núcleo pulsante ===
        pulse = int(10 + 5 * math.sin(current_time * 5))
        pygame.draw.circle(screen, pulse_color, (center_x, center_y), pulse)

        # === Nome do assistente ===
        text = font_large.render(ASSISTANT_NAME.upper(), True, primary_color)
        screen.blit(text, (center_x - text.get_width() // 2, center_y - 140))

        # === Status ===
        status = font_medium.render(f"Inicializando... {int(progress * 100)}%", True, text_color)
        screen.blit(status, (center_x - status.get_width() // 2, center_y + radius + 40))

        pygame.display.flip()

        if progress >= 1.0:
            time.sleep(0.5)
            running = False

        time.sleep(0.016)  # 60 FPS
    
    pygame.quit()