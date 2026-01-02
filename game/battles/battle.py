import pygame
from game.ui.dialog import DialogBox

class Battle:
    def __init__(self, screen, config_path, session):
        self.screen = screen
        self.session = session
        self.finished = False
        self.is_victory = False

        try:
            self.font_large = pygame.font.SysFont("arial", 48, bold=True)
            self.font_small = pygame.font.SysFont("arial", 24)
        except:
            self.font_large = pygame.font.Font(None, 60)
            self.font_small = pygame.font.Font(None, 30)

        self.width, self.height = screen.get_size()
        
    def handle_event(self, event):
        """ Gestioneaza input-ul in timpul 'luptei' (ecranului de loading) """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.is_victory = True
                self.finished = True
                print("DEBUG: Battle skipped via E (Auto-Win)")

    def update(self, dt):
        """ Nu avem logica de timp sau animatii complexe """
        pass

    def draw(self):
        """ Deseneaza ecranul BATTLE STARTED """
        self.screen.fill((0, 0, 0))

        text_surf = self.font_large.render("BATTLE STARTED", True, (255, 0, 0))
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2 - 20))
        self.screen.blit(text_surf, text_rect)

        hint_surf = self.font_small.render("Press E to Skip (Auto-Win)", True, (255, 255, 255))
        hint_rect = hint_surf.get_rect(center=(self.width // 2, self.height // 2 + 40))
        self.screen.blit(hint_surf, hint_rect)