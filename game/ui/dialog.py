import pygame

class DialogBox:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.active = False
        
        self.full_text = ""
        self.displayed_text = ""
        self.char_index = 0
        self.done_typing = True
        
        self.last_update = 0
        self.type_speed = 30
        
        try:
            self.font = pygame.font.SysFont("consolas", 22, bold=True)
        except:
            self.font = pygame.font.Font(None, 24)
            
        box_height = 150
        self.rect = pygame.Rect(50, screen_height - box_height - 20, screen_width - 100, box_height)
        
        self.pending_boss_data = None 

    def show(self, text):
        if self.active and self.full_text == text and self.done_typing:
            self.hide()
            return

        self.active = True
        self.full_text = text
        self.displayed_text = ""
        self.char_index = 0
        self.done_typing = False
        self.last_update = pygame.time.get_ticks()

    def hide(self):
        self.active = False
        self.full_text = ""
        self.displayed_text = ""
        self.done_typing = True

    def skip_animation(self):
        self.displayed_text = self.full_text
        self.done_typing = True

    def update(self):
        if self.active and not self.done_typing:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.type_speed:
                if self.char_index < len(self.full_text):
                    self.displayed_text += self.full_text[self.char_index]
                    self.char_index += 1
                    self.last_update = now
                else:
                    self.done_typing = True

    def draw(self, screen):
        if not self.active:
            return

        self.update()

        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(200)
        s.fill((0, 0, 50)) 
        screen.blit(s, (self.rect.x, self.rect.y))
        
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
        
        text_surf = self.font.render(self.displayed_text, True, (255, 255, 255))
        
        text_rect = text_surf.get_rect(topleft=(self.rect.x + 20, self.rect.y + 20))
        screen.blit(text_surf, text_rect)
        
        if self.done_typing:
            hint = self.font.render(">> E", True, (200, 200, 0))
            screen.blit(hint, (self.rect.right - 60, self.rect.bottom - 40))