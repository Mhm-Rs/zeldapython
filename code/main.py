import pygame
import sys

from level import Level
from settings import *


class Game:
    def __init__(self):
        # general setup for pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))

        # setup title
        pygame.display.set_caption("Zelda Python")

        # for icon
        self.icon = pygame.image.load("../graphics/test/icon.png")
        pygame.display.set_icon(self.icon)

        # to get real time
        self.clock = pygame.time.Clock()

        # game level
        self.level = Level()

        # for title screen
        self.active = True
        self.title_screen = pygame.image.load("../graphics/test/titlescreen.png")
        self.screen.blit(self.title_screen, (0, 0))
        pygame.display.flip()

        # sound_
        self.main_sound = pygame.mixer.Sound("../audio/main.ogg")
        self.main_sound.set_volume(0.8)

    def run(self):
        while True:
            # check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # access the upgrade menu through the u key
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.level.toggle_upgrade_menu()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.active:
                        self.active = False
                        self.main_sound.play(loops=-1)

            if not self.active:
                self.screen.fill(WATER_COLOR)
                self.level.run()
                pygame.display.update()
                self.clock.tick(FPS)


# create an instance if it's the main class
if __name__ == '__main__':
    game = Game()
    game.run()
