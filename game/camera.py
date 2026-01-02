import pygame

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.map_width = map_width
        self.map_height = map_height

    def apply(self, entity_rect):
        return entity_rect.move(self.camera_rect.topleft[0] * -1, self.camera_rect.topleft[1] * -1)

    def update(self, target_rect):
        x = target_rect.centerx - self.camera_rect.width // 2
        y = target_rect.centery - self.camera_rect.height // 2

        x = max(0, x)
        y = max(0, y)
        x = min(self.map_width - self.camera_rect.width, x)
        y = min(self.map_height - self.camera_rect.height, y)

        self.camera_rect.topleft = (x, y)
