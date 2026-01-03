import pygame
import random

class BossStrategy:
    def __init__(self, battle):
        self.battle = battle
    
    def update(self, dt):
        pass

    def on_phase_start(self, phase_data):
        pass

    def get_cell_display(self, val, rect, mouse_pos):
        return str(val)

class StandardBoss(BossStrategy):
    pass 

class HazardStateBoss(BossStrategy):
    def __init__(self, battle):
        super().__init__(battle)
        self.timer = 0
        self.interval = 2.0

    def update(self, dt):
        idx = self.battle.current_phase_idx

        self.timer += dt
        if self.timer >= self.interval:
            self.timer = 0
            if self.battle.selected_cells:
                self.battle.selected_cells.clear()

class DisfunctionalBoss(BossStrategy):
    def get_cell_display(self, val, rect, mouse_pos):
        dist = ((mouse_pos[0] - rect.centerx)**2 + (mouse_pos[1] - rect.centery)**2)**0.5
        if dist < 80:
            return str(val)
        return "HIDDEN"


class FinalBoss(BossStrategy):
    def __init__(self, battle):
        super().__init__(battle)
        
        self.saboteur_timer = 0
        self.saboteur_interval = 4.0

        self.glitch_interval = 500

    def update(self, dt):
        round_num = self.battle.current_phase_idx + 1

        if round_num == 4 or round_num == 6:
            self.saboteur_timer += dt
            if self.saboteur_timer >= self.saboteur_interval:
                self.saboteur_timer = 0
                if self.battle.selected_cells:
                    self.battle.selected_cells.clear()

    def get_cell_display(self, val, rect, mouse_pos):
        round_num = self.battle.current_phase_idx + 1

        if round_num == 3 or round_num == 5:
            dist = ((mouse_pos[0] - rect.centerx)**2 + (mouse_pos[1] - rect.centery)**2)**0.5
            if dist < 70: 
                return str(val)
            return "?"

        if round_num == 7 or round_num == 8:            
            current_time = pygame.time.get_ticks()
            
            time_step = current_time // self.glitch_interval
            
            pseudo_random = (rect.x + rect.y * 13 + time_step * 7) % 10
            
            if pseudo_random < 4:
                return " "
            
            return str(val)

        return str(val)
