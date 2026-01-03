import pygame
import os

class DialogBox:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        root_path = os.path.join(os.path.dirname(__file__), "..", "..")
        font_path = os.path.join(root_path, "assets", "fonts", "pixel.ttf")
        
        self.font_size = 28
        try:
            self.font = pygame.font.Font(font_path, self.font_size)
        except:
            self.font = pygame.font.SysFont("couriernew", self.font_size, bold=True)
            
        self.box_height = 160
        self.padding = 20
        self.rect = pygame.Rect(
            50, 
            screen_height - self.box_height - 20, 
            screen_width - 100, 
            self.box_height
        )
        
        self.active = False
        self.full_text = ""
        self.display_lines = []
        self.char_index = 0
        self.last_update = 0
        self.type_speed = 35
        self.done_typing = False 

    def wrap_text(self, text):

        words = text.split(' ')
        lines = []
        current_line = ""
        
        max_width = self.rect.width - (self.padding * 2)

        for word in words:
            test_line = current_line + word + " "
            text_w, text_h = self.font.size(test_line)
            
            if text_w < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        
        lines.append(current_line)
        return lines

    def show(self, text):
        self.active = True
        self.full_text = text
        self.display_lines = self.wrap_text(text)
        self.char_index = 0
        self.last_update = pygame.time.get_ticks()
        self.done_typing = False

    def hide(self):
        self.active = False
        self.full_text = ""

    def skip_animation(self):
        total_len = sum(len(line) for line in self.display_lines)
        self.char_index = total_len
        self.done_typing = True

    def update(self):
        if not self.active or self.done_typing:
            return

        now = pygame.time.get_ticks()
        if now - self.last_update > self.type_speed:
            self.last_update = now
            self.char_index += 1
            
            total_len = sum(len(line) for line in self.display_lines)
            if self.char_index >= total_len:
                self.char_index = total_len
                self.done_typing = True

    def draw(self, screen):
        if not self.active:
            return

        self.update()

        pygame.draw.rect(screen, (0, 0, 0), self.rect)
        
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 4)

        curr_chars = self.char_index
        y_offset = self.rect.y + self.padding
        
        for line in self.display_lines:
            if curr_chars <= 0:
                break
                
            if curr_chars >= len(line):
                text_to_render = line
                curr_chars -= len(line)
            else:
                text_to_render = line[:curr_chars]
                curr_chars = 0
            
            text_surf = self.font.render(text_to_render, False, (255, 255, 255))
            screen.blit(text_surf, (self.rect.x + self.padding, y_offset))
            
            y_offset += self.font.get_height() + 5