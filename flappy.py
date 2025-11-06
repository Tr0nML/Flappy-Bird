import pygame, random, sys, os, math
from pygame.locals import (
    QUIT, KEYDOWN, K_q, K_ESCAPE, K_F11, K_f, K_SPACE, K_UP, K_r, MOUSEBUTTONDOWN
)

# === CONFIG ===
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 6
GRAVITY = 0.6
GAME_SPEED = 5
FPS = 60

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100
PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150

# === RESOURCE LOADER ===
def resource_path(relative_path):
    """PyInstaller-safe path resolver."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# === INITIALIZATION ===
pygame.init()
audio_available = True
try:
    pygame.mixer.init()
except Exception:
    audio_available = False
    print("No audio device found — running silently.")

is_fullscreen = False
game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird by Tanmay")
clock = pygame.time.Clock()


# === ASSETS ===
BACKGROUND = pygame.image.load(
    resource_path("assets/sprites/background-day.png")
).convert()
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load(
    resource_path("assets/sprites/message.png")
).convert_alpha()

BIRD_IMAGES = [
    pygame.image.load(resource_path(f"assets/sprites/bluebird-{name}flap.png")).convert_alpha()
    for name in ("up", "mid", "down")
]

PIPE_IMAGE_BASE = pygame.image.load(
    resource_path("assets/sprites/pipe-green.png")
).convert_alpha()
PIPE_IMAGE_BASE = pygame.transform.scale(PIPE_IMAGE_BASE, (PIPE_WIDTH, PIPE_HEIGHT))

GROUND_IMAGE = pygame.image.load(
    resource_path("assets/sprites/base.png")
).convert_alpha()
GROUND_IMAGE = pygame.transform.scale(GROUND_IMAGE, (GROUND_WIDTH, GROUND_HEIGHT))

NUMBER_IMAGES = [
    pygame.image.load(resource_path(f"assets/sprites/{i}.png")).convert_alpha()
    for i in range(10)
]

# === SOUNDS ===
def load_sound(path):
    if not audio_available:
        return None
    try:
        return pygame.mixer.Sound(resource_path(path))
    except Exception:
        return None

wing_snd = load_sound("assets/audio/wing.wav")
hit_snd = load_sound("assets/audio/hit.wav")
point_snd = load_sound("assets/audio/point.wav")


# === CLASSES ===
class Bird(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.images = images
        self.speed = SPEED
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH / 6
        self.rect.y = SCREEN_HEIGHT / 2
        self.idle_angle = 0

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect.y += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        """Idle animation with soft bobbing."""
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.idle_angle += 0.1
        self.rect.y = SCREEN_HEIGHT / 2 + 10 * math.sin(self.idle_angle)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize, image):
        super().__init__()
        self.inverted = inverted
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.y = -(self.rect.height - ysize)
        else:
            self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - ysize
        self.mask = pygame.mask.from_surface(self.image)
        self.scored = False

    def update(self):
        self.rect.x -= GAME_SPEED


class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= GAME_SPEED


# === HELPERS ===
def is_off_screen(sprite):
    return sprite.rect.right < 0


def get_random_pipes(xpos, image):
    play_height = SCREEN_HEIGHT - GROUND_HEIGHT
    min_top = 80
    max_top = play_height - PIPE_GAP - 80
    top_height = random.randint(min_top, max_top)
    bottom_height = play_height - PIPE_GAP - top_height
    bottom = Pipe(False, xpos, bottom_height, image)
    top = Pipe(True, xpos, top_height, image)
    return bottom, top


def display_score(surface, score):
    digits = [int(x) for x in str(score)]
    total_w = sum(NUMBER_IMAGES[d].get_width() for d in digits)
    x = (SCREEN_WIDTH - total_w) / 2
    y = SCREEN_HEIGHT * 0.1
    for d in digits:
        surface.blit(NUMBER_IMAGES[d], (x, y))
        x += NUMBER_IMAGES[d].get_width()


def render_center_text(text, y, size=32, color=(255, 255, 255)):
    font = pygame.font.Font(None, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, int(y)))
    return surf, rect


def reset_game():
    bird = Bird(BIRD_IMAGES)
    bird_group = pygame.sprite.GroupSingle(bird)
    ground_group = pygame.sprite.Group(
        Ground(0, GROUND_IMAGE),
        Ground(GROUND_WIDTH, GROUND_IMAGE)
    )
    pipe_group = pygame.sprite.Group()
    for i in range(2):
        p_bottom, p_top = get_random_pipes(SCREEN_WIDTH + i * 300, PIPE_IMAGE_BASE)
        pipe_group.add(p_bottom, p_top)
    return bird, bird_group, ground_group, pipe_group, 0


def toggle_fullscreen():
    global screen, is_fullscreen
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird by Tanmay")


def render_scaled_game():
    """Render the game surface stretched to fill the fullscreen display."""
    screen.fill((0, 0, 0))
    if is_fullscreen:
        sw, sh = screen.get_size()
        stretched_surface = pygame.transform.smoothscale(game_surface, (sw, sh))
        screen.blit(stretched_surface, (0, 0))
    else:
        screen.blit(game_surface, (0, 0))



# !== MAIN LOOP !==
bird, bird_group, ground_group, pipe_group, score = reset_game()
state = "BEGIN"
running = True

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key in (K_q, K_ESCAPE):
                running = False
            elif event.key in (K_F11, K_f):
                toggle_fullscreen()
            elif state == "BEGIN" and event.key in (K_SPACE, K_UP):
                bird.bump()
                if wing_snd: wing_snd.play()
                state = "PLAYING"
            elif state == "PLAYING" and event.key in (K_SPACE, K_UP):
                bird.bump()
                if wing_snd: wing_snd.play()
            elif state == "GAME_OVER" and event.key in (K_r, K_SPACE, K_UP):
                bird, bird_group, ground_group, pipe_group, score = reset_game()
                state = "BEGIN"
        elif event.type == MOUSEBUTTONDOWN:
            if state == "BEGIN":
                bird.bump()
                if wing_snd: wing_snd.play()
                state = "PLAYING"
            elif state == "PLAYING":
                bird.bump()
                if wing_snd: wing_snd.play()

    # === STATE HANDLERS ===
    if state == "BEGIN":
        game_surface.blit(BACKGROUND, (0, 0))
        game_surface.blit(BEGIN_IMAGE, (120, 150))
        bird.begin()
        ground_group.update()
        ground_group.draw(game_surface)
        bird_group.draw(game_surface)
        display_score(game_surface, 0)
        hint_surf, hint_rect = render_center_text(
            "Press F11 for Fullscreen", SCREEN_HEIGHT * 0.85, 24, (200, 200, 200)
        )
        game_surface.blit(hint_surf, hint_rect)
        render_scaled_game()
        pygame.display.flip()
        continue

    if state == "PLAYING":
        game_surface.blit(BACKGROUND, (0, 0))

        # recycle ground
        first_ground = ground_group.sprites()[0]
        if is_off_screen(first_ground):
            ground_group.remove(first_ground)
            last_x = max(g.rect.right for g in ground_group)
            ground_group.add(Ground(last_x, GROUND_IMAGE))

        # recycle pipes safely in pairs
        leftmost = sorted(pipe_group, key=lambda p: p.rect.x)[0]
        if is_off_screen(leftmost):
            for _ in range(2):
                pipe_group.remove(sorted(pipe_group, key=lambda p: p.rect.x)[0])
            new_bottom, new_top = get_random_pipes(SCREEN_WIDTH + 100, PIPE_IMAGE_BASE)
            pipe_group.add(new_bottom, new_top)

        # physics and draw
        bird_group.update()
        ground_group.update()
        pipe_group.update()

        pipe_group.draw(game_surface)
        ground_group.draw(game_surface)
        bird_group.draw(game_surface)

        # scoring
        bird_mid = bird.rect.centerx
        for p in pipe_group:
            if not p.inverted:
                p_mid = p.rect.centerx
                if p_mid <= bird_mid < p_mid + GAME_SPEED and not p.scored:
                    p.scored = True
                    score += 1
                    if point_snd: point_snd.play()

        display_score(game_surface, score)
        render_scaled_game()
        pygame.display.flip()

        # collisions and top death
        hit_ground = pygame.sprite.spritecollide(bird, ground_group, False, pygame.sprite.collide_mask)
        hit_pipe = pygame.sprite.spritecollide(bird, pipe_group, False, pygame.sprite.collide_mask)
        if hit_ground or hit_pipe or bird.rect.top <= 0:
            if hit_snd: hit_snd.play()
            state = "GAME_OVER"
        continue

    if state == "GAME_OVER":
        game_surface.blit(BACKGROUND, (0, 0))
        pipe_group.draw(game_surface)
        ground_group.draw(game_surface)
        bird_group.draw(game_surface)
        display_score(game_surface, score)
        title, rect = render_center_text("Game Over", SCREEN_HEIGHT * 0.3, 56)
        tip, rect2 = render_center_text("Press Space to Restart", SCREEN_HEIGHT * 0.45, 32)
        quit_t, rect3 = render_center_text("Press Q or Esc to Quit", SCREEN_HEIGHT * 0.52, 28)
        for s, r in [(title, rect), (tip, rect2), (quit_t, rect3)]:
            game_surface.blit(s, r)
        render_scaled_game()
        pygame.display.flip()

pygame.quit()
