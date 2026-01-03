import pygame
import sys
import os
import json

from game.camera import Camera
from game.map.map_loader import MapLoader
from game.player.player import Player
from game.ui.dialog import DialogBox
from game.cutscenes.boss_scene import BossScene
from game.battles.battle import Battle
from game.player.session import Session
from game.saveStates import SaveManager

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

STATE_INTRO = 0
STATE_SAVE_SELECT = 1
STATE_SLOT_CONFIRM = 2
STATE_TITLE = 3
STATE_GAME = 4
STATE_BOSS_SEQ = 5
STATE_BATTLE = 6

def main():
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Karnaugh Warriors")
    clock = pygame.time.Clock()

    game_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.join(game_dir, "..")
    
    dialog_ui = DialogBox(SCREEN_WIDTH, SCREEN_HEIGHT)
    font_path = os.path.join(root_path, "assets", "fonts", "pixel.ttf")
    
    try:
        title_font = pygame.font.Font(font_path, 60)
        game_font = pygame.font.Font(font_path, 28)
        small_font = pygame.font.Font(font_path, 20)
    except:
        title_font = pygame.font.SysFont("couriernew", 60, bold=True)
        game_font = pygame.font.SysFont("couriernew", 28, bold=True)
        small_font = pygame.font.SysFont("couriernew", 20)

    boss_cutscene = BossScene(SCREEN_WIDTH, SCREEN_HEIGHT, game_font)
    game_session = Session(max_health=100)
    save_manager = SaveManager()

    try:
        intro_path = os.path.join(root_path, "assets", "maps", "intro_bg.png")
        intro_bg = pygame.image.load(intro_path).convert()
        intro_bg = pygame.transform.scale(intro_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        intro_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        intro_bg.fill((50, 50, 50))

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
    
    is_tutorial = False
    is_new_game = True 
    
    pending_slot = None 

    current_state = STATE_INTRO
    dialog_ui.show("ACS CTI initializat. Apasa E pentru a continua...")

    running = True
    while running:
        dt = clock.get_time() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if game_session.current_slot is not None:
                    print("Auto-save la exit...")
                    save_manager.save_game(game_session, player)
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
                                current_state = STATE_SAVE_SELECT
                     if is_shift and dialog_ui.active: dialog_ui.skip_animation()

                elif current_state == STATE_SAVE_SELECT:
                    selected_slot = None
                    if event.key == pygame.K_1: selected_slot = 1
                    elif event.key == pygame.K_2: selected_slot = 2
                    elif event.key == pygame.K_3: selected_slot = 3
                    
                    if selected_slot:
                        if save_manager.is_slot_written(selected_slot):
                            pending_slot = selected_slot
                            current_state = STATE_SLOT_CONFIRM
                        else:
                            game_session.reset()
                            game_session.current_slot = selected_slot
                            player.rect.topleft = (start_x, start_y)
                            
                            is_new_game = True
                            current_state = STATE_TITLE
                            dialog_ui.show(f"Slot {selected_slot} selectat. Joc now btw!")

                elif current_state == STATE_SLOT_CONFIRM:
                    if event.key == pygame.K_c:
                        save_manager.load_game(pending_slot, game_session, player)
                        is_new_game = False
                        current_state = STATE_TITLE
                        dialog_ui.show(f"Slot {pending_slot} incarcat. La munca, nu la intins mana!")
                        
                    elif event.key == pygame.K_n:
                        game_session.reset()
                        game_session.current_slot = pending_slot
                        player.rect.topleft = (start_x, start_y)
                        is_new_game = True
                        current_state = STATE_TITLE
                        dialog_ui.show(f"Slot {pending_slot} suprascris. Joc now btw!")
                        
                    elif event.key == pygame.K_ESCAPE:
                        pending_slot = None
                        current_state = STATE_SAVE_SELECT

                elif current_state == STATE_TITLE:
                    if event.key == pygame.K_e:
                        if dialog_ui.active: dialog_ui.hide()
                        if is_new_game:
                            tut_path = os.path.join(root_path, "configs", "Karnaugh", "K_tutorial.json")
                            try:
                                current_battle = Battle(screen, tut_path, game_session)
                                current_state = STATE_BATTLE
                                is_tutorial = True 
                            except:
                                current_state = STATE_GAME
                        else:
                            current_state = STATE_GAME

                elif current_state == STATE_GAME:
                    if event.key == pygame.K_f:
                        print(f"Player: {player.rect.topleft}")

                    if event.key == pygame.K_e:
                        if dialog_ui.active:
                            if not dialog_ui.done_typing: dialog_ui.skip_animation()
                            else:
                                dialog_ui.hide()
                                if hasattr(dialog_ui, 'pending_boss_data') and dialog_ui.pending_boss_data:
                                    b_data = dialog_ui.pending_boss_data
                                    current_boss_id = b_data.get('boss_id', 0)
                                    img_name = b_data.get('boss_img', 'boss.png') 
                                    line_text = b_data.get('boss_line', '...')
                                    config_json = b_data.get('battle_config')
                                    music_file = b_data.get('boss_music')

                                    can_fight = True
                                    already_beaten = False
                                    
                                    if current_boss_id == 1 and game_session.beaten_boss1: already_beaten = True
                                    if current_boss_id == 2 and game_session.beaten_boss2: already_beaten = True
                                    if current_boss_id == 3 and game_session.beaten_boss3: already_beaten = True
                                    if current_boss_id == 4 and game_session.beaten_boss4: already_beaten = True
                                    if current_boss_id == 5 and game_session.beaten_boss5: already_beaten = True
                                    if current_boss_id == 2 and not game_session.beaten_boss1: can_fight = False
                                    if current_boss_id == 3 and not game_session.beaten_boss2: can_fight = False
                                    if current_boss_id == 4 and not game_session.beaten_boss3: can_fight = False
                                    if current_boss_id == 5 and not game_session.beaten_boss4: can_fight = False

                                    if already_beaten:
                                        dialog_ui.show("Acest inamic a fost deja invins. Nataflet cu parul cret!")
                                        dialog_ui.pending_boss_data = None
                                    elif not can_fight:
                                        dialog_ui.show("Inca nu esti destul de puternic...")
                                        dialog_ui.pending_boss_data = None
                                    else:
                                        current_state = STATE_BOSS_SEQ
                                        boss_cutscene.start(img_name, line_text, config_json, music_file)
                                        dialog_ui.pending_boss_data = None
                                        is_tutorial = False
                        else:
                            interaction_data = game_map.check_interaction(player.hitbox)
                            if interaction_data:
                                dialog_ui.show(interaction_data['text'])
                                if interaction_data.get('type') == 'boss_trigger':
                                    dialog_ui.pending_boss_data = interaction_data
                                else:
                                    dialog_ui.pending_boss_data = None
                    
                    if is_shift and dialog_ui.active: dialog_ui.skip_animation()

                elif current_state == STATE_BOSS_SEQ:
                    if event.key == pygame.K_e:
                        res = boss_cutscene.next_phase()
                        if res == "DONE":
                            p = os.path.join(root_path, boss_cutscene.battle_config_path)
                            current_battle = Battle(screen, p, game_session)
                            current_state = STATE_BATTLE

        if current_state == STATE_INTRO:
            screen.blit(intro_bg, (0, 0))
            dialog_ui.draw(screen)


        if current_state == STATE_INTRO:
            screen.blit(intro_bg, (0, 0))
            dialog_ui.draw(screen)

        elif current_state == STATE_SAVE_SELECT:
            screen.fill((5, 5, 25)) 
            
            title_s = title_font.render("SELECT SAVE SLOT", True, (100, 200, 255))
            screen.blit(title_s, (SCREEN_WIDTH//2 - title_s.get_width()//2, 50))
            
            for i in range(1, 4):
                info_text = save_manager.get_save_info(i)
                
                color = (255, 255, 255) 
                if "GOL" in info_text: 
                    color = (100, 100, 120)
                
                slot_surf = game_font.render(f"[{i}] {info_text}", True, color)
                screen.blit(slot_surf, (100, 150 + i * 60))
            
            hint = small_font.render("Apasa 1, 2 sau 3 pentru a alege.", True, (150, 150, 150))
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 500))

        elif current_state == STATE_SLOT_CONFIRM:
            screen.fill((10, 10, 35)) 
            
            t = title_font.render(f"SLOT {pending_slot} EXISTA!", True, (255, 140, 0))
            screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 100))
            
            info_txt = save_manager.get_save_info(pending_slot)
            info_surf = small_font.render(info_txt, True, (200, 200, 255))
            screen.blit(info_surf, (SCREEN_WIDTH//2 - info_surf.get_width()//2, 180))

            msg1 = game_font.render("Apasa [C] pentru a CONTINUA", True, (100, 255, 100))
            screen.blit(msg1, (SCREEN_WIDTH//2 - msg1.get_width()//2, 280))
            
            msg2 = game_font.render("Apasa [N] pentru JOC NOU (Sterge progresul)", True, (255, 100, 100))
            screen.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, 350))
            
            esc = small_font.render("[ESC] Inapoi", True, (150, 150, 170))
            screen.blit(esc, (SCREEN_WIDTH//2 - esc.get_width()//2, 520))


        elif current_state == STATE_TITLE:
            screen.fill((0, 0, 0))
            t = title_font.render("Karnaugh Warriors", False, (255, 255, 255))
            screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, SCREEN_HEIGHT//2))
            
            st_txt = "NEW GAME START" if is_new_game else "CONTINUE GAME"
            st_s = game_font.render(st_txt, True, (0, 255, 0))
            screen.blit(st_s, (SCREEN_WIDTH//2 - st_s.get_width()//2, SCREEN_HEIGHT//2 + 60))
            
            hint = game_font.render("Press E to Play", False, (100, 100, 100))
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT//2 + 120))
            dialog_ui.draw(screen)

        elif current_state == STATE_GAME:
            if not dialog_ui.active: player.handle_input(game_map)
            camera.update(player.rect)
            screen.fill((0,0,0))
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
                    if is_tutorial:
                        game_session.reset()
                        current_state = STATE_GAME
                        is_tutorial = False
                        current_battle = None
                        dialog_ui.show("Tutorial terminat!")
                    else:
                        if current_battle.is_victory:
                            game_session.battles_won += 1
                            if current_boss_id == 1: game_session.beaten_boss1 = True
                            if current_boss_id == 2: game_session.beaten_boss2 = True
                            if current_boss_id == 3: game_session.beaten_boss3 = True
                            if current_boss_id == 4: game_session.beaten_boss4 = True
                            if current_boss_id == 5: game_session.beaten_boss5 = True
                            current_state = STATE_GAME
                            dialog_ui.show("Victorie!")
                        else:
                            if not game_session.is_alive:
                                game_session.reset()
                                player.rect.topleft = (start_x, start_y)
                                current_state = STATE_GAME
                                dialog_ui.show("Ai fost invins... Te-ai intors la inceputul hartii.")
                            else:
                                current_state = STATE_GAME
                        current_battle = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()