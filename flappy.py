import pygame
import random 
import sys 
import os
import math
import json
import platform

from pygame.locals import (
    QUIT, KEYDOWN, K_q, K_l, K_ESCAPE, K_F11, K_f, K_SPACE, K_UP, K_r, MOUSEBUTTONDOWN, VIDEORESIZE
)

# === CONFIG ===
BASE_WIDTH = 400
BASE_HEIGHT = 600
SPEED = 6
GRAVITY = 0.6
GAME_SPEED = 5
FPS = 60

GROUND_HEIGHT = 100
PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150
PIPE_SPACING = 300

MAX_LEADERBOARD_ENTRIES = 10
def get_data_dir(app_name="FlappyBird"):
    system = platform.system()
    if system == "Windows":
        base = os.getenv('APPDATA') or os.path.expanduser("~\\AppData\\Roaming")
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.path.expanduser("~/.local/share")
    data_dir = os.path.join(base, app_name)
    try:
        os.makedirs(data_dir, exist_ok=True)
    except OSError:
        pass
    return data_dir

LEADERBOARD_FILE = os.path.join(get_data_dir("FlappyBird"), "flappy_scores.json")

# === RESOURCE LOADER ===
def resource_path(relative_path):
    """PyInstaller-safe path resolver."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# === LEADERBOARD ===
class Leaderboard:
    def __init__(self, max_entries=10):
        self.max_entries = max_entries
        self.scores = []
        self.load()
    
    def load(self):
        """Load scores from file."""
        try:
            if os.path.exists(LEADERBOARD_FILE):
                with open(LEADERBOARD_FILE, 'r') as f:
                    data = json.load(f)
                    self.scores = data.get('scores', [])
        except Exception as e:
            print(f"Could not load leaderboard: {e}")
            self.scores = []
    
    def save(self):
        """Save scores to file."""
        try:
            with open(LEADERBOARD_FILE, 'w') as f:
                json.dump({'scores': self.scores}, f, indent=2)
        except Exception as e:
            print(f"Could not save leaderboard: {e}")
    
    def add_score(self, score):
        """Add a score and return its rank (1-indexed), or None if not in top scores."""
        if score <= 0:
            return None
        
        self.scores.append(score)
        self.scores.sort(reverse=True)
        self.scores = self.scores[:self.max_entries]
        
        if score in self.scores:
            rank = self.scores.index(score) + 1
            self.save()
            return rank
        return None
    
    def get_top_scores(self):
        """Return list of top scores."""
        return self.scores.copy()
    
    def is_high_score(self, score):
        """Check if score would make it to leaderboard."""
        if len(self.scores) < self.max_entries:
            return score > 0
        return score > min(self.scores)


# === INITIALIZATION ===
pygame.init()
audio_available = True
try:
    pygame.mixer.init()
except Exception:
    audio_available = False
    print("No audio device found – running silently.")

is_fullscreen = False
current_width = BASE_WIDTH
current_height = BASE_HEIGHT
screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bird by Tanmay")
clock = pygame.time.Clock()

leaderboard = Leaderboard(MAX_LEADERBOARD_ENTRIES)


# === ASSETS ===
BACKGROUND_ORIGINAL = pygame.image.load(
    resource_path("assets/sprites/background-day.png")
).convert()

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

GROUND_IMAGE_TILE = pygame.image.load(
    resource_path("assets/sprites/base.png")
).convert_alpha()

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


# === VIEWPORT FUNCTIONS ===
def get_viewport_width():
    """Get current viewport width."""
    return current_width

def get_viewport_height():
    """Get current viewport height (always BASE_HEIGHT)."""
    return BASE_HEIGHT

def create_background_surface(width):
    """Create a tiled background surface for the given width."""
    bg_scaled = pygame.transform.scale(BACKGROUND_ORIGINAL, (BASE_WIDTH, BASE_HEIGHT))
    tiles_needed = math.ceil(width / BASE_WIDTH) + 1
    bg_surface = pygame.Surface((tiles_needed * BASE_WIDTH, BASE_HEIGHT))
    for i in range(tiles_needed):
        bg_surface.blit(bg_scaled, (i * BASE_WIDTH, 0))
    return bg_surface

def create_ground_image(width):
    """Create a ground image for the given width."""
    tile_width = GROUND_IMAGE_TILE.get_width()
    scaled_tile = pygame.transform.scale(GROUND_IMAGE_TILE, (tile_width, GROUND_HEIGHT))
    tiles_needed = math.ceil(width / tile_width) + 2
    ground_surface = pygame.Surface((tiles_needed * tile_width, GROUND_HEIGHT))
    ground_surface = ground_surface.convert_alpha()
    for i in range(tiles_needed):
        ground_surface.blit(scaled_tile, (i * tile_width, 0))
    return ground_surface


# === CLASSES ===
class Bird(pygame.sprite.Sprite):
    def __init__(self, images, viewport_width):
        super().__init__()
        self.images = images
        self.speed = SPEED
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = viewport_width / 6
        self.rect.y = BASE_HEIGHT / 2
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
        self.rect.y = BASE_HEIGHT / 2 + 10 * math.sin(self.idle_angle)


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
            self.rect.y = BASE_HEIGHT - GROUND_HEIGHT - ysize
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
        self.rect.y = BASE_HEIGHT - GROUND_HEIGHT
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= GAME_SPEED


# === HELPERS ===
def is_off_screen(sprite):
    return sprite.rect.right < 0


def get_random_pipes(xpos, image):
    play_height = BASE_HEIGHT - GROUND_HEIGHT
    min_top = 80
    max_top = play_height - PIPE_GAP - 80
    top_height = random.randint(min_top, max_top)
    bottom_height = play_height - PIPE_GAP - top_height
    bottom = Pipe(False, xpos, bottom_height, image)
    top = Pipe(True, xpos, top_height, image)
    return bottom, top


def display_score(surface, score, viewport_width):
    digits = [int(x) for x in str(score)]
    total_w = sum(NUMBER_IMAGES[d].get_width() for d in digits)
    x = (viewport_width - total_w) / 2
    y = BASE_HEIGHT * 0.1
    for d in digits:
        surface.blit(NUMBER_IMAGES[d], (x, y))
        x += NUMBER_IMAGES[d].get_width()


def render_center_text(text, y, size=32, color=(255, 255, 255), viewport_width=BASE_WIDTH):
    font = pygame.font.Font(None, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(viewport_width // 2, int(y)))
    return surf, rect


def render_text_with_shadow(text, y, size=32, color=(255, 255, 255), viewport_width=BASE_WIDTH, shadow_offset=2):
    """Render text with a shadow for better visibility."""
    font = pygame.font.Font(None, size)
    
    # Create shadow
    shadow_surf = font.render(text, True, (0, 0, 0))
    shadow_rect = shadow_surf.get_rect(center=(viewport_width // 2 + shadow_offset, int(y) + shadow_offset))
    
    # Create main text
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(viewport_width // 2, int(y)))
    
    return shadow_surf, shadow_rect, text_surf, text_rect


def render_text_with_bg(surface, text, y, size=32, text_color=(255, 255, 255), 
                        bg_color=(0, 0, 0, 180), viewport_width=BASE_WIDTH, padding=10):
    """Render text with a semi-transparent background."""
    font = pygame.font.Font(None, size)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(viewport_width // 2, int(y)))
    
    # Create background rectangle
    bg_rect = text_rect.inflate(padding * 2, padding)
    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surf.fill(bg_color)
    
    surface.blit(bg_surf, bg_rect)
    surface.blit(text_surf, text_rect)


def reset_game(viewport_width):
    bird = Bird(BIRD_IMAGES, viewport_width)
    bird_group = pygame.sprite.GroupSingle(bird)
    
    ground_image = create_ground_image(viewport_width * 2)
    ground_group = pygame.sprite.Group(
        Ground(0, ground_image),
        Ground(ground_image.get_width(), ground_image)
    )
    
    pipe_group = pygame.sprite.Group()
    # Spawn enough pipes to fill the viewport + some extra
    num_pipes = math.ceil(viewport_width / PIPE_SPACING) + 1
    for i in range(num_pipes):
        p_bottom, p_top = get_random_pipes(viewport_width + i * PIPE_SPACING, PIPE_IMAGE_BASE)
        pipe_group.add(p_bottom, p_top)
    
    return bird, bird_group, ground_group, pipe_group, 0


def toggle_fullscreen():
    global screen, is_fullscreen, current_width, current_height
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        current_width, current_height = screen.get_size()
    else:
        current_width = BASE_WIDTH
        current_height = BASE_HEIGHT
        screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
    pygame.display.set_caption("Flappy Bird by Tanmay")


def render_leaderboard(surface, viewport_width, current_score=None, rank=None):
    """Render the leaderboard with enhanced UI."""
    top_scores = leaderboard.get_top_scores()
    
    # Create a semi-transparent panel for the leaderboard
    panel_width = min(500, viewport_width - 40)
    panel_height = 450
    panel_x = (viewport_width - panel_width) // 2
    panel_y = 75
    
    panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    # Dark background with border
    pygame.draw.rect(panel_surf, (20, 20, 40, 230), (0, 0, panel_width, panel_height), border_radius=15)
    pygame.draw.rect(panel_surf, (255, 215, 0), (0, 0, panel_width, panel_height), 3, border_radius=15)
    
    surface.blit(panel_surf, (panel_x, panel_y))
    
    # Title with shadow
    title_font = pygame.font.Font(None, 56)
    title_shadow = title_font.render("HIGH SCORES", True, (0, 0, 0))
    title_text = title_font.render("HIGH SCORES", True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(viewport_width // 2, panel_y + 40))
    surface.blit(title_shadow, title_rect.move(3, 3))
    surface.blit(title_text, title_rect)
    
    # Rank message if applicable
    if rank:
        rank_font = pygame.font.Font(None, 32)
        rank_text_str = f"🎉 You ranked #{rank}! 🎉"
        rank_surf = rank_font.render(rank_text_str, True, (100, 255, 100))
        rank_rect = rank_surf.get_rect(center=(viewport_width // 2, panel_y + 85))
        surface.blit(rank_surf, rank_rect)
        start_y = panel_y + 120
    else:
        start_y = panel_y + 85
    
    # Medal emojis for top 3
    medals = ["🥇", "🥈", "🥉"]
    
    # Render scores with enhanced styling
    score_font = pygame.font.Font(None, 32)
    for i, score in enumerate(top_scores[:10]):
        y_pos = start_y + i * 35
        
        # Determine color based on rank
        if i == 0:
            color = (255, 215, 0)  # Gold
        elif i == 1:
            color = (192, 192, 192)  # Silver
        elif i == 2:
            color = (205, 127, 50)  # Bronze
        else:
            color = (255, 255, 255)  # White
        
        # Highlight current score
        if current_score is not None and score == current_score and i + 1 == rank:
            # Draw highlight background
            highlight_surf = pygame.Surface((panel_width - 20, 32), pygame.SRCALPHA)
            highlight_surf.fill((100, 200, 100, 100))
            surface.blit(highlight_surf, (panel_x + 10, y_pos - 3))
            color = (150, 255, 150)
        
        # Format score text with medal for top 3
        if i < 3:
            score_text = f"{medals[i]} #{i+1}  {score} points"
        else:
            score_text = f"  #{i+1}  {score} points"
        
        # Render with shadow
        shadow_surf = score_font.render(score_text, True, (0, 0, 0))
        text_surf = score_font.render(score_text, True, color)
        text_x = panel_x + 30
        
        surface.blit(shadow_surf, (text_x + 2, y_pos + 2))
        surface.blit(text_surf, (text_x, y_pos))
    
    # Footer message
    if not top_scores:
        empty_font = pygame.font.Font(None, 28)
        empty_text = empty_font.render("No scores yet. Be the first!", True, (200, 200, 200))
        empty_rect = empty_text.get_rect(center=(viewport_width // 2, start_y + 150))
        surface.blit(empty_text, empty_rect)


# !== MAIN LOOP !==
viewport_width = get_viewport_width()
bird, bird_group, ground_group, pipe_group, score = reset_game(viewport_width)
background = create_background_surface(viewport_width)
state = "BEGIN"
running = True
show_leaderboard = False
final_rank = None

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == VIDEORESIZE:
            if not is_fullscreen:
                current_width = max(BASE_WIDTH, event.w)
                current_height = BASE_HEIGHT
                screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                viewport_width = get_viewport_width()
                background = create_background_surface(viewport_width)
                # Reset game with new viewport
                bird, bird_group, ground_group, pipe_group, score = reset_game(viewport_width)
                state = "BEGIN"
        elif event.type == KEYDOWN:
            if event.key in (K_q, K_ESCAPE):
                running = False
            elif event.key in (K_F11, K_f):
                toggle_fullscreen()
                viewport_width = get_viewport_width()
                background = create_background_surface(viewport_width)
                # Reset game with new viewport
                bird, bird_group, ground_group, pipe_group, score = reset_game(viewport_width)
                state = "BEGIN"
            elif state == "BEGIN" and event.key in (K_SPACE, K_UP):
                bird.bump()
                if wing_snd: 
                    wing_snd.play()
                state = "PLAYING"
                show_leaderboard = False
            elif state == "PLAYING" and event.key in (K_SPACE, K_UP):
                bird.bump()
                if wing_snd: 
                    wing_snd.play()
            elif state == "GAME_OVER" and event.key in (K_r, K_SPACE, K_UP):
                bird, bird_group, ground_group, pipe_group, score = reset_game(viewport_width)
                state = "BEGIN"
                show_leaderboard = False
                final_rank = None
            elif state in ("GAME_OVER", "BEGIN") and event.key == K_l:
                show_leaderboard = not show_leaderboard
        elif event.type == MOUSEBUTTONDOWN:
            if state == "BEGIN":
                bird.bump()
                if wing_snd: 
                    wing_snd.play()
                state = "PLAYING"
                show_leaderboard = False
            elif state == "PLAYING":
                bird.bump()
                if wing_snd: 
                    wing_snd.play()

    # Create game surface for current viewport
    game_surface = pygame.Surface((viewport_width, BASE_HEIGHT))

    # === STATE HANDLERS ===
    if state == "BEGIN":
        game_surface.blit(background, (0, 0))
        
        # Always update and draw bird and ground
        bird.begin()
        ground_group.update()
        ground_group.draw(game_surface)
        bird_group.draw(game_surface)
        display_score(game_surface, 0, viewport_width)
        
        if show_leaderboard:
            # Show leaderboard on begin screen
            render_leaderboard(game_surface, viewport_width)
            render_text_with_bg(game_surface, "Press L to hide | Space to Start", 
                              BASE_HEIGHT * 0.92, 24, (255, 255, 255), 
                              (0, 0, 0, 180), viewport_width, 8)
        else:
            msg_x = (viewport_width - BEGIN_IMAGE.get_width()) / 2
            game_surface.blit(BEGIN_IMAGE, (msg_x, 150))
            
            # Enhanced hint messages with backgrounds
            render_text_with_bg(game_surface, 
                              "F11: Fullscreen  |  Resize: See More World", 
                              BASE_HEIGHT * 0.78, 22, (100, 255, 255), 
                              (0, 0, 0, 180), viewport_width, 8)
            
            render_text_with_bg(game_surface, 
                              "Press L to view Leaderboard", 
                              BASE_HEIGHT * 0.85, 20, (255, 255, 100), 
                              (0, 0, 0, 180), viewport_width, 8)
            
            # Show high score with enhanced styling
            top_scores = leaderboard.get_top_scores()
            if top_scores:
                render_text_with_bg(game_surface, 
                                  f"🏆 High Score: {top_scores[0]}", 
                                  BASE_HEIGHT * 0.92, 26, (255, 215, 0), 
                                  (0, 0, 0, 200), viewport_width, 10)
        
        # Scale to screen
        if current_height != BASE_HEIGHT:
            scale_factor = current_height / BASE_HEIGHT
            scaled_width = int(viewport_width * scale_factor)
            game_surface = pygame.transform.scale(game_surface, (scaled_width, current_height))
        
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        continue

    if state == "PLAYING":
        game_surface.blit(background, (0, 0))

        # Recycle ground
        first_ground = ground_group.sprites()[0]
        if is_off_screen(first_ground):
            ground_group.remove(first_ground)
            last_x = max(g.rect.right for g in ground_group)
            ground_image = create_ground_image(viewport_width * 2)
            ground_group.add(Ground(last_x, ground_image))

        # Recycle pipes safely in pairs
        leftmost = sorted(pipe_group, key=lambda p: p.rect.x)[0]
        if is_off_screen(leftmost):
            for _ in range(2):
                pipe_group.remove(sorted(pipe_group, key=lambda p: p.rect.x)[0])
            rightmost_x = max(p.rect.x for p in pipe_group)
            new_bottom, new_top = get_random_pipes(rightmost_x + PIPE_SPACING, PIPE_IMAGE_BASE)
            pipe_group.add(new_bottom, new_top)

        # Physics and draw
        bird_group.update()
        ground_group.update()
        pipe_group.update()

        pipe_group.draw(game_surface)
        ground_group.draw(game_surface)
        bird_group.draw(game_surface)

        # Scoring
        bird_mid = bird.rect.centerx
        for p in pipe_group:
            if not p.inverted:
                p_mid = p.rect.centerx
                if p_mid <= bird_mid < p_mid + GAME_SPEED and not p.scored:
                    p.scored = True
                    score += 1
                    if point_snd: 
                        point_snd.play()

        display_score(game_surface, score, viewport_width)
        
        # Scale to screen
        if current_height != BASE_HEIGHT:
            scale_factor = current_height / BASE_HEIGHT
            scaled_width = int(viewport_width * scale_factor)
            game_surface = pygame.transform.scale(game_surface, (scaled_width, current_height))
        
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()

        # Collisions and top death
        hit_ground = pygame.sprite.spritecollide(bird, ground_group, False, pygame.sprite.collide_mask)
        hit_pipe = pygame.sprite.spritecollide(bird, pipe_group, False, pygame.sprite.collide_mask)
        if hit_ground or hit_pipe or bird.rect.top <= 0:
            if hit_snd: 
                hit_snd.play()
            # Check if high score
            final_rank = leaderboard.add_score(score)
            state = "GAME_OVER"
        continue

    if state == "GAME_OVER":
        game_surface.blit(background, (0, 0))
        pipe_group.draw(game_surface)
        ground_group.draw(game_surface)
        bird_group.draw(game_surface)
        display_score(game_surface, score, viewport_width)
        
        if show_leaderboard:
            # Show full leaderboard
            render_leaderboard(game_surface, viewport_width, score, final_rank)
            render_text_with_bg(game_surface, 
                              "L: Hide  |  Space: Restart  |  Q: Quit", 
                              BASE_HEIGHT * 0.92, 24, (255, 255, 255), 
                              (0, 0, 0, 180), viewport_width, 8)
        else:
            # Game Over title with shadow
            title_font = pygame.font.Font(None, 64)
            shadow = title_font.render("GAME OVER", True, (0, 0, 0))
            title = title_font.render("GAME OVER", True, (255, 50, 50))
            title_rect = title.get_rect(center=(viewport_width // 2, BASE_HEIGHT * 0.3))
            game_surface.blit(shadow, title_rect.move(3, 3))
            game_surface.blit(title, title_rect)
            
            # Show rank if high score
            if final_rank:
                render_text_with_bg(game_surface, 
                                  f"🎉 New High Score! Rank #{final_rank} 🎉", 
                                  BASE_HEIGHT * 0.42, 32, (150, 255, 150), 
                                  (0, 50, 0, 200), viewport_width, 12)
            
            # Instructions with enhanced visibility
            render_text_with_bg(game_surface, 
                              "Press SPACE to Restart", 
                              BASE_HEIGHT * 0.55, 32, (255, 255, 255), 
                              (0, 0, 0, 180), viewport_width, 10)
            
            render_text_with_bg(game_surface, 
                              "L: Leaderboard  |  Q: Quit", 
                              BASE_HEIGHT * 0.64, 24, (200, 200, 255), 
                              (0, 0, 0, 180), viewport_width, 8)
        
        # Scale to screen
        if current_height != BASE_HEIGHT:
            scale_factor = current_height / BASE_HEIGHT
            scaled_width = int(viewport_width * scale_factor)
            game_surface = pygame.transform.scale(game_surface, (scaled_width, current_height))
        
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()

pygame.quit()