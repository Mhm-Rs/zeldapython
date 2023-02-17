import pygame
from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, groups,sprite_type, surface = pygame.Surface((TILESIZE,TILESIZE))):

        # add the tile to the group it belongs
        super().__init__(groups)

        # store the type of sprite
        self.sprite_type = sprite_type
        y_offset = HITBOX_OFFSET[sprite_type]

        # use the image that has been passed
        self.image = surface

        # position the rectangle of the image
        if(sprite_type == "object"):
            # apply an offset since the image is larger than 64x64
            self.rect = self.image.get_rect(topleft=(position[0], position[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=position)

        # get a rectangle shrinked by y pixels horizontally and x pixels vertically
        self.hitbox = self.rect.inflate(0, y_offset)
