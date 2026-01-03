import pygame
import os

class Player:
    def __init__(self, x, y):
        self.WIDTH = 60
        self.HEIGHT = 60
        
        root_path = os.path.join(os.path.dirname(__file__), "..", "..")
        sprites_dir = os.path.join(root_path, "assets", "sprites", "rotations")
        
        self.images = {}
        
        directions = [
            "north", "south", "east", "west",
            "north-east", "north-west", "south-east", "south-west"
        ]

        try:
            for d in directions:
                path = os.path.join(sprites_dir, f"{d}.png")
                img = pygame.image.load(path).convert_alpha()
                self.images[d] = pygame.transform.smoothscale(img, (self.WIDTH, self.HEIGHT))
            
            self.current_image = self.images['south']
            
        except Exception as e:
            print(f"EROARE la incarcarea imaginilor din 'rotations': {e}")
            self.current_image = pygame.Surface((self.WIDTH, self.HEIGHT))
            self.current_image.fill((255, 0, 0))
            self.images = {}

        self.rect = self.current_image.get_rect(topleft=(x, y))
        
        self.hitbox = pygame.Rect(0, 0, 30, 20)
        self.update_hitbox_pos()
        self.speed = 4

        self.last_direction = 'south'

    def update_hitbox_pos(self):
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom

    def get_direction_name(self, dx, dy):
        if dy < 0:
            if dx > 0: return "north-east"
            if dx < 0: return "north-west"
            return "north"
        
        if dy > 0:
            if dx > 0: return "south-east"
            if dx < 0: return "south-west"
            return "south"
        
        if dx > 0: return "east"
        if dx < 0: return "west"
        
        return None

    def handle_input(self, map_loader):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:    dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  dy = self.speed

        dir_x = 0
        if dx > 0: dir_x = 1
        elif dx < 0: dir_x = -1
        
        dir_y = 0
        if dy > 0: dir_y = 1
        elif dy < 0: dir_y = -1

        direction_key = self.get_direction_name(dir_x, dir_y)

        if direction_key and self.images:
            self.current_image = self.images[direction_key]
            self.last_direction = direction_key
        

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
        screen.blit(self.current_image, camera.apply(self.rect))