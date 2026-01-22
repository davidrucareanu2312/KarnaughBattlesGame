import pygame
import os

class MapLoader:
    def __init__(self):
        root_path = os.path.join(os.path.dirname(__file__), "..", "..")
        assets_path = os.path.join(root_path, "assets", "maps")
        
        try:
            self.map_img = pygame.image.load(os.path.join(assets_path, "campus.png")).convert()
            raw_mask = pygame.image.load(os.path.join(assets_path, "campus_mask.png")).convert()
        except FileNotFoundError as e:
            print(f"EROARE CRITICĂ: {e}")
            raise

        map_size = self.map_img.get_size()
        self.mask_surf = pygame.transform.scale(raw_mask, map_size)
        
        self.walkable_mask = pygame.mask.from_threshold(
            self.mask_surf, (255, 255, 255), (128, 128, 128)
        )

        self.interactions = [
            {
                'rect': pygame.Rect(228, 636, 50, 80),
                'text': "Ripoff PRECIS. (Pare periculos...)",
                'type': 'boss_trigger',
                'boss_id': 1,
                'boss_img': 'boss_sprites/sprite_boss1.jpeg',
                'boss_line': "I may be former president, but I am CURRENT logical projec...tor??",
                'battle_config': 'configs/Karnaugh/K_boss_1.json'
            },
            
            {
                'rect': pygame.Rect(788, 184, 50, 80),
                'text': "EC Ripoff. Te simti amenintat.",
                'type': 'boss_trigger',
                'boss_id': 2,
                'boss_img': 'boss_sprites/sprite_boss2.jpeg', 
                'boss_line': "Cogito ergo sum... TE PROIECTEZ LOGIC.",
                'battle_config': 'configs/Karnaugh/K_boss_2.json'
            },

            {
                'rect': pygame.Rect(1480, 412, 50, 80),
                'text': "ED Ripoff. Te simti slabit...",
                'type': 'boss_trigger',
                'boss_id': 3,
                'boss_img': 'boss_sprites/sprite_boss3.jpeg',
                'boss_line': "OOO MY GODDDDD!!!",
                'battle_config': 'configs/Karnaugh/K_boss_3.json'
            },

            {
                'rect': pygame.Rect(1208, 916, 50, 80),
                'text': "AN si OZN-ul. Te simti amenintat logic..",
                'type': 'boss_trigger',
                'boss_id': 4,
                'boss_img': 'boss_sprites/khiru.png',
                'boss_line': "Eu sunt regele. Vezi sa nu pici.",
                'battle_config': 'configs/Karnaugh/K_boss_4.json'
            },
            {
                'rect': pygame.Rect(432, 928, 50, 80),
                'text': "Scena pe care ocazional canta Fuego.",
                'type': 'boss_trigger',
                'boss_id': 5,
                'boss_img': 'boss_sprites/fuego.png',
                
                'boss_music': 'impodobeste.mp3', 
                
                'boss_line': "Impodobeste mama bradul...",
                'battle_config': 'configs/Karnaugh/K_boss_5.json' 
            },

            { 'rect': pygame.Rect(724, 652, 50, 80), 'text': "Fantana... David a aprobat apa." },
            { 'rect': pygame.Rect(536, 1016, 50, 80), 'text': "Asculti..Fuego...neironic??...?" },
            { 'rect': pygame.Rect(584, 364, 50, 80), 'text': "Statuia vestitului profesor ale carui initiale seamana cu o diagonalizare..." },
            { 'rect': pygame.Rect(520, 372, 50, 80), 'text': "Statuia vestitului profesor ale carui initiale seamana cu o diagonalizare..." },
            { 'rect': pygame.Rect(556, 96, 50, 80), 'text': "Statuia vestitului profesor ale carui initiale seamana cu o diagonalizare..." },
            { 'rect': pygame.Rect(904, 1400, 50, 80), 'text': "Aceasta masina aproape te-a calcat in campus... de vreo 3 ori." },
            { 'rect': pygame.Rect(1240, 1400, 50, 80), 'text': "O masina VERDE." },
            { 'rect': pygame.Rect(1176, 1364, 50, 80), 'text': "Copacul intelepciunii... Nu stii de ce, dar te simti... DETERMINAT!" },
            { 'rect': pygame.Rect(1100, 1408, 50, 80), 'text': "Copacul intelepciunii... Nu stii de ce, dar te simti... DETERMINAT!" },
            { 'rect': pygame.Rect(1068, 1372, 50, 80), 'text': "Copacul intelepciunii... Nu stii de ce, dar te simti... DETERMINAT!" },
            { 'rect': pygame.Rect(640, 1424, 50, 80), 'text': "Mergi pe jos, rege." },
            { 'rect': pygame.Rect(1640, 856, 50, 80), 'text': "Cantina de langa palatul maestrului portilor logice." }


        ]

    def find_safe_spawn(self):
        w, h = self.mask_surf.get_size()
        player_w, player_h = 50, 80
        for y in range(100, h - 100, 50):
            for x in range(100, w - 100, 50):
                feet_rect = pygame.Rect(x + 10, y + 60, 30, 20)
                if self.is_walkable_rect(feet_rect):
                    return x, y
        return 100, 100

    def is_walkable_rect(self, rect):
        points = [(rect.left, rect.top), (rect.right, rect.top),
                  (rect.left, rect.bottom), (rect.right, rect.bottom),
                  (rect.centerx, rect.centery)]
        mw, mh = self.walkable_mask.get_size()
        for px, py in points:
            if not (0 <= int(px) < mw and 0 <= int(py) < mh): return False
            if not self.walkable_mask.get_at((int(px), int(py))): return False
        return True

    def check_interaction(self, player_hitbox):
        for item in self.interactions:
            interaction_area = item['rect'].inflate(20, 20)
            if player_hitbox.colliderect(interaction_area):
                return item 
        return None

    def get_size(self):
        return self.map_img.get_size()

    def draw(self, screen, camera):
        pos = camera.apply(self.map_img.get_rect())
        screen.blit(self.map_img, pos)