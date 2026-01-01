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
