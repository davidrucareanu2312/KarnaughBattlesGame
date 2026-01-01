import pygame
import sys
import os

from game.battles.battle import Battle
from game.player.session import Session

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def main():
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Karnaugh Warriors - Battle Debugger")
    clock = pygame.time.Clock()

    game_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.join(game_dir, "..")

    game_session = Session(max_health=100)
    
    current_battle = None
    in_battle = False

    battle_config_path = os.path.join(root_path, "configs", "Karnaugh", "K_boss_1.json")

    running = True
    while running:
        dt = clock.get_time() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if in_battle and current_battle:
                current_battle.handle_event(event)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        try:    
                            current_battle = Battle(screen, battle_config_path, game_session)
                            in_battle = True
                        except Exception as e:
                            print(f"Eroare la pornirea luptei: {e}")

        screen.fill((30, 30, 30))

        if in_battle and current_battle:
            current_battle.update(dt)
            current_battle.draw()

            if current_battle.finished:
                in_battle = False
                current_battle = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()