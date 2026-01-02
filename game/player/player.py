
import pygame
import os

class Player:
    def __init__(self, x, y):
        root_path = os.path.join(os.path.dirname(__file__), "..", "..")
        sprite_path = os.path.join(root_path, "assets", "sprites", "player.png")
        
        try:
            full_img = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.smoothscale(full_img, (50, 80))
        except:
            self.image = pygame.Surface((50, 80))
            self.image.fill((255, 0, 0))
            
        self.rect = self.image.get_rect(topleft=(x, y))

        self.hitbox_width = 30
        self.hitbox_height = 20
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.update_hitbox_pos()
        
        self.speed = 4

    def update_hitbox_pos(self):
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom

    def handle_input(self, map_loader):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:    dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  dy = self.speed

        if dx != 0:
            test_hitbox = self.hitbox.copy()
            test_hitbox.x += dx
            
            if map_loader.is_walkable_rect(test_hitbox):
                self.rect.x += dx
                self.update_hitbox_pos()
        
        if dy != 0:
            test_hitbox = self.hitbox.copy()
            test_hitbox.y += dy
            
            if map_loader.is_walkable_rect(test_hitbox):
                self.rect.y += dy
                self.update_hitbox_pos()
                
    def draw(self, screen, camera):
        draw_rect = camera.apply(self.rect)
        screen.blit(self.image, draw_rect)