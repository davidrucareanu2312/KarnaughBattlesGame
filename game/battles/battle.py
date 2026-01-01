import pygame
import json
import os
from .solver import solve_karnaugh
from .k_utils import is_valid_group, term_from_group
from .bosses import StandardBoss, HazardStateBoss
from .renderer import BattleRenderer

class Battle:
    def __init__(self, screen, config_path, session):
        self.screen = screen
        self.finished = False
        self.session = session
        
        w, h = screen.get_size()

        self.renderer = BattleRenderer(screen) 
        
        self.max_health = session.max_health
        self.current_health = session.max_health
        
        with open(config_path) as f:
            self.config = json.load(f)
            
        self.boss_name = self.config.get("campaign_name", "Unknown Boss")
        self.time_left = self.config.get("total_time", 300)
        
        self.min_round_score_threshold = self.config.get("minimal_round_score", 0.5)
        self.min_total_score_threshold = self.config.get("minimal_score", 0.5)
        
        self.phases = self.config["levels"] 
        self.total_phases = len(self.phases)
        self.current_phase_idx = 0

        sprite_path = self.config.get("boss_sprite", "")
        self.boss_image = None
        if os.path.exists(sprite_path):
            try:
                img = pygame.image.load(sprite_path).convert_alpha()
                self.boss_image = pygame.transform.scale(img, (150, 150))
            except Exception as e:
                print(f"Eroare incarcare sprite: {e}")
        
        self.defeat_text = "Ai fost invins."

        boss_type = self.config.get("boss_behavior", "standard")
        self.boss_logic = StandardBoss(self)
        if boss_type == "hazard": self.boss_logic = HazardStateBoss(self)

        self.rows = 0
        self.cols = 0
        self.cell_width = 0
        self.cell_height = 0
        self.margin = 5
        self.corner_label = ""
        self.row_labels = []
        self.col_labels = []
        self.cells = []
        self.dont_care = []
        self.level_name = ""

        self.selected_cells = set()
        self.selected_groups = []
        self.show_options = False
        self.show_summary = False
        self.show_end_screen = False  
        self.is_victory = False 
        
        self.user_solution = ""
        self.optimal_solution = ""
        
        self.weight = 1.0          
        self.calculated_score = 0.0 
        self.round_score = 0.0      
        self.total_score = 0.0      
        self.max_possible_score = 0.0 

        self.load_phase(0)

    def calculate_metrics(self, sol_str):
        clean = sol_str.replace(" ", "")
        if clean == "0" or clean == "1":
            return 1, 1 
        terms = clean.split("+")
        num_terms = len(terms)
        total_len = 0
        for t in terms:
            length = sum(1 for char in t if char.isalpha())
            total_len += max(1, length)
        return num_terms, total_len

    def check_game_end_condition(self):
        self.show_end_screen = True
        if self.total_score >= self.min_total_score_threshold:
            self.is_victory = True
            self.session.beaten_boss = True
        else:
            self.is_victory = False
            self.defeat_text = "restanta la PL, nu ai luat destul pe parcurs"
            self.session.beaten_boss = False

    def load_phase(self, index):
        if index >= len(self.phases):
            self.check_game_end_condition()
            return

        phase_data = self.phases[index]
        self.level_name = phase_data.get("level_name", f"Phase {index+1}")
        self.num_vars = phase_data["num_vars"]
        self.cells = phase_data["cells"]
        self.dont_care = phase_data.get("dont_care", [])
        
        self.weight = phase_data.get("weight", 1.0) 
        self.max_possible_score += self.weight 
        
        self.selected_cells = set()
        self.selected_groups = []
        self.show_options = False
        self.show_summary = False
        self.calculated_score = 0.0
        self.round_score = 0.0
        
        self.setup_grid_layout()
        self.boss_logic.on_phase_start(phase_data)

    def setup_grid_layout(self):
        if self.num_vars == 2:
            self.rows, self.cols = 2, 2
            self.cell_width, self.cell_height = 160, 160
            self.row_labels, self.col_labels = ["0", "1"], ["0", "1"]
            self.corner_label = "A \\ B"
        elif self.num_vars == 3:
            self.rows, self.cols = 2, 4
            self.cell_width, self.cell_height = 160, 160
            self.row_labels, self.col_labels = ["0", "1"], ["00", "01", "11", "10"]
            self.corner_label = "A \\ BC"
        elif self.num_vars == 4:
            self.rows, self.cols = 4, 4
            self.cell_width, self.cell_height = 100, 100
            self.row_labels, self.col_labels = ["00", "01", "11", "10"], ["00", "01", "11", "10"]
            self.corner_label = "AB \\ CD"
        
        self.margin = 5

    def update(self, dt):
        if self.show_end_screen:
            return

        if not self.finished and not self.show_summary:
            self.time_left -= dt
            self.boss_logic.update(dt)
            
            if self.time_left <= 0:
                self.time_left = 0
                self.is_victory = False
                self.defeat_text = "nu a mai ramas timp sa iti termini temele"
                self.show_end_screen = True
            
            if not self.session.is_alive:
                self.is_victory = False
                self.defeat_text = "ai ramas fara HP, esti obosit"
                self.show_end_screen = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.show_end_screen:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.finished = True
                return 

            if event.key == pygame.K_ESCAPE:
                self.finished = True
                return

            if self.show_summary:
                if event.key == pygame.K_n or event.key == pygame.K_RETURN:
                    if not self.session.is_alive:
                        self.is_victory = False
                        self.defeat_text = "ai ramas fara HP, esti obosit"
                        self.show_end_screen = True
                        return

                    phases_completed = self.current_phase_idx + 1
                    if phases_completed < self.total_phases:
                        self.current_phase_idx += 1
                        self.load_phase(self.current_phase_idx)
                    else:
                        self.check_game_end_condition()
                
                elif event.key == pygame.K_r:
                    self.total_score -= self.round_score 
                    self.load_phase(self.current_phase_idx)
                return

            if self.show_options:
                if event.key == pygame.K_s:
                    user_terms = [term_from_group(g, self.num_vars, self.rows, self.cols) for g in self.selected_groups]
                    self.user_solution = " + ".join(user_terms) if user_terms else "0"
                    self.optimal_solution = solve_karnaugh(self.cells, self.dont_care, self.num_vars)
                    
                    n_user, l_user = self.calculate_metrics(self.user_solution)
                    n_opt, l_opt   = self.calculate_metrics(self.optimal_solution)
                    
                    ratio_terms = n_user / max(1, n_opt)
                    ratio_lens  = l_user / max(1, l_opt)
                    sum_ratios = ratio_terms + ratio_lens
                    
                    if sum_ratios == 0: sum_ratios = 2
                    self.calculated_score = 2.0 / sum_ratios 
                    
                    self.round_score = self.calculated_score * self.weight
                    self.total_score += self.round_score
                    
                    if self.calculated_score < self.min_round_score_threshold:
                        damage = 10 * self.weight
                        self.session.take_damage(damage)
                        self.current_health -= damage
                    
                    self.show_summary = True
                    self.show_options = False
                elif event.key == pygame.K_a:
                    self.selected_groups.clear()
                    self.selected_cells.clear()
                    self.show_options = False
                return

            if event.key == pygame.K_RETURN:
                if self.selected_cells:
                    group = set(self.selected_cells)
                    if is_valid_group(group, self.cells, self.dont_care, self.rows, self.cols):
                        self.selected_groups.append(group)
                    self.selected_cells.clear()
                    if self.check_complete():
                        self.show_options = True

        elif event.type == pygame.MOUSEBUTTONDOWN and not self.show_summary and not self.show_end_screen:
            mx, my = event.pos
            if self.rows > 0:
                screen_w, screen_h = self.screen.get_size()
                grid_width = self.cols * (self.cell_width + self.margin)
                grid_height = self.rows * (self.cell_height + self.margin)
                start_x = (screen_w - grid_width) // 2
                start_y = (screen_h - grid_height) // 2 + 50 

                for r in range(self.rows):
                    for c in range(self.cols):
                        idx = r * self.cols + c
                        rect = pygame.Rect(start_x + c*(self.cell_width+self.margin), start_y + r*(self.cell_height+self.margin), self.cell_width, self.cell_height)
                        if rect.collidepoint(mx, my):
                            if idx in self.selected_cells: self.selected_cells.remove(idx)
                            else: self.selected_cells.add(idx)

    def check_complete(self):
        covered = set().union(*self.selected_groups)
        for idx, val in enumerate(self.cells):
            if idx not in self.dont_care and val == 1 and idx not in covered:
                return False
        return True

    def draw(self):
        self.renderer.draw(self)