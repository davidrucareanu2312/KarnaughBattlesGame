import pygame
import os

class BossScene:
    def __init__(self, screen_width, screen_height, font):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.phase = 0
        
        self.root_path = os.path.join(os.path.dirname(__file__), "..", "..")
        
        self.boss_image = pygame.Surface((200, 200))
        self.boss_image.fill((200, 0, 0))

        self.full_text = ""
        self.display_text = ""
        self.char_index = 0
        self.last_update = 0
        self.type_speed = 60
        
        self.battle_config_path = None

    def start(self, image_filename, dialogue_text, config_path, music_filename=None):
        """
        Inițializează scena cu boss-ul specificat.
        """
        self.phase = 0
        self.full_text = dialogue_text 
        self.display_text = ""
        self.char_index = 0
        self.battle_config_path = config_path

        try:
            img_path = os.path.join(self.root_path, "assets", "sprites", image_filename)
            loaded_img = pygame.image.load(img_path).convert_alpha()

            TARGET_HEIGHT = 400
            
            orig_w, orig_h = loaded_img.get_size()
            aspect_ratio = orig_w / orig_h
            
            new_width = int(TARGET_HEIGHT * aspect_ratio)
            
            self.boss_image = pygame.transform.smoothscale(loaded_img, (new_width, TARGET_HEIGHT))
            
        except Exception as e:
            print(f"[BossScene] Eroare la incarcarea imaginii '{image_filename}': {e}")
            self.boss_image = pygame.Surface((200, 400))
            self.boss_image.fill((255, 0, 0))

        if music_filename:
            try:
                music_path = os.path.join(self.root_path, "assets", "music", music_filename)
                
                pygame.mixer.music.stop()
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)
                
            except Exception as e:
                print(f"[BossScene] Eroare la incarcarea muzicii '{music_filename}': {e}")

    def update(self):
        if self.phase == 1:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.type_speed:
                if self.char_index < len(self.full_text):
                    self.display_text += self.full_text[self.char_index]
                    self.char_index += 1
                    self.last_update = now

    def next_phase(self):
        self.phase += 1
        if self.phase > 2:
            return "DONE"
        return "CONTINUE"

    def draw_speech_bubble(self, screen, x, y, width, height, text):
        points = [(x + 20, y + height), (x + 50, y + height), (x - 20, y + height + 30)]
        pygame.draw.polygon(screen, (255, 255, 255), points)
        
        bubble_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (255, 255, 255), bubble_rect, 0, 10)
        pygame.draw.rect(screen, (0, 0, 0), bubble_rect, 3, 10)
        
        text_surf = self.font.render(text, False, (0, 0, 0))
        text_rect = text_surf.get_rect(center=bubble_rect.center)
        screen.blit(text_surf, text_rect)

    def draw(self, screen):
        screen.fill((0, 0, 0)) 

        if self.phase == 0:
            pass

        elif self.phase == 1:
            boss_rect = self.boss_image.get_rect()
            
            boss_rect.center = (self.screen_width // 2, self.screen_height // 2)
            
            screen.blit(self.boss_image, boss_rect)
            
            if self.display_text:
                bubble_w = max(200, len(self.display_text) * 15)
                
                bubble_x = boss_rect.centerx - (bubble_w // 2)

                target_y = boss_rect.top - 90
                
                if target_y < 20:
                    target_y = 20
                
                self.draw_speech_bubble(screen, bubble_x, target_y, bubble_w, 60, self.display_text)

        elif self.phase == 2:
            msg = self.font.render("BATTLE STARTING...", False, (255, 0, 0))
            screen.blit(msg, (100, 200))