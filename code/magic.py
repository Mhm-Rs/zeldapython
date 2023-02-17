import pygame
from settings import *
from random import randint

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

        # sounds
        self.sounds = {
            "heal": pygame.mixer.Sound("../audio/heal.wav"),
            "flame": pygame.mixer.Sound("../audio/fire.wav")
        }

    def heal(self, player, strength, cost, groups):
        if player.energy >= cost and player.health < player.stats["health"]:
            # increase health and decrease energy
            player.health += strength
            player.energy -= cost
            if player.health >= player.stats["health"]:
                # if after healing there is too much health, go back to the max amount
                player.health = player.stats["health"]

            # play the aura and the heal animations
            self.sounds["heal"].play()
            self.animation_player.create_particles("aura", player.rect.center, groups)
            self.animation_player.create_particles("heal", player.rect.center + pygame.math.Vector2(0, -60), groups)

    def flame(self, player, cost, groups):
        if player.energy >= cost:
            # draw 5 flame animations in the direction the player is facing
            player.energy -= cost

            # get the direction (status without idle or attack)
            direction = player.status
            if "_idle" in direction:
                direction = direction.replace("_idle", "")
            elif "_attack" in direction:
                direction = direction.replace("_attack", "")

            # use math to figure out where to place the frames
            if direction == "right":
                math_direction = pygame.math.Vector2(1, 0)
            elif direction == "left":
                math_direction = pygame.math.Vector2(-1, 0)
            elif direction == "up":
                math_direction = pygame.math.Vector2(0, -1)
            else:
                math_direction = pygame.math.Vector2(0, 1)

            self.sounds["flame"].play()
            for i in range(1,6):
                if math_direction.x:
                    # horizontal placement
                    # place 5 flames next to each other and to the player
                    offset_x = TILESIZE * (math_direction.x * i)
                    # add a random offset to make the flames diverge
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles("flame", (x, y), groups)
                else:
                    # vertical placement
                    # place 5 flames next to each other and to the player
                    offset_y = TILESIZE * (math_direction.y * i)
                    # add a random offset to make the flames diverge
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles("flame", (x, y), groups)


