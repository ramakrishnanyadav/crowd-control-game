import pygame
import sys
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE
from scenes.scene_manager import SceneManager
from scenes.menu_scene import MenuScene
from scenes.game_scene import  GameScene  # ← Changed this line
from scenes.results_scene import ResultsScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    
    scene_manager = SceneManager()
    menu_scene = MenuScene(scene_manager)
    game_scene = GameScene(scene_manager)  # ← This now creates EnhancedGameScene
    results_scene = ResultsScene(scene_manager)
    
    scene_manager.add_scene('menu', menu_scene)
    scene_manager.add_scene('game', game_scene)
    scene_manager.add_scene('results', results_scene)
    scene_manager.change_scene('menu')
    
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                scene_manager.handle_event(event)
        scene_manager.update(dt)
        scene_manager.render(screen)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()