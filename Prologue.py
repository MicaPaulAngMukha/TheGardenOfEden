import pygame
import sys
import os
import Start
from display_scaler import DisplayScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── colours ────────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DIM_WHITE  = (200, 200, 200)

# ── timing ─────────────────────────────────────────────────────────────────
TYPEWRITER_DELAY  = 2      # frames per character (normal)
FAST_DELAY        = 0      # frames per character when S is held
FADE_FRAMES       = 30    # frames for image cross-fade
IMAGE_HOLD_FRAMES = 90    # minimum frames to show an image before next slide

WIDTH, HEIGHT = 793, 650


# ═══════════════════════════════════════════════════════════════════════════
# Slide definitions
# Each slide is a dict:
#   image  – filename inside StoryImages/ (or None for black screen)
#   lines  – list of text lines shown one after another on this slide
#             (each line finishes typing before the next begins)
# ═══════════════════════════════════════════════════════════════════════════
SLIDES = [
    # ── 0: black ──────────────────────────────────────────────────────────
    {
        "image": None,
        "lines": ["Adam..."],
    },
    # ── 1: Image1 – Adam in the garden ────────────────────────────────────
    {
        "image": "Image1.png",
        "lines": [
            "... the first man, created from dust",
            "and breathed in life.",
            "Placed into the garden with no strife.",
        ],
    },
    # ── 2: Image2 ─────────────────────────────────────────────────────────
    {
        "image": "Image2.png",
        "lines": [
            "He lived, he cared, it was duty bound.",
            "Humble beginnings, and with it no sound.",
        ],
    },
    # ── 3: Image3 – Adam with animals ─────────────────────────────────────
    {
        "image": "Image3.png",
        "lines": [
            "Adam lived alone, surrounded by none.",
            "None but animals, he learned to hunt.",
            "The loneliness of man, caused him to yell,",
        ],
    },
    # ── 4: Image4 – Adam yelling ──────────────────────────────────────────
    {
        "image": "Image4.png",
        "lines": [
            "'I am so lonely, I cannot bear!'",
        ],
    },
    # ── 5: Image5 – Heavens ───────────────────────────────────────────────
    {
        "image": "Image5.png",
        "lines": [
            "His yells and cries heard from the heavens,",
            "Before the day reached seven, they gave him presence.",
        ],
    },
    # ── 6: Image6 – Eve ───────────────────────────────────────────────────
    {
        "image": "Image6.png",
        "lines": [
            "Born from his rib, she came to be.",
            "A woman, a companion, and she was named Eve.",
        ],
    },
    # ── 7: Image7 – Adam and Eve ──────────────────────────────────────────
    {
        "image": "Image7.png",
        "lines": [
            "Man and woman, lived in peace.",
            "Within the paradise, all they knew was ease.",
        ],
    },
    # ── 8: Image8 – Eve by the tree ───────────────────────────────────────
    {
        "image": "Image8.png",
        "lines": [
            "Until the day, Eve heard a sound.",
            "A hiss, a call, from the tree she found.",
            "In the garden, came a call,",
        ],
    },
    # ── 9: Image9 – Naga ──────────────────────────────────────────────────
    {
        "image": "Image9.png",
        "lines": [
            "from the tree, a serpent crawled.",
            "A serpent, smart, conniving as he,",
            "Came from the tree and questioned she.",
        ],
    },
    # ── 10: Image10 – Naga close-up ───────────────────────────────────────
    {
        "image": "Image10.png",
        "lines": [
            "'Were you truly commanded to not eat from the fruit?'",
            "and Eve replied, a hasty rebut.",
            "The serpent smiled and told onto she,",
            "'You surely won't die, your eyes shall open wide.",
            "Gain knowledge, and wisdom, beyond you can compare.",
            "Why not take a bite?' a question he bare.",
        ],
    },
    # ── 11: Image11 – Eve eating apple ────────────────────────────────────
    {
        "image": "Image11.png",
        "lines": [
            "Eve, convinced, took a bite,",
            "unaware of the consequences in plain sight.",
        ],
    },
    # ── 12: Image12 – Eve telling Adam ────────────────────────────────────
    {
        "image": "Image12.png",
        "lines": [
            "she called for Adam, persuaded to take a bite.",
        ],
    },
    # ── 13: black ─────────────────────────────────────────────────────────
    {
        "image": None,
        "lines": [
            "And within that moment, they now knew strife.",
        ],
    },
    # ── 14: Image13 – Adam and Eve trembling ──────────────────────────────
    {
        "image": "Image13.png",
        "lines": [
            "The heavens raged, and the two crumbled.",
            "An angel sent from above, sent them to fumble.",
            "Cast from the garden, they could no longer return.",
            "The paradise they once knew...",
            "now was not theirs.",
        ],
    },
    # ── 15: black ─────────────────────────────────────────────────────────
    {
        "image": None,
        "lines": [
            "Legend say, the tree still grew fruit.",
            "But the cost of knowledge, is a deadly pursuit.",
        ],
    },
]

STORY_IMAGE_DIR = os.path.join(BASE_DIR, "StoryImages")


# ═══════════════════════════════════════════════════════════════════════════
class Prologue:
    """
    Undertale-style prologue sequence.

    Usage:
        from Prologue import Prologue
        p = Prologue(screen, clock)
        p.run()          # blocks until finished or skipped
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        pygame.mixer.music.load(os.path.join(BASE_DIR, "audio", "PrologueMusic.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.screen = screen
        self.clock  = clock
        self.W, self.H = 793, 650  # Native resolution
        
        # Create display scaler and game surface
        self.scaler = DisplayScaler(self.W, self.H)
        self.game_surface = pygame.Surface((self.W, self.H))

        # ── font ──────────────────────────────────────────────────────────
        font_path = os.path.join(BASE_DIR, "font", "PixelifySans-VariableFont_wght.ttf")
        self.font = pygame.font.Font(font_path, 22) if os.path.exists(font_path) \
                    else pygame.font.SysFont("monospace", 22)

        # ── state ─────────────────────────────────────────────────────────
        self.slide_idx   = 0
        self.line_idx    = 0

        # typewriter
        self.tw_text     = ""
        self.tw_visible  = 0
        self.tw_timer    = 0
        self.tw_done     = False

        # image fade
        self.current_img : pygame.Surface | None = None
        self.next_img    : pygame.Surface | None = None
        self.fade_alpha  = 255          # alpha of next_img during crossfade
        self.fading      = False
        self.fade_timer  = 0

        # hold timer so images aren't instantly skipped
        self.hold_timer  = 0

        self._load_slide(0)

    # ── helpers ────────────────────────────────────────────────────────────
    def _load_image(self, filename) -> pygame.Surface | None:
        if not filename:
            return None
        path = os.path.join(STORY_IMAGE_DIR, filename)
        if not os.path.exists(path):
            return None
        img = pygame.image.load(path).convert_alpha()
        # Scale to fit screen while keeping aspect ratio
        iw, ih = img.get_size()
        scale = min(self.W / iw, self.H / ih)
        return pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))

    def _load_slide(self, idx: int):
        if idx >= len(SLIDES):
            return
        slide = SLIDES[idx]

        # Prepare image crossfade
        new_img = self._load_image(slide["image"])
        if new_img != self.current_img:
            self.next_img   = new_img
            self.fading     = True
            self.fade_alpha = 0
            self.fade_timer = 0
        # else: same image (or both None) – no crossfade needed

        self.slide_idx  = idx
        self.line_idx   = 0
        self.hold_timer = 0
        self._start_line(0)

    def _start_line(self, idx: int):
        lines = SLIDES[self.slide_idx]["lines"]
        if idx >= len(lines):
            return
        self.line_idx   = idx
        self.tw_text    = lines[idx]
        self.tw_visible = 0
        self.tw_timer   = 0
        self.tw_done    = False

    def _advance(self):
        """Called when player presses Enter/Space (or auto-advances)."""
        lines = SLIDES[self.slide_idx]["lines"]

        if not self.tw_done:
            # finish current line instantly
            self.tw_visible = len(self.tw_text)
            self.tw_done    = True
            return

        next_line = self.line_idx + 1
        if next_line < len(lines):
            self._start_line(next_line)
        else:
            # Move to next slide
            next_slide = self.slide_idx + 1
            if next_slide < len(SLIDES):
                self._load_slide(next_slide)
            else:
                self._finished = True

    # ── public ─────────────────────────────────────────────────────────────
    def run(self):
        """Block until the prologue ends or the player skips it entirely."""
        self._finished = False

        while not self._finished:
            dt = self.clock.tick(60)
            fast = pygame.key.get_pressed()[pygame.K_s]


            # ── events ────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.fadeout(500)
                        self._finished = True  # hard skip to start menu
                        return

                    # S pressed once (not held) → advance / speed up
                    if event.key == pygame.K_s:
                        self._advance()

                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._advance()

            # S held → turbo typewriter
            if fast and not self.tw_done:
                self.tw_visible = len(self.tw_text)
                self.tw_done    = True

            # ── typewriter update ─────────────────────────────────────────
            if not self.tw_done:
                self.tw_timer += 1
                delay = FAST_DELAY if fast else TYPEWRITER_DELAY
                if self.tw_timer > delay:
                    self.tw_timer = 0
                    self.tw_visible = min(self.tw_visible + 1, len(self.tw_text))
                    if self.tw_visible == len(self.tw_text):
                        self.tw_done = True

            # ── image crossfade update ────────────────────────────────────
            if self.fading:
                self.fade_timer += 1
                self.fade_alpha = min(255, int(255 * self.fade_timer / FADE_FRAMES))
                if self.fade_timer >= FADE_FRAMES:
                    self.current_img = self.next_img
                    self.next_img    = None
                    self.fading      = False

            # hold timer (counts only when typewriter is done)
            if self.tw_done:
                self.hold_timer += 1

            # ── draw ──────────────────────────────────────────────────────
            self.game_surface.fill(BLACK)

            # Draw current image (full alpha)
            if self.current_img:
                ix = self.W // 2 - self.current_img.get_width() // 2
                iy = self.H // 2 - self.current_img.get_height() // 2
                self.game_surface.blit(self.current_img, (ix, iy))

            # Draw next image fading in
            if self.fading and self.next_img:
                tmp = self.next_img.copy()
                tmp.set_alpha(self.fade_alpha)
                ix = self.W // 2 - tmp.get_width() // 2
                iy = self.H // 2 - tmp.get_height() // 2
                self.game_surface.blit(tmp, (ix, iy))

            # Semi-transparent bottom bar for text
            bar_h = 110
            bar = pygame.Surface((self.W, bar_h), pygame.SRCALPHA)
            bar.fill((0, 0, 0, 175))
            self.game_surface.blit(bar, (0, self.H - bar_h))

            # Typewriter text (word-wrapped)
            self._draw_text(self.tw_text[:self.tw_visible],
                            self.W - 80, self.H - bar_h + 14)

            # Hint
            hint_col = (120, 120, 120)
            hint = self.font.render("[S] skip / fast-forward   [ESC] skip all", True, hint_col)
            self.game_surface.blit(hint, (self.W // 2 - hint.get_width() // 2, self.H - 22))

            # Scale and display with letterboxing/pillarboxing
            self.scaler.display(self.screen, self.game_surface)
            pygame.display.flip()

        pygame.mixer.music.fadeout(800)
        pygame.time.wait(850)

    def _draw_text(self, text: str, max_w: int, y_start: int):
        """Draw word-wrapped text centred at the bottom bar."""
        words  = text.split(" ")
        lines  = []
        line   = ""
        for w in words:
            test = (line + " " + w).strip()
            if self.font.size(test)[0] <= max_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)

        y = y_start
        for ln in lines:
            surf = self.font.render(ln, True, WHITE)
            self.game_surface.blit(surf, (self.W // 2 - surf.get_width() // 2, y))
            y += surf.get_height() + 6


# ═══════════════════════════════════════════════════════════════════════════
# Stand-alone test entry point
# ═══════════════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    clock  = pygame.time.Clock()

    p = Prologue(screen, clock)
    p.run()

    # After prologue → hand off to start menu (or wherever)
    # import StartMenu; StartMenu.main()
    Start.main()
    pygame.quit()


if __name__ == "__main__":
    main()