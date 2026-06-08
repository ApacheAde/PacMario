#!/usr/bin/env python3
"""
PacMario.py
A neon 8-bit Pac-Man style game with a Mario twist!
Collect coins, grab power stars to turn the tables on the ghosts,
and survive the neon maze.

pip install pygame
python PacMario.py

Controls:
  Arrow keys or WASD - Move Mario
  P - Pause
  ESC - Quit / Back to title
"""

import pygame
import sys
import random
import os
import math

# ====================== DEPENDENCY CHECK ======================
try:
    import pygame
except ImportError:
    print("=" * 60)
    print("PacMario requires pygame!")
    print("=" * 60)
    print()
    print("Install with:")
    print("    pip install pygame")
    print()
    print("Windows quick start:")
    print("    winget install Python.Python.3.12")
    print("    pip install pygame")
    print()
    input("Press Enter to exit...")
    sys.exit(1)

# ====================== CONSTANTS ======================
WIDTH, HEIGHT = 800, 620
TILE_SIZE = 20
MAZE_OFFSET_X = 80
MAZE_OFFSET_Y = 70
MAZE_COLS = 28
MAZE_ROWS = 25

FPS = 60

# Eye-catching NEON colors (8-bit cyberpunk vibe)
BG = (5, 0, 15)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_LIME = (50, 255, 100)
NEON_PINK = (255, 80, 200)
NEON_YELLOW = (255, 255, 50)
NEON_BLUE = (80, 150, 255)
NEON_RED = (255, 50, 80)
NEON_ORANGE = (255, 180, 50)
NEON_WHITE = (255, 255, 255)
WALL_NEON = NEON_BLUE
GLOW = (30, 30, 60)

# ====================== 8-BIT SOUND (pure Python generated) ======================
def create_8bit_tone(freq, duration_ms, volume=0.5, wave_type="square"):
    """Generate simple 8-bit style tones (square or saw)."""
    sample_rate = 22050
    n_samples = int(sample_rate * duration_ms / 1000)
    if n_samples < 1:
        n_samples = 1
    buf = bytearray()
    period = sample_rate / max(freq, 1)
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == "square":
            val = 127 if (i % period) < (period / 2) else -128
        else:  # saw
            val = int(255 * ((i % period) / period) - 128)
        sample = int(128 + val * volume)
        buf.append(max(0, min(255, sample)))
    try:
        snd = pygame.mixer.Sound(buffer=bytes(buf))
        return snd
    except:
        return None

class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-8, channels=1, buffer=256)
        self.enabled = True
        self.sounds = {}
        self._generate_sounds()

    def _generate_sounds(self):
        try:
            # Classic 8-bit Pac-Man inspired sounds
            self.sounds['dot'] = create_8bit_tone(880, 45, 0.35)
            self.sounds['power'] = create_8bit_tone(660, 120, 0.5)
            self.sounds['ghost_eat'] = create_8bit_tone(440, 180, 0.6, "saw")
            self.sounds['death'] = create_8bit_tone(200, 600, 0.7)
            self.sounds['start'] = create_8bit_tone(523, 80, 0.4)
            self.sounds['siren'] = create_8bit_tone(140, 90, 0.25)
            self.sounds['level_up'] = create_8bit_tone(784, 150, 0.5)
            # Extra Mario flavor
            self.sounds['coin'] = create_8bit_tone(1200, 60, 0.4)
            self.sounds['stomp'] = create_8bit_tone(350, 140, 0.55)
        except Exception:
            self.enabled = False

    def play(self, name, volume=1.0):
        if not self.enabled or name not in self.sounds:
            return
        snd = self.sounds[name]
        if snd:
            snd.set_volume(volume)
            snd.play()

    def play_siren(self, on=True):
        if not self.enabled or 'siren' not in self.sounds:
            return
        snd = self.sounds['siren']
        if on:
            snd.set_volume(0.18)
            if not pygame.mixer.get_busy():
                snd.play(-1)  # loop
        else:
            snd.stop()

# ====================== MAZE (classic Pac-Man inspired, Mario flavored) ======================
# # = wall, . = coin, O = power star, P = Mario start, G = ghost house
MAZE_LAYOUT = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#O####.#####.##.#####.####O#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###GG### ##.#     ",
    "######.## #      # ##.######",
    "      .   #      #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.##### ## #####.#     ",
    "######.##### ## #####.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#O####.#####.##.#####.####O#",
    "#...##................##...#",
    "############################",
]

def is_wall(x, y):
    """Check if grid position is wall."""
    if x < 0 or x >= MAZE_COLS or y < 0 or y >= MAZE_ROWS:
        return True
    return MAZE_LAYOUT[y][x] == '#'

# ====================== GAME OBJECTS ======================
class Mario:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        self.speed = 2.8
        self.mouth_frame = 0

    def update(self, dots):
        # Try to change direction if queued
        new_gx = self.grid_x + self.next_dir_x
        new_gy = self.grid_y + self.next_dir_y
        if not is_wall(new_gx, new_gy):
            self.dir_x = self.next_dir_x
            self.dir_y = self.next_dir_y

        # Move
        if self.dir_x != 0 or self.dir_y != 0:
            new_px = self.pixel_x + self.dir_x * self.speed
            new_py = self.pixel_y + self.dir_y * self.speed

            # Check wall ahead
            test_gx = int((new_px + self.dir_x * 8) / TILE_SIZE)
            test_gy = int((new_py + self.dir_y * 8) / TILE_SIZE)
            if not is_wall(test_gx, test_gy):
                self.pixel_x = new_px
                self.pixel_y = new_py
            else:
                # Snap to grid when hitting wall
                self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
                self.pixel_y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
                self.dir_x = 0
                self.dir_y = 0

            # Update grid position
            self.grid_x = int(self.pixel_x / TILE_SIZE)
            self.grid_y = int(self.pixel_y / TILE_SIZE)

            # Eat coin
            key = (self.grid_x, self.grid_y)
            if key in dots:
                dots.remove(key)
                return "dot"

        self.mouth_frame = (self.mouth_frame + 1) % 12
        return None

    def set_direction(self, dx, dy):
        self.next_dir_x = dx
        self.next_dir_y = dy

    def draw(self, surface, power_up=False):
        x = int(self.pixel_x + MAZE_OFFSET_X)
        y = int(self.pixel_y + MAZE_OFFSET_Y)

        # Neon Mario - 8-bit style with glow
        color_main = NEON_RED if not power_up else NEON_YELLOW
        color_body = NEON_BLUE
        color_hat = NEON_RED

        # Glow layer
        for i in range(3, 0, -1):
            alpha = 40 + i * 15
            glow_c = (*color_main[:3], alpha)
            s = pygame.Surface((TILE_SIZE+6, TILE_SIZE+6), pygame.SRCALPHA)
            pygame.draw.ellipse(s, glow_c, (0, 0, TILE_SIZE+6, TILE_SIZE+6))
            surface.blit(s, (x - TILE_SIZE//2 - 3, y - TILE_SIZE//2 - 3))

        # Hat (red neon)
        pygame.draw.rect(surface, color_hat, (x - 7, y - 9, 14, 6))
        pygame.draw.rect(surface, NEON_MAGENTA, (x - 5, y - 8, 10, 3))  # brim glow

        # Head / face
        pygame.draw.circle(surface, (255, 220, 180), (x, y - 1), 6)
        # Mustache (Mario classic)
        pygame.draw.rect(surface, (60, 30, 10), (x - 4, y + 1, 8, 2))

        # Body (blue overalls)
        pygame.draw.rect(surface, color_body, (x - 6, y + 4, 12, 8))
        # Buttons (neon yellow)
        pygame.draw.circle(surface, NEON_YELLOW, (x - 2, y + 7), 1)
        pygame.draw.circle(surface, NEON_YELLOW, (x + 2, y + 7), 1)

        # Legs animation
        leg_offset = 2 if (self.mouth_frame // 3) % 2 == 0 else -2
        pygame.draw.rect(surface, (40, 40, 40), (x - 5, y + 11, 3, 5))
        pygame.draw.rect(surface, (40, 40, 40), (x + 2 + leg_offset, y + 11, 3, 5))

        # Eyes
        eye_x = x + (2 if self.dir_x > 0 else -2 if self.dir_x < 0 else 0)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x - 2, y - 2), 1)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x + 2, y - 2), 1)

class Ghost:
    def __init__(self, grid_x, grid_y, color, name):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.color = color
        self.name = name
        self.dir_x = 0
        self.dir_y = -1
        self.speed = 2.2
        self.frightened = False
        self.returning = False

    def update(self, mario, frightened):
        self.frightened = frightened
        target_x = mario.grid_x
        target_y = mario.grid_y

        if self.returning:
            target_x, target_y = 14, 12  # ghost house

        # Simple but effective ghost AI (chase + some randomness)
        possible_dirs = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            if (dx, dy) == (-self.dir_x, -self.dir_y):
                continue  # no immediate reverse
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if not is_wall(nx, ny):
                possible_dirs.append((dx, dy))

        if possible_dirs:
            # Choose best direction toward target (or away if frightened)
            best = None
            best_dist = float('inf') if not self.frightened else -float('inf')

            for dx, dy in possible_dirs:
                dist = (self.grid_x + dx - target_x)**2 + (self.grid_y + dy - target_y)**2
                if self.frightened:
                    dist = -dist  # run away
                if (dist < best_dist and not self.frightened) or (dist > best_dist and self.frightened):
                    best_dist = dist
                    best = (dx, dy)

            if best:
                self.dir_x, self.dir_y = best
            else:
                self.dir_x, self.dir_y = random.choice(possible_dirs)

        # Move
        self.pixel_x += self.dir_x * self.speed
        self.pixel_y += self.dir_y * self.speed

        # Update grid
        self.grid_x = int(self.pixel_x / TILE_SIZE)
        self.grid_y = int(self.pixel_y / TILE_SIZE)

        # Snap when close to center of tile
        if abs(self.pixel_x - (self.grid_x * TILE_SIZE + TILE_SIZE//2)) < 2:
            self.pixel_x = self.grid_x * TILE_SIZE + TILE_SIZE//2
        if abs(self.pixel_y - (self.grid_y * TILE_SIZE + TILE_SIZE//2)) < 2:
            self.pixel_y = self.grid_y * TILE_SIZE + TILE_SIZE//2

        # If returned to house
        if self.returning and abs(self.grid_x - 14) < 2 and abs(self.grid_y - 12) < 2:
            self.returning = False
            self.speed = 2.2

    def draw(self, surface):
        x = int(self.pixel_x + MAZE_OFFSET_X)
        y = int(self.pixel_y + MAZE_OFFSET_Y)

        color = self.color
        if self.frightened:
            color = NEON_BLUE if (pygame.time.get_ticks() // 200) % 2 == 0 else NEON_WHITE
        if self.returning:
            color = (80, 80, 80)

        # Neon glow
        for i in range(4, 0, -1):
            s = pygame.Surface((TILE_SIZE + 8, TILE_SIZE + 8), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*color[:3], 25 * i), (0, 0, TILE_SIZE + 8, TILE_SIZE + 8))
            surface.blit(s, (x - TILE_SIZE//2 - 4, y - TILE_SIZE//2 - 4))

        # Ghost body
        pygame.draw.ellipse(surface, color, (x - 8, y - 8, 16, 14))
        pygame.draw.rect(surface, color, (x - 8, y - 1, 16, 10))

        # Wavy bottom
        for i in range(3):
            wx = x - 6 + i * 6
            pygame.draw.circle(surface, color, (wx, y + 8), 3)

        # Eyes (classic)
        eye_color = NEON_WHITE if not self.frightened else NEON_CYAN
        pygame.draw.ellipse(surface, eye_color, (x - 5, y - 5, 4, 5))
        pygame.draw.ellipse(surface, eye_color, (x + 1, y - 5, 4, 5))

        # Pupils that look toward Mario
        px = 1 if self.dir_x > 0 else -1 if self.dir_x < 0 else 0
        py = 1 if self.dir_y > 0 else -1 if self.dir_y < 0 else 0
        pygame.draw.circle(surface, (0, 0, 0), (x - 3 + px, y - 3 + py), 1)
        pygame.draw.circle(surface, (0, 0, 0), (x + 3 + px, y - 3 + py), 1)

# ====================== MAIN GAME ======================
class PacMarioGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PacMario - Neon 8-Bit Adventure")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 22, bold=True)
        self.big_font = pygame.font.SysFont("Courier New", 48, bold=True)
        self.title_font = pygame.font.SysFont("Courier New", 64, bold=True)

        self.highscore_file = os.path.join(os.path.dirname(__file__), "pacmario_highscore.txt")
        self.high_score = self.load_highscore()

        self.sound = SoundManager()
        self.state = "title"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.power_timer = 0
        self.dots = set()
        self.player = None
        self.ghosts = []
        self.frame = 0

        self.reset_level()

    def load_highscore(self):
        try:
            if os.path.exists(self.highscore_file):
                with open(self.highscore_file, "r") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_highscore(self):
        try:
            if self.score > self.high_score:
                self.high_score = self.score
                with open(self.highscore_file, "w") as f:
                    f.write(str(self.high_score))
        except:
            pass

    def reset_level(self):
        self.dots = set()
        self.player = None
        self.ghosts = []

        # Parse maze for dots and starts
        player_start = (13, 19)
        ghost_starts = [(11, 12), (13, 12), (15, 12), (17, 12)]

        for y, row in enumerate(MAZE_LAYOUT):
            for x, cell in enumerate(row):
                if cell == '.':
                    self.dots.add((x, y))
                elif cell == 'O':
                    self.dots.add((x, y))  # treat power as special dot
                elif cell == 'P':
                    player_start = (x, y)
                elif cell == 'G':
                    if len(ghost_starts) < 4:
                        ghost_starts.append((x, y))

        self.player = Mario(player_start[0], player_start[1])

        colors = [NEON_RED, NEON_PINK, NEON_CYAN, NEON_ORANGE]
        names = ["Boo", "Goomba", "Koopa", "ShyGuy"]
        self.ghosts = [Ghost(gx, gy, colors[i], names[i]) for i, (gx, gy) in enumerate(ghost_starts[:4])]

        self.power_timer = 0
        self.sound.play_siren(False)

    def start_new_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.reset_level()
        self.sound.play('start')
        self.state = "playing"

    def next_level(self):
        self.level += 1
        self.sound.play('level_up')
        # Make it harder
        for g in self.ghosts:
            g.speed = min(3.0, 2.2 + self.level * 0.12)
        self.reset_level()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx, dy = -1, 0
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx, dy = 1, 0
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dx, dy = 0, -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dx, dy = 0, 1

        if dx != 0 or dy != 0:
            self.player.set_direction(dx, dy)

    def update(self):
        if self.state != "playing":
            return

        self.handle_input()

        # Update Mario
        result = self.player.update(self.dots)
        if result == "dot":
            self.score += 10
            self.sound.play('coin' if random.random() > 0.3 else 'dot', 0.6)

        # Check power pellet (special dots placed at corners in layout)
        key = (self.player.grid_x, self.player.grid_y)
        if key in self.dots and MAZE_LAYOUT[self.player.grid_y][self.player.grid_x] == 'O':
            self.dots.remove(key)
            self.score += 50
            self.power_timer = 420  # ~7 seconds at 60fps
            self.sound.play('power')
            self.sound.play_siren(False)

        # Update ghosts
        frightened = self.power_timer > 0
        for ghost in self.ghosts:
            ghost.update(self.player, frightened)

            # Collision
            if abs(ghost.pixel_x - self.player.pixel_x) < 12 and abs(ghost.pixel_y - self.player.pixel_y) < 12:
                if frightened and not ghost.returning:
                    self.score += 200 * (2 ** min(3, self.level))
                    ghost.returning = True
                    ghost.speed = 3.5
                    self.sound.play('stomp')
                elif not ghost.returning:
                    self.lives -= 1
                    self.sound.play('death')
                    self.sound.play_siren(False)
                    if self.lives <= 0:
                        self.state = "gameover"
                        self.save_highscore()
                    else:
                        # Respawn
                        self.player = Mario(13, 19)
                        for g in self.ghosts:
                            g.pixel_x = g.grid_x * TILE_SIZE + TILE_SIZE // 2
                            g.pixel_y = g.grid_y * TILE_SIZE + TILE_SIZE // 2
                            g.dir_x, g.dir_y = 0, -1
                            g.returning = False
                    return

        # Power timer
        if self.power_timer > 0:
            self.power_timer -= 1
            if self.power_timer == 0:
                self.sound.play_siren(True)

        # Check win
        if not self.dots:
            self.next_level()

        # Occasional siren
        if self.power_timer == 0 and random.randint(1, 40) == 1:
            self.sound.play_siren(True)

        self.frame += 1

    def draw_maze(self):
        for y in range(MAZE_ROWS):
            for x in range(MAZE_COLS):
                cell = MAZE_LAYOUT[y][x]
                px = x * TILE_SIZE + MAZE_OFFSET_X
                py = y * TILE_SIZE + MAZE_OFFSET_Y

                if cell == '#':
                    # Neon glowing walls
                    pygame.draw.rect(self.screen, (20, 30, 60), (px, py, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, WALL_NEON, (px + 1, py + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                    # Inner highlight
                    pygame.draw.rect(self.screen, NEON_CYAN, (px + 4, py + 4, TILE_SIZE - 8, 2), 1)

                elif (x, y) in self.dots:
                    cx = px + TILE_SIZE // 2
                    cy = py + TILE_SIZE // 2
                    if cell == 'O':
                        # Power Star (pulsing)
                        size = 6 + int(math.sin(self.frame / 5) * 2)
                        pygame.draw.circle(self.screen, NEON_YELLOW, (cx, cy), size)
                        pygame.draw.circle(self.screen, NEON_WHITE, (cx, cy), size - 2)
                    else:
                        # Coin
                        pygame.draw.circle(self.screen, NEON_YELLOW, (cx, cy), 3)
                        pygame.draw.circle(self.screen, NEON_WHITE, (cx, cy), 1)

    def draw_ui(self):
        # Top bar
        pygame.draw.rect(self.screen, (15, 5, 30), (0, 0, WIDTH, 55))
        draw_text = lambda t, x, y, c, f=self.font: self.screen.blit(f.render(t, True, c), (x, y))

        draw_text(f"SCORE: {self.score:05d}", 30, 8, NEON_CYAN)
        draw_text(f"HIGH: {self.high_score:05d}", 280, 8, NEON_MAGENTA)
        draw_text(f"LEVEL {self.level}", 550, 8, NEON_LIME)

        # Lives (small Marios)
        draw_text("LIVES", 30, 32, NEON_PINK)
        for i in range(self.lives):
            lx = 100 + i * 28
            pygame.draw.circle(self.screen, NEON_RED, (lx, 42), 6)
            pygame.draw.circle(self.screen, NEON_BLUE, (lx, 45), 4)

        # Power up indicator
        if self.power_timer > 0:
            secs = self.power_timer // 60 + 1
            draw_text(f"STAR POWER! {secs}", 300, 32, NEON_YELLOW)

    def draw(self):
        self.screen.fill(BG)

        # Subtle neon grid background
        for x in range(0, WIDTH, 40):
            pygame.draw.line(self.screen, GLOW, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(self.screen, GLOW, (0, y), (WIDTH, y), 1)

        if self.state == "title":
            # Big neon title
            self.screen.blit(self.title_font.render("PAC-MARIO", True, NEON_CYAN), (200, 140))
            self.screen.blit(self.title_font.render("2", True, NEON_MAGENTA), (580, 140))

            self.screen.blit(self.big_font.render("NEON 8-BIT ADVENTURE", True, NEON_LIME), (170, 220))

            self.screen.blit(self.font.render("Collect the coins!", True, NEON_YELLOW), (260, 300))
            self.screen.blit(self.font.render("Grab power stars to stomp ghosts", True, NEON_PINK), (180, 330))

            self.screen.blit(self.font.render("ARROWS / WASD to move", True, NEON_CYAN), (240, 400))
            self.screen.blit(self.font.render("PRESS SPACE TO START", True, NEON_WHITE), (210, 460))
            self.screen.blit(self.font.render("P = Pause   ESC = Quit", True, NEON_ORANGE), (250, 500))

            # Demo Mario + Ghost
            demo_m = Mario(10, 22)
            demo_m.pixel_x = 280
            demo_m.pixel_y = 560
            demo_m.draw(self.screen, True)

            demo_g = Ghost(18, 22, NEON_RED, "Boo")
            demo_g.pixel_x = 480
            demo_g.pixel_y = 560
            demo_g.draw(self.screen)

        elif self.state in ("playing", "gameover"):
            self.draw_maze()

            # Draw ghosts first (behind)
            for ghost in self.ghosts:
                ghost.draw(self.screen)

            # Draw Mario
            self.player.draw(self.screen, self.power_timer > 0)

            self.draw_ui()

            if self.state == "gameover":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                self.screen.blit(self.big_font.render("GAME OVER", True, NEON_RED), (250, 220))
                self.screen.blit(self.font.render(f"FINAL SCORE: {self.score}", True, NEON_WHITE), (280, 300))
                if self.score >= self.high_score:
                    self.screen.blit(self.font.render("NEW HIGH SCORE!", True, NEON_YELLOW), (270, 340))
                self.screen.blit(self.font.render("PRESS SPACE TO PLAY AGAIN", True, NEON_CYAN), (200, 410))
                self.screen.blit(self.font.render("ESC TO QUIT", True, NEON_PINK), (310, 450))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "title"
                            self.sound.play_siren(False)
                        else:
                            running = False
                    elif event.key == pygame.K_SPACE:
                        if self.state == "title":
                            self.start_new_game()
                        elif self.state == "gameover":
                            self.start_new_game()
                    elif event.key == pygame.K_p:
                        if self.state == "playing":
                            self.state = "title"  # simple pause via title for now

            if self.state == "playing":
                self.update()

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PacMarioGame()
    game.run()
