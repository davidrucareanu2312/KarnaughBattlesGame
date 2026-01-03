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

        if idx > 0:
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
                    print(f"FINAL BOSS (Runda {round_num}): Sabotaj activat! Selecție ștearsă.")
                    self.battle.selected_cells.clear()

    def get_cell_display(self, val, rect, mouse_pos):
        round_num = self.battle.current_phase_idx + 1

        if round_num == 3 or round_num == 5:
            dist = ((mouse_pos[0] - rect.centerx)**2 + (mouse_pos[1] - rect.centery)**2)**0.5
            if dist < 70: 
                return str(val)
            return "?"

        if round_num == 7 or round_num == 8:

            import pygame
            current_time = pygame.time.get_ticks()
            
            time_step = current_time // self.glitch_interval
            
            pseudo_random = (rect.x + rect.y * 13 + time_step * 7) % 10
            
            if pseudo_random < 4:
                return " "
            
            return str(val)

        return str(val)

class TutorialBoss(BossStrategy):
    def __init__(self, battle):
        super().__init__(battle)
        self.blink_timer = 0
        self.show_hint = False
        self.hint_interval = 0.8 

    def on_phase_start(self, phase_data):
        idx = self.battle.current_phase_idx

        if idx == 0:
            msgs = [
                "Lecția 1: Celulele de 1.",
                "Trebuie să acoperi TOATE celulele de 1.",
                "Fă grupurile cât mai mari posibil (puteri ale lui 2).",
                "NU selecta celulele de 0! Le voi bloca pentru tine acum."
            ]
            self.battle.queue_dialogue(msgs)

        elif idx == 1:
            msgs = [
                "Lecția 2: Riscuri și Ajutoare.",
                "Vezi bara de sus? E HP-ul tau, ai grija sa nu scada sub 0, oricum vei fi obosit",
                "Dacă soluția ta e greșită (prea mulți termeni), pierzi HP!",
                "Celulele 'X' sunt Don't Care. Le poți folosi ca 1 sau 0,",
                "oricum te ajută să faci grupul mai mare!",
                "In dreapta sus ai timpul ramas, daca expira, you're out"
            ]
            self.battle.queue_dialogue(msgs)

    def update(self, dt):
        self.blink_timer += dt
        if self.blink_timer >= self.hint_interval:
            self.blink_timer = 0
            self.show_hint = not self.show_hint

        if self.battle.current_phase_idx == 0:
            to_remove = []
            for idx in self.battle.selected_cells:
                if self.battle.cells[idx] == 0 and idx not in self.battle.dont_care:
                    to_remove.append(idx)
            
            if to_remove:
                for idx in to_remove:
                    self.battle.selected_cells.remove(idx)
                print("TUTORIAL: Ți-am scos 0-ul. Concentrează-te pe 1!")

    def get_cell_display(self, val, rect, mouse_pos):
        if rect.collidepoint(mouse_pos):
            if str(val) == "1": return "CLICK"
            if str(val) == "0": return "NO"
            if str(val) == "X": return "JOKER"

        if str(val) == "1":
            if self.show_hint:
                return "[1]"
            return " 1 "
            
        return str(val)
