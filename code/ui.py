import pygame
from settings import *


class UI:
    def __init__(self):
        # * General info

        # get the surface as the screen (the same used anywhere else)
        self.display_surface = pygame.display.get_surface()

        # use the suitable font
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # * Bar setup

        # create the health bar (a rectangle placed on (10,10))
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)

        # create the energy bar (a rectangle placed on (10,34))
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        # convert the graphics of weapon data dictionnary as a list of images
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            fullpath = weapon["graphic"]
            weapon_image = pygame.image.load(fullpath)
            self.weapon_graphics.append(weapon_image)

        # convert the graphics of weapon data dictionnary as a list of images
        self.magic_graphics = []
        for magic in magic_data.values():
            fullpath = magic["graphic"]
            magic_image = pygame.image.load(fullpath)
            self.magic_graphics.append(magic_image)

    def show_bar(self, current_amount, max_amount, background_rect, color):
        # draw the background of the bar
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, background_rect)

        # converting stat to pixel

        # apply rule of three : for example for health 100 = health = max_amount = 200px=width of background rect,
        # therefore current_width = current_amount*200/max_amount

        ratio = current_amount / max_amount
        current_width = background_rect.width * ratio

        # position the rect for the stat in the same position as the background one and then change its width
        current_rect = background_rect.copy()
        current_rect.width = current_width

        # draw the bar
        pygame.draw.rect(self.display_surface, color, current_rect)

        # add a border around the bar
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, background_rect, 3)

    def show_exp(self, exp):
        # get the exp as a text and display it 
        text_surf = self.font.render("EXP : " + str(int(exp)), False, TEXT_COLOR)

        # get the position where we'll display
        x = self.display_surface.get_size()[0] - 20
        y = self.display_surface.get_size()[1] - 20
        text_rect = text_surf.get_rect(bottomright=(x, y))

        # add a background
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))

        # add the border of the background
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

        # display the text
        self.display_surface.blit(text_surf, text_rect)

    def selection_box(self, left, top, has_switched):
        # display the box which will contain an item(weapon / magic) 

        # get the rect
        background_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)

        # display the background
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, background_rect)

        # add a border
        if has_switched:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, background_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, background_rect, 3)

        # return the rect for later use for the weapon/magic
        return background_rect

    def weapon_overlay(self, weapon_index, has_switched):
        # display the weapon box
        background_rect = self.selection_box(10, 630, has_switched)

        # get the surface as the current selected weapon 
        weapon_surf = self.weapon_graphics[weapon_index]

        # get the rectangle 
        weapon_rect = weapon_surf.get_rect(center=background_rect.center)

        # display the weapon
        self.display_surface.blit(weapon_surf, weapon_rect)

    def magic_overlay(self, magic_index, has_switched):
        # display the weapon box
        background_rect = self.selection_box(80, 635, has_switched)

        # get the surface as the current selected magic
        magic_surf = self.magic_graphics[magic_index]

        # get the rectangle
        magic_rect = magic_surf.get_rect(center=background_rect.center)

        # display the magic
        self.display_surface.blit(magic_surf, magic_rect)

    def display(self, player):
        # display both bars
        self.show_bar(player.health, player.stats["health"], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats["energy"], self.energy_bar_rect, ENERGY_COLOR)

        # display exp
        self.show_exp(player.exp)

        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon)
        self.magic_overlay(player.magic_index, not player.can_switch_magic)
