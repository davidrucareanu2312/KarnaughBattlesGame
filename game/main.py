import pygame
import sys
import os

from game.camera import Camera
from game.map.map_loader import MapLoader
from game.player.player import Player
from game.ui.dialog import DialogBox
from game.cutscenes.boss_scene import BossScene
from game.battles.battle import Battle
from game.player.session import Session

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

STATE_INTRO = 0
STATE_TITLE = 1
STATE_GAME = 2
STATE_BOSS_SEQ = 3
STATE_BATTLE = 4

def main():
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Karnaugh Warriors")
    clock = pygame.time.Clock()

    dialog_ui = DialogBox(SCREEN_WIDTH, SCREEN_HEIGHT)
    root_path = os.path.join(os.path.dirname(__file__), "..")
    
    font_path = os.path.join(root_path, "assets", "fonts", "pixel.ttf")
    try:
        title_font = pygame.font.Font(font_path, 80)
        game_font = pygame.font.Font(font_path, 28)
    except:
        title_font = pygame.font.SysFont("couriernew", 80, bold=True)
        game_font = pygame.font.SysFont("couriernew", 28, bold=True)

    boss_cutscene = BossScene(SCREEN_WIDTH, SCREEN_HEIGHT, game_font)
    game_session = Session(max_health=100)

    try:
        intro_path = os.path.join(root_path, "assets", "maps", "intro_bg.png")
        intro_bg = pygame.image.load(intro_path).convert()
        intro_bg = pygame.transform.scale(intro_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        intro_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        intro_bg.fill((30, 30, 30))

    try:
        game_map = MapLoader()
        start_x, start_y = game_map.find_safe_spawn()
        player = Player(start_x, start_y)
        map_w, map_h = game_map.get_size()
        camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, map_w, map_h)
    except Exception as e:
        print(f"EROARE LA INIȚIALIZARE: {e}")
        sys.exit()

    current_battle = None
    current_boss_id = 0 
    current_state = STATE_INTRO
    
    dialog_ui.show("Sistem initializat... Apasa E pentru a continua.")

    running = True
    while running:
        dt = clock.get_time() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_state == STATE_BATTLE and current_battle:
                current_battle.handle_event(event)

            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                is_shift = mods & pygame.KMOD_SHIFT

                if current_state == STATE_INTRO:
                     if event.key == pygame.K_e:
                        if dialog_ui.active:
                            if not dialog_ui.done_typing: dialog_ui.skip_animation()
                            else: 
                                dialog_ui.hide()
                                current_state = STATE_TITLE
                     if is_shift and dialog_ui.active: dialog_ui.skip_animation()

                elif current_state == STATE_TITLE:
                    if event.key == pygame.K_e:
                        current_state = STATE_GAME

                elif current_state == STATE_GAME:
                    if event.key == pygame.K_f:
                        r = player.rect
                        print(f"DEBUG: Player la x={r.x}, y={r.y}")

                    if event.key == pygame.K_e:
                        if dialog_ui.active:
                            if not dialog_ui.done_typing:
                                dialog_ui.skip_animation()
                            else:
                                dialog_ui.hide()
                                
                                if hasattr(dialog_ui, 'pending_boss_data') and dialog_ui.pending_boss_data:
                                    b_data = dialog_ui.pending_boss_data
                                    
                                    img_name = b_data.get('boss_img', 'boss.png') 
                                    line_text = b_data.get('boss_line', '...')
                                    config_json = b_data.get('battle_config', 'configs/Karnaugh/K_template.json')
                                    music_file = b_data.get('boss_music')
                                    current_boss_id = b_data.get('boss_id', 0)
                                    
                                    already_beaten = False
                                    if current_boss_id == 1 and game_session.beaten_boss1: already_beaten = True
                                    if current_boss_id == 2 and game_session.beaten_boss2: already_beaten = True
                                    if current_boss_id == 3 and game_session.beaten_boss3: already_beaten = True
                                    if current_boss_id == 4 and game_session.beaten_boss4: already_beaten = True
                                    if current_boss_id == 5 and game_session.beaten_boss5: already_beaten = True
                                    
                                    can_fight = True
                                    
                                    if current_boss_id == 2 and not game_session.beaten_boss1: can_fight = False
                                    if current_boss_id == 3 and not game_session.beaten_boss2: can_fight = False
                                    if current_boss_id == 4 and not game_session.beaten_boss3: can_fight = False
                                    if current_boss_id == 5 and not game_session.beaten_boss4: can_fight = False

                                    if already_beaten:
                                        dialog_ui.show("Acest inamic a fost deja invins.")
                                        dialog_ui.pending_boss_data = None
                                    
                                    elif not can_fight:
                                        dialog_ui.show("Inca nu esti destul de puternic...")
                                        dialog_ui.pending_boss_data = None
                                        
                                    else:
                                        current_state = STATE_BOSS_SEQ
                                        boss_cutscene.start(img_name, line_text, config_json, music_file)
                                        dialog_ui.pending_boss_data = None

                        else:
                            interaction_data = game_map.check_interaction(player.hitbox)
                            if interaction_data:
                                msg = interaction_data['text']
                                dialog_ui.show(msg)
                                if is_shift: dialog_ui.skip_animation()
                                
                                if interaction_data.get('type') == 'boss_trigger':
                                    dialog_ui.pending_boss_data = interaction_data
                                else:
                                    dialog_ui.pending_boss_data = None
                    
                    if is_shift and dialog_ui.active: dialog_ui.skip_animation()

                elif current_state == STATE_BOSS_SEQ:
                    if event.key == pygame.K_e:
                        result = boss_cutscene.next_phase()
                        if result == "DONE":
                            conf_path = boss_cutscene.battle_config_path
                            full_path = os.path.join(root_path, conf_path)
                            try:
                                current_battle = Battle(screen, full_path, game_session)
                                current_state = STATE_BATTLE
                            except Exception as e:
                                print(f"Eroare pornire luptă: {e}")
                                current_state = STATE_GAME


        if current_state == STATE_INTRO:
            screen.blit(intro_bg, (0, 0))
            dialog_ui.draw(screen)

        elif current_state == STATE_TITLE:
            screen.fill((0, 0, 0))
            text_surf = title_font.render("Karnaugh Warriors", False, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surf, text_rect)
            hint = game_font.render("Press E to Start", False, (100, 100, 100))
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT//2 + 80))

        elif current_state == STATE_GAME:
            if not dialog_ui.active:
                player.handle_input(game_map)
            camera.update(player.rect)

            screen.fill((0, 0, 0))
            game_map.draw(screen, camera)
            player.draw(screen, camera)
            dialog_ui.draw(screen)

        elif current_state == STATE_BOSS_SEQ:
            boss_cutscene.update()
            boss_cutscene.draw(screen)

        elif current_state == STATE_BATTLE:
            if current_battle:
                current_battle.update(dt)
                current_battle.draw()
                
                if current_battle.finished:
                    pygame.mixer.music.stop()
                    
                    if current_battle.is_victory:
                        game_session.battles_won += 1
                        
                        if current_boss_id == 1: game_session.beaten_boss1 = True
                        elif current_boss_id == 2: game_session.beaten_boss2 = True
                        elif current_boss_id == 3: game_session.beaten_boss3 = True
                        elif current_boss_id == 4: game_session.beaten_boss4 = True
                        elif current_boss_id == 5: game_session.beaten_boss5 = True
                        
                        print(f"Boss {current_boss_id} DEFEATED!")
                        
                        current_state = STATE_GAME
                        
                        if current_boss_id == 1:
                            dialog_ui.show("Urmatorul tau adversar se situeaza in cladirea din nord.")
                        elif current_boss_id == 2:
                            dialog_ui.show("Urmatorul tau adversar se situeaza in cladirea din sud.")
                        elif current_boss_id == 3:
                            dialog_ui.show("Urmatorul tau adversar se situeaza in cladirea de langa cantina.")
                        elif current_boss_id == 4:
                            dialog_ui.show("Simti o energie festiva venind dinspre scena...")
                        elif current_boss_id == 5:
                            dialog_ui.show("FELICITARI! Ai absolvit sesiunea cu brio!")

                    if not game_session.is_alive:
                        print("GAME OVER - RESPAWNING")
                        game_session.reset() 
                        current_state = STATE_GAME 
                        dialog_ui.show("Ai fost invins... Te-ai intors la inceputul hartii.")
                    
                    current_battle = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()