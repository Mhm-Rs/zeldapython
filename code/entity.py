import pygame
from math import sin
# contains methods that will be used for both the player and the enemy


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # * MOVEMENT ATTRIBUTES

        # set a vector for the entity : x=0, y=0
        self.direction = pygame.math.Vector2()

        # index of the frame for animation
        self.frame_index = 0

        # speed of the animation
        self.animation_speed = 0.15

    def move(self, speed):
        # normalise the self.direction vector (get it back to 1) if the vector has any length
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # change the hitbox, so that it "moves" and then check for the collisions
        self.hitbox.x += self.direction.x * speed
        self.collision("horizontal")

        self.hitbox.y += self.direction.y * speed
        self.collision("vertical")

        # after checking for collisions, put the rectangle where the hitbox is
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        # check for a collision of the x axis
        if direction == "horizontal":
            for sprite in self.obstacle_sprites:
                if (sprite.hitbox.colliderect(self.hitbox)):
                    # if the entity is moving to the right, move it to the left side of the obstacle
                    if (self.direction.x > 0):
                        self.hitbox.right = sprite.hitbox.left
                    if (self.direction.x < 0):
                        self.hitbox.left = sprite.hitbox.right

        if direction == "vertical":
            # check for a collision of the y axis
            for sprite in self.obstacle_sprites:
                if (sprite.hitbox.colliderect(self.hitbox)):
                    # if the entity is moving down, move it to the top side of the obstacle
                    if (self.direction.y > 0):
                        self.hitbox.bottom = sprite.hitbox.top
                    if (self.direction.y < 0):
                        self.hitbox.top = sprite.hitbox.bottom

    def flicker_value(self):
        # flicker between 255 and 0 using the sin function
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0
