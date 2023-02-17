import pygame
from settings import *


class Upgrade:
    def __init__(self, player):

        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attribute_number = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # selection system
        self.selection_index = self.attribute_number // 2
        self.selection_time = None
        self.can_select = True
        self.cooldown = 300

        # item dimensions : each item should have 80% of the surface as height
        # and have the same width depending on the number of items
        self.height = self.display_surface.get_size()[1] * 0.8
        self.width = self.display_surface.get_size()[0] // (self.attribute_number + 1)
        self.create_items()


    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_select:
            if keys[pygame.K_RIGHT] and self.selection_index < self.attribute_number - 1:
                self.selection_index += 1
                self.can_select = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index > 0:
                self.selection_index -= 1
                self.can_select = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_select = False
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_index].upgrade_stat(self.player)

    def selection_cooldown(self):
        if not self.can_select:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= self.cooldown:
                self.can_select = True

    def create_items(self):
        self.item_list = []

        # create items and store them
        for item, index in enumerate(range(self.attribute_number)):
            # horizontal position
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attribute_number

            # item * increment : width of the rectangle,
            # (increment - self.width)//2 : offset (so that they are not directly next to each other)
            left = (item * increment) + (increment - self.width) // 2

            # vertical position
            # place the item on top of the screen with a 10% offset
            top = self.display_surface.get_size()[1] * 0.1

            item = Item(left, top, self.width, self.height, index, self.font)
            self.item_list.append(item)

    def display(self):
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            # get attributes
            name = self.attribute_names[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)

            item.display(self.display_surface, self.selection_index, name, value, max_value, cost)


# boxes of the upgrade class
class Item:
    def __init__(self, left, top, width, height, index, font):
        self.rect = pygame.Rect(left, top, width, height)
        self.index = index
        self.font = font

    def display_names(self, surface, name, cost, selected):
        # use the suitable color
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        # title text
        title_surf = self.font.render(name, False, color)
        # place the rectangle on the top
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0,20))

        # cost text
        cost_surf = self.font.render("Cost : " + str(int(cost)), False, color)
        cost_rect = cost_surf.get_rect(midbottom=self.rect.midbottom + pygame.math.Vector2(0,-20))

        # draw everything
        surface.blit(title_surf, title_rect)
        surface.blit(cost_surf, cost_rect)

    def display_bar(self, surface, value, max_value, selected):

        # drawing setup
        top = self.rect.midtop + pygame.math.Vector2(0,60)
        bottom = self.rect.midbottom + pygame.math.Vector2(0,-60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        # bar setup

        full_height = bottom[1] - top[1]
        rectangle_height = (value / max_value) * full_height

        value_rect = pygame.Rect(top[0] - UPGRADE_RECT_WIDTH//2, bottom[1] - rectangle_height, UPGRADE_RECT_WIDTH, UPGRADE_RECT_HEIGHT)

        # draw elements
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    def upgrade_stat(self, player):
        upgrade_attribute = list(player.stats.keys())[self.index]

        if player.exp >= player.upgrade_cost[upgrade_attribute] and \
                player.stats[upgrade_attribute] < player.max_stats[upgrade_attribute]:
            # upgrade a stat if possible, and make the cost greater
            player.exp -= player.upgrade_cost[upgrade_attribute]
            player.stats[upgrade_attribute] *= UPGRADE_RATIO

            if player.stats[upgrade_attribute] > player.max_stats[upgrade_attribute]:
                player.stats[upgrade_attribute] = player.max_stats[upgrade_attribute]

            player.upgrade_cost[upgrade_attribute] *= UPGRADE_COST_RATIO

    def display(self, surface, selection_number, name, value, max_value, cost):
        bg_color = UI_BG_COLOR
        border_color = UI_BORDER_COLOR

        if self.index == selection_number:
            bg_color = UPGRADE_BG_COLOR_SELECTED
            border_color = UI_BORDER_COLOR

        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 4)
        self.display_names(surface, name, cost, self.index == selection_number)
        self.display_bar(surface, value, max_value, self.index == selection_number)

