import pygame

class BattleRenderer:
    def __init__(self, screen):
        self.screen = screen
        
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.label_font = pygame.font.SysFont("Consolas", 24, bold=True)
        self.corner_font = pygame.font.SysFont("Consolas", 28, bold=True)

    def draw(self, battle):
        self.screen.fill((0, 0, 0))
        
        if battle.show_end_screen:
            self._draw_end_screen(battle)
            return 

        screen_w, screen_h = self.screen.get_size()
        
        start_x, start_y = 50, 100
        if battle.rows > 0:
            grid_width = battle.cols * (battle.cell_width + battle.margin)
            grid_height = battle.rows * (battle.cell_height + battle.margin)
            start_x = (screen_w - grid_width) // 2
            start_y = (screen_h - grid_height) // 2 + 50 

        self._draw_health_bar(battle, screen_w, 50)
        self._draw_header(battle, screen_w)

        if battle.boss_image:
            sprite_x = screen_w - battle.boss_image.get_width() - 20
            self.screen.blit(battle.boss_image, (sprite_x, 60))

        if battle.rows > 0:
            self._draw_grid(battle, start_x, start_y)

        # --- LOGICA NOUA PENTRU DIALOG BOX ---
        if battle.dialog_box.active:
            # 1. Apelăm metoda draw din DialogBox
            battle.dialog_box.draw(self.screen)
            
            # 2. Desenăm elemente extra (Nume Boss, Hint Space) care nu sunt in clasa DialogBox
            
            # Numele boss-ului deasupra cutiei (ajustat la rect-ul cutiei)
            # rect-ul este accesibil prin battle.dialog_box.rect
            box_rect = battle.dialog_box.rect
            name_y = box_rect.y - 30
            
            if not battle.is_tutorial:
                name_surf = self.font.render(f"{battle.boss_name}:", True, (255, 100, 100))
                self.screen.blit(name_surf, (box_rect.x, name_y))
            
            # Textul [SPACE] doar dacă s-a terminat de scris
            if battle.dialog_box.done_typing:
                cont_txt = self.font.render("[SPACE] Continua...", True, (150, 150, 150))
                # Blink effect
                if pygame.time.get_ticks() % 1000 < 500:
                    self.screen.blit(cont_txt, (box_rect.right - 200, box_rect.bottom - 40))

        elif battle.show_summary:
            self._draw_summary(battle)
        elif battle.show_options:
            self._draw_options(battle, screen_w, screen_h)

    # ... (Metodele _draw_health_bar, _draw_header, _draw_grid, _draw_summary, _draw_options, _draw_end_screen raman neschimbate) ...
    
    def _draw_health_bar(self, battle, screen_w, y_pos):
        bar_width = 400
        bar_height = 30
        bar_x = (screen_w - bar_width) // 2
        
        pygame.draw.rect(self.screen, (50, 0, 0), (bar_x, y_pos, bar_width, bar_height))
        
        current = battle.session.current_health
        maximum = battle.session.max_health
        health_percent = max(0, current / maximum)
        
        current_bar_width = int(bar_width * health_percent)
        pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, y_pos, current_bar_width, bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, y_pos, bar_width, bar_height), 2)
        
        hp_txt = self.font.render(f"{int(current)}/{maximum}", True, (255, 255, 255))
        self.screen.blit(hp_txt, hp_txt.get_rect(center=(screen_w // 2, y_pos + 15)))
        
        if not battle.is_tutorial:
            boss_txt = self.font.render(battle.boss_name, True, (255, 255, 255))
            self.screen.blit(boss_txt, boss_txt.get_rect(center=(screen_w // 2, y_pos - 20)))

    def _draw_header(self, battle, screen_w):
        self.screen.blit(self.font.render(f"Faza: {battle.current_phase_idx + 1}/{battle.total_phases}", True, (255, 200, 0)), (20, 20))
        self.screen.blit(self.font.render(f"Scor: {battle.total_score:.2f}", True, (0, 255, 255)), (20, 50))
        self.screen.blit(self.font.render(f"Timp: {int(battle.time_left)}s", True, (0, 255, 0)), (screen_w - 150, 20))

    def _draw_grid(self, battle, start_x, start_y):
        if battle.corner_label:
            self.screen.blit(self.font.render(battle.corner_label, True, (255, 100, 100)), (start_x - 55, start_y - 30))
        
        for c in range(battle.cols):
             if c < len(battle.col_labels):
                lbl = battle.col_labels[c]
                txt = self.label_font.render(lbl, True, (100, 200, 255))
                x_pos = start_x + c*(battle.cell_width+battle.margin) + (battle.cell_width//2) - (txt.get_width()//2)
                self.screen.blit(txt, (x_pos, start_y - 25))

        for r in range(battle.rows):
             if r < len(battle.row_labels):
                lbl = battle.row_labels[r]
                txt = self.label_font.render(lbl, True, (100, 200, 255))
                y_pos = start_y + r*(battle.cell_height+battle.margin) + (battle.cell_height//2) - (txt.get_height()//2)
                self.screen.blit(txt, (start_x - 50, y_pos))

        mx, my = pygame.mouse.get_pos()
        for r in range(battle.rows):
            for c in range(battle.cols):
                idx = r * battle.cols + c
                if idx < len(battle.cells):
                    val = battle.cells[idx]
                    rect = pygame.Rect(start_x + c*(battle.cell_width+battle.margin), start_y + r*(battle.cell_height+battle.margin), battle.cell_width, battle.cell_height)
                    
                    color = (200, 200, 200) if idx in battle.dont_care else (255, 255, 255)
                    pygame.draw.rect(self.screen, color, rect)
                    
                    for group in battle.selected_groups:
                        if idx in group: pygame.draw.rect(self.screen, (255, 215, 0), rect, width=8)
                    if idx in battle.selected_cells:
                        pygame.draw.circle(self.screen, (0, 200, 0), rect.center, min(battle.cell_width, battle.cell_height)//3, width=5)

                    base_text = "X" if idx in battle.dont_care else str(val)
                    display_text = battle.boss_logic.get_cell_display(base_text, rect, (mx, my))
                    
                    if display_text == "HIDDEN":
                        pygame.draw.circle(self.screen, (150, 150, 150), rect.center, 20) 
                    else:
                        txt = self.font.render(display_text, True, (0,0,0))
                        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def _draw_summary(self, battle):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        cx, cy = self.screen.get_width() // 2, self.screen.get_height() // 2

        if not battle.is_tutorial:
            # --- CAZ NORMAL: Statistici Detaliate ---
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0,0))
            
            self.screen.blit(self.font.render(f"Faza {battle.current_phase_idx+1} Completă", True, (0, 255, 0)), (cx-100, cy-120))
            self.screen.blit(self.font.render(f"Tu: {battle.user_solution}", True, (200, 200, 255)), (cx-150, cy-70))
            self.screen.blit(self.font.render(f"Optim: {battle.optimal_solution}", True, (100, 255, 100)), (cx-150, cy-20))
            
            score_txt = f"Scor: {battle.calculated_score:.2f} x {battle.weight} = +{battle.round_score:.2f}"
            self.screen.blit(self.font.render(score_txt, True, (255, 255, 0)), (cx-150, cy+30))
            
            if battle.calculated_score < battle.min_round_score_threshold:
                dmg_txt = self.font.render(f"DAMAGE TAKEN: -{10 * battle.weight}", True, (255, 0, 0))
                self.screen.blit(dmg_txt, dmg_txt.get_rect(center=(cx, cy + 70)))

            self.screen.blit(self.font.render("[N] Next  [R] Retry", True, (255, 255, 0)), (cx-100, cy+130))
        
        else:
            # --- CAZ TUTORIAL: Mesaj Incurajare + Fundal Gri ---
            # Fundal Gri Transparent (80, 80, 80, 220)
            overlay.fill((80, 80, 80, 220)) 
            self.screen.blit(overlay, (0, 0))

            # Mesajul cerut
            msg = self.font.render("BRAVO, jocul diagramelor karnaugh iti vine natural", True, (255, 255, 255))
            self.screen.blit(msg, msg.get_rect(center=(cx, cy - 20)))

            # Navigatia (ca sa poti trece mai departe)
            nav = self.font.render("[N] Next  [R] Retry", True, (255, 255, 0))
            self.screen.blit(nav, nav.get_rect(center=(cx, cy + 80)))

    def _draw_options(self, battle, w, h):
        msg_save = self.font.render("[S] Save & Check", True, (0, 255, 0))
        self.screen.blit(msg_save, msg_save.get_rect(center=(w//2, h-50)))

    def _draw_end_screen(self, battle):
        # 1. Background semi-transparent cu nuanță în funcție de rezultat
        if not battle.is_tutorial:
            s = pygame.Surface(self.screen.get_size())
            s.set_alpha(240)
            # Verde închis pentru victorie, Roșu închis pentru înfrângere
            bg_col = (20, 40, 20) if battle.is_victory else (40, 10, 10)
            s.fill(bg_col)
            self.screen.blit(s, (0, 0))
            
            cx, cy = self.screen.get_width() // 2, self.screen.get_height() // 2
            
            # 2. Desenare Imagine Boss (cu păstrarea proporțiilor - Aspect Ratio)
            if battle.boss_image:
                # Calculăm scara pentru a încăpea într-un box de 200x200 fără distorsionare
                img_rect = battle.boss_image.get_rect()
                max_size = 200
                scale_factor = min(max_size / img_rect.width, max_size / img_rect.height)
                new_size = (int(img_rect.width * scale_factor), int(img_rect.height * scale_factor))
                
                # Folosim smoothscale pentru calitate mai bună
                boss_big = pygame.transform.smoothscale(battle.boss_image, new_size)
                
                # Poziționăm imaginea mai sus de centru
                draw_rect = boss_big.get_rect(center=(cx, cy - 180))
                self.screen.blit(boss_big, draw_rect)
                
                # Desenăm un contur subțire în jurul imaginii
                pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, 2)

            # 3. Titlu (Victory/Defeat) cu umbră
            if battle.is_victory:
                main_text = "VICTORY!"
                col = (50, 255, 50) # Verde aprins
                sub_text = f"Ai învins boss-ul {battle.boss_name}!"
            else:
                main_text = "DEFEAT"
                col = (255, 50, 50) # Roșu aprins
                # Verificăm dacă există atributul, altfel mesaj generic
                sub_text = getattr(battle, 'defeat_text', "Nu ai acumulat suficient scor.")

            # Desenare umbră titlu (offset +2px)
            title_shadow = self.title_font.render(main_text, True, (0, 0, 0))
            self.screen.blit(title_shadow, title_shadow.get_rect(center=(cx + 3, cy + 3)))
            
            # Desenare titlu principal
            title = self.title_font.render(main_text, True, col)
            self.screen.blit(title, title.get_rect(center=(cx, cy)))
            
            # 4. Motiv / Subtext
            reason = self.font.render(sub_text, True, (220, 220, 220))
            self.screen.blit(reason, reason.get_rect(center=(cx, cy + 50)))

            # 5. Scoruri
            # Culoarea scorului: Verde dacă e peste prag, Roșu dacă e sub
            score_color = (100, 255, 100) if battle.total_score >= battle.min_total_score_threshold else (255, 100, 100)
            
            score_text = f"SCOR FINAL: {battle.total_score:.2f} / {battle.max_possible_score:.2f}"
            sc_surf = self.font.render(score_text, True, score_color)
            self.screen.blit(sc_surf, sc_surf.get_rect(center=(cx, cy + 100)))
            
            req_surf = self.font.render(f"Necesar promovare: {battle.min_total_score_threshold}", True, (255, 215, 0))
            self.screen.blit(req_surf, req_surf.get_rect(center=(cx, cy + 140)))
            
            # 6. Mesaj de ieșire (cu efect de blink)
            current_time = pygame.time.get_ticks()
            if current_time % 1000 < 600: # Textul e vizibil 600ms, invizibil 400ms
                exit_msg = self.font.render("Apasa [ENTER] pentru a iesi", True, (180, 180, 180))
                self.screen.blit(exit_msg, exit_msg.get_rect(center=(cx, cy + 220)))
        else:
            if battle.boss_image:
                
                cx, cy = self.screen.get_width() // 2, self.screen.get_height() // 2
                # Calculăm scara pentru a încăpea într-un box de 200x200 fără distorsionare
                img_rect = battle.boss_image.get_rect()
                max_size = 200
                scale_factor = min(max_size / img_rect.width, max_size / img_rect.height)
                new_size = (int(img_rect.width * scale_factor), int(img_rect.height * scale_factor))
                
                # Folosim smoothscale pentru calitate mai bună
                boss_big = pygame.transform.smoothscale(battle.boss_image, new_size)
                
                # Poziționăm imaginea mai sus de centru
                draw_rect = boss_big.get_rect(center=(cx, cy - 180))
                self.screen.blit(boss_big, draw_rect)
                
                # Desenăm un contur subțire în jurul imaginii
                pygame.draw.rect(self.screen, (255, 255, 255), draw_rect, 2)
